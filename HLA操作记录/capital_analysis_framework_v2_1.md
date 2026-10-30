# 资本行为分析框架 v2.1
# Capital Behavior Analysis Framework
# 基于：果论三分法 × 资本生命周期模型 × 趋势-偏离双因子
# v2.1 修订说明：修复 CPS 公式 bug，重构 Exit，AEI 拆分，Profit_Retention 多周期，穿透率改为风险因子，GS 定位收敛

---

## 核心认知前提

价格不是研究对象，是结果。
真正的因果链条如下：

```
产业变化（Industry）
    ↓
企业价值变化（Business）
    ↓
资本进入（Capital Entry）        ← AEI 衡量
    ↓
资本持续（Capital Persistence）  ← CPS 衡量
    ↓
资本退出（Capital Exit）         ← Exit Index 衡量
    ↓
市场状态（Market State）         ← GS / State 衡量（过滤器）
    ↓
价格执行（Marginal Pricing）     ← 执行层，不是判断层
```

四层分工：
- AEI：钱有没有进来？
- CPS：钱有没有留下？（Capital Commitment，资本承诺度）
- Exit：钱是不是在走？
- GS：市场现在允不允许交易？

---

## PHASE 0｜快速过滤层（Easy Mode）

目的：一眼定生死，不浪费时间

```
Gap60 = (MA60 - P) / P
Gap90 = (MA90 - P) / P

IF Gap60 > 0.05 AND Gap90 > 0.05
    → ❌ 扔垃圾桶，不分析

ELSE IF Gap60 > 0 AND Gap90 > 0
    → ⚠️ 谨慎，后续必须极强才考虑

ELSE
    → ✅ 进入详细评估
```

补充：若 MA60 或 MA90 斜率明显为负，无论 Gap 大小，一律扔垃圾桶。

---

## PHASE 1｜资本进入评估 AEI
### Capital Entry Index

v2.1 修订：AEI 拆为两个子指标，独立输出，不合并评分

---

### 1A｜隐性进入效率 AEI_Hidden
原始 AEI，衡量低成本悄悄拿货的效率

```
Delta_C = concentration_t - concentration_{t-1}
Delta_P = profit_ratio_t - profit_ratio_{t-1}

过滤噪音：
  if Delta_C < 0.05 → Delta_C = 0
  if Delta_P < 0.50 → Delta_P = 0

Power = max(Delta_C, Delta_P × 0.4)
Effort = volume_t / mean_volume_20d + ε

if Power ≤ 0:
    AEI_Hidden = 0
else:
    AEI_Hidden = Power / Effort

AEI_Hidden_smoothed = EMA(AEI_Hidden, span=3)
```

| AEI_Hidden | 信号 | 含义 |
|------------|------|------|
| > 3.0 | S级 | 暴力隐性吸筹 |
| 1.5–3.0 | A级 | 积极隐性进入 |
| 0.5–1.5 | B级 | 试探性进入 |
| 0–0.5 | 弱 | 正常波动 |
| 0 | 中性 | 锁仓/钝化期 |
| < 0 | 派发 | 筹码发散 |

---

### 1B｜资本进入强度 AEI_Strength
新增，衡量公开放量买入的强度（牛市主升不是悄悄买）

```
Price_Trend_5 = (price_t - price_{t-5}) / price_{t-5}   # 5日价格方向
Amount_Ratio  = amount_t / mean_amount_20d               # 成交额相对均值
Conc_Change   = concentration_t - concentration_{t-5}    # 5日集中度变化

AEI_Strength = (
    0.40 × clamp(Price_Trend_5 × 10, 0, 1)   # 上涨方向，负值归零
  + 0.35 × clamp(Amount_Ratio - 1, 0, 2) / 2  # 放量程度，标准化0-1
  + 0.25 × clamp(Conc_Change / 2, 0, 1)        # 集中度提升
) × 100   # 输出 0–100
```

| AEI_Strength | 含义 |
|--------------|------|
| ≥ 70 | 公开强势买入，资金抢筹 |
| 40–70 | 温和放量进入 |
| < 40 | 无明显主动买入 |

---

### 1C｜进入信号组合判断

| AEI_Hidden | AEI_Strength | 解读 |
|------------|--------------|------|
| 高 | 低 | 隐性吸筹，静悄悄拿货 |
| 低 | 高 | 公开抢筹，市场热度高 |
| 高 | 高 | 最强进入信号（双重确认） |
| 低 | 低 | 无明显进入 |

趋势判断：
```
5日累计 AEI_Hidden = sum(AEI_Hidden_{t-4} to AEI_Hidden_t)

> 4.5 → 真吸筹趋势
2.5–4.5 → 弱真（需观察）
< 2.5 → 假吸筹/中性
```

动态校准（强制执行）：
- AEI_Hidden = 0 连续 ≥ 3 天，但股价未跌且获利盘未减 → 判定为"主力锁仓"，非无吸筹
- AEI_Hidden 创 20 日新高 → 标注"超预期爆发性吸筹"

---

## PHASE 2｜资本持续评估 CPS
### Capital Persistence Score（0–100分）

v2.1 修订：
- 改名 Capital Persistence（资本承诺度），避免 Holding Time 假精度
- 加入 Concentration_Stability，降低 Cost_Stability 权重
- Profit_Retention 改为三周期加权
- Turnover_Absorption 修复方向 bug

```
CPS = 0.30 × Cost_Stability
    + 0.25 × Concentration_Stability   ← 新增
    + 0.20 × Profit_Retention          ← 改为三周期
    + 0.15 × Turnover_Absorption       ← 修复公式
    + 0.10 × Price_Structure
```

---

### 2.1 成本稳定性 Cost_Stability
衡量：成本重心有没有大幅迁移

```
cost_change = abs(avg_cost_t - avg_cost_{t-20}) / avg_cost_{t-20}
Cost_Stability = clamp(1 - cost_change, 0, 1)
```

注意：成本稳定 ≠ 一定好，需结合集中度同步判断。
- 成本稳定 + 集中度稳定 = 真锁仓
- 成本稳定 + 集中度下降 = 可能悄悄换人

| 值 | 含义 |
|----|------|
| 0.9–1.0 | 高度锁仓 |
| 0.7–0.9 | 稳定 |
| < 0.7 | 成本明显迁移 |

---

### 2.2 集中度稳定性 Concentration_Stability（新增）
衡量：筹码持有结构有没有发生质变

```
conc_change = abs(concentration_t - concentration_{t-20}) / max(concentration_{t-20}, 1)
Concentration_Stability = clamp(1 - conc_change, 0, 1)
```

联合判断逻辑：
```
Cost_Stability 高 AND Concentration_Stability 高
→ 真实锁仓，资本承诺深

Cost_Stability 高 AND Concentration_Stability 低
→ 成本伪稳，筹码在分散，警惕换人派发

Cost_Stability 低 AND Concentration_Stability 高
→ 换手但筹码集中度保持，健康换手，新资金接棒

Cost_Stability 低 AND Concentration_Stability 低
→ 资本离场迹象
```

---

### 2.3 获利盘保持 Profit_Retention（三周期加权）
v2.1 修订：加入短/中/长三个时间维度，长期权重最大

```
PR_10  = clamp(1 - abs(profit_ratio_t - profit_ratio_{t-10}) / 100, 0, 1)
PR_20  = clamp(1 - abs(profit_ratio_t - profit_ratio_{t-20}) / 100, 0, 1)
PR_60  = clamp(1 - abs(profit_ratio_t - profit_ratio_{t-60}) / 100, 0, 1)

Profit_Retention = 0.20 × PR_10 + 0.30 × PR_20 + 0.50 × PR_60
```

逻辑：PR_60 权重最大，因为资本承诺本质是时间的函数。
60日获利盘稳定 = 长期持有者没有大规模撤离 = 资本承诺深。

| Profit_Retention | 含义 |
|------------------|------|
| ≥ 0.85 | 长期持有者稳定，高承诺 |
| 0.65–0.85 | 一般 |
| < 0.65 | 获利盘明显兑现，警惕 |

---

### 2.4 换手吸收 Turnover_Absorption（修复方向 bug）
v2.1 修订：原公式在下跌缩量时也可能得高分，现在加入方向过滤

```
Price_Return_20 = (price_t - price_{t-20}) / price_{t-20}
Volume_Ratio    = volume_ma5 / volume_ma20

# 核心修复：方向过滤
if Price_Return_20 <= 0:
    TA_raw = 0   # 下跌不给分，无论缩量多少
else:
    TA_raw = Price_Return_20 × (1 - clamp(Volume_Ratio, 0, 2) / 2)
    # 上涨越多、量比越低 → 分越高

Turnover_Absorption = clamp(TA_raw × 5, 0, 1)  # 标准化至 0–1
```

| 情形 | 分数 |
|------|------|
| 上涨 + 量比 < 0.8（明显缩量） | 高 |
| 上涨 + 量比 ≈ 1.0（正常量） | 中 |
| 上涨 + 量比 > 1.5（明显放量） | 低中 |
| 下跌（无论量） | 0 |

---

### 2.5 价格结构 Price_Structure
衡量：价格是否维持在资本成本优势区

```
penetration = (price_t - low_70_t) / (high_70_t - low_70_t) × 100
trend = price_t > avg_cost_t

评分：
  trend=True  + penetration 20–80 → 1.0（黄金区）
  trend=True  + penetration > 80  → 0.8（高位）
  trend=True  + penetration < 20  → 0.6（低位但趋势正确）
  trend=False + penetration > 10  → 0.3（水下但未破位）
  trend=False + penetration ≤ 10  → 0.0（破位）
```

---

CPS 综合判断：

| CPS | 含义 |
|-----|------|
| ≥ 80 | 资本深度承诺，锁仓明显 |
| 60–80 | 健康持有 |
| 40–60 | 承诺一般，需观察 |
| < 40 | 资本承诺弱，警惕 |

---

## PHASE 3｜资本退出评估 Exit Index

v2.1 修订：加入"价格行为"维度，区分健康换手 vs 派发换手

核心逻辑：
- 健康换手：价格上涨 + 成交增加 + 集中度保持
- 派发换手：价格滞涨/下跌 + 成交增加 + 集中度下降 + 获利盘下降

```
Exit_Index = 0.30 × Profit_Drop
           + 0.25 × Concentration_Drop
           + 0.20 × Price_Stagnation    ← 新增，高位放量滞涨
           + 0.15 × Cost_Drift          ← 原 Cost_Distribution
           + 0.10 × Turnover_Spike      ← 原 Turnover_Expansion
```

各子指标计算：

```
# 获利盘下降（最重要）
Profit_Drop = clamp(
    (profit_ratio_{t-10} - profit_ratio_t) / 100, 0, 1
)

# 集中度下降
Concentration_Drop = clamp(
    (concentration_{t-10} - concentration_t) / concentration_{t-10}, 0, 1
)

# 高位放量滞涨（新增核心指标）
# 价格涨幅 < 2% 但量比 > 1.5，说明大量交易推不动价格
if abs(Price_Return_5) < 0.02 and volume_ma5/volume_ma20 > 1.5:
    Price_Stagnation = 1.0
elif abs(Price_Return_5) < 0.02 and volume_ma5/volume_ma20 > 1.2:
    Price_Stagnation = 0.5
else:
    Price_Stagnation = 0.0

# 成本漂移（快速上移 = 换手，不代表一定派发，需结合集中度）
cost_drift_rate = (avg_cost_t - avg_cost_{t-10}) / avg_cost_{t-10}
Cost_Drift = clamp(cost_drift_rate × 5, 0, 1)

# 换手异常放大
Turnover_Spike = clamp(
    (turnover_t / mean_turnover_20d - 1) / 2, 0, 1
)
```

Exit 信号判断：

| Exit_Index | 含义 |
|------------|------|
| ≥ 0.65 | 明显派发，高风险，优先减仓 |
| 0.35–0.65 | 轻微派发或健康换手，需辨别 |
| < 0.35 | 正常或锁仓 |

辅助辨别（健康换手 vs 派发）：
```
if Exit_Index 0.35–0.65:
    if Price_Return_10 > 0.05 and Concentration_Drop < 0.1:
        → 健康换手（新资金接棒，不是出货）
    else:
        → 派发嫌疑，降低仓位
```

Exit 优先级：无论 AEI/CPS 多高，Exit_Index ≥ 0.65 时优先执行减仓。

---

## PHASE 4｜市场状态引擎 GS
### Market State Engine（定位：过滤器，不是评分器）

v2.1 修订：GS 定位收敛，只回答"市场现在允不允许交易"
不再和 Capital Score 合并评分，避免与 CPS 重复

---

### 4.1 现价差值法（P评分）

```
D5  = P - MA5
D10 = P - MA10
D20 = P - MA20
D30 = P - MA30

P_score = sign(D5) + sign(D10) + sign(D20) + sign(D30)
粘合定义：|D| / MA ≤ 0.3% → sign = 0
```

| P值 | 结论 |
|-----|------|
| ≤ -3 | 强空头，不碰 |
| -2 ~ 0 | 弱空/粘合，观望 |
| 1 ~ 2 | 多头初启，观察 |
| ≥ 3 | 稳定多头，可跟 |

---

### 4.2 State 判定（日K 10根均线）

均线集合：MA5 / 10 / 20 / 30 / 40 / 50 / 60 / 70 / 80 / 90

严格按顺序判断，命中即停止：

```python
# State 0：结构性空头
if P < MA30 < MA60 < MA90:
    State = 0  → 扔垃圾桶

# State 3/3+：结构性多头
elif P > MA30 > MA60 > MA90:
    State = 3
    if P > MA10 > MA30 > MA50 > MA70 > MA90:
        State = "3+"

# State 2：结构开始允许
elif P > MA30 and abs(Gap60) < 0.01:
    State = 2
    if P > MA30 and P > MA60:
        MaxGap = max(abs(Gap10), abs(Gap20), abs(Gap30), abs(Gap40), abs(Gap50), abs(Gap60))
        if MaxGap <= 0.015: SubState = "2B-Compress"
        elif MaxGap <= 0.03: SubState = "2B-EarlyBull"
        else: SubState = "2A"
    else:
        SubState = "2A"

# State 1：弱反弹
elif P > MA30 and P < MA60 and MA60 < MA90:
    State = 1

# State X：横盘无趋势
else:
    State = "X"
```

State 行为映射：

| State | 含义 | 行为 |
|-------|------|------|
| 0 | 结构性空头 | 全禁 |
| 1 | 弱反弹 | 不参与 |
| 2A | 未放行 | 观察 |
| 2B-Compress | 最佳粘合 | 小试/果弹 |
| 2B-EarlyBull | 轻多头 | 轻仓 |
| 3 | 多头 | 主仓 |
| 3+ | 强多头 | 顺势加权 |
| X | 横盘 | 观察 |

---

### 4.3 Gap + 斜率双因子

所有 10 根均线输出：

```
GapX  = (P - MAx) / MAx          → 距离风险
SlopeX = (MAx_t - MAx_{t-1}) / MAx_{t-1} × 100   → 方向速度
```

动能评分（SlopeScore，基于 S10/S20/S30）：

```python
score = 0
if S10 > 0 and S20 > 0 and S30 > 0: score += 40   # 全正
if S10 > S20 > S30: score += 30                     # 加速
if abs(S20 - S30) < 0.1: score += 20               # 中期稳定
if S10 < S20: score -= 20                           # 动能衰减（预警）
SlopeScore = clamp(score, 0, 100)
```

GapScore（以 Gap60 为核心，位置风险因子）：

| Gap60 | 分数 | 注 |
|-------|------|----|
| ≤ 1.5% | 100 | 最优买点区 |
| ≤ 3% | 85 | 良好 |
| ≤ 5% | 65 | 可接受 |
| ≤ 8% | 45 | 偏高 |
| > 8% | 25 | 追高风险大 |

GS 综合市场评分（仅作过滤，不进入 Capital Score）：

```
GS_Score = StateScore × 0.4 + SlopeScore × 0.3 + GapScore × 0.3
```

StateScore 映射同之前，GS_Score 用途：

| GS_Score | 市场允许度 |
|----------|-----------|
| ≥ 80 | 允许重仓 |
| 65–80 | 允许轻仓 |
| 50–65 | 观察等待 |
| < 50 | 市场不允许，即便 Capital Score 高也不进 |

---

## PHASE 5｜筹码结构判断

### 5.1 穿透率（风险因子，非买卖条件）
v2.1 修订：穿透率不直接决定买卖，改为风险调节因子

```
penetration = (P - low_70) / (high_70 - low_70) × 100

风险系数 Risk_Factor：
  penetration < 20：低位区，风险低，可积极建仓
  penetration 20–60：稳健区，正常操作
  penetration 60–80：偏高，降低仓位上限至 70%
  penetration > 80：高位区，仓位上限 50%，只持不追
```

注意：成长股穿透率高不等于见顶，需结合产业判断。
高 penetration + 产业加速 = 继续持有
高 penetration + 产业减速 = 谨慎减仓

### 5.2 成本溢价

```
cost_premium = (P / avg_cost - 1) × 100

< 0：股价在成本下方 → 明确弱势
0–3：趋势刚启动
3–10：健康上涨
> 10：溢价较高，结合产业判断是否继续持有
```

### 5.3 资本承诺深度评估（替代"Holding Time"）
v2.1 修订：不叫 Holding Time，改为可观察的 Capital Commitment 评估

```
# 指标1：成本漂移率（20日）
cost_drift_20 = abs(avg_cost_t - avg_cost_{t-20}) / avg_cost_{t-20}

# 指标2：集中度漂移率（20日）
conc_drift_20 = abs(concentration_t - concentration_{t-20}) / max(concentration_{t-20}, 1)

# 综合承诺深度
Commitment_Score = clamp(1 - (cost_drift_20 × 0.5 + conc_drift_20 × 0.5), 0, 1)

解读：
  ≥ 0.90：高承诺，原有资本深度锁定
  0.70–0.90：中等承诺
  < 0.70：承诺弱，资本结构不稳定
```

### 5.4 BUY/HOLD/SELL 信号

```python
trend = P > avg_cost
penetration = (P - low_70) / (high_70 - low_70) × 100
risk_ok = penetration <= 80   # 穿透率改为风险判断，不是硬卡死

if trend and 20 <= penetration <= 80 and volume_ratio >= 1.0:
    signal = "BUY"
    position_limit = 1.0

elif trend and penetration > 80 and volume_ratio >= 1.0:
    signal = "BUY"
    position_limit = 0.5   # 高位减仓上限

elif not trend and (penetration < 10 or cost_premium < -3.0):
    signal = "SELL"

else:
    signal = "HOLD"
    if trend and penetration > 80:
        desc = "高位锁仓（持有但不追，仓位上限50%）"
    elif not trend:
        desc = "水下蓄势（未破位，等待站上成本线）"
    else:
        desc = "中继震荡（等量能确认）"
```

---

## 综合资本状态矩阵

```
                  CPS 高（≥60）        CPS 低（<60）
AEI_Hidden 高   │ Strong Accum.      │ Hot Money      │
                │ 隐性吸筹+深度承诺   │ 短线热钱进入   │
AEI_Hidden 低   │ Holding Phase      │ Weak / Watch   │
                │ 锁仓蓄势，等待启动  │ 无资金支撑     │
AEI_Strength 高 │ 加分：公开抢筹确认  │ 可能是短期炒作 │

Exit ≥ 0.65 → Distribution（最高优先级，无论其他分数，先减仓）
```

---

## 综合评分 Capital Score

注意：Capital Score 只评估资本状态，GS 独立评估市场状态
两者必须同时达标才执行操作

```
Capital_Score = AEI_norm    × 0.25
              + CPS          × 0.50
              + Commitment   × 0.25

AEI_norm = clamp(AEI_Hidden / 3, 0, 1) × 100

最终决策逻辑：
if Exit_Index >= 0.65:
    → 减仓（优先级最高，覆盖一切）

elif Capital_Score >= 70 and GS_Score >= 65:
    → 可操作（两者同时达标）

elif Capital_Score >= 70 and GS_Score < 65:
    → 等待市场放行（资本好但市场结构差）

elif Capital_Score < 70 and GS_Score >= 65:
    → 观察（市场好但资本承诺不足）

else:
    → 不参与
```

Capital Score 解读：

| Capital_Score | 含义 |
|---------------|------|
| ≥ 80 | 资本状态优秀 |
| 60–80 | 健康 |
| 40–60 | 观察 |
| < 40 | 弱势，不参与 |

---

## 最终输出｜综合报告格式

```
════════════════════════════════════════
[股票名称(代码)] 综合分析报告
最新数据：YYYY-MM-DD  收盘价 XX.XX
════════════════════════════════════════

【Q1】走势是否健康？
→ [结论] + 核心依据（1–2句）

【Q2】State + 操作建议
→ State: [X]  GS_Score: XX  市场允许度: [允许/观察/不允许]
→ 操作: BUY / HOLD / SELL  仓位上限: XX%

【Q3】Capital Score 综合分
→ AEI_Hidden: XX（隐性进入） | AEI_Strength: XX（进入强度）
→ CPS: XX（资本承诺度）
→ Exit_Index: XX（退出风险）
→ Capital_Score: XX → [优秀/健康/观察/弱势]

【Q4】后续走势判断
→ [大概节奏描述，1–3句]

【Q5】主升浪时间预判
→ 基于 AEI 趋势 + 均线收敛速度 + CPS 稳定性
→ 预计：[X 周 / X 个月内]，节奏：[描述]

【Q6】资本承诺判断
→ AEI_Hidden 近期：[进入/锁仓/派发]
→ AEI_Strength 近期：[强/弱]
→ CPS: XX | Commitment_Score: XX
→ 联合判断：[Strong Accum. / Holding Phase / Hot Money / Distribution]
→ 结论：资本收集[完毕/进行中/未开始]，后续动作预判：[...]

════════════════════════════════════════
【今日核心分析与指引】
[一段话：当前行情判断 + 操作建议 + 注意事项]
════════════════════════════════════════
```

---

## 数据输入清单

### 必须字段（每日）

| 字段 | 说明 |
|------|------|
| price_t | 收盘价 |
| volume_t | 成交量（万股） |
| turnover_t | 换手率 % |
| amount_t | 成交额（万元） |
| avg_cost_t | 筹码平均成本 |
| low_70_t | 70%成本区下沿 |
| high_70_t | 70%成本区上沿 |
| concentration_t | 筹码集中度 % |
| profit_ratio_t | 获利比例 % |
| volume_ratio_t | 量比 |
| MA5/10/20/30/40/50/60/70/80/90 | 日K 10根均线（最新交易日） |

### 推荐字段（二期）

| 字段 | 说明 |
|------|------|
| big_buy_t / big_sell_t | 大单买卖数据 |
| 分时量价 | 资金节奏判断 |
| ETF 持仓变化 | 机构配置动向 |

---

## 框架分工总结

| 模块 | 回答的问题 | 性质 |
|------|-----------|------|
| PHASE 0 | 值不值得分析？ | 过滤器 |
| AEI_Hidden | 有没有悄悄进钱？ | 资本进入（隐性） |
| AEI_Strength | 有没有公开抢筹？ | 资本进入（显性） |
| CPS | 进来的钱还在不在？ | 资本承诺 |
| Exit Index | 钱是不是在走？ | 资本退出 |
| GS / State | 市场结构允许交易吗？ | 市场过滤器 |
| 筹码结构 | 静态截面风险在哪？ | 风险定位 |
| Capital Score | 综合资本状态如何？ | 最终评分 |

---

## 核心原则

1. Exit 优先级最高：Exit_Index ≥ 0.65，无论其他分数，优先减仓
2. Capital Score + GS_Score 双达标才操作：资本好但市场不允许，等；市场好但资本不足，观察
3. AEI_Hidden + AEI_Strength 双高才是最强进入信号：单一不足以判断
4. Profit_Retention 的 PR_60 权重最大：长期获利盘稳定才是真承诺
5. 穿透率是风险因子不是开关：高穿透率 = 调低仓位上限，不是直接不买
6. 动能衰减 S10 < S20 是预警，不等价格跌才反应
7. 成本稳定必须配合集中度稳定才算真锁仓

---

## v2.0 → v2.1 修订清单

| 项目 | v2.0 | v2.1 |
|------|------|------|
| AEI | 单一指标 | 拆为 AEI_Hidden + AEI_Strength |
| CPS 权重 | Cost 40% | Cost 30% + Conc 25%，降低成本权重 |
| Concentration_Stability | 无 | 新增，25% 权重 |
| Profit_Retention | 单一20日 | 三周期 10/20/60日，60日权重50% |
| Turnover_Absorption | 有方向bug | 修复：下跌时强制归零 |
| Exit Index | 无价格行为 | 新增 Price_Stagnation（高位滞涨） |
| 穿透率 | 买卖条件 | 改为风险因子，调节仓位上限 |
| GS 定位 | 参与综合评分 | 独立为市场过滤器，不进 Capital Score |
| Holding Time | 概念但不可测 | 改为 Commitment_Score（可计算） |
| 决策逻辑 | 单一评分 | Capital Score + GS_Score 双达标机制 |

---

*Capital Behavior Analysis Framework v2.1*
*整合：果论三分法 × AEI双引擎 × CPS × Exit Index × GS市场引擎*
*修订基于：GPT v2.0 审查意见 + Claude 独立判断*
