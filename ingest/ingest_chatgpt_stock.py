#!/usr/bin/env python3
"""Download a ChatGPT export from Drive and archive only stock-related material.

The runner, rather than the Agent, handles the large ZIP.  A stock-related
conversation is archived as a complete conversation (all mapping branches and
all message objects), so short follow-up messages cannot be lost by keyword
filtering.  Raw selected JSON is retained alongside readable transcripts.
No source text is truncated.  The source ZIP is optionally backed up to a
Release, never committed to Git.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlencode

ROOT = Path(__file__).resolve().parents[1]
OUT_REL = os.environ.get("OUT_DIR", "GPT股票记录入库")
OUT = Path(OUT_REL) if os.path.isabs(OUT_REL) else ROOT / OUT_REL
OUT_REL = os.path.relpath(OUT, ROOT) if OUT.is_relative_to(ROOT) else str(OUT)
SOURCE_IDS = [x.strip() for x in os.environ.get("SOURCE_IDS", "").split(",") if x.strip()]
SOURCE_MD5 = [x.strip().lower() for x in os.environ.get("SOURCE_MD5", "").split(",")]
SOURCE_RELEASE = os.environ.get("SOURCE_RELEASE", "").strip()
LOCAL_FILES = [x.strip() for x in os.environ.get("LOCAL_FILES", "").split(",") if x.strip()]
BACKUP = os.environ.get("BACKUP", "1") == "1"
OCR = os.environ.get("OCR", "1") == "1"
OCR_MIN_KB = float(os.environ.get("OCR_MIN_KB", "8"))
WORKERS = int(os.environ.get("WORKERS", "2"))  # kept in RUN for pipeline compatibility
CHECKPOINT_MIN = float(os.environ.get("CHECKPOINT_MIN", "10"))
TITLE = os.environ.get("TITLE", "ChatGPT 股票相关记录")
GIT_REF = os.environ.get("GIT_REF", "")
IN_ACTIONS = bool(os.environ.get("GITHUB_ACTIONS"))
RELEASE_TAG = os.environ.get("RELEASE_TAG", "files-gpt-stock-archive-2026-10-30")
WORK = Path(os.environ.get("WORK_DIR", "/tmp/gpt-stock-work"))
RAW = WORK / "raw"
UNPACK = WORK / "unpacked"
TMP = WORK / "tmp"
for p in (RAW, UNPACK, TMP):
    p.mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP)
T0 = time.time()
ERRORS: list[str] = []
MISSING_ASSETS: list[str] = []


def log(*args):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S"), *args, flush=True)


def run(cmd, timeout=600, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kwargs)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
    tmp.replace(path)


def status_note(text: str):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "_run_status.md").open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} {text}\n")


def git_commit_push(message: str):
    if not IN_ACTIONS or not GIT_REF or not OUT.is_relative_to(ROOT):
        return
    run(["git", "add", "--all", "--", OUT_REL], cwd=ROOT)
    result = run(["git", "commit", "-q", "-m", message], cwd=ROOT)
    if result.returncode != 0:
        return
    for attempt in range(4):
        run(["git", "pull", "-q", "--rebase", "-X", "theirs", "origin", GIT_REF], cwd=ROOT, timeout=300)
        pushed = run(["git", "push", "-q", "origin", f"HEAD:{GIT_REF}"], cwd=ROOT, timeout=300)
        if pushed.returncode == 0:
            log("pushed", message)
            return
        time.sleep(10 + attempt * 10)
    log("push failed; final workflow step will retry")


def abort(code: int, why: str):
    log("ABORT", why)
    status_note(f"**ABORT (exit {code})**：{why}")
    git_commit_push(f"GPT股票记录入库: ABORT {why[:70]}")
    raise SystemExit(code)


# ----------------------------- Drive download -----------------------------
def confirm_url(body: str, fid: str) -> str | None:
    from html.parser import HTMLParser

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.forms = []
            self.current = None

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "form":
                self.current = {"action": attrs.get("action", ""), "fields": {}}
                self.forms.append(self.current)
            elif tag == "input" and self.current is not None and attrs.get("name"):
                self.current["fields"][attrs["name"]] = attrs.get("value", "")

    parser = Parser()
    try:
        parser.feed(body)
    except Exception:
        return None
    for form in parser.forms:
        if "download" not in form["action"] and "uc?" not in form["action"]:
            continue
        fields = dict(form["fields"])
        fields.setdefault("id", fid)
        fields.setdefault("export", "download")
        fields.setdefault("confirm", "t")
        return form["action"] + ("&" if "?" in form["action"] else "?") + urlencode(fields)
    return None


def drive_download(fid: str, dest: Path) -> tuple[str, str | None]:
    import requests

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    name = fid
    expected = 0
    errors = []
    urls = [
        "https://drive.usercontent.google.com/download?id={id}&export=download&confirm=t",
        "https://drive.google.com/uc?export=download&id={id}&confirm=t",
    ]
    for attempt in range(6):
        for template in urls:
            url = template.format(id=fid)
            for hop in range(2):
                got = dest.stat().st_size if dest.exists() else 0
                request_headers = dict(headers)
                if got and (not expected or got < expected):
                    request_headers["Range"] = f"bytes={got}-"
                try:
                    with session.get(url, stream=True, timeout=(20, 180), headers=request_headers) as response:
                        if response.status_code == 416 and expected and got >= expected:
                            return name, None
                        if response.status_code not in (200, 206):
                            errors.append(f"HTTP {response.status_code}")
                            break
                        disposition = response.headers.get("Content-Disposition", "")
                        match = re.search(r"filename\*=UTF-8''([^;]+)", disposition) or re.search(r'filename="?([^";]+)"?', disposition)
                        if match:
                            name = unquote(match.group(1))
                            try:
                                name = name.encode("latin-1").decode("utf-8")
                            except (UnicodeEncodeError, UnicodeDecodeError):
                                pass
                        if "text/html" in response.headers.get("Content-Type", ""):
                            body = response.content[:400000].decode("utf-8", "ignore")
                            if any(x in body for x in ("ServiceLogin", "accounts.google.com", "Request access")):
                                return name, "NOT_SHARED: Drive returned a login/access page"
                            if "quota" in body.lower() or "too many users" in body.lower():
                                return name, "QUOTA_LOCKED: anonymous Drive download quota is locked"
                            next_url = confirm_url(body, fid)
                            if next_url and hop == 0 and next_url != url:
                                url = next_url
                                continue
                            errors.append("HTML instead of file")
                            break
                        mode = "ab" if response.status_code == 206 else "wb"
                        if mode == "wb":
                            got = 0
                        total = int(response.headers.get("Content-Length") or 0) + got
                        if not expected and total:
                            expected = total
                        with dest.open(mode) as f:
                            for chunk in response.iter_content(1 << 20):
                                if chunk:
                                    f.write(chunk)
                    size = dest.stat().st_size
                    if expected and size < expected:
                        errors.append(f"partial {size}/{expected}; resuming")
                        continue
                    return name, None
                except Exception as exc:
                    errors.append(f"{type(exc).__name__}: {str(exc)[:140]}")
                    break
        time.sleep(3 + attempt * 5)
    try:
        import gdown
        if dest.exists():
            dest.unlink()
        if gdown.download(id=fid, output=str(dest), quiet=True) and dest.stat().st_size:
            return name, None
    except Exception as exc:
        errors.append(f"gdown: {str(exc)[:140]}")
    return name, " | ".join(dict.fromkeys(errors)) or "download failed"


def resolve_source() -> tuple[str, Path]:
    if LOCAL_FILES:
        source = Path(LOCAL_FILES[0])
        if not source.is_file():
            abort(1, f"LOCAL_FILES not found: {source}")
        return source.name, source
    if SOURCE_RELEASE:
        release_dir = RAW / "release"
        shutil.rmtree(release_dir, ignore_errors=True)
        release_dir.mkdir(parents=True, exist_ok=True)
        result = run(["gh", "release", "download", SOURCE_RELEASE, "-D", str(release_dir), "--clobber"], cwd=ROOT, timeout=7200)
        if result.returncode != 0:
            abort(3, f"Release download failed: {(result.stderr or result.stdout)[-300:]}")
        sources = [p for p in release_dir.iterdir() if p.is_file()]
        if not sources:
            abort(3, "Release contained no source file")
        source = sources[0]
        if SOURCE_MD5 and re.fullmatch(r"[0-9a-f]{32}", SOURCE_MD5[0] or ""):
            actual = md5_file(source)
            log("MD5", actual)
            if actual != SOURCE_MD5[0]:
                abort(3, f"MD5 mismatch: {actual} != {SOURCE_MD5[0]}")
        return source.name, source
    if not SOURCE_IDS:
        abort(1, "SOURCE_IDS or SOURCE_RELEASE is required")
    fid = SOURCE_IDS[0]
    dest = RAW / (fid + ".zip")
    name, error = drive_download(fid, dest)
    if error:
        abort(2 if error.startswith("NOT_SHARED") else 3, f"Drive download failed: {error}")
    if SOURCE_MD5 and re.fullmatch(r"[0-9a-f]{32}", SOURCE_MD5[0] or ""):
        actual = md5_file(dest)
        log("MD5", actual)
        if actual != SOURCE_MD5[0]:
            abort(3, f"MD5 mismatch: {actual} != {SOURCE_MD5[0]}")
    return name, dest


def backup_source(name: str, source: Path):
    if SOURCE_RELEASE:
        return  # The source is already in this Release; do not upload it again.
    if not (BACKUP and IN_ACTIONS and shutil.which("gh")):
        return
    if run(["gh", "release", "view", RELEASE_TAG], cwd=ROOT).returncode != 0:
        result = run(["gh", "release", "create", RELEASE_TAG, "--title", "ChatGPT export source backup", "--notes", TITLE], cwd=ROOT)
        if result.returncode != 0:
            ERRORS.append("Release create failed: " + (result.stderr or result.stdout)[-300:])
            return
    result = run(["gh", "release", "upload", RELEASE_TAG, str(source), "--clobber"], cwd=ROOT, timeout=7200)
    if result.returncode != 0:
        ERRORS.append("Release upload failed: " + (result.stderr or result.stdout)[-300:])
    else:
        log("source backed up to Release", RELEASE_TAG)


# ----------------------------- ZIP and text -------------------------------
def fixed_name(info: zipfile.ZipInfo) -> str:
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode("cp437", "replace")
    for encoding in ("gb18030", "utf-8", "big5", "shift_jis"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return info.filename


def unzip_source(source: Path) -> int:
    if not zipfile.is_zipfile(source):
        abort(3, "source is not a valid ZIP")
    shutil.rmtree(UNPACK, ignore_errors=True)
    UNPACK.mkdir(parents=True)
    count = 0
    listing = []
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            name = fixed_name(info).replace("\\", "/")
            if info.is_dir() or name.startswith("__MACOSX/") or Path(name).name.startswith("._"):
                continue
            target = (UNPACK / name).resolve()
            if not str(target).startswith(str(UNPACK.resolve()) + os.sep):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target = target.with_name(target.name + "." + hashlib.sha1(name.encode()).hexdigest()[:8])
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst, 2 << 20)
            count += 1
            listing.append(f"{name}\t{info.file_size}")
    (OUT / "_zip_listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    log("unpacked members", count)
    return count


def decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "big5", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", "replace")


def read_text(path: Path) -> str:
    return decode_bytes(path.read_bytes())


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def part_text(part) -> str:
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        # Keep both human-readable text and asset references in the readable copy.
        if isinstance(part.get("text"), str):
            return part["text"]
        return json_text(part)
    return json_text(part)


def message_content(message: dict) -> str:
    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if not isinstance(content, dict):
        return json_text(content)
    pieces = []
    if isinstance(content.get("parts"), list):
        pieces.extend(part_text(p) for p in content["parts"])
    elif isinstance(content.get("parts"), (str, dict)):
        pieces.append(part_text(content["parts"]))
    for key in ("text", "result", "thoughts", "summary", "code", "args", "request", "response"):
        if key in content and content[key] is not None and key != "parts":
            value = content[key]
            pieces.append(value if isinstance(value, str) else json_text(value))
    if pieces:
        return "\n".join(pieces)
    return json_text(content)


def message_rows(conversation: dict) -> list[dict]:
    rows = []
    mapping = conversation.get("mapping")
    if isinstance(mapping, dict):
        for order, (node_id, node) in enumerate(mapping.items()):
            if not isinstance(node, dict) or not isinstance(node.get("message"), dict):
                continue
            message = node["message"]
            author = message.get("author") or {}
            rows.append({
                "node_id": node_id,
                "message": message,
                "role": author.get("role", "unknown") if isinstance(author, dict) else str(author),
                "time": message.get("create_time") or 0,
                "order": order,
            })
    elif isinstance(conversation.get("messages"), list):
        for order, message in enumerate(conversation["messages"]):
            if not isinstance(message, dict):
                continue
            author = message.get("author") or {}
            rows.append({
                "node_id": str(message.get("id", order)),
                "message": message,
                "role": author.get("role", message.get("role", "unknown")) if isinstance(author, dict) else str(author),
                "time": message.get("create_time") or 0,
                "order": order,
            })
    rows.sort(key=lambda r: (r["time"] or 0, r["order"]))
    return rows


def conversation_search_text(conversation: dict) -> str:
    rows = message_rows(conversation)
    # Include all textual fields as a fallback for nonstandard export content.
    return "\n".join([
        str(conversation.get("title", "")),
        "\n".join(message_content(r["message"]) for r in rows),
        json_text({k: v for k, v in conversation.items() if k not in ("mapping", "messages")}),
    ])


# Direct stock/investment terms are deliberately high recall.  A conversation
# is the selection unit; ambiguous standalone files require the same matcher.
STRONG_TERMS = [
    "股票", "股市", "股价", "股指", "股东", "股息", "分红", "派息", "回购", "注销",
    "持仓", "建仓", "加仓", "减仓", "清仓", "仓位", "涨停", "跌停", "做t", "做T",
    "盘前", "盘后", "收盘", "开盘", "复盘", "看盘", "k线", "K线", "日线", "周线", "月线",
    "均线", "成交量", "量能", "换手率", "市盈率", "市净率", "估值", "财报", "年报", "季报",
    "归母", "扣非", "净利润", "营收", "业绩预告", "上市公司", "证券", "券商", "交易所",
    "沪深", "a股", "A股", "港股", "美股", "港股通", "纳斯达克", "标普", "道琼斯", "etf", "ETF",
    "ipo", "IPO", "吸筹", "主力资金", "北向资金", "融资融券", "交割单", "大盘", "板块",
    "牛市", "熊市", "成本价", "浮盈", "浮亏", "市值", "止盈", "止损", "割肉", "套牢", "抄底",
    "追涨", "杀跌", "支撑位", "压力位", "投资", "定投", "价值投资", "收息", "资产配置", "投资组合",
    "海澜之家", "海澜", "海尔智家", "海尔", "格力电器", "云铝股份", "五粮液", "顺丰控股",
    "汇川技术", "迈瑞医疗", "江西铜业", "华能蒙电", "工业富联", "中国铝业", "紫金矿业",
    "中国银行", "泸州老窖", "美的集团", "贵州茅台", "宁德时代", "比亚迪", "腾讯控股", "阿里巴巴",
    "东方财富", "同花顺", "招商银行", "中国平安", "中国神华", "中远海控", "中芯国际", "中际旭创",
    "新易盛", "沪电股份", "立讯精密", "恒瑞医药", "药明康德", "中国中免", "谷歌", "微软", "英伟达",
    "特斯拉", "亚马逊", "台积电", "英伟达", "纳斯达克", "标准普尔", "股票账户", "证券交易",
    "stock", "stocks", "equity", "equities", "dividend", "dividends", "buyback", "repurchase",
    "earnings", "ticker", "market cap", "portfolio", "nasdaq", "nyse", "hkex", "etf", "ipo",
    "p/e", "peg", "eps", "roe", "dps", "dcf", "bullish", "bearish", "short squeeze",
    "call option", "put option", "GOOG", "GOOGL", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META",
    "AMD", "AVGO", "NFLX", "TSM", "HLA", "SLA", "GTC", "MA20", "MA40", "MACD", "RSI", "KDJ",
    "CMF", "POC", "SAR", "PE", "PB", "ROE", "EPS", "DPS",
]
# Remove duplicate literal terms while retaining deterministic longest-first matching.
STRONG_TERMS = sorted(set(STRONG_TERMS), key=len, reverse=True)
def _term_pattern(term: str) -> str:
    # ASCII acronyms such as PE/ROE must not match inside ordinary English words.
    if re.fullmatch(r"[A-Za-z0-9/.\-]+", term):
        return r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
    return re.escape(term)

TERM_RE = re.compile("|".join(_term_pattern(x) for x in STRONG_TERMS), re.IGNORECASE)
TICKER_RE = re.compile(r"(?<!\d)(?:000|001|002|003|300|301|600|601|603|605|688|689|830|831|832|833|834|835|836|837|838|839|870|871|872|873|874|875|876|877|878|879|920)\d{3}(?!\d)")
EN_TICKER_RE = re.compile(r"(?<![A-Za-z0-9])(?:GOOG|GOOGL|AAPL|MSFT|NVDA|TSLA|AMZN|META|AMD|AVGO|NFLX|TSM|HLA|SLA)(?![A-Za-z0-9])")


def stock_hits(text: str) -> list[str]:
    hits = {m.group(0) for m in TERM_RE.finditer(text)}
    hits.update(m.group(0) for m in TICKER_RE.finditer(text))
    hits.update(m.group(0) for m in EN_TICKER_RE.finditer(text))
    return sorted(hits, key=str.lower)


def is_stock_text(text: str) -> bool:
    return bool(stock_hits(text))


def safe_name(value: str, limit=90) -> str:
    value = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "_", value, flags=re.UNICODE).strip("._")
    return (value or "untitled")[:limit]


def asset_refs(value, refs: set[str], key: str = ""):
    if isinstance(value, dict):
        for k, v in value.items():
            asset_refs(v, refs, str(k).lower())
    elif isinstance(value, list):
        for v in value:
            asset_refs(v, refs, key)
    elif isinstance(value, str):
        if key in {"asset_pointer", "file_id", "attachment_id", "filename", "file_name"}:
            refs.add(value)
        elif key in {"url", "download_url"} and ("file" in value or "asset" in value or "sediment" in value):
            refs.add(value)
        for match in re.finditer(r"(?:file[-_][A-Za-z0-9_-]+|sediment://[^\s\"'<>]+|file-service://[^\s\"'<>]+)", value):
            refs.add(match.group(0))


def referenced_path(path: Path, refs: set[str]) -> bool:
    if not refs:
        return False
    rel = str(path.relative_to(UNPACK)).replace("\\", "/")
    base = path.name
    for ref in refs:
        token = ref.rsplit("/", 1)[-1].split("?", 1)[0]
        if not token:
            continue
        if token in rel or token in base or ref in rel:
            return True
        # Export asset pointers sometimes omit an extension or use a UUID only.
        stem = Path(token).stem
        if len(stem) >= 8 and stem in rel:
            return True
    return False


def extract_document(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext in {".txt", ".md", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml", ".log", ".py", ".js", ".html", ".htm"}:
        if ext in {".html", ".htm"}:
            try:
                from bs4 import BeautifulSoup
                return BeautifulSoup(read_text(path), "html.parser").get_text("\n"), "beautifulsoup"
            except Exception:
                pass
        return read_text(path), "text"
    if ext == ".docx":
        import docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        document = docx.Document(path)
        out = []
        for element in document.element.body.iterchildren():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "p":
                out.append(Paragraph(element, document).text)
            elif tag == "tbl":
                for row in Table(element, document).rows:
                    out.append(" | ".join(cell.text for cell in row.cells))
        for section in document.sections:
            for part in (section.header, section.footer):
                out.extend(p.text for p in part.paragraphs)
        return "\n".join(out), "python-docx"
    if ext in {".xlsx", ".xlsm"}:
        import openpyxl
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
        out = []
        for sheet in workbook.worksheets:
            out.append(f"## sheet: {sheet.title} ({sheet.sheet_state})")
            for row in sheet.iter_rows(values_only=True):
                out.append("\t".join("" if v is None else str(v) for v in row))
        return "\n".join(out), "openpyxl"
    if ext == ".xls":
        import xlrd
        workbook = xlrd.open_workbook(path, formatting_info=False)
        out = []
        for sheet in workbook.sheets():
            out.append(f"## sheet: {sheet.name}")
            for row in range(sheet.nrows):
                out.append("\t".join(str(v) for v in sheet.row_values(row)))
        return "\n".join(out), "xlrd"
    if ext == ".pdf":
        import pdfplumber
        out = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                out.append(f"--- page {i} ---")
                out.append(page.extract_text() or "")
                for table in page.extract_tables() or []:
                    out.extend(" | ".join("" if c is None else str(c) for c in row) for row in table)
        text = "\n".join(out)
        if OCR and shutil.which("pdftoppm") and len(re.sub(r"\W", "", text)) < 30 * max(1, len(out)):
            image_dir = TMP / ("pdf_" + hashlib.sha1(str(path).encode()).hexdigest()[:12])
            image_dir.mkdir(parents=True, exist_ok=True)
            run(["pdftoppm", "-r", "200", "-png", str(path), str(image_dir / "page")], timeout=1800)
            ocr = []
            for image in sorted(image_dir.glob("*.png")):
                result = run(["tesseract", str(image), "stdout", "-l", "chi_sim+eng", "--psm", "6"], timeout=300)
                ocr.append(f"--- {image.name} ---\n{result.stdout}")
            if ocr:
                text += "\n" + "\n".join(ocr)
            shutil.rmtree(image_dir, ignore_errors=True)
        return text, "pdfplumber+ocr-if-needed"
    if ext == ".pptx":
        from pptx import Presentation
        presentation = Presentation(path)
        out = []
        for i, slide in enumerate(presentation.slides, 1):
            out.append(f"--- slide {i} ---")
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False):
                    out.append(shape.text_frame.text)
                if getattr(shape, "has_table", False):
                    for row in shape.table.rows:
                        out.append(" | ".join(cell.text for cell in row.cells))
            if slide.has_notes_slide:
                out.append(slide.notes_slide.notes_text_frame.text)
        return "\n".join(out), "python-pptx"
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".gif"}:
        if OCR and path.stat().st_size >= OCR_MIN_KB * 1024 and shutil.which("tesseract"):
            result = run(["tesseract", str(path), "stdout", "-l", "chi_sim+eng", "--psm", "6"], timeout=300)
            return result.stdout, "tesseract"
        return "", "metadata-only"
    return "", "metadata-only"


def copy_attachment(source: Path, relative: str, text: str, method: str, reason: str) -> dict:
    destination = OUT / "附加文件" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    record = {
        "source_path": relative,
        "file": str(destination.relative_to(OUT)).replace("\\", "/"),
        "bytes": source.stat().st_size,
        "sha256": sha256_file(source),
        "reason": reason,
        "extraction_method": method,
    }
    if text:
        text_path = destination.with_name(destination.name + ".txt")
        text_path.write_text(text, encoding="utf-8")
        record["text_file"] = str(text_path.relative_to(OUT)).replace("\\", "/")
        record["text_chars"] = len(text)
    return record


def conversation_list(value):
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        if isinstance(value.get("conversations"), list):
            return [x for x in value["conversations"] if isinstance(x, dict)]
        if "mapping" in value or "messages" in value:
            return [value]
    return []


def load_conversations(paths: list[Path]) -> list[dict]:
    conversations = []
    for path in paths:
        try:
            value = json.loads(read_text(path))
            conversations.extend(conversation_list(value))
        except Exception as exc:
            abort(4, f"cannot decode {path.name}: {type(exc).__name__}: {exc}")
    return conversations


def archive_conversations(conversations: list[dict]) -> tuple[list[dict], set[str], int]:
    selected = []
    all_message_count = 0
    refs: set[str] = set()
    for conversation in conversations:
        rows = message_rows(conversation)
        all_message_count += len(rows)
        hits = stock_hits(conversation_search_text(conversation))
        if not hits:
            continue
        selected.append((conversation, rows, hits))
        asset_refs(conversation, refs)
    records = []
    for index, (conversation, rows, hits) in enumerate(selected, 1):
        cid = str(conversation.get("conversation_id") or conversation.get("id") or f"conversation-{index}")
        title = str(conversation.get("title") or "untitled")
        base = f"{index:04d}_{safe_name(title, 65)}_{safe_name(cid, 18)}"
        raw_path = OUT / "会话原始JSON" / (base + ".json")
        text_path = OUT / "会话全文" / (base + ".md")
        # The original object is serialized without deleting or rewriting any fields.
        write_json(raw_path, conversation)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        with text_path.open("w", encoding="utf-8") as out:
            out.write(f"# {title}\n\n")
            out.write(f"- 会话ID：`{cid}`\n- 选中原因：{', '.join(hits)}\n- 原始消息数：{len(rows)}\n")
            out.write("- 保留范围：该命中会话的全部 mapping 分支、全部角色消息；原始字段见同名 JSON。\n\n")
            for number, row in enumerate(rows, 1):
                message = row["message"]
                mid = str(message.get("id", row["node_id"]))
                role = row["role"]
                content = message_content(message)
                out.write(f"\n===== MESSAGE {number} | role={role} | id={mid} | node={row['node_id']} =====\n")
                out.write(content)
                out.write(f"\n===== END MESSAGE {number} =====\n")
        records.append({
            "conversation_id": cid,
            "title": title,
            "raw_file": str(raw_path.relative_to(OUT)).replace("\\", "/"),
            "text_file": str(text_path.relative_to(OUT)).replace("\\", "/"),
            "message_count": len(rows),
            "text_chars": sum(len(message_content(r["message"])) for r in rows),
            "matched_terms": hits,
            "raw_sha256": sha256_file(raw_path),
        })
    return records, refs, all_message_count


def archive_other_files(refs: set[str], conversation_paths: list[Path]) -> tuple[list[dict], int]:
    records = []
    scanned = 0
    conversation_paths = {p.resolve() for p in conversation_paths}
    for source in sorted(UNPACK.rglob("*")):
        if not source.is_file() or source.resolve() in conversation_paths:
            continue
        relative_path = source.relative_to(UNPACK)
        relative = str(relative_path).replace("\\", "/")
        if relative.startswith("__MACOSX/") or source.name in {"chat.html", "user.json", "message_feedback.json"}:
            continue
        scanned += 1
        referenced = referenced_path(source, refs)
        text = ""
        method = "not-needed"
        # A referenced attachment belongs to a selected stock conversation.  For
        # unreferenced files, inspect content/OCR before allowing it into the archive.
        try:
            if referenced:
                text, method = extract_document(source)
            elif source.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".gif"}:
                text, method = extract_document(source)
            else:
                text, method = extract_document(source)
        except Exception as exc:
            ERRORS.append(f"{relative}: {type(exc).__name__}: {str(exc)[:240]}")
            if not referenced:
                continue
        related = referenced or is_stock_text(relative + "\n" + text)
        if not related:
            continue
        records.append(copy_attachment(source, relative, text, method, "selected conversation attachment" if referenced else "standalone stock content"))
    return records, scanned


def write_reports(source_name: str, source: Path, member_count: int, total_conversations: int,
                  total_messages: int, records: list[dict], attachments: list[dict], scanned: int):
    selected_messages = sum(r["message_count"] for r in records)
    manifest = {
        "schema": "gpt-stock-archive-v1",
        "title": TITLE,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "name": source_name,
            "bytes": source.stat().st_size,
            "md5": md5_file(source),
            "sha256": sha256_file(source),
            "zip_members_extracted": member_count,
            "backup_release": RELEASE_TAG if BACKUP else None,
        },
        "selection": {
            "unit": "conversation",
            "rule": "Any high-recall stock/investment term, stock company name, or stock ticker in title/message/metadata selects the complete conversation. Unmatched conversations are not archived.",
            "context_preserved": True,
            "raw_json_fields_preserved": True,
            "text_truncated": False,
            "all_mapping_branches_included": True,
        },
        "counts": {
            "total_conversations": total_conversations,
            "total_messages_in_source_conversations": total_messages,
            "selected_conversations": len(records),
            "unselected_conversations": total_conversations - len(records),
            "selected_messages": selected_messages,
            "selected_message_characters": sum(r["text_chars"] for r in records),
            "standalone_files_scanned": scanned,
            "attachments_archived": len(attachments),
            "errors": len(ERRORS),
            "missing_asset_references": len(MISSING_ASSETS),
        },
        "conversations": records,
        "attachments": attachments,
        "errors": ERRORS,
        "missing_asset_references": MISSING_ASSETS,
    }
    write_json(OUT / "manifest.json", manifest)
    coverage = [
        "# 入库覆盖率与完整性核对", "",
        f"- 来源：`{source_name}`",
        f"- ZIP：{source.stat().st_size:,} bytes；MD5 `{md5_file(source)}`；SHA256 `{sha256_file(source)}`",
        f"- 解压成员：{member_count:,}；源会话：{total_conversations:,}；源消息：{total_messages:,}",
        f"- 命中并完整入库会话：**{len(records):,}**；未命中会话：{total_conversations - len(records):,}",
        f"- 入库消息：**{selected_messages:,}**；消息正文字符：{sum(r['text_chars'] for r in records):,}",
        f"- 其他文件扫描：{scanned:,}；股票相关附件/文件入库：{len(attachments):,}",
        f"- 原始 JSON：逐会话保存，字段不删减；全文 Markdown：逐消息保存；未使用字符截断。",
        f"- 抽取错误：{len(ERRORS)}；缺失附件引用：{len(MISSING_ASSETS)}", "",
        "## 逐会话核对", "",
        "| # | 会话ID | 消息数 | 正文字符 | 原始JSON | 全文 |",
        "|---:|---|---:|---:|---|---|",
    ]
    for i, record in enumerate(records, 1):
        coverage.append(f"| {i} | `{record['conversation_id']}` | {record['message_count']} | {record['text_chars']:,} | `{record['raw_file']}` | `{record['text_file']}` |")
    if ERRORS:
        coverage += ["", "## 错误（原始文件仍保留时已注明）", ""] + [f"- {e}" for e in ERRORS]
    if MISSING_ASSETS:
        coverage += ["", "## 未在 ZIP 找到的附件引用", ""] + [f"- `{x}`" for x in MISSING_ASSETS]
    (OUT / "_coverage.md").write_text("\n".join(coverage) + "\n", encoding="utf-8")
    readme = f"""# GPT 股票相关记录入库

来源：ChatGPT 完整导出 ZIP（{source_name}）。本目录只接收命中股票/证券投资主题的会话及其关联附件；未命中会话不复制到本目录。

## 目录

- `会话原始JSON/`：每个命中会话的完整原始对象，保留所有字段、所有 mapping 分支、全部角色消息和工具内容。
- `会话全文/`：同一会话的逐消息可读全文；消息正文不截断，原始 JSON 是字段级权威底稿。
- `附加文件/`：命中会话引用的附件，以及独立扫描后命中股票主题的文件；原始字节复制，能抽取文字的旁边附 `.txt`。
- `manifest.json`：来源 MD5/SHA256、逐会话路径、消息数、字符数、附件哈希和选择命中词。
- `_coverage.md`：总量与逐会话完整性核对。

## 选择口径

以**完整会话**为最小保留单位：标题、任意消息或会话元数据命中股票/证券投资词、公司名称或股票代码，即将该会话全部消息保留。这样不会把“继续”“按刚才说的做”等没有重复关键词的后续上下文删掉。完全不命中的会话不入库。独立文件只有在文件内容/OCR命中，或被命中会话引用时才入库。

这是一份原始资料归档，不是摘要，也不是投资建议。后续分析引用时应回到具体会话 JSON/Markdown 和本目录的持仓事实卡核对时点。

生成时间：{datetime.now(timezone.utc).isoformat()}。
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    status_note("START " + TITLE)
    source_name, source = resolve_source()
    log("source", source_name, source.stat().st_size)
    status_note(f"SOURCE {source_name}；{source.stat().st_size} bytes")
    backup_source(source_name, source)
    member_count = unzip_source(source)
    conversation_paths = sorted(UNPACK.rglob("conversations.json"))
    if not conversation_paths:
        abort(4, "no conversations.json found; refusing to substitute a partial HTML extraction")
    conversations = load_conversations(conversation_paths)
    if not conversations:
        abort(4, "conversations.json decoded but contained no conversation objects")
    log("conversations", len(conversations))
    records, refs, total_messages = archive_conversations(conversations)
    log("selected conversations", len(records), "asset refs", len(refs))
    attachments, scanned = archive_other_files(refs, conversation_paths)
    # Check references only for diagnostics; raw selected JSON still retains every pointer.
    for ref in sorted(refs):
        token = ref.rsplit("/", 1)[-1].split("?", 1)[0]
        if len(token) < 8:
            continue
        if not any(token in str(p.relative_to(UNPACK)) for p in UNPACK.rglob("*") if p.is_file()):
            MISSING_ASSETS.append(ref)
    write_reports(source_name, source, member_count, len(conversations), total_messages, records, attachments, scanned)
    status_note(f"DONE selected {len(records)}/{len(conversations)} conversations; {sum(r['message_count'] for r in records)} messages; attachments {len(attachments)}; errors {len(ERRORS)}")
    total_bytes = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    log("output", total_bytes, "bytes", "files", sum(1 for p in OUT.rglob("*") if p.is_file()))
    git_commit_push(f"GPT股票记录入库: {len(records)} 会话 / {sum(r['message_count'] for r in records)} 消息")
    log("done in", int(time.time() - T0), "seconds")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        log(traceback.format_exc())
        status_note("**CRASH**\n```\n" + traceback.format_exc()[-4000:] + "\n```")
        git_commit_push("GPT股票记录入库: CRASH")
        raise
