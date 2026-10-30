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
ASSET_NAME_MAP: dict[str, str] = {}


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
                "node": node,
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
                "node": {"message": message},
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
    if term == "做T":
        return r"(?<![A-Za-z])做[Tt](?![A-Za-z])"
    if re.fullmatch(r"[A-Za-z0-9/.\-]+", term):
        return r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
    return re.escape(term)

TERM_RE = re.compile("|".join(_term_pattern(x) for x in STRONG_TERMS), re.IGNORECASE)
TICKER_RE = re.compile(r"(?<!\d)(?:000|001|002|003|300|301|600|601|603|605|688|689|830|831|832|833|834|835|836|837|838|839|870|871|872|873|874|875|876|877|878|879|920)\d{3}(?!\d)")
EN_TICKER_RE = re.compile(r"(?<![A-Za-z0-9])(?:GOOG|GOOGL|AAPL|MSFT|NVDA|TSLA|AMZN|META|AMD|AVGO|NFLX|TSM)(?![A-Za-z0-9])")


def stock_hits(text: str) -> list[str]:
    hits = {m.group(0) for m in TERM_RE.finditer(text)}
    hits.update(m.group(0) for m in TICKER_RE.finditer(text))
    hits.update(m.group(0) for m in EN_TICKER_RE.finditer(text))
    return sorted(hits, key=str.lower)


CORE_TERMS = [
    "股票", "股市", "股价", "股息", "分红", "派息", "股票账户", "证券交易", "证券", "券商", "交易所",
    "A股", "港股", "美股", "港股通", "沪深", "纳斯达克", "标普", "道琼斯", "ETF", "IPO", "涨停", "跌停",
    "做T", "持仓", "建仓", "加仓", "减仓", "清仓", "仓位", "K线", "日线", "周线", "月线", "均线", "成交量",
    "换手率", "市盈率", "市净率", "估值", "财报", "归母", "扣非", "业绩预告", "吸筹", "主力资金", "北向资金",
    "融资融券", "交割单", "大盘", "牛市", "熊市", "浮盈", "浮亏", "止损", "止盈", "套牢", "抄底", "追涨",
    "杀跌", "支撑位", "压力位", "收息", "定投", "价值投资", "投资组合", "市值", "回购", "盘前",
    "盘后", "收盘", "开盘", "看盘", "量能", "dividend", "dividends", "buyback", "repurchase", "earnings",
    "海澜之家", "海尔智家", "格力电器", "云铝股份", "五粮液", "顺丰控股", "汇川技术", "迈瑞医疗", "江西铜业",
    "华能蒙电", "工业富联", "中国铝业", "紫金矿业", "中国银行", "泸州老窖", "美的集团", "贵州茅台", "宁德时代",
    "比亚迪", "腾讯控股", "东方财富", "同花顺", "招商银行", "中国平安", "中国神华", "中远海控", "中芯国际",
    "中际旭创", "新易盛", "沪电股份", "立讯精密", "恒瑞医药", "药明康德", "中国中免", "台积电",
]
SUPPORT_TERMS = [
    "投资", "营收", "净利润", "年报", "季报", "复盘", "板块", "成本价", "股东", "资产配置", "stock", "stocks", "portfolio", "equity",
    "POC", "PoC", "SLA", "Meta", "PE", "PB", "ROE", "EPS", "DPS", "GTC", "MA20", "MA40", "MACD", "RSI", "KDJ",
    "SAR", "HLA", "GOOG", "GOOGL", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "AMD", "AVGO", "NFLX", "TSM",
    "谷歌", "微软", "英伟达", "特斯拉", "亚马逊", "阿里巴巴", "海澜", "海尔", "美团", "福特",
]
CORE_RE = re.compile("|".join(_term_pattern(x) for x in sorted(set(CORE_TERMS), key=len, reverse=True)), re.IGNORECASE)
SUPPORT_RE = re.compile("|".join(_term_pattern(x) for x in sorted(set(SUPPORT_TERMS), key=len, reverse=True)), re.IGNORECASE)
TITLE_RE = re.compile(r"股票|股市|股价|ETF|美股|港股|A股|投资|分红|收息|股权|持仓|仓位|估值|财报|QDII|SCHG|SCHB|HPQ|HPE|NVO|DOW|BOC|GLW|TCAI|CHPS|EUV|CBRS|长牛|多头|空头|波段|财富|财商|FIRE|被动收入|资产配置|美团|福特|四大行|长电|海澜|海尔|五粮液|铝价|强股|资本流动", re.IGNORECASE)
NONSTOCK_CONTEXT_RE = re.compile(r"PoE|DWDM|SEO|交换机|路由器|光模块|客户|报价|出口|增值税|健康|饮食|尿道|婚姻|孩子|旅行|WhatsApp|Playwright|Selenium|HTML|CSS|token|Claude|Arena|Steam|英语|域名|账号|FIPS|认证|无人机|光纤|MSTP|Centec|Marvell|Olycom|Netas|Saga|Sales Engineer|领英|LinkedIn|FAQ|产品规格|宣传文案", re.IGNORECASE)
NONSTOCK_MESSAGE_RE = re.compile(r"PoE|DWDM|SEO|交换机|路由器|光模块|光通信|NDAA|consignment|授权|供应商|订单|军工|出口|税务|法律|客户|无人机|光纤|MSTP|Centec|Marvell|Olycom|Netas|Saga|Sales Engineer|领英|LinkedIn|WhatsApp|饮食|尿道|婚姻|孩子|旅行|域名|账号|Steam|Playwright|Claude|Arena|HTML|CSS|token|英语|FAQ|报价|采购|库存|白酒|茅台酒|酿造|酒精|礼品卡", re.IGNORECASE)
HARD_MARKET_RE = re.compile(r"股票|股市|股价|股息|持仓|建仓|加仓|减仓|清仓|涨停|跌停|K线|均线|成交量|换手率|市盈率|市净率|吸筹|主力资金|北向资金|融资融券|交割单|做[Tt](?![A-Za-z])|止损|止盈|浮盈|浮亏|牛市|熊市|大盘|美股|港股|A股|ETF|IPO|纳斯达克|道琼斯|标普|证券|券商|交易所|收息|定投|价值投资|归母|扣非|财报|股票账户|证券交易", re.IGNORECASE)
EXPLICIT_STOCK_RE = re.compile(r"股价|股息率|股票投资|股票分红|买股票|股票分析|股票研究|股票策略|股票交易|股票市场|A股|港股|美股|ETF|IPO|纳斯达克|道琼斯|标普", re.IGNORECASE)
COMPANY_CONTEXT_RE = re.compile(r"海澜之家|海尔智家|格力电器|云铝股份|五粮液|顺丰控股|汇川技术|迈瑞医疗|江西铜业|华能蒙电|工业富联|中国铝业|紫金矿业|中国银行|泸州老窖|美的集团|贵州茅台|宁德时代|比亚迪|腾讯控股|东方财富|同花顺|招商银行|中国平安|中国神华|中远海控|中芯国际|中际旭创|新易盛|沪电股份|立讯精密|恒瑞医药|药明康德|中国中免")


def relevance(text: str, title: str = "") -> tuple[bool, list[str]]:
    core = {m.group(0) for m in CORE_RE.finditer(text)}
    support = {m.group(0) for m in SUPPORT_RE.finditer(text)}
    tickers = {m.group(0) for m in TICKER_RE.finditer(text)}
    tickers.update(m.group(0) for m in EN_TICKER_RE.finditer(text))
    hits = sorted(core | support | tickers, key=str.lower)
    if NONSTOCK_MESSAGE_RE.search(text):
        market_score = len(HARD_MARKET_RE.findall(text)) + (1 if COMPANY_CONTEXT_RE.search(text) else 0)
        if not EXPLICIT_STOCK_RE.search(text) and market_score < 2:
            return False, hits
    if core:
        return True, hits
    title_stock = bool(TITLE_RE.search(title) or TICKER_RE.fullmatch(title.strip()) or EN_TICKER_RE.fullmatch(title.strip()))
    invest = {x.lower() for x in support} & {"投资", "stock", "stocks", "portfolio", "equity", "资产配置", "投资组合"}
    finance = {x.lower() for x in support} & {"净利润", "年报", "季报", "pe", "pb", "roe", "eps", "dps"}
    if tickers and (title_stock or invest or finance):
        return True, hits
    if invest and finance:
        return True, hits
    return False, hits


def is_stock_text(text: str) -> bool:
    return relevance(text)[0]


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
        if key in {"asset_pointer", "file_id", "attachment_id"}:
            if not value.startswith(("http://", "https://")) and value not in {"file_path", "file-service"}:
                refs.add(value)
        elif key in {"filename", "file_name"}:
            if not value.startswith(("http://", "https://")) and value not in {"file_path", "file-service"}:
                refs.add(value)
        elif key in {"url", "download_url"} and value.startswith(("sediment://", "file-service://")):
            refs.add(value)
        scan_value = re.sub(r"https?://[^\s\"'<>]+", "", value)
        for match in re.finditer(r"(?<![A-Za-z0-9])(?:file_(?:[A-Za-z0-9_-]+)|file-(?!service\b)[A-Za-z0-9_-]+|sediment://[^\s\"'<>]+|file-service://[^\s\"'<>]+)", scan_value):
            refs.add(match.group(0))


def load_asset_name_map():
    path = UNPACK / "conversation_asset_file_names.json"
    if not path.is_file():
        return
    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        ERRORS.append(f"conversation_asset_file_names.json: {type(exc).__name__}: {exc}")
        return

    def walk(value, hint=""):
        if isinstance(value, dict):
            local_id = next((value[k] for k in ("file_id", "asset_pointer", "attachment_id", "id") if isinstance(value.get(k), str)), hint)
            local_name = next((value[k] for k in ("file_name", "filename", "name", "original_filename") if isinstance(value.get(k), str)), "")
            if local_id and local_name and re.search(r"file[_-][A-Za-z0-9_-]+", local_id):
                ASSET_NAME_MAP[local_id] = local_name
            for key, child in value.items():
                if isinstance(child, str) and re.search(r"file[_-][A-Za-z0-9_-]+", str(key)):
                    ASSET_NAME_MAP[str(key)] = child
                walk(child, str(key))
        elif isinstance(value, list):
            for child in value:
                walk(child, hint)

    walk(data)
    log("asset filename mappings", len(ASSET_NAME_MAP))


def mapped_asset_name(ref: str) -> str:
    candidates = [ref, ref.rsplit("/", 1)[-1]]
    match = re.search(r"file[_-][A-Za-z0-9_-]+", ref)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        if candidate in ASSET_NAME_MAP:
            return ASSET_NAME_MAP[candidate]
    return ""


def asset_name_for_path(path: Path) -> str:
    name = path.name
    for key, value in ASSET_NAME_MAP.items():
        token = key.rsplit("/", 1)[-1]
        if token and (token in name or token in str(path)):
            return value
    return ""


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
        mapped = mapped_asset_name(ref)
        if mapped and (mapped in rel or Path(mapped).name in base):
            return True
        # Export asset pointers sometimes omit an extension or use a UUID only.
        stem = Path(token).stem
        if len(stem) >= 8 and stem in rel:
            return True
    return False


def extract_document(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext == ".dat":
        # ChatGPT exports often store attachments as extensionless .dat files.
        with path.open("rb") as head_file:
            head = head_file.read(16)
        if head.startswith(b"\x89PNG"):
            ext = ".png"
        elif head.startswith(b"\xff\xd8\xff"):
            ext = ".jpg"
        elif head.startswith((b"GIF87a", b"GIF89a")):
            ext = ".gif"
        elif head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            ext = ".webp"
        elif head.startswith(b"%PDF"):
            ext = ".pdf"
        elif head.startswith(b"PK"):
            try:
                with zipfile.ZipFile(path) as z:
                    names = z.namelist()
                if any(x.startswith("word/") for x in names):
                    ext = ".docx"
                elif any(x.startswith("xl/") for x in names):
                    ext = ".xlsx"
                elif any(x.startswith("ppt/") for x in names):
                    ext = ".pptx"
            except Exception:
                pass
        else:
            # Textual .dat attachments are still fully inspected.
            try:
                sample = path.read_bytes()
                sample.decode("utf-8")
                ext = ".txt"
            except UnicodeDecodeError:
                pass
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
        out = []
        with path.open("rb") as workbook_file:
            workbook = openpyxl.load_workbook(workbook_file, read_only=True, data_only=False)
            for sheet in workbook.worksheets:
                out.append(f"## sheet: {sheet.title} ({sheet.sheet_state})")
                for row in sheet.iter_rows(values_only=True):
                    out.append("\t".join("" if v is None else str(v) for v in row))
            workbook.close()
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
    original_name = asset_name_for_path(source)
    if original_name:
        record["original_filename"] = original_name
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
    records = []
    all_message_count = 0
    refs: set[str] = set()
    for conversation in conversations:
        rows = message_rows(conversation)
        all_message_count += len(rows)
        cid = str(conversation.get("conversation_id") or conversation.get("id") or f"conversation-{len(records) + 1}")
        title = str(conversation.get("title") or "untitled")
        title_stock = bool(TITLE_RE.search(title) or TICKER_RE.fullmatch(title.strip()) or EN_TICKER_RE.fullmatch(title.strip()))
        chosen = []
        for index, row in enumerate(rows):
            text = message_content(row["message"])
            related, hits = relevance(text, title)
            if related:
                chosen.append((index, row, "stock-keyword", hits))
        # Only a stock-titled conversation can supply short, clearly non-offtopic
        # context (e.g. "继续" or a brief follow-up) without importing the whole chat.
        if title_stock and chosen:
            chosen_indices = {x[0] for x in chosen}
            for index, row in enumerate(rows):
                if index in chosen_indices:
                    continue
                text = message_content(row["message"])
                if len(text) > 800 or NONSTOCK_CONTEXT_RE.search(text):
                    continue
                neighbours = [rows[j] for j in (index - 1, index + 1) if 0 <= j < len(rows)]
                if any(relevance(message_content(n["message"]), title)[0] for n in neighbours):
                    chosen.append((index, row, "stock-title-context", stock_hits(text)))
        if not chosen:
            continue
        chosen.sort(key=lambda x: x[0])
        for _, row, _, _ in chosen:
            asset_refs(row["node"], refs)
        all_hits = sorted({term for _, _, _, hits in chosen for term in hits}, key=str.lower)
        base = f"{len(records) + 1:04d}_{safe_name(title, 65)}_{safe_name(cid, 18)}"
        raw_path = OUT / "股票消息原始JSON" / (base + ".json")
        text_path = OUT / "股票消息全文" / (base + ".md")
        raw_object = {
            "conversation_metadata": {k: v for k, v in conversation.items() if k not in ("mapping", "messages")},
            "selection_unit": "message",
            "selected_nodes": [
                {
                    "node_id": row["node_id"],
                    "selection_reason": reason,
                    "matched_terms": hits,
                    "node": row["node"],
                }
                for _, row, reason, hits in chosen
            ],
        }
        write_json(raw_path, raw_object)
        text_path.parent.mkdir(parents=True, exist_ok=True)
        with text_path.open("w", encoding="utf-8") as out:
            out.write(f"# {title}\n\n")
            out.write(f"- 会话ID：`{cid}`\n- 源会话消息数：{len(rows)}\n- 本次入库股票消息数：{len(chosen)}\n")
            out.write("- 保留范围：仅股票相关消息节点；节点原始字段未删减，正文未截断。\n\n")
            for number, (_, row, reason, hits) in enumerate(chosen, 1):
                message = row["message"]
                mid = str(message.get("id", row["node_id"]))
                out.write(f"\n===== MESSAGE {number} | role={row['role']} | id={mid} | node={row['node_id']} | reason={reason} =====\n")
                out.write(message_content(message))
                out.write(f"\n===== END MESSAGE {number} =====\n")
        records.append({
            "conversation_id": cid,
            "title": title,
            "raw_file": str(raw_path.relative_to(OUT)).replace("\\", "/"),
            "text_file": str(text_path.relative_to(OUT)).replace("\\", "/"),
            "message_count": len(chosen),
            "source_message_count": len(rows),
            "text_chars": sum(len(message_content(row["message"])) for _, row, _, _ in chosen),
            "matched_terms": all_hits,
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
        if relative.startswith("__MACOSX/") or source.name in {"chat.html", "user.json", "message_feedback.json", "ads.json", "conversation_asset_file_names.json"}:
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
        original_name = asset_name_for_path(source)
        related = referenced or is_stock_text(relative + "\n" + original_name + "\n" + text)
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
            "unit": "message",
            "rule": "Strict stock/investment relevance per message; ambiguous portfolio/stock/POC/Meta/SLA/acronym matches alone are excluded. Stock-titled conversations may add only short adjacent context without obvious non-stock topics.",
            "context_preserved": "original parent/children/node fields and short stock-title context only",
            "raw_json_fields_preserved": True,
            "text_truncated": False,
            "all_mapping_branches_included": "all branches are scanned; only selected nodes are archived",
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
        f"- 原始 JSON：按消息节点保存，节点字段不删减；全文 Markdown：逐条股票消息保存；未使用字符截断。",
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

来源：ChatGPT 完整导出 ZIP（{source_name}）。本目录只接收命中股票/证券投资主题的消息及其关联附件；未命中消息不复制到本目录。

## 目录

- `股票消息原始JSON/`：按对话分文件保存股票相关消息节点；原始节点字段、父子关系、角色和附件指针不删减。
- `股票消息全文/`：对应的逐条股票消息可读全文；正文不截断，原始 JSON 是字段级权威底稿。
- `附加文件/`：命中消息引用的附件，以及独立扫描后命中股票主题的文件；原始字节复制，能抽取文字的旁边附 `.txt`。
- `manifest.json`：来源 MD5/SHA256、逐对话路径、入选/源消息数、字符数、附件哈希和选择命中词。
- `_coverage.md`：总量与逐对话完整性核对。

## 选择口径

以**消息**为基本筛选单位，不把命中对话里的工作、健康、SEO 等无关内容一并带入。股票/证券投资核心词直接入选；portfolio、stock、POC、Meta、SLA、PE/PB/ROE 等歧义词单独出现时不入选；代码须结合投资语境。股票标题下只补入与命中消息相邻、简短且无明显无关主题的上下文。所有 mapping 分支都会扫描，原始节点完整保留，正文不截断。独立文件只有在内容/OCR命中，或被命中消息引用时才入库。

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
    load_asset_name_map()
    conversation_paths = sorted(UNPACK.rglob("conversations.json"))
    conversation_paths += [p for p in sorted(UNPACK.rglob("conversations-*.json")) if p not in conversation_paths]
    if not conversation_paths:
        abort(4, "no conversations.json or conversations-*.json found; refusing to substitute a partial HTML extraction")
    conversations = load_conversations(conversation_paths)
    if not conversations:
        abort(4, "conversations.json decoded but contained no conversation objects")
    log("conversations", len(conversations))
    records, refs, total_messages = archive_conversations(conversations)
    log("selected conversations", len(records), "asset refs", len(refs))
    attachments, scanned = archive_other_files(refs, conversation_paths)
    # Check references only for diagnostics; raw selected JSON still retains every pointer.
    all_unpack_files = [p for p in UNPACK.rglob("*") if p.is_file()]
    for ref in sorted(refs):
        if ref.startswith(("http://", "https://")) or ref in {"file_path", "file-service"}:
            continue
        candidate = ref.rsplit("/", 1)[-1].split("?", 1)[0]
        match = re.search(r"file_(?:[A-Za-z0-9_-]+)|file-(?!service\b)[A-Za-z0-9_-]+", candidate)
        if not match:
            continue
        token = match.group(0)
        if not any(token in str(p.relative_to(UNPACK)) for p in all_unpack_files):
            MISSING_ASSETS.append(ref)
    write_reports(source_name, source, member_count, len(conversations), total_messages, records, attachments, scanned)
    # The member listing is only a diagnostic for format failures, not archive content.
    (OUT / "_zip_listing.txt").unlink(missing_ok=True)
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
