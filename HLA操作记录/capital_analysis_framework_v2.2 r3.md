# 资本行为分析框架 v2.2（通用版）
# Capital Behavior Analysis Framework — A-Share General Edition

> 版本：v2.2 r3（2026-10-12 定稿）
> 适用：沪深北 A 股个股（通用）
> 承接：v2.1（果论三分法 × 资本生命周期模型 × 趋势-偏离双因子）
> 定位：本文件是**通用方法论**，不含任何个股专属参数。个股的持仓事实、硬性触发线、基本面快照、环境指数配置，一律写入独立的《标的专项档案》，与本文件分开维护，不得混写。

---

## 修订摘要

| 版本 | 主要修订 |
|---|---|
| v2.2 r0 | 承接 v2.1：筹码口径统一宽度型 W；AEI 价格驱动闸门；λ 折扣；Exit 补入放量下跌；GS 补全 State X 分值；新增环境归因层（PHASE 6）；新增持仓模式（PHASE 7） |
| v2.2 r1 | Chip_Frozen 改 5 日窗口；均线斜率窗口 N=5；Phase 0 "明显下降" 改 5 日累计 ≤ −3 tick；Exit 放量下跌阈值 −3%→−2%；环境归因补"相对抗跌/落后"标签；新增附录 H 计算规范 |
| v2.2 r2 | 均线口径自检（平台 MA = 前 k 日均值，不含当日）；附录 H 补均线自检与缺日重建规则；W 双口径正式写入公式层 |
| v2.2 r3 | **环境数据查询规范**：明确每次报告前必须检索当日指数收盘数据（大盘 / 板块 / 风格），并以标准表格输出，无法查到则注明"未核实"；质押率口径说明：质押率指控股股东所持股份中被质押的比例，不是全市场流通股占比 |

---

## 使用边界

| 模式 | 适用 | 决策依据 |
|---|---|---|
| Entry Mode | 新资金 / 交易性仓位 | Capital Score + GS_Score 双达标；Exit 优先 |
| Holder Mode | 已持仓、有明确持有目的 | 预设硬性触发线；技术指标仅作观察 |

State / GS / Capital Score 回答"现在适不适合投入新资金"，不等价于"已持仓者该不该卖"。持仓者行动以 PHASE 7 触发线为准。

---

## 约定：符号、单位、平台口径

### 单位

| 字段 | 单位 |
|---|---|
| W、获利比例 profit、换手率 | 百分数数值；差值单位 pp |
| 涨跌幅、Gap、cost_change | 小数（0.03 = 3%） |
| 均线斜率 S | %/日 |

> 易错点：`ΔP < 0.50` 指 **0.5 个百分点**，不是 50 个百分点。

### 筹码集中度口径自检（每只新标的首次使用时必做）

```
W90 = (H90 − L90) / (H90 + L90) × 100
W70 = (H70 − L70) / (H70 + L70) × 100
```

内部统一：**越小 = 越集中**。东方财富等主流平台报告的"集中度"通常为宽度型，用公式验证后再套用。

**W 双口径规则**
- 默认 `W = W90`；W70 作核心筹码交叉验证。
- `Chip_Frozen`：W90 与 W70 的 5 日累计变化**都**低于 `C_tol` 且成本 5 日变化低于 `cost_tol` 才算冻结。
- `Conc_Gain`：取 W90 与 W70 中变紧幅度较大者；方向相反且差值均 ≥ `C_tol`，标注"口径冲突"，Conc_Gain 按 0 处理。
- `W_Disperse_10`：取 W90 与 W70 中变宽幅度较大者（偏保守）。
- 每日报告中两个口径数值都列出，不合并。

```
Conc_Gain_t   = W_{t-1} − W_t
Conc_Gain_5   = W_{t-5} − W_t
W_Disperse_10 = W_t − W_{t-10}
```

### 最小变动价位噪声容差

```
tick     = 0.01
mid      = (H70 + L70) / 2
C_tol    = max(0.05, 100 × tick / mid)      # pp
cost_tol = max(2 × tick, 0.002 × avg_cost)  # 元
```

### 均线口径（r2 核实）

平台日线 MA_k(t) = 截至 t−1 的前 k 个交易日收盘价均值（**不含当日**）。自检：用收盘价重算 MA5/MA10，与平台值对比，差值 ≤ 0.011 即为该口径。

### 质押率口径说明（r3 新增）

"控股股东质押率"指控股股东**所持股份中被质押的比例**，即：

```
质押率 = 控股股东被质押股份数 / 控股股东持股总数
```

不是被质押股份占全市场总股本的比例（那个数字通常小得多）。档案中记录时必须注明是哪家主体（控股股东法人实体）的持股质押率，并附上来源公告日期。

---

## 核心认知前提

因果链：产业变化 → 企业价值 → **资本进入（AEI）→ 资本持续（CPS）→ 资本退出（Exit）** → 环境（Context）→ 市场状态（GS / State）→ 价格执行

---

## PHASE 0｜快速过滤层

```
Dn60 = (MA60 − P) / P
Dn90 = (MA90 − P) / P

Dn60 > 0.05 AND Dn90 > 0.05    → 扔垃圾桶
Dn60 > 0 AND Dn90 > 0           → 谨慎
else                             → 进入详细评估
```

MA60 或 MA90 的 5 日累计变化 ≤ −3 × tick → 一律扔垃圾桶。

---

## PHASE 1｜资本进入评估 AEI

### 1A｜隐性进入效率 AEI_Hidden

```python
Conc_Gain_eff = Conc_Gain_t  if Conc_Gain_t >= C_tol  else 0
ΔP_f          = ΔP_t         if ΔP_t >= 0.50           else 0   # pp

Conc_Confirm = (Conc_Gain_eff > 0)
ΔP_eff       = ΔP_f  if Conc_Confirm  else 0

Power_raw = max(Conc_Gain_eff, 0.4 × ΔP_f)    # 机械，展示不采信
Power     = max(Conc_Gain_eff, 0.4 × ΔP_eff)  # 采信

Effort = volume_t / mean_volume_20d + 1e-6

AEI_Hidden_raw = Power_raw / Effort
AEI_Hidden     = Power     / Effort   # ≥ 0
```

每日同时报机械读数与采信读数。若 raw ≥ 0.5 而采信为 0，标注：
> 价格驱动读数（机械 X.X，未获集中度确认，不采信）

| AEI_Hidden（采信） | 信号 |
|---|---|
| > 3.0 | S 级 |
| 1.5–3.0 | A 级 |
| 0.5–1.5 | B 级 |
| 0–0.5 | 弱 |
| 0（无确认） | 中性 |

5 日累计：> 4.5 = 真吸筹；2.5–4.5 = 弱真；< 2.5 = 中性。

### 1B｜资本进入强度 AEI_Strength

```python
pt5 = P_t / P_{t-5} − 1
ar  = amount_t / mean_amount_20d
cg5 = max(W90_{t-5} − W90_t, W70_{t-5} − W70_t, 0)

AEI_Strength = (0.40 × clamp(pt5×10, 0, 1)
              + 0.35 × clamp(ar−1, 0, 2)/2
              + 0.25 × clamp(cg5/2, 0, 1)) × 100
```

---

## PHASE 2｜资本持续评估 CPS（0–100）

λ（价格驱动折扣）：Chip_Frozen_Days ≥ 3 时 λ = 0.5，否则 λ = 1.0。

```
CPS = 0.30 × Cost_Stability
    + 0.25 × Concentration_Stability
    + 0.20 × Profit_Retention
    + 0.15 × Turnover_Absorption
    + 0.10 × Price_Structure
```

```python
# 成本稳定性
cch = 0 if abs(avg_cost_t - avg_cost_{t-20}) <= cost_tol \
      else abs(avg_cost_t - avg_cost_{t-20}) / avg_cost_{t-20}
Cost_Stability = clamp(1 − cch, 0, 1)

# 集中度稳定性（W90）
wch = 0 if abs(W90_t - W90_{t-20}) < C_tol \
      else abs(W90_t - W90_{t-20}) / max(W90_{t-20}, 1)
Concentration_Stability = clamp(1 − wch, 0, 1)

# 获利盘保持（λ 折扣）
PR_n = clamp(1 − λ × abs(profit_t − profit_{t-n}) / 100, 0, 1)  # n∈{10,20,60}
Profit_Retention = 0.20×PR_10 + 0.30×PR_20 + 0.50×PR_60

# 换手吸收
ret20 = P_t / P_{t-20} − 1
vr    = vol_ma5 / vol_ma20
ta    = 0 if ret20<=0 else ret20 × (1 − clamp(vr,0,2)/2)
Turnover_Absorption = clamp(ta×5, 0, 1)

# 价格结构
pen = (P − l70) / (h70 − l70) × 100
Price_Structure = (1.0 if P>avg_cost and 20<=pen<=80
                   else 0.8 if P>avg_cost and pen>80
                   else 0.6 if P>avg_cost and pen<20
                   else 0.3 if P<=avg_cost and pen>10
                   else 0.0)
```

---

## PHASE 3｜资本退出评估 Exit Index

```
Exit = 0.30×Profit_Drop + 0.25×Concentration_Disperse
     + 0.20×Price_Action_Risk + 0.15×Cost_Drift + 0.10×Turnover_Spike
```

```python
Profit_Drop = λ × clamp((profit_{t-10} − profit_t)/100, 0, 1)

# W90/W70 中较大变宽幅度
def disp(k):
    a = W90_t − W90_{t-k}; b = W70_t − W70_{t-k}
    return max(clamp(a/max(W90_{t-k},1),0,1) if a>=C_tol else 0,
               clamp(b/max(W70_{t-k},1),0,1) if b>=C_tol else 0)
Concentration_Disperse = disp(10)

r5 = P_t / P_{t-5} − 1
vr = vol_ma5 / vol_ma20
Price_Action_Risk = (1.0 if r5<=-0.02 and vr>1.5
                     else 0.5 if r5<=-0.02 and vr>1.2
                     else 1.0 if abs(r5)<0.02 and vr>1.5
                     else 0.5 if abs(r5)<0.02 and vr>1.2
                     else 0.0)

d = avg_cost_t − avg_cost_{t-10}
Cost_Drift = 0 if d<=cost_tol else clamp(d/avg_cost_{t-10}×5, 0, 1)

Turnover_Spike = clamp((turn_t/mean_turn_20d − 1)/2, 0, 1)
```

| Exit | 含义 |
|---|---|
| ≥ 0.65 | 明显派发，优先减仓 |
| 0.35–0.65 | 辨别（r10>5% 且 Conc_Disperse<0.1 → 健康换手；否则派发嫌疑） |
| < 0.35 | 正常或锁仓 |

---

## PHASE 4｜市场状态引擎 GS

### 4.1 P_score

```python
sign_k = 0 if abs(P - MA_k)/MA_k <= 0.003 else int(copysign(1, P-MA_k))
P_score = sign_5 + sign_10 + sign_20 + sign_30   # 范围 −4 至 +4
```

### 4.2 State

```python
if P < MA30 < MA60 < MA90:                         State = '0'
elif P > MA30 > MA60 > MA90:
    State = '3+' if P>MA10>MA30>MA50>MA70>MA90 else '3'
elif P > MA30 and abs((P-MA60)/MA60) < 0.01:
    gmax = max(abs((P-MA_k)/MA_k) for k in [10,20,30,40,50,60])
    if P > MA60:
        State = ('2B-Compress' if gmax<=0.015
                 else '2B-EarlyBull' if gmax<=0.03
                 else '2A')
    else: State = '2A'
elif P > MA30 and P < MA60 and MA60 < MA90:        State = '1'
else:                                               State = 'X'
```

### 4.3 GS_Score

斜率（N=5）：`S_k = (MA_k,t / MA_k,t-5 − 1) × 100 / 5`

Phase 0 "明显下降"：MA_k,t − MA_k,t-5 ≤ −3 × tick

SlopeScore：S10/S20/S30 均正 +40；S10>S20>S30 +30；|S20−S30|<0.1 +20；S10<S20 −20；clamp(0,100)

GapScore：|Gap60| ≤1.5%=100，≤3%=85，≤5%=65，≤8%=45，>8%=25

StateScore：0→0，1→20，X→40，2A→55，2B-EarlyBull→75，2B-Compress→85，3→90，3+→100

```python
GS = StateScore×0.4 + SlopeScore×0.3 + GapScore×0.3
if State=='0': GS=0
if State=='1': GS=min(GS,49)
if State=='X': GS=min(GS,64)
```

### 4.4 持续性计数器与 λ

```python
# 5 日窗口筹码冻结
Chip_Frozen = (abs(W90_t−W90_{t-5})<C_tol and abs(W70_t−W70_{t-5})<C_tol
               and abs(avg_cost_t−avg_cost_{t-5})<=cost_tol)
Chip_Frozen_Days  = 连续 Chip_Frozen 天数
P_bear_streak     = 连续 P_score ≤ −3 天数
P_bull_streak     = 连续 P_score ≥ 3 天数
Below_MA60_Days   = 连续 P < MA60 天数
Vol_Dry_Days      = 连续 volume_t < 0.7×mean_volume_20d 天数

λ = 0.5 if Chip_Frozen_Days >= 3 else 1.0
```

---

## PHASE 5｜筹码结构

```python
penetration  = (P − l70) / (h70 − l70) × 100
cost_premium = (P / avg_cost − 1) × 100
Commitment   = clamp(1 − (0.5×cost_drift_20 + 0.5×conc_drift_20), 0, 1)
```

---

## 综合决策（Entry Mode）

```python
AEI_norm      = clamp(AEI_Hidden/3, 0, 1) × 100
Capital_Score = 0.25×AEI_norm + 0.50×CPS + 0.25×Commitment×100

if Exit >= 0.65:                              → 减仓（覆盖一切）
elif Capital_Score>=70 and GS>=65:            → 可操作
elif Capital_Score>=70 and GS<65:             → 等待市场放行
elif Capital_Score<70  and GS>=65:            → 观察
else:                                         → 不参与
```

逆风环境（Mkt + Sec 同为弱）：建议"双达标"连续 2 日才操作。

---

## PHASE 6｜环境归因层 Context

**定位**：归因标注层，不进入 Capital Score / GS 评分，但每次报告前**必须**查询。

### 6.1 环境数据查询规范（r3 新增，强制执行）

每次出报告前，必须检索当日以下指数的收盘数据，并以标准表格形式列在报告 Q1 的环境部分：

```
| 指数 | 收盘 | 涨跌幅 |
|------|------|--------|
| 沪深300       | XXXX.XX | +X.XX% |
| 上证指数      | XXXX.XX | +X.XX% |
| 申万[行业]    | XXXX.XX | +X.XX% |
| 中证红利（或风格指数） | XXXX.XX | +X.XX% |
```

- 行业指数、风格指数的具体选择写入《标的专项档案》第 6 节。
- 查不到当日收盘数据（例如检索结果只有盘中读数），在表格对应行注明"盘中 XX%，收盘未核实"，**不得凭盘中数据替代收盘数据作归因结论**。
- 查不到任何数据，该格写"未核实"，归因结论暂不作判定。

### 6.2 相对强弱与归因指标

```python
r_stock_1 = P_t / P_{t-1} − 1
r_x_1     = 指数当日涨跌幅
RS_1_x    = r_stock_1 − r_x_1

σ60 = std(个股日收益率, 60日)
τ_1d = max(0.003, 0.5 × σ60)
β_x  = cov(r_stock, r_x)/var(r_x)，60 日，限幅[0.3,1.5]，样本不足取 1

Explain_x = clamp(β_x × r_x_1 / r_stock_1, 0, 1) if (
    sign(r_x_1)==sign(r_stock_1) and abs(r_stock_1)>=τ_1d) else 0
Explain_max = max(Explain_mkt, Explain_sec, Explain_sty)
```

### 6.3 归因标签

| 条件 | 标签 |
|---|---|
| \|r_stock_1\| < τ_1d | 无显著波动；仍列出 RS 事实 |
| Explain_max ≥ 0.7 | 共振型（注明来源） |
| 0.3 ≤ Explain_max < 0.7 | 部分共振 |
| Explain_max ≥ 0.7 且 RS_x ≥ +τ_1d（下跌日） | 共振型·相对抗跌 |
| Explain_max < 0.3 且 RS 均 ≤ −τ_1d | 个股独弱 |
| Explain_max < 0.3 且 RS 均 ≥ +τ_1d | 个股独强 |

**数据完整性**：环境数据与个股同日、用收盘口径。查不到就写"未核实"，禁止凭感觉归因。

---

## PHASE 7｜持仓模式 Holder Mode

### 7.1 分层

| 层 | 内容 | 作用 |
|---|---|---|
| 硬性触发线 | 预设、可核实的事实性条件 | 命中即复核，唯一行动入口 |
| 观察项 W1–W6 | 可能预警触发线的信号 | 汇总"关注"状态，只提示 |
| 参考面板 | State/GS/Capital Score/归因/量能 | 新资金参考，持仓者仅作背景 |

观察项命中 ≥ 2 → 持仓状态升为"关注"。

### 7.2 收息型专用指标（H-Income）

三个股息率口径**严格分开**：

```
Cash_dividend = Shares_held × DPS          # 实际到手，与成本无关
Yield_on_cost = DPS / cost_per_share        # 自评回报率
Yield_price   = DPS / P                     # 市场定价口径
Spread        = Yield_price − Y10           # 债性利差
```

全年 DPS 预估：`DPS_fc = NP_fc × Payout_fc / Shares_total`，以三档 NP_fc × 三档 Payout_fc 的敏感性网格给出。

### 7.3 复核流程

命中触发线后：核实事实（以公告财报为准）→ 判定一次性/持续性 → 评估对持有目的影响 → 交还持有人决策。**复核 ≠ 自动卖出。**

### 7.4 事件检查点预注册规则

披露前写好三档结果与处理，写入专项档案，披露后按条款执行，**不得回改**。

### 7.5 触发线变更规则

修改须记录日期、原值、新值、理由。披露后不得回改。触发事件后 10 个交易日内只能收紧，不得放宽。

### 7.6 Holder Mode 报告结构

```
持仓状态：正常持有 / 关注 / 复核
硬性触发线面板（逐条）
观察项面板（命中项）
收息面板：DPS_fc / Yield_price / Yield_on_cost / Spread / 已实施分红
参考面板：State/GS/Capital Score（标注"新资金参考"）/ Exit / 归因 / 计数器
```

---

## 附录 A｜外部量能报告交叉核对规范

1. 评分项分为**窗口继承项**（近 N 日均值、量能趋势、历史背离）与**当日新增项**（实时量能调整、当日新增背离）。评级变化必须说明驱动来自哪一类。
2. 地量累积不等于派发。判定"派发嫌疑"需同时具备放量下跌或新增背离，以及 Exit 分量中集中度变散或成本漂移。
3. 量价背离涨跌幅口径：区分"昨收→收盘"与"今开→最新价"，引用时注明。
4. 结合环境归因区分"共振型背离"与"独弱型背离"。
5. 报告中"减仓/清仓"建议是交易型通用模板，Holder Mode 仅作观察。

---

## 附录 B｜输出模板

### Entry Mode

```
══════════════════════════════════════
[名称(代码)]  YYYY-MM-DD  收盘 XX.XX
══════════════════════════════════════

【环境数据】（出报告前必须检索，见 PHASE 6.1）
| 指数 | 收盘 | 涨跌幅 |
|------|------|--------|
| 沪深300       | ... | ...% |
| 上证指数      | ... | ...% |
| 申万[行业]    | ... | ...% |
| [风格指数]    | ... | ...% |

Q1 走势是否健康
→ 结论 + 归因标签

Q2 State + 操作建议
→ State / P_score（连续 X 日）/ GS / 市场允许度

Q3 Capital Score
→ AEI_Hidden（采信/机械）/ AEI_Strength
→ CPS / Commitment
→ Exit（各分量逐一列出）
→ Capital_Score / GS_Score

Q4 后续走势判断（关键价位）

Q5 主升浪时间预判

Q6 资本承诺判断（W90/W70/冻结天数/矩阵位置）

Q7 分时成交量维度（窗口继承 vs 当日新增）

今日核心指引
══════════════════════════════════════
```

Holder Mode：Q2 替换为持仓状态 + 触发线面板 + 收息面板，环境数据表格同样必须。

---

## 附录 C｜数据输入清单

**每日必须字段**：price/prev、volume/amount/turnover/vr、avg_cost/l70/h70/l90/h90/c70/c90、profit_ratio、MA5–MA90（含历史序列）。

**环境字段**：Mkt/Sec/Sty 指数当日收盘，至少保留 60 日（估 β 用）。

**完整性规则**
1. 首次使用：完成 W 口径自检和均线口径自检，tick / C_tol 写入档案。
2. 缺失字段：写"未核实"，说明受影响结论，不悄悄补位。
3. 动态 PE 跳变：用"市值 ÷ PE"反推分母，核对是否为口径切换；统一用 TTM 或全年口径，注明净利润构成。
4. 涨跌幅：统一用"昨收→收盘"口径。

---

## 附录 D｜标的专项档案模板

```
# [名称(代码)] 专项档案（配套 v2.2）

0. 更新记录
1. 持仓事实（成本/数量/操作纪律）
2. 持仓类型（H-Income / H-Trend / H-Thesis）
3. 硬性触发线（逐条，含阈值/核实来源/当前状态）
   含事件检查点预注册
4. 基本面快照（带日期，过期即更新）
5. 关键验证节点日历
6. 环境配置（Mkt/Sec/Sty 指数具体名称和代码 / tick / C_tol / cost_tol）
7. 标的特有解读规则与数据口径注意事项
8. 输出偏好
9. 状态快照（带日期，每次报告后更新）
10. 已知偏差与更正记录
```

---

## 附录 E｜方法论校准（跨标的通用经验）

1. 价格是边际成交，不要用当日价格反推"筹码必然扩散"。
2. 权重：资金行为指标 > 短期均线噪音。
3. MA5/MA10 单日方向反复属正常噪音；配合放量 + 集中度变散才值得警惕。
4. 筹码数据跨平台有差异，连续多日不变不必然是未刷新。
5. 低于 C_tol 的变化不解读。
6. 获利比例是价格的函数，须由集中度/成本同步变化确认才采信为资本行为。
7. 量能报告评级先分窗口继承与当日新增，再判断"没人交易"还是"有人出货"。
8. 归因前必须核实环境收盘数据（PHASE 6.1），查不到就写"未核实"。
9. GapScore 对偏离过大主动降分，是模型特性，不等于趋势变差。
10. 风格性冷落是背景，不代表个股基本面另有问题。
11. P_score 持续天数比单日读数重要。
12. 估值统一用 TTM 或全年口径，用"市值÷PE"反推分母自检。
13. 均线口径自检：确认是否含当日，一经确认全程保持一致。
14. "减仓/清仓"评级标签是通用模板，持仓者以触发线为准。
15. 质押率 = 控股股东被质押股份 ÷ 其持股总数，不是全市场占比，记录时注明主体与来源公告。

---

## 附录 F｜参数总表

| 参数 | 默认 | 位置 |
|---|---|---|
| tick | 0.01 | 约定 |
| C_tol | max(0.05, 100×tick/mid) pp | 约定 |
| cost_tol | max(2×tick, 0.002×avg_cost) | 约定 |
| ΔP 过滤 | 0.50 pp | PHASE 1A |
| EMA span | 3 | PHASE 1A |
| 5 日 AEI 阈值 | 4.5 / 2.5 | PHASE 1 |
| CPS 权重 | 0.30/0.25/0.20/0.15/0.10 | PHASE 2 |
| PR 周期权重 | 0.20/0.30/0.50 | PHASE 2 |
| Exit 权重 | 0.30/0.25/0.20/0.15/0.10 | PHASE 3 |
| Exit 阈值 | 0.35 / 0.65 | PHASE 3 |
| 放量下跌判定 | r5 ≤ −2% 且 vr > 1.5 | PHASE 3 |
| 粘合容差 | 0.3% | PHASE 4.1 |
| 斜率窗口 N | 5 | PHASE 4.3 |
| "明显下降"阈值 | 5 日变化 ≤ −3 tick | PHASE 0 |
| StateScore 映射 | 见 PHASE 4.3 | PHASE 4.3 |
| GS 上限（State 1/X） | 49 / 64 | PHASE 4.3 |
| λ 折扣 / 触发天数 | 0.5 / ≥3 日 | PHASE 4.4 |
| Chip_Frozen 窗口 | 5 日 | PHASE 4.4 |
| Vol_Dry 阈值 | 0.7 × 20 日均量 | PHASE 4.4 |
| τ_1d | max(0.3%, 0.5×σ60) | PHASE 6 |
| β 限幅 / 窗口 | [0.3,1.5] / 60 日 | PHASE 6 |
| 共振阈值 | 0.7 / 0.3 | PHASE 6 |
| 独弱/强持续 | 连续 ≥ 3 日 | PHASE 6 |
| 持仓"关注"阈值 | 观察项命中 ≥ 2 | PHASE 7 |

---

## 附录 G｜局限性声明

1. 本框架为分析工具，不构成投资建议。
2. 筹码数据是估算值，有平台差异；框架加入噪声容差但不能消除估算不确定性。
3. 阈值与权重是设计默认值，未系统回测，不同标的应校准。
4. 技术与筹码指标不含基本面与消息面。
5. 环境归因依赖数据时点与口径一致性，不可核实时输出"未核实"。
6. 评分体系面向新资金进场决策；持仓者以预设触发线为准。

---

## 附录 H｜计算规范

1. 逐日指标由代码计算，不心算：P_score、State、W90/W70、Chip_Frozen、AEI 双读数、Exit 各分量、GS、计数器。
2. 输入以表格保存，历史窗口 ≥ 60 日，日期连续，缺日显式补录。基准量（20 日均量/均额/均换手）取截至前一交易日的 20 日均值（不含当日）。涨跌幅取"昨收→收盘"口径。
3. **均线口径自检**：首次使用某数据源，用收盘价重算 MA5/MA10，核对是否含当日。口径确认后全程保持一致，在报告中标注（如适用）。
4. **缺日重建**：先请使用者补发。允许重建但必须标注重建字段与依据，并说明对哪些指标有影响。节假日休市不算缺日。
5. 输出前自检：单位（pp vs 小数）、符号（W 方向）、噪声（是否低于 C_tol）、日期（环境数据是否同一交易日）、计数器（是否因缺日断开）。
6. 保留计算日志，便于事后复算与更正。
7. 发现旧结论与重算不符，在专项档案第 10 节注明日期、原结论、更正、是否影响结论，并作废旧叙述。

---

*Capital Behavior Analysis Framework v2.2 r3（A-Share General Edition）*
*整合：果论三分法 × AEI 双引擎 × CPS × Exit Index × GS 市场引擎 × 环境归因层 × 持仓模式*
