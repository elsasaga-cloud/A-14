# Mikrotik vs 交换机价值分析

- 会话ID：`6a5f05a9-f7e8-83ec-8013-92b6e57b32dc`
- 源会话消息数：54
- 本次入库股票消息数：1
- 保留范围：仅股票相关消息节点；节点原始字段未删减，正文未截断。


===== MESSAGE 1 | role=assistant | id=67bd39a0-7686-4d15-9548-4f8c51077d13 | node=67bd39a0-7686-4d15-9548-4f8c51077d13 | reason=stock-keyword =====
我认真看了 Claude 这份，其实**80%是通用B2B获客方法**，如果卖机械、电子元器件、PCB都适用。

但对于**你的 Saga（Marvell Access Switch + Centec Aggregation/Core + OEM/ODM）**来说，我觉得还可以增加一些**更垂直、更高ROI**的方法。

我按你的业务重新整理一下。

---

# 第一类（★★★★★）—— 找「Marvell生态」

这是Claude没有深入讲的。

你的客户不是所有交换机客户。

而是：

> **已经认可 Marvell Managed Ethernet 的公司。**

所以要建立一个数据库。

例如：

| 品牌 | 芯片 | 主要产品 | 是否OEM | 是否目标 |
|------|------|----------|----------|----------|
| MikroTik | Marvell | Access | 否 | ⭐⭐⭐⭐⭐ |
| PLANET | Marvell | Industrial | 部分 | ⭐⭐⭐⭐⭐ |
| ORing | Marvell | Industrial | 部分 | ⭐⭐⭐⭐⭐ |
| Korenix | Marvell | Industrial | 未知 | ⭐⭐⭐⭐ |
| Atop | Marvell | Industrial | 未知 | ⭐⭐⭐⭐ |
| Netonix | Marvell | WISP | 否 | ⭐⭐⭐⭐⭐ |

然后：

继续扩展。

不是找：

> 谁有交换机

而是：

> 谁有Marvell交换机。

---

# 第二类（★★★★★）—— SDK开发者反推

这个Claude完全没提。

Marvell其实有：

SDK。

很多公司招聘：

```
Marvell SDK
Prestera SDK
DX SDK
```

或者：

```
98DX
Prestera
Marvell Switch
```

这种招聘。

例如：

LinkedIn：

```
Marvell SDK engineer

Prestera

98DX
```

招聘这些人的公司：

就是：

**自己做交换机产品。**

很多：

OEM品牌。

这是非常好的线索。

---

# 第三类（★★★★★）—— Firmware版本追踪

很多品牌：

Firmware下载页面：

```
Release Note

Version

Bug Fix
```

例如：

```
Firmware V7.3
```

里面会写：

```
Support 98DX3236

Support ERPS

Support PoE++
```

你可以：

建立：

```
Brand

Firmware

Chip

Function

Last update
```

数据库。

这样：

以后客户说：

> We need ERPS.

你马上知道：

哪个品牌支持。

---

# 第四类（★★★★★）—— MIB数据库

这个其实你已经开始做了。

建议：

建立：

```
Brand

MIB

Trap

OID

SNMP

CLI

SSH

REST API

NETCONF
```

例如：

|Brand|SNMP|Trap|REST|
|------|-----|------|------|
|MikroTik|✔|✔|API|
|PLANET|✔|✔|部分|
|SmartByte|✔|✔|待确认|

以后：

Frank问：

> API?

你马上知道：

差距在哪。

---

# 第五类（★★★★★）—— NMS生态

Claude提Apollo。

我觉得：

更值得的是：

找：

```
NMS company

Network monitoring

Industrial monitoring

SCADA software

Remote monitoring
```

例如：

Frank。

这类客户：

价值远高于：

Distributor。

---

# 第六类（★★★★★）—— GitHub

这里不要搜：

```
managed switch
```

而是：

搜：

```
Prestera

Marvell

98DX

DX3236

switchdev

ONIE

SONiC

Open Network Linux
```

很多：

工程师：

会暴露：

公司。

---

# 第七类（★★★★☆）—— ONIE生态

这个Claude没提。

很多：

交换机：

支持：

ONIE。

你可以：

搜：

```
ONIE compatible switch

ONIE partner

ONIE hardware
```

这类客户：

一般：

技术水平很高。

OEM概率高。

---

# 第八类（★★★★★）—— SONiC

你之前其实聊过。

虽然你现在：

不想卖SONiC。

但是：

很多公司：

以前：

做SONiC。

后来：

又推出：

普通Managed Switch。

所以：

可以反查。

例如：

```
SONiC

whitebox

NOS

Marvell
```

---

# 第九类（★★★★★）—— LinkedIn换一种搜法

不要：

```
switch
```

太宽。

建议：

```
Marvell

Prestera

Industrial Ethernet

PoE Switch

Fiber Switch

Managed Ethernet

Layer2 Switch

Layer3 Switch

Network Appliance
```

以及：

```
Firmware Engineer

Embedded Engineer

Product Manager

Hardware Manager
```

这种。

很多：

产品经理：

回复率比采购高。

---

# 第十类（★★★★★）—— 型号替代数据库（我最推荐）

你前面已经开始做。

继续做：

例如：

```
MikroTik CRS326
↓

SmartByte STC-24G

↓

价格

芯片

PoE

ERPS

CLI

SNMP
```

形成：

替代表。

以后：

客户：

```
Currently using CRS326.
```

你：

立即：

发：

```
Equivalent Product
```

这个成交率非常高。

---

# 第十一类（★★★★☆）—— 规格书SEO

这个结合你的网站。

例如：

建立：

```
CRS326 Alternative

PLANET Alternative

ORing Alternative

Cisco CBS Alternative

```

页面。

例如：

```
Alternative to MikroTik CRS326-24G-2S+RM

Alternative to PLANET IGS6329

Alternative to ORing IPS3082
```

Google很容易吃长尾。

---

# 第十二类（★★★★★）—— 认证数据库反推

不是：

FCC。

而是：

直接搜：

```
Declaration of Conformity

CE

UKCA

RoHS
```

PDF。

很多：

里面：

写：

```
Manufacturer

OEM

Importer
```

非常容易：

找到：

品牌。

---

# 我认为你未来真正应该建立的是一个Git仓库

就像你股票那个项目一样。

例如：

```
Marvell-Ecosystem/

├── Brand/
│     Mikrotik.md
│     Planet.md
│     Oring.md
│
├── Chip/
│     98DX3236.md
│     98DX226S.md
│
├── Customer/
│     SIMREX.md
│     Angora.md
│
├── Replacement/
│     CRS326.md
│     CRS328.md
│
├── NMS/
│     SNMP.md
│     MIB.md
│     Trap.md
│
├── Firmware/
│     ReleaseNotes/
│
└── LinkedIn/
      SearchQueries.md
```

---

## 我认为按照 **Saga 的业务模型**，这些获客方法的真实优先级应该是：

| 优先级 | 方法 | 为什么 |
|--------|------|---------|
| ⭐⭐⭐⭐⭐ | **Marvell品牌数据库** | 找与你产品最重合的生态，而不是泛交换机市场 |
| ⭐⭐⭐⭐⭐ | **型号替代库（Alternative Matrix）** | 直接回答客户“我们现在用 CRS326”这类问题，最容易转化 |
| ⭐⭐⭐⭐⭐ | **NMS / MIB / SNMP能力库** | 与 Frank、SIMREX、工业方案商直接相关，差异化明显 |
| ⭐⭐⭐⭐⭐ | **LinkedIn + Apollo 精准开发** | 搜 Marvell、Industrial Ethernet、Prestera 等关键词，而不是泛搜 switch |
| ⭐⭐⭐⭐☆ | **ImportYeti / Panjiva 海关数据** | 验证真实采购行为，寻找持续进口中国交换机的客户 |
| ⭐⭐⭐⭐☆ | **招聘 / Firmware / SDK 反推** | 找正在开发新产品或维护 Marvell 平台的品牌，时机好 |
| ⭐⭐⭐☆☆ | **Google PDF / CE / FCC / DoC** | 补充品牌、型号和OEM关系，适合作为研究工具 |
| ⭐⭐☆☆☆ | **GitHub / 专利 / Reddit** | 能发现一些高质量机会，但投入时间较大，作为长期补充即可 |

我觉得这套比通用的 B2B 获客方法更符合你未来 10 年想建立的 **Marvell Managed Ethernet 知识资产**。这些内容完全可以沉淀到 Git 仓库里，让 AI 持续帮你扩展、分类和分析，最后形成 Saga 自己独有的竞争壁垒。
===== END MESSAGE 1 =====
