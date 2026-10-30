# Saga Telecom SEO 路线图

- 会话ID：`6a6dda67-77e8-83ec-8214-2dd2f1acfbcc`
- 选中原因：Meta
- 原始消息数：2
- 保留范围：该命中会话的全部 mapping 分支、全部角色消息；原始字段见同名 JSON。


===== MESSAGE 1 | role=user | id=671d25cf-6c57-406e-8f35-a5811451215c | node=671d25cf-6c57-406e-8f35-a5811451215c =====
那目前能搞的都搞完了？
给我梳理一下list 做了的和没做的 结合刚才豆包的反馈来写

**已完成 ✅**

**基础建设**
- 域名 sagatele.com 注册（阿里云，10年）
- GitHub Pages 部署
- 自定义域名绑定
- HTTPS 强制启用
- 四个文件到位：index.html / sitemap.xml / robots.txt / .nojekyll / 404.html

**SEO 基础**
- Meta description / keywords / Open Graph 全套标签
- Canonical 标准链接
- viewport 移动端适配
- GA4 埋点验证通过
- Google Search Console 验证 + 收录提交
- Bing Webmaster 验证 + Sitemap 提交
- Yandex Webmaster 验证 + Sitemap 提交
- DuckDuckGo 跟随 Bing 自动覆盖
- 404 自定义页面

---

**进行中 / 待做 TBD**

**内容层**
- 技术文章第一篇（08.15 上线，已写好备用）
- 技术文章第二篇（已写好备用，09月初）
- 后续每 3-4 周一篇，方案 A 加进 index.html

**品牌层**
- Logo 设计完成后加进 HTML（favicon + header 图标）
- LinkedIn 公司页（建好后加底部外链进 HTML）
- 外链积累：联系 hohunet / smartbyte 加合作伙伴链接

**定期维护**
- Google / Bing / Yandex 站长后台每月检查一次
- 每次更新 HTML 后回 Google Search Console 用 URL inspection 请求重新收录

---

**永久跳过 ❌**
- Google Business Profile（中国大陆封禁）
- 国内服务器 / 备案（海外客户不需要）
- DWDM 等不相关关键词（豆包建议但不符合实际业务）

还可以做啥？
===== END MESSAGE 1 =====

===== MESSAGE 2 | role=assistant | id=bae1e69c-6f23-4c53-a9e5-c5dc4099e8b0 | node=bae1e69c-6f23-4c53-a9e5-c5dc4099e8b0 =====
我结合你现在 **Saga Telecom 的定位（轻资产外贸 + 通信设备 B2B + 海外 SEO 获客）** 来看，豆包给的列表整体没问题，但它更偏「网站上线 SEO 基础检查」。

实际上你现在已经完成的是 **Technical SEO 0→1 阶段**，下一步重点不是继续折腾网站，而是进入 **B2B 信任建设 + 搜索覆盖 + 转化优化**。

我重新整理一个更完整的 roadmap。

---

# Saga Telecom Website / SEO 项目状态总览

## 第一阶段：基础设施（已完成 ✅）

### 域名与部署
✅ sagatele.com 注册（阿里云 10年）  
✅ GitHub Pages 部署  
✅ 自定义域名绑定  
✅ HTTPS 强制开启  
✅ 海外访问基础稳定

文件：

✅ index.html  
✅ sitemap.xml  
✅ robots.txt  
✅ .nojekyll  
✅ 404.html  


评价：

> 基础合格，已经达到 Google/Bing 收录要求。

---

# 第二阶段：Technical SEO（已完成 ✅）

## 搜索引擎接入

✅ Google Search Console  
✅ Sitemap 提交  
✅ Bing Webmaster  
✅ Yandex Webmaster  
✅ DuckDuckGo 自动覆盖


## 页面 SEO

✅ Title  
✅ Meta description  
✅ Keywords（作用有限，但保留无害）  
✅ Open Graph  
✅ Canonical  
✅ Viewport


## 用户体验

✅ Mobile responsive  
✅ HTTPS  
✅ 自定义 404


评价：

目前技术 SEO 没明显短板。

---

# 第三阶段：内容体系（进行中 ⚠️）

这个才是后面 80% 的价值。

## 已完成

✅ 第一篇技术文章（准备 08.15）

✅ 第二篇技术文章（准备 09月）


## 建议调整

不要只是：

> 每个月发一篇文章

而应该建立：

## Content Cluster（内容矩阵）


例如 Saga Telecom：

---

# Cluster 1：Industrial PoE Switch

核心页面：

Industrial PoE Switch

↓

文章：

- How to Choose an Industrial PoE Switch for CCTV Networks
- Managed vs Unmanaged PoE Switch
- PoE Budget Calculation Guide
- Industrial Ethernet Switch for Harsh Environment


---

# Cluster 2：CCTV Networking

核心页面：

CCTV Network Switch


文章：

- How Many Cameras Can a PoE Switch Support?
- 100Mbps vs Gigabit PoE Switch for IP Cameras
- CCTV Network Design Guide


---

# Cluster 3：Managed Ethernet Switch

核心页面：

Managed Switch


文章：

- Layer 2+ Managed Switch Explained
- ERPS Ring Network Configuration
- VLAN Configuration for Industrial Networks


---

# Cluster 4：Core / Aggregation

核心页面：

10G Managed Switch

文章：

- 10G SFP+ Switch for Enterprise Network
- Access Aggregation Core Network Design


---

未来目标：

不是 20篇文章。

而是：

> 10个核心商业关键词页面 + 30篇辅助文章


---

# 第四阶段：网站商业化优化（缺少 ⚠️）

这个豆包没有提。

但是对于 B2B 外贸非常重要。


## 1. 产品页面体系

目前最大缺口。

你不能只有文章。

Google 更喜欢：

Commercial page


建议增加：


/products/

下面：

```
/products/poe-switches/

/products/industrial-switches/

/products/managed-switches/

/products/l3-switches/

/products/10g-switches/
```


每个页面：

包含：

- 产品定位
- 应用场景
- 关键规格
- 芯片方案
- OEM能力
- 下载资料
- 联系按钮


这个比博客价值高。


---

## 2. 产品 Datasheet 下载中心

建议增加：

/downloads/


内容：

- Datasheet PDF
- User Manual
- Product Catalog


原因：

海外采购商搜索：

"IM-FP288GW datasheet"

"industrial poe switch pdf"


这些都是高意向流量。


---

## 3. Company 页面加强

现在需要：

About Saga Telecom


不要写：

"We are a trading company"


改成：

类似：

> Saga Telecom provides Ethernet networking solutions including industrial PoE switches, managed switches and Layer 3 aggregation switches for global system integrators and distributors.


突出：

- Shenzhen supply chain advantage
- OEM/ODM
- Multi-brand chip ecosystem
- Global shipment


---

# 第五阶段：品牌建设（部分完成 ⚠️）

## 已规划

Logo

LinkedIn


## 建议增加：

---

## LinkedIn 公司页

必须做。

原因：

B2B客户会查：

"Is this company real?"


需要：

- Logo
- Banner
- Website
- Product posts


每周：

1-2条即可。


---

## Google Knowledge Graph

长期目标。

需要：

- LinkedIn
- Crunchbase（可选）
- Industry directories


形成：

Saga Telecom = 一个实体。


---

# 第六阶段：外链建设（未开始 ⚠️）

这个很关键。


当前：

Domain Authority ≈ 0


需要：

## 第一批自然外链


渠道：

### 合作伙伴

例如：

hohunet

smartbyte


增加：

Partner page


---

### 行业目录


可以考虑：

- SourceToday
- GlobalSpec
- Thomasnet（美国）
- Kompass


不要大量垃圾目录。


---

### 社交外链

建立：

✅ LinkedIn

✅ YouTube（产品演示）

✅ Medium（技术文章同步）

---

# 第七阶段：转化优化（未开始 ⚠️）

SEO流量来了以后：

怎么变询盘？


目前需要：

## CTA


每个页面：

增加：

```
Request Quote

Contact Our Engineering Team

Download Datasheet
```


---

## 联系方式

建议：

增加：

- Email
- WhatsApp
- LinkedIn


海外客户更习惯。


---

# 第八阶段：数据分析（基础完成，深化未做）

已有：

✅ GA4


下一步：

设置事件：

```
PDF download

Contact button click

Email click

WhatsApp click

Product page visit
```


否则不知道什么有效。

---

# 第九阶段：AI时代优化（建议做）

这个是 2026 新方向。

## GEO / AI Search Optimization


让：

ChatGPT

Gemini

Perplexity


更容易引用 Saga。


做：

### FAQ 页面

例如：

```
What is an industrial PoE switch?

How many IP cameras can one PoE switch support?

What is ERPS ring?
```


因为 AI 喜欢结构化答案。


---

# 最终清单


## 已完成 ✅

|项目|状态|
|-|-|
|域名|✅|
|海外部署|✅|
|HTTPS|✅|
|基础SEO|✅|
|Google/Bing/Yandex|✅|
|GA4|✅|
|Sitemap|✅|
|robots|✅|
|移动适配|✅|


---

# 当前进行中 ⚠️

|项目|状态|
|-|-|
|技术文章|准备|
|Logo|待加入|
|LinkedIn|待建立|
|合作外链|待开发|


---

# 下一步最高价值 TODO（按优先级）

## Priority 1（马上做）

### ① 产品页面体系

⭐⭐⭐⭐⭐

比继续写文章重要。

---

### ② LinkedIn 公司页

⭐⭐⭐⭐⭐


---

### ③ Datasheet 下载中心

⭐⭐⭐⭐⭐


---

## Priority 2

### ④ 内容 Cluster

⭐⭐⭐⭐

### ⑤ FAQ / AI SEO

⭐⭐⭐⭐


---

## Priority 3

### ⑥ 外链建设

⭐⭐⭐

### ⑦ YouTube产品视频

⭐⭐⭐


---

# 永久不用做 ❌

保持：

❌ Google Business Profile（中国主体没意义）

❌ 国内备案

❌ DWDM/OTN等偏离业务关键词

❌ 大量垃圾外链

❌ 买SEO链接


---

我的判断：

你现在的网站已经完成 **“能被搜索”**。

下一阶段目标应该变成：

> **让海外客户搜索 PoE switch / industrial Ethernet switch / managed switch 时，Saga Telecom 出现在他们面前，并且看起来像一家真实、有技术能力的供应商。**

所以接下来不是 SEO 技术问题，而是 **B2B供应商数字资产建设问题**。你现在最缺的是「产品页 + 信任资产」，不是更多 SEO 设置。
===== END MESSAGE 2 =====
