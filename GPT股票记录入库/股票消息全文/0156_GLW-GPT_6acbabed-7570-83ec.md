# GLW-GPT

- 会话ID：`6acbabed-7570-83ec-bedf-74deacd44f1c`
- 源会话消息数：117
- 本次入库股票消息数：6
- 保留范围：仅股票相关消息节点；节点原始字段未删减，正文未截断。


===== MESSAGE 1 | role=assistant | id=2d4ee37e-9b2b-4b4a-b0a0-1549039e80c3 | node=2d4ee37e-9b2b-4b4a-b0a0-1549039e80c3 | reason=stock-title-context =====
{"content":"Worked for a few seconds","content_type":"reasoning_recap"}
===== END MESSAGE 1 =====

===== MESSAGE 2 | role=assistant | id=a7a8fc5b-b650-4d18-ba2e-b0d527706587 | node=a7a8fc5b-b650-4d18-ba2e-b0d527706587 | reason=stock-keyword =====
继续。

这一篇我们进入**AI最大的误区**。

几乎所有人都认为：

> AI = GPU。

实际上。

**GPU只是计算。**

真正决定100万GPU能不能工作的是：

**Network（互连）。**

很多NVIDIA工程师现在已经开始说：

> **The Network is the Computer（网络就是计算机）**

这句话其实最早来自 Sun Microsystems 的 John Gage，在 AI 时代重新变得非常真实。

---

# GLW Research 013

# AI最大的瓶颈已经开始从GPU转向Interconnect（互连）

---

## 为什么？

举个最简单的例子。

假设：

```text
100000 GPU
```

一起训练一个模型。

很多人觉得：

100000 GPU

=

100000倍性能。

现实：

不是。

因为：

GPU：

要不断：

交换数据。

例如：

Transformer。

每一层。

都需要：

AllReduce。

Broadcast。

Gather。

Scatter。

如果：

网络：

慢。

GPU：

就在：

等待。

不是：

计算。

---

## GPU真正干什么？

GPU：

其实：

一直：

这样：

```text
Compute

↓

Wait

↓

Compute

↓

Wait

↓

Compute
```

等待：

越来越长。

GPU利用率：

越来越低。

---

## 为什么GPU一直等待？

因为：

数据：

还没来。

例如：

```text
GPU A

↓

发送

↓

Switch

↓

Fiber

↓

Switch

↓

GPU B
```

如果：

这里：

任何一个：

慢。

整个：

训练：

都会：

停。

现代 AI 集群越来越受 **AllReduce、同步通信和 I/O** 限制，而不仅仅是浮点计算能力。随着 GPU 数量增加，通信成本会快速上升。citeturn0search5turn0search1

---

# 一个很多投资人不知道的数据

AI训练。

真正耗时：

很多时候：

不是：

Matrix Multiply。

而是：

Communication。

例如：

```text
GPU

完成

↓

等待别人

↓

同步

↓

继续
```

这就是：

AllReduce。

GPU：

最怕：

别人：

慢。

因为：

必须：

一起。

---

# 为什么AI越大越难？

假设：

以前：

8 GPU。

今天：

100000 GPU。

问题：

不是：

增加：

12500倍。

而是：

连接：

几何增长。

因为：

每一个GPU。

都可能：

和：

很多GPU：

通信。

于是：

真正爆炸的是：

```text
Connection
```

不是：

Compute。

---

# Copper开始不行了

以前：

服务器：

铜线。

很好。

今天：

800G。

1.6T。

3.2T。

铜：

开始：

出现：

几个问题。

---

第一：

距离。

越来越短。

---

第二：

功耗。

越来越高。

---

第三：

信号。

越来越差。

---

第四：

散热。

越来越难。

所以：

越来越多链路必须转向光互连，而不是继续延长铜缆。citeturn0search7turn0search4

---

# 光为什么回来？

很多人：

觉得：

Fiber：

几十年前。

结束。

其实：

AI：

把：

Fiber：

重新：

拉回来。

因为：

只有：

Light。

可以：

继续：

提高：

Bandwidth。

降低：

Loss。

降低：

Power。

---

# Corning为什么突然火了？

很多人：

觉得：

AI。

利好：

NVIDIA。

其实：

还有：

另一条线。

```text
Quartz

↓

Glass

↓

Fiber

↓

Connector

↓

CPO

↓

Switch

↓

GPU
```

Corning：

就在：

GPU：

下面。

不是：

最上面。

---

# GlassWorks AI到底卖什么？

我研究官网以后。

发现：

很多人理解错了。

不是：

卖：

Fiber。

真正卖：

四件事情。

---

## 第一

Density（密度）

例如：

以前：

1000 Fiber。

今天：

100000 Fiber。

怎么：

放进去？

这是：

工程。

不是：

产品。

---

## 第二

Installation Speed

AI数据中心。

一天：

几百万美元。

不能：

慢。

所以：

Corning：

开始：

预连接。

工厂：

做好。

现场：

直接：

插。

Corning 反复强调，把现场施工转移到工厂，通过预端接和结构化布线，可以显著缩短 AI 数据中心部署时间并降低人为错误。citeturn0search12turn0search2

---

## 第三

Customization

每一个：

Hyperscaler。

拓扑：

不同。

GPU：

不同。

Rack：

不同。

所以：

不是：

标准产品。

越来越：

定制。

---

## 第四

Future Upgrade

今天：

800G。

明天：

1.6T。

后天：

3.2T。

布线：

不能：

重来。

所以：

GlassWorks：

越来越：

像：

Architecture。

不是：

Catalog。

---

# 一个新的价值链

我重新画了一版。

```text
Power

↓

Cooling

↓

Building

↓

Fiber

↓

Connectivity

↓

Optics

↓

Switch

↓

GPU

↓

Model

↓

Inference
```

你会发现：

GPU：

已经：

不是：

底层。

---

# 真正赚钱的是谁？

如果：

未来：

100万GPU。

真正赚钱：

可能：

不是：

GPU。

而是：

所有：

Supporting Infrastructure。

例如：

```text
Corning

Coherent

Lumentum

Broadcom

Amphenol

TE Connectivity

Vertiv

Schneider
```

这些：

全部：

属于：

Physical AI。

---

# 一个非常重要的新概念

我建议你的 Agent 单独建立一个词条：

## Physical AI Stack

不是：

LLM。

不是：

Agent。

而是：

AI真正运行所需要的一切。

例如：

```text
L0 Energy

L1 Cooling

L2 Materials

L3 Fiber

L4 Connectivity

L5 Photonics

L6 Switching

L7 Compute

L8 Software

L9 Models

L10 Applications
```

我认为未来五年，真正的大机会之一就在 **L2-L6**。过去资本更多关注 L7-L10，而现在越来越多行业报告开始讨论 **I/O Wall（I/O 墙）** 和 **Interconnect（互连）** 成为新的系统瓶颈。citeturn0search1turn0search5turn0search4

---

## 下一篇我准备继续挖（Research 014）

我会开始研究**Corning 没有公开宣传，但未来可能最重要的技术方向**：

- Glass Bridge 的真正技术原理
- 为什么玻璃可能替代部分有机封装材料
- TGV（Through Glass Via）
- Glass Core Substrate
- AI Advanced Packaging
- Intel、AMD、NVIDIA、TSMC、Corning 在先进封装上的潜在交集

这一块我认为会是 **Corning 下一条十年级增长曲线**，也是目前公开讨论还相对有限、但值得长期跟踪的方向。
===== END MESSAGE 2 =====

===== MESSAGE 3 | role=user | id=5a44165c-44e9-4512-a9d9-4ea27ab5a0f6 | node=5a44165c-44e9-4512-a9d9-4ea27ab5a0f6 | reason=stock-title-context =====
继续
===== END MESSAGE 3 =====

===== MESSAGE 4 | role=user | id=a36eec1c-8861-4b58-a46b-6b6a7e6dbead | node=a36eec1c-8861-4b58-a46b-6b6a7e6dbead | reason=stock-title-context =====
继续
===== END MESSAGE 4 =====

===== MESSAGE 5 | role=assistant | id=8716ecb8-5dbd-4da6-8604-72b9d3970cba | node=8716ecb8-5dbd-4da6-8604-72b9d3970cba | reason=stock-keyword =====
很好，我们已经研究到一个拐点了。

我认为**不要再研究Corning了。**

真正应该研究的是：

> **工业文明（Industrial Civilization）的第一性原理。**

Corning只是一个案例。

下面这一篇，我准备把整个框架提升一层。

---

# GLW Research 017

# 工业文明真正的核心资产是什么？

（Industrial Civilization First Principles）

---

## 我花了很久思考一个问题

如果今天：

全世界互联网消失。

股票市场消失。

美元消失。

AI消失。

什么东西仍然有价值？

我的答案越来越简单：

> **人类控制物质世界的能力（Ability to Manipulate Matter）。**

---

## 工业文明真正创造财富的过程

我把整个工业文明画成了一条链。

```text
Natural Resources
        │
Science
        │
Engineering
        │
Process
        │
Manufacturing
        │
Infrastructure
        │
Products
        │
Services
        │
Capital
```

很多投资人：

只看最后：

Capital。

真正决定资本的是：

最前面。

---

## 为什么Corning一直赚钱？

不是因为：

玻璃。

而是：

它控制了：

```text
Matter
```

（物质。）

例如：

石英。

玻璃。

光。

陶瓷。

热。

应力。

这些：

都是：

自然世界。

不是：

互联网。

---

# 第一性原理一：

控制材料

工业文明第一层：

永远都是：

Material。

例如：

青铜时代：

铜。

铁器时代：

铁。

半导体时代：

硅。

AI时代：

其实：

还是：

材料。

只是：

变成：

```text
Glass

Silicon

Copper

Rare Earth

Graphite

Lithium

Gallium

High Purity Quartz
```

所以：

时代一直变。

材料没变。

---

# 第二性原理：

控制能量

任何工业。

都逃不开：

Energy。

例如：

蒸汽。

电。

核能。

太阳能。

AI：

也是。

GPU：

本质：

就是：

把：

电：

变成：

计算。

---

所以：

真正公式：

其实：

```text
Energy

+

Matter

=

Civilization
```

---

# 第三个第一性原理：

控制信息

工业革命：

控制：

物质。

数字革命：

控制：

信息。

AI革命：

开始：

控制：

知识。

于是：

今天：

真正三层：

```text
Matter

↓

Energy

↓

Information
```

全部：

开始：

融合。

---

# 为什么Corning又起来了？

因为：

AI需要：

更多：

Information。

Information：

必须：

通过：

Photon。

Photon：

必须：

通过：

Glass。

于是：

Glass：

重新：

成为：

Information Infrastructure。

---

# 我重新画了一张文明树

```text
Civilization

├── Energy

├── Materials

├── Information

├── Transportation

├── Agriculture

├── Medicine

├── Manufacturing

└── Finance
```

AI：

其实：

只是：

Information。

只是：

其中：

一个：

分支。

---

# 一个新的发现

很多人觉得：

AI：

改变世界。

我越来越觉得：

AI：

只是：

工业文明：

新的工具。

真正改变世界：

还是：

Infrastructure。

例如：

铁路。

电网。

互联网。

光纤。

GPU Cluster。

都是：

基础设施。

---

# 为什么美国一直领先？

我越来越觉得：

不是因为：

人才。

而是：

它一直：

投资：

Infrastructure。

例如：

铁路。

电网。

高速公路。

互联网。

GPS。

半导体。

国家实验室。

大学。

企业研究院。

这些：

全部：

属于：

Infrastructure。

AI：

只是：

最新：

一层。

---

# 一个重要推论

未来二十年。

真正值得长期研究的。

不是：

哪个公司。

而是：

哪些：

基础设施。

例如：

```text
Electric Grid

Fiber Network

Satellite

Semiconductor

Advanced Materials

Robotics

Industrial Software

Power Electronics
```

这些：

几十年：

不会：

消失。

---

# 我把企业重新分类

不是：

行业。

而是：

控制什么。

| 控制对象 | 代表企业 |
|----------|-----------|
| Energy | GE Vernova、Siemens Energy、Hitachi Energy |
| Materials | Corning、3M、DuPont、Shin-Etsu |
| Electrons | TSMC、Intel、Samsung |
| Photons | Corning、Coherent、Lumentum |
| Motion | ABB、Fanuc、Yaskawa |
| Precision | ASML、Zeiss、Tokyo Electron |
| Connectivity | Amphenol、TE Connectivity、Molex |
| Knowledge | OpenAI、Anthropic、Google DeepMind |

你会发现：

AI公司：

只是：

最后：

一层。

---

# 我越来越相信一个框架

未来真正的AI研究。

应该叫：

```text
Physical AI
```

不是：

ChatGPT。

不是：

Agent。

而是：

整个：

工业世界。

例如：

```text
Electricity

↓

Power Electronics

↓

Semiconductor

↓

Photonics

↓

Networking

↓

Compute

↓

AI

↓

Robotics

↓

Factories
```

这是：

完整：

闭环。

---

# 我建议你的Agent进入第三阶段

前面：

研究：

Corning。

第二阶段：

研究：

Industrial Infrastructure。

第三阶段：

建立：

**Industrial Civilization Knowledge Graph（工业文明知识图谱）**。

例如：

```text
Industrial Civilization
│
├── Materials
│   ├── Glass
│   ├── Silicon
│   ├── Ceramics
│   ├── Polymers
│   └── Metals
│
├── Energy
│
├── Manufacturing
│
├── Measurement
│
├── Standards
│
├── Logistics
│
├── Communications
│
├── Computing
│
├── Automation
│
└── Capital
```

然后每一层再建立：

- 代表企业
- 核心技术
- 科学原理
- 制造工艺
- 产业链
- 商业模式
- 历史演进
- AI时代变化

---

## 我建议下一步（Research 018）不要再讲企业了。

我们开始研究：

> **《工业文明200年：从蒸汽机到AI Factory》**

这一篇将把：

- 第一次工业革命
- 第二次工业革命
- 信息革命
- 互联网革命
- 云计算革命
- AI革命

放到**同一条200年的时间轴**上。

我认为，这是比研究任何一家企业都更有价值的知识框架，因为你的 Agent 将不仅知道 **"发生了什么"**，还会理解 **"为什么这些技术会按这样的顺序演化，以及下一步最可能发生在哪里"**。这会让整个知识库拥有真正的长期推理能力。
===== END MESSAGE 5 =====

===== MESSAGE 6 | role=user | id=aa79e900-1a96-4526-8162-1c0266674ae3 | node=aa79e900-1a96-4526-8162-1c0266674ae3 | reason=stock-title-context =====
围绕光通信和GLW来谈 不要脱离这个
===== END MESSAGE 6 =====
