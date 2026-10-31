# 源 ZIP 反向交叉检查

本报告只记录审计元数据，不复制未入选消息正文。hard 为独立的高召回股票信号扫描，broad 为较宽的股票词扫描；命中不等于必然应入库，需结合主题判断。

- 源会话：341；源消息节点：4715；已入库节点：1358
- 入库节点在源会话中找不到：0
- 源消息 hard 股票信号：1343；其中未入库：**130**
- 未入库但仅有 broad 股票信号：**11**
- 股票标题下、邻近入选消息但未入库的短上下文：**12**
- 已入库但含非股票语境词的消息（供误收复核）：**352**
- 未入库 hard 消息引用且 ZIP 中实际存在的附件：**4**

## 未入库 hard 信号消息（逐条复核清单）

| 会话 | 节点ID | 角色 | 字符数 | hard 命中 | 当前分类器命中 |
|---|---|---|---:|---|---|
| 散热孔设计选择 | `335959d0-a0e6-4d69-85f3-84b679fc0b07` | assistant | 2,014 | etf |  |
| 芯片功能开发与需求 | `5fe4c76b-49aa-4dd1-ac23-5e8289fe92a5` | assistant | 2,793 | etF | 复盘 |
| 芯片功能开发与需求 | `9db10184-50b6-4014-ab71-300986b645fd` | assistant | 1,158 | etF |  |
| 芯片功能开发与需求 | `7a096430-4a27-4a17-bfd9-d6ed9392f461` | assistant | 6,309 | ETF, etF |  |
| TQR玩法 | `8383c218-b285-4d10-b4f9-7d645677c4df` | user | 27 | 期权 |  |
| 513500 | `ad4a8e03-853a-47de-a17d-802824e202a7` | user | 286 | 定投 | 定投, 投资 |
| 513500 | `7925c347-3144-4824-8805-fd050cff3e17` | assistant | 2,095 | 基金, 定投 | 定投 |
| 513500 | `9d295fef-10e3-40ea-881b-315f5688030a` | assistant | 2,132 | 清仓 | 清仓 |
| Netas | `f93256b2-c649-43bf-8573-9853e00888ad` | assistant | 3,004 | 分红, 涨停 | 分红, 涨停, 股东, 营收 |
| Netas | `94573ff2-d8ed-48fa-ab10-aa581fb0078a` | user | 3,229 | 定投 | 定投 |
| Netas | `e296a243-2f43-4da1-b777-978a1a169735` | assistant | 1,441 | 筹码 |  |
| 纳指100与电子奴隶制 | `6fddbb9c-8364-4921-a1d2-fd13d159aced` | user | 2,155 | 中国银行, 分红 | 中国银行, 分红, 投资, 资产配置 |
| 纳指100与电子奴隶制 | `124edcac-56d3-4583-8b06-99d9ec9e472d` | user | 220 | 分红 | 分红 |
| 纳指100与电子奴隶制 | `d4fe635d-4fbc-43c2-b221-d7e9b636f24b` | assistant | 1,846 | 分红 | 分红 |
| 纳指100与电子奴隶制 | `e275f061-af70-4b7a-bc3e-5dbaf8a8851f` | user | 1,912 | 分红 | 分红 |
| 纳指100与电子奴隶制 | `8380dbe8-610f-48f2-998d-e6ee2c5840df` | assistant | 1,827 | 中国银行, 分红 | 中国银行, 分红, 投资 |
| 纳指100与电子奴隶制 | `526a7606-04eb-4b8e-9852-0de21f3666d5` | assistant | 1,928 | 中国银行, 分红 | 中国银行, 分红, 投资 |
| 纳指100与电子奴隶制 | `ab154d7f-35b1-4f38-bf47-90673e9fa472` | assistant | 2,160 | 分红 | 分红, 投资 |
| 纳指100与电子奴隶制 | `d5663737-9291-4719-ac21-eb3cc6829f1c` | assistant | 1,851 | 分红, 股票 | 分红, 投资, 股票 |
| 纳指100与电子奴隶制 | `c866c575-9d5c-4487-acfb-956685d1d2cb` | user | 168 | 分红, 期权 | 分红, 投资 |
| 纳指100与电子奴隶制 | `4e299930-9642-4d23-b95f-2c26671ca40a` | assistant | 2,113 | 分红 | 分红, 投资 |
| 纳指100与电子奴隶制 | `c499b392-9375-465d-9d67-fb8b7f4192f7` | assistant | 2,129 | 分红, 基金, 期权 | 分红, 投资 |
| 纳指100与电子奴隶制 | `1e10999f-e324-44ba-b243-d8bf2504db3f` | user | 1,879 | 分红, 期权, 筹码 | 分红 |
| 纳指100与电子奴隶制 | `98c69eaf-899e-4066-bf57-4334135b9504` | assistant | 1,819 | 分红, 期权 | 分红 |
| 纳指100与电子奴隶制 | `1aed3887-4859-4666-bf4b-1312f091089d` | user | 3,924 | 分红, 浮盈, 筹码 | 分红, 投资, 浮盈 |
| 纳指100与电子奴隶制 | `bc7ae2ce-bdd0-4af0-81cc-19c0ea61c42c` | assistant | 1,765 | 分红 | 分红, 投资 |
| 挪威模式投资思维 | `b101e180-d2ca-498a-a6a4-c754e98ddfc8` | user | 195 | 基金 | 投资 |
| 挪威模式投资思维 | `5f87caea-9b15-46b3-899f-f45815a7805f` | assistant | 1,575 | 分红, 基金 | 分红, 投资, 英伟达 |
| 挪威模式投资思维 | `e60d26b0-36a7-4700-9423-ada037e3ca77` | assistant | 2,475 | 分红, 基金, 股票 | 估值, 分红, 投资, 股票, 英伟达 |
| 挪威模式投资思维 | `019a8103-5b73-4c31-ae17-d88dcaa5d024` | user | 47 | 基金 | 投资 |
| 挪威模式投资思维 | `9c979b33-ea8e-4c19-9a3a-fec74a5f6ef3` | assistant | 2,131 | 分红, 基金, 定投 | 分红, 定投, 投资, 股东 |
| 人际与精力管理 | `d426c801-c3db-4979-b7d0-6628f6fae791` | assistant | 1,420 | 股票 | 投资, 股票 |
| 深圳长期发展布局 | `da211a13-4a2a-4983-9c1f-dab6f124cf6c` | assistant | 2,375 | 分红 | 分红 |
| 通信行业长期发展 | `9ab2ccbd-ee6d-4740-80ef-a0554e4528a4` | user | 55,435 | 分红 | 分红, 复盘, 投资 |
| 客户二次评估与成交概率_ALL | `fdcb1cbd-fff3-48c7-9562-85e76241211c` | user | 8,213 | etf, ipo | Stock, 谷歌, 阿里巴巴 |
| 客户二次评估与成交概率_ALL | `9546547d-8ba1-435b-8860-3ebbf5ed964c` | assistant | 3,943 | ipo |  |
| 客户二次评估与成交概率_ALL | `0dccbb91-bfd3-4fc7-acd4-9a6055f0f4c9` | user | 3,086 | ipo |  |
| 客户二次评估与成交概率_ALL | `3fdfd6e4-c5f2-47aa-9138-4674cb6c06d6` | assistant | 2,677 | ipo |  |
| 客户二次评估与成交概率_ALL | `72e9780f-2f26-45ed-ac44-068915adbea5` | user | 8,367 | ipo | Stock, 谷歌 |
| 客户二次评估与成交概率_ALL | `e16c32c2-4ada-4485-8931-a29275532738` | user | 9,047 | etf, ipo | Stock, 谷歌, 阿里巴巴 |
| 客户二次评估与成交概率_ALL | `96aed6c3-330a-431f-ba56-c920ac96c09b` | assistant | 3,040 | ipo |  |
| 客户二次评估与成交概率_ALL | `29fbda2e-6601-4389-9aaf-f4ed1b706796` | user | 9,399 | ipo | Stock, 谷歌 |
| MSTP设备分析 | `d7fe35fc-f03e-4de8-b5fc-8407a8c91d77` | assistant | 2,146 | TSM | TSM |
| MSTP设备分析 | `eeee50ad-e4e7-402c-8d66-0c1667a02bd1` | assistant | 1,864 | TSM | TSM |
| 惠普估值与期权策略 | `42039ef2-9f77-4d42-8541-619b667734ca` | user | 62 | 筹码 |  |
| 时间增益行为模型 | `6494bc45-ded6-4275-8029-806fdc0faeaf` | assistant | 2,323 | 分红, 股票 | 003816, 600863, stock, 分红, 投资, 股票 |
| 饮食系统构建指南 | `f7e43c4a-3a0d-440a-835f-f2552d999ce9` | assistant | 1,936 | 分红, 股票 | 仓位, 分红, 投资, 股票 |
| 通胀与普通人生活 | `43861c5d-876e-470d-895d-b2dd45927c39` | assistant | 1,773 | 海澜之家 | 投资, 海澜, 海澜之家, 资产配置 |
| 通胀与普通人生活 | `e73044d2-5f62-41cc-8cb7-691be7a661bf` | assistant | 2,032 | 股票 | 投资, 股票 |
| 世界公民配置升级 | `cff984dc-9efe-4445-80bb-415b5f2e2bc9` | assistant | 2,366 | 股票 | 投资, 股票账户 |
| 世界公民配置升级 | `c1501c81-12c6-474b-93a4-0d8c819d608c` | assistant | 1,949 | 分红 | 分红, 投资 |
| 韩国QDII与半导体配置 | `726400ea-53ad-4288-a039-578e2e04193e` | user | 86 | QDII |  |
| 财商与系统培育 | `01f50a10-6a59-496f-8f1f-d8892e083d71` | assistant | 2,436 | 分红 | 分红, 投资 |
| 婚姻决策与风险 | `3188cf0d-ad76-4f1e-ab6f-2ce3441e414a` | assistant | 2,209 | 止损 | 止损 |
| TCAI ETF分析 | `9f5f65f2-ee1b-44a6-950b-d7eb112fb4a7` | user | 282 | 券商 | 券商, 投资 |
| Marvell接入层芯片分析 | `bdd2832e-d8b6-4c58-abe3-221abd9fb55e` | user | 12 | IPO |  |
| Playwright 1.59.0 安装解决方案 | `ee4fd22b-3039-4104-90af-f833ae73505f` | assistant | 1,661 | 股票 | 微软, 股票 |
| Playwright 1.59.0 安装解决方案 | `534c5536-a36d-4a31-8ce7-28f55f160d9c` | user | 2,098 | 持仓 | 持仓 |
| Playwright 1.59.0 安装解决方案 | `c14f491f-1638-4764-88ad-a7159b3a4233` | assistant | 1,754 | 基金, 股票 | 股票 |
| Playwright 1.59.0 安装解决方案 | `1c173355-b296-489b-9219-ac399274aa9b` | user | 567 | AAPL, MSFT, NVDA | AAPL, MSFT, NVDA |
| A2A时代外贸自动化 | `27f69760-ce75-4841-8228-c5287cd4b7d2` | assistant | 2,307 | 股票 | 股票 |
| 注意力边界与社交 | `ae0a304c-750d-4724-be88-a84b95af5be6` | user | 668 | 止损 | 止损 |
| EUV ETF持仓分析 | `baafe9a4-83a0-4f48-9458-67d3b15ebb58` | assistant | 2,294 | 股票 | 投资, 股票 |
| 老钱筹码分析 | `bbee0270-4bb9-4db3-8e80-9eaa2752d6ba` | user | 83 | 筹码 |  |
| 苹果礼品卡有效期 | `90266ae9-d196-4bd3-884d-fe81e822d2b2` | assistant | 1,165 | 券商 | 券商 |
| 量化抓取优化建议 | `2fb5e61d-0bd4-4b1c-a90a-9efdd51879ca` | user | 245 | 东方财富 | 东方财富 |
| HSBC App Store问题 | `4c601335-fd4d-4109-bf1e-df412a07e062` | assistant | 1,277 | 证券 | 投资, 证券, 资产配置 |
| 金升阳模块对应分析 | `8ffaa7eb-7189-4f18-98b4-f12d6d2b1b6d` | assistant | 3,387 | AMD | AMD |
| 公司背景疑问 | `889af213-e087-4c50-9bbb-8bdc77497c40` | user | 111 | 股票 | 股票 |
| A股波段股推荐 | `a946c3ec-5013-4c51-aa8c-a77e0a85fe9b` | assistant | 2,355 | 五粮液, 分红, 基金, 泸州老窖, 海澜之家 | HLA, PE, 五粮液, 估值, 分红, 泸州老窖, 海澜, 海澜之家 |
| A股波段股推荐 | `28f9281c-3d3f-4a6b-b003-116d4394fdc7` | assistant | 1,716 | 中国铝业, 五粮液, 工业富联, 汇川技术, 江西铜业, 海澜之家, 紫金矿业, 迈瑞医疗, 顺丰控股 | 中国铝业, 五粮液, 工业富联, 市值, 汇川技术, 江西铜业, 海澜, 海澜之家, 紫金矿业, 迈瑞医疗, 顺丰控股 |
| A股波段股推荐 | `10badae2-3f7a-4c16-9341-7cb41da29be2` | assistant | 422 | 中国铝业, 江西铜业, 紫金矿业 | 中国铝业, 江西铜业, 紫金矿业 |
| 铝价分析与投资逻辑 | `25aca061-8385-4c28-b5bb-5323c1a1c78c` | user | 347 | 云铝股份, 期货 | 云铝股份 |
| 英文领英宣传文案 | `20cf6da8-db85-4b3a-b976-61d1368db930` | assistant | 1,742 | IPo | Portfolio |
| 强股分析与思考 | `b8ecc722-529d-4996-a977-fedce4fad0b7` | user | 472 | 筹码, 财报 | 板块, 财报 |
| 买房争论分析 | `e2716a56-93f1-49a5-b93d-17782f0efff7` | assistant | 1,803 | 股票 | 投资, 股票 |
| 买房争论分析 | `aec1484d-7994-4869-8a57-8486b69f9947` | user | 518 | AAPL, AMD, AMZN, AVGO, GOOG, GOOGL, META, MSFT, NVDA, TSLA, TSM | AAPL, AMD, AMZN, AVGO, GOOG, GOOGL, META, MSFT, NVDA, TSLA, TSM |
| PoE Watchdog Case Study | `8d3a695a-4194-4dde-8380-eadc069d8e45` | assistant | 8,040 | iPo |  |
| 客户测试开关回复 | `7aa646f5-6b81-4485-a2c5-81009c6d5cee` | assistant | 2,395 | iPo |  |
| 轻FIRE模式可行性分析 | `178f1bc7-ff90-460e-9d9a-c4fc69fe88f3` | user | 754 | 股票 | 投资, 股票 |
| 轻FIRE模式可行性分析 | `f75d9edc-fd9f-42c8-8ab6-3739bd66f0e1` | assistant | 1,950 | 股票 | 投资, 股票 |
| 美国AI战略分析 | `13aa80e7-45ac-4a82-8710-7af5855ec508` | user | 2,148 | 基金 | 亚马逊, 微软, 投资, 英伟达, 谷歌 |
| Mikrotik vs 交换机价值分析 | `a4760194-ecc3-4d4f-bedc-30fc287cfe91` | user | 1,601 | etF |  |
| Mikrotik vs 交换机价值分析 | `8be13bf7-69ca-478e-8ef6-93ca73190b7c` | assistant | 2,788 | etF |  |
| Mikrotik vs 交换机价值分析 | `b6f5b8db-d991-4234-99ce-a7ff62b1bca7` | user | 993 | IPO |  |
| Mikrotik vs 交换机价值分析 | `70077f4f-e345-4540-9b59-2448ac76aaa1` | assistant | 2,957 | IPO |  |
| Mikrotik vs 交换机价值分析 | `67bd39a0-7686-4d15-9548-4f8c51077d13` | assistant | 4,494 | 股票 | 股票 |
| 捷克客户评估 | `fbdbd328-676b-4419-8b70-6dc4608f3f5c` | user | 4,779 | etf, ipo, IPO | Stock |
| 捷克客户评估 | `be13e010-0a20-4192-859b-eb0fa4e10851` | assistant | 3,534 | ipo, IPO |  |
| 捷克客户评估 | `578b4b80-8048-4b23-ba9c-76eae3f8ddc9` | user | 9,415 | etf, etF, ipo, IPO |  |
| 捷克客户评估 | `2dcb6a65-41c0-4789-b4b1-40a99df5eb6f` | assistant | 3,271 | etF, ipo, IPO |  |
| 捷克客户评估 | `c8d4a803-6e60-46b7-bdea-dccb893ceea3` | user | 5,247 | ipo, IPO | Stock |
| 东南亚客户评估 | `27ea7a8d-43e3-493b-a6bc-9b66985d55d0` | user | 5,911 | IPO | Stock |
| 显示VS Code运行按钮 | `af042697-2e39-4cd7-aee0-bcc573eca48e` | user | 744 | 筹码 |  |
| Trueno Group 匹配度分析 | `4c53efa6-56a6-4487-8648-7f63919f803c` | assistant | 2,136 | 财报 | 财报 |
| 减少注意力损耗 | `79d2db5b-4d3a-415f-a7ff-f0c692d7b117` | assistant | 2,642 | 股票 | 股票 |
| Saga模式 | `69ab0fa8-9825-4147-875b-7cd378443ec9` | assistant | 2,085 | 股票 | 投资, 股票 |
| Saga模式 | `4e7fdd3f-bbdd-47cf-8134-1acb8e9f4a9e` | user | 119 | 分红, 股票 | 分红, 投资, 股票 |
| Saga模式 | `8ecd2283-f2cd-47a4-8af1-379c78c8fa95` | user | 81 | 股票 | 股票 |
| Saga模式 | `f707076e-2f14-4635-a32c-0460d22d98f8` | user | 99 | 股票 | 股票 |
| 域名选择与注册查询 | `cfcd3cde-c6c9-4b52-b438-dbf9cb763470` | assistant | 1,505 | IPO |  |
| 域名选择与注册查询 | `f0f410b9-61aa-45e1-ac13-fc844e56ccda` | assistant | 2,539 | ipo |  |
| 域名选择与注册查询 | `88ac3835-2bbf-4467-a07d-f16978d4667b` | assistant | 2,745 | ipo |  |
| 域名选择与注册查询 | `a5b7afec-a8a3-4875-8a65-8b2503de21e2` | assistant | 2,976 | ipo |  |
| 域名选择与注册查询 | `ab48701a-ba5c-4327-94c3-20aba7fbac51` | assistant | 3,335 | ipo |  |
| 域名选择与注册查询 | `87a3a6de-11f5-47ab-a03f-2d8337aa5de3` | assistant | 2,772 | ipo |  |
| 域名选择与注册查询 | `970de019-86ed-4e15-8678-523ec8fee8fe` | assistant | 2,619 | ipo |  |
| 域名选择与注册查询 | `0b54bb46-c6b0-45fe-8d90-a930b6577727` | assistant | 2,889 | ipo |  |
| 域名选择与注册查询 | `790913f3-93e0-479e-8a0e-cdf1b9f39a2e` | assistant | 2,548 | ipo |  |
| 域名选择与注册查询 | `a4276d6f-68cd-4703-ab1a-44c29693b2fd` | assistant | 2,382 | ipo |  |
| 域名选择与注册查询 | `b424d390-c91d-478e-9d49-079e0642e0c7` | assistant | 785 | IPO |  |
| 手机安全建议 | `a513aa4d-126e-4566-a863-aad8722fe0d7` | assistant | 1,775 | 止损 | 止损 |
| GLW-GPT | `be8d6974-3311-4750-92cc-60fa8de2b656` | assistant | 2,222 | 财报 | Meta, 微软, 投资, 财报 |
| GLW-GPT | `285d0acf-82d5-469a-8307-59f261069988` | assistant | 3,950 | AMD, NVDA, 财报 | AMD, Meta, NVDA, 微软, 投资, 财报 |
| GLW-GPT | `454ca65e-39c6-4217-800b-cdb2be5c5607` | assistant | 3,510 | 基金 | Meta, 投资 |
| GLW-GPT | `2789581f-322d-40d1-8fae-5c2da8dc27c3` | assistant | 3,081 | 财报 | 投资, 财报 |
| GLW-GPT | `049f0b19-2f34-4be2-818d-3a2134bd3e4c` | assistant | 3,931 | 财报 | 财报 |
| GLW-GPT | `55c3d043-cd83-46cf-a5a6-c074d59ec942` | assistant | 3,639 | 财报 | 财报 |
| GLW-GPT | `e1adba1c-366c-450d-bbae-ca71213d2e37` | assistant | 3,574 | 股票 | 股票 |
| GLW-GPT | `be00fbf6-e14c-429c-ae91-3104397aaf67` | assistant | 4,149 | AMD | AMD, Earnings, Meta, 投资 |
| GLW-GPT | `4c1bb5b7-38bc-4cb3-9edc-e812e6ebfd47` | assistant | 3,275 | 财报 | 财报 |
| GLW-GPT | `335994fc-e3b9-4c7a-a7ad-52d0342cdf4e` | assistant | 4,393 | AMD | AMD, GTC, Meta, 投资 |
| GLW-GPT | `71e82bed-b4ec-41f5-8452-8f1bd8372fc3` | assistant | 4,689 | AMD | AMD, GTC, Meta, 投资 |
| GLW-GPT | `795c170c-111b-4500-8547-508dd2358394` | assistant | 4,781 | 中际旭创, 新易盛 | GTC, Meta, 中际旭创, 投资, 新易盛 |
| GLW-GPT | `286642a3-07ae-495a-99b2-b627d9d56624` | assistant | 4,005 | AMD | AMD, Meta, 投资 |
| GLW-GPT | `aeee2186-380c-4099-a047-4c1584af3ae2` | assistant | 4,624 | AMD, 财报 | AMD, GTC, Meta, 投资, 财报 |
| 交换机租赁模式探索 | `f95c2855-178d-4ecf-af9d-0e34f8f1c29e` | user | 203 | 股票 | 股票 |
| Learn English Words | `e70cb948-6300-417f-a301-5271f324207e` | assistant | 570 | 贵州茅台 | 贵州茅台 |
| 光开关特性 | `85a5d3a3-fdde-474f-9e90-ad6cb36b8e29` | assistant | 679 | ipo |  |
| 光开关特性 | `bc1cdd17-7179-46e5-b27b-e34d76093dfe` | assistant | 1,168 | ipo |  |

## 短上下文候选

- NVO目标价与股权结构 / `41b8b33f-2c32-4d42-8b30-5f58f21ee40b` / 45 字符
- 投资决策逻辑分析 / `5f374c9f-6c15-4de2-8645-0722544bbcfa` / 53 字符
- 长牛股筛选策略 / `187b58f0-c511-4faf-860b-cbe0ecfede9d` / 109 字符
- A股波段股推荐 / `10badae2-3f7a-4c16-9341-7cb41da29be2` / 422 字符
- 资本流动与价格形成 / `9e35e467-068f-4147-9216-5e73bbfd288c` / 60 字符
- 资本流动与价格形成 / `63fcb7cc-0b39-46b6-a35c-a4ab3ff08397` / 4 字符
- 资本流动与价格形成 / `7e1ec886-7093-40f0-8acf-695838e12068` / 61 字符
- 投资框架分析 / `91d9c4ef-de5e-4b7c-b40d-ba51e14109f3` / 77 字符
- 美股特点分析 / `8c1571d8-c729-401c-b89c-d208394a4a1d` / 77 字符
- 普通人被动收入方式 / `388655cb-6cd9-475b-bb58-c6ece4b378a5` / 119 字符
- GLW-GPT / `349807f3-2121-4633-9074-4744461ac268` / 77 字符
- GLW-GPT / `7290d91d-8b63-4471-aa61-a595d5fdb769` / 77 字符

## 未入库会话标题与信号计数

| 会话 | 源消息数 | hard 未入库 | broad-only 未入库 |
|---|---:|---:|---:|
| Optical Testing Board | 101 | 0 | 0 |
| 16×16 Optical Switch Manual | 173 | 0 | 0 |
| Family Fun Rainy Day | 14 | 0 | 0 |
| Olycom PoE DWDM Overview | 4 | 0 | 0 |
| 小规模纳税人出口流程 | 24 | 0 | 0 |
| 散热孔设计选择 | 14 | 1 | 0 |
| 芯片功能开发与需求 | 69 | 3 | 0 |
| Saga | 62 | 0 | 0 |
| PoE switch applications | 14 | 0 | 0 |
| 重写SEO标题 | 52 | 0 | 0 |
| 尼日利亚市场分析 | 32 | 0 | 0 |
| CENTEC功能表评估 | 2 | 0 | 0 |
| 1U交换机文案写作指南 | 6 | 0 | 0 |
| Rewritten Application Overview | 26 | 0 | 0 |
| B2B半自动过滤优化 | 64 | 0 | 0 |
| 英文标题与关键词 | 2 | 0 | 0 |
| 技术流绑定实践 | 4 | 0 | 0 |
| 深圳长期发展布局 | 2 | 1 | 0 |
| 通信行业长期发展 | 8 | 1 | 0 |
| 工业交换机布线图 | 1 | 0 | 0 |
| Drone Fiber 需求解析 | 26 | 0 | 0 |
| 客户跟进分析_US | 36 | 0 | 0 |
| 土耳其警察RFP分析 | 21 | 0 | 0 |
| 客户二次评估与成交概率_ALL | 13 | 8 | 0 |
| 产品功能与用途解析 | 16 | 0 | 0 |
| L3+ 功能分析 | 6 | 0 | 0 |
| 芯片分析与识别 | 22 | 0 | 0 |
| O 产品卖点 | 25 | 0 | 0 |
| Sales Engineer 职位解析 | 8 | 0 | 0 |
| MSTP设备分析 | 6 | 2 | 0 |
| 公司介绍重写与差异化 | 10 | 0 | 0 |
| 台湾Marvell工业交换机厂商 | 14 | 0 | 0 |
| 项目型包装盒升级方案 | 6 | 0 | 0 |
| Project-Based Cabinet Ethernet | 13 | 0 | 0 |
| 国外采购商整理 | 9 | 0 | 2 |
| WhatsApp下载问题解析 | 2 | 0 | 0 |
| Power and PoE++ in Networks | 5 | 0 | 0 |
| 啤酒与健身后受凉 | 4 | 0 | 0 |
| E-Mark 网络交换机关键词 | 4 | 0 | 0 |
| 存在主义核心观点分析 | 2 | 0 | 0 |
| FX风险与增值税成本 | 18 | 0 | 0 |
| 定制型交换机需求解析 | 18 | 0 | 0 |
| DWDM 长距离传输解析 | 4 | 0 | 0 |
| 销售核心交换机知识 | 10 | 0 | 0 |
| Ethernet over SDH Solution | 6 | 0 | 0 |
| BYPASS OLP 基础设施应用 | 4 | 0 | 0 |
| 型号规格匹配分析 | 2 | 0 | 0 |
| 户外监控系统清单 | 2 | 0 | 0 |
| 工业以太网优化建议 | 4 | 0 | 0 |
| AI与交换机处理数据区别 | 8 | 0 | 0 |
| 时间增益行为模型 | 2 | 1 | 0 |
| 报价单优化建议 | 4 | 0 | 0 |
| 饮食系统构建指南 | 18 | 1 | 0 |
| OLP Bypass Protection Solution | 1 | 0 | 0 |
| 售后SOP优化流程 | 3 | 0 | 0 |
| 野外网络交换机核查 | 6 | 0 | 0 |
| 售后SOP优化流程 | 2 | 0 | 0 |
| 工业PoE++交换机 | 10 | 0 | 0 |
| 举铁与健康寿命 | 12 | 0 | 0 |
| WS-C3650-48FQ-E停产分析 | 2 | 0 | 0 |
| 设备类型与需求差异 | 8 | 0 | 0 |
| 韩国安全认证需求分析 | 11 | 0 | 0 |
| 英文三段论结构 | 2 | 0 | 0 |
| 找类似Larch Networks公司 | 12 | 0 | 0 |
| OBM定义与客户询问 | 4 | 0 | 0 |
| VSC7428 SNMP温度监控 | 2 | 0 | 0 |
| Power Without Limits | 1 | 0 | 0 |
| 单位换算与存储对比 | 4 | 0 | 0 |
| Solar PoE System Design | 8 | 0 | 0 |
| 工业L2交换机需求分析 | 5 | 0 | 0 |
| 光电转换小板规格书 | 2 | 0 | 0 |
| IM-FP21008GW性能分析 | 11 | 0 | 0 |
| TA-7224GE Switch Overview | 2 | 0 | 0 |
| 标书要求冲突分析 | 8 | 0 | 0 |
| 工业L2交换机需求 | 14 | 0 | 0 |
| Off-Grid Solar CCTV System | 1 | 0 | 0 |
| 工业设备标签设计 | 9 | 0 | 0 |
| 说明书评估分析 | 2 | 0 | 0 |
| AC5芯片开发信 | 2 | 0 | 0 |
| 通信多路复用器解释 | 2 | 0 | 0 |
| 创建claude配置文件 | 32 | 0 | 0 |
| 解决402错误与Git问题 | 20 | 0 | 0 |
| Claude Code 调试问题 | 26 | 0 | 0 |
| Claude Desktop 配置指南 | 20 | 0 | 0 |
| Sales Track Record 解释 | 2 | 0 | 0 |
| AI光交换的未来 | 2 | 0 | 0 |
| 智能保护与旁路技术 | 2 | 0 | 0 |
| 无人机光纤传输方案 | 32 | 0 | 0 |
| 摄像头参数查询 | 4 | 0 | 0 |
| 尿道异物感分析 | 14 | 0 | 0 |
| PowerShell curl 解决方案 | 8 | 0 | 0 |
| DWDM CE标准解析 | 2 | 0 | 0 |
| 产品发展方向建议 | 6 | 0 | 0 |
| A2A时代外贸自动化 | 2 | 1 | 0 |
| 皮肤问题分析与建议 | 21 | 0 | 0 |
| OCM卡全称及功能 | 14 | 0 | 1 |
| 核心交换机厂商 | 4 | 0 | 1 |
| 注意力边界与社交 | 6 | 1 | 0 |
| Saga交换机ERPS支持分析 | 8 | 0 | 0 |
| 城域环网方案分析 | 3 | 0 | 0 |
| PayPal 付款失败原因 | 4 | 0 | 0 |
| FIPS 140-3 认证设备 | 4 | 0 | 0 |
| 金升阳模块对应分析 | 16 | 1 | 0 |
| 400G/800G DCI Solution | 9 | 0 | 0 |
| 英文SEO内容写作 | 10 | 0 | 0 |
| 存在主义与选择自由 | 2 | 0 | 0 |
| VLAN trunk配置问题 | 2 | 0 | 0 |
| 双向通信光模块设计 | 6 | 0 | 0 |
| Off-grid CCTV Solution | 1 | 0 | 0 |
| 安防光传输案例分析 | 8 | 0 | 0 |
| 海报设计要求 | 2 | 0 | 0 |
| 印度光纤保护案例分析 | 8 | 0 | 0 |
| 时间查询 | 3 | 0 | 0 |
| Surveillance Network Deployment Challenges | 1 | 0 | 0 |
| Strengthening Client Partnership | 6 | 0 | 0 |
| 印度客户调研报告 | 1 | 0 | 0 |
| CCTV Surveillance System Overview | 8 | 0 | 0 |
| 英文宣传文案写作 | 2 | 0 | 0 |
| OEM光纤测试设备 | 2 | 0 | 0 |
| 股东证明材料处理 | 4 | 0 | 0 |
| UAV Fiber Optic Solution | 4 | 0 | 0 |
| E-Mark交换机推广策略 | 2 | 0 | 0 |
| 英文领英宣传文案 | 10 | 1 | 0 |
| 排版换行技巧 | 2 | 0 | 0 |
| 无人机光纤通信系统 | 15 | 0 | 0 |
| 生育观念与压力 | 8 | 0 | 1 |
| 注意力与人生提升 | 4 | 0 | 0 |
| PoE Watchdog Case Study | 5 | 1 | 0 |
| 400G链路OSNR分析 | 9 | 0 | 0 |
| TA510-GE-X UAV Fiber Converter | 4 | 0 | 0 |
| 拼写符号检查报告 | 7 | 0 | 0 |
| 土耳其通信市场分析 | 4 | 0 | 0 |
| Marvell方案公司与网站 | 2 | 0 | 0 |
| HTML排版与技术表述问题 | 2 | 0 | 0 |
| 古代男性身体表现 | 6 | 0 | 0 |
| 存量思维与人际关系 | 2 | 0 | 0 |
| LinkedIn英文领英文案 | 6 | 0 | 0 |
| LinkedIn简介写作 | 6 | 0 | 0 |
| AC5 Lite MACSec 支持 | 8 | 0 | 0 |
| NDAA Compliance Explanation | 5 | 0 | 0 |
| OTN DWDM Transmission Network | 8 | 0 | 0 |
| 客户测试开关回复 | 2 | 1 | 0 |
| Claude 账号限制分析 | 32 | 0 | 0 |
| Angora | 16 | 0 | 0 |
| Mikrotik vs 交换机价值分析 | 54 | 5 | 0 |
| 捷克客户评估 | 6 | 5 | 0 |
| 东南亚客户评估 | 4 | 1 | 0 |
| RTL8372N 扩展端口方案 | 4 | 0 | 0 |
| 产品规格与定制选项 | 13 | 0 | 0 |
| SEO Case Study Writing | 5 | 0 | 0 |
| 芯片型号分析 | 2 | 0 | 0 |
| 轻运营入金渠道 | 2 | 0 | 0 |
| 应用图优化建议 | 8 | 0 | 0 |
| 应用图优化要求 | 2 | 0 | 0 |
| Saga Telecom SEO 路线图 | 2 | 0 | 0 |
| Q4规格书框架建议 | 2 | 0 | 0 |
| 应用图优化要求 | 1 | 0 | 0 |
| LinkedIn SEO 内容写作 | 4 | 0 | 0 |
| Trueno Group 匹配度分析 | 12 | 1 | 0 |
| 头脑风暴商业模式 | 4 | 0 | 0 |
| 学习欧洲商业模式 | 4 | 0 | 0 |
| 客户拓扑图请求 | 3 | 0 | 0 |
| HTML审核与优化建议 | 11 | 0 | 0 |
| EC21 Banner建议 | 2 | 0 | 0 |
| 长期数字资产管理 | 8 | 0 | 0 |
| PTP精确时间协议解释 | 2 | 0 | 0 |
| 规格书替代对比 | 2 | 0 | 0 |
| X | 2 | 0 | 0 |
| 品牌资产化系统 | 42 | 0 | 0 |
| 代码化工作方法论 | 2 | 0 | 0 |
| 减少注意力损耗 | 2 | 1 | 0 |
| SEO评分分析 | 8 | 0 | 0 |
| Steam找回账号 सलाह | 15 | 0 | 1 |
| 优化客户调研MD | 2 | 0 | 0 |
| A-069 | 14 | 0 | 0 |
| A-311 | 4 | 0 | 0 |
| 域名选择与注册查询 | 58 | 11 | 0 |
| EDFA 设备用户手册 | 94 | 0 | 0 |
| 光开关特性 | 60 | 2 | 0 |
| 20 slots: 1/19. | 42 | 0 | 0 |
| ETK Trading Korea Info | 8 | 0 | 0 |
| New chat | 3 | 0 | 0 |
| New chat | 2 | 0 | 0 |
