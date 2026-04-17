<!-- Source: https://docs.polymarket.com/cn/concepts/markets-events -->

Polymarket 上的每个预测都围绕两个核心概念构建：
市场（Market）
和
事件（Event）
。理解它们之间的关系是在平台上进行开发的基础。

市场
市场
是 Polymarket 上最基本的可交易单元。每个市场代表一个 Yes/No 二元结果的问题。
每个市场都有以下标识符：
标识符
说明
Condition ID
市场条件在 CTF 合约中的唯一标识符
Question ID
用于判定的市场问题哈希值
Token IDs
在 CLOB 上进行交易的 ERC1155 代币 ID——一个对应 Yes，一个对应 No
只有当
enableOrderBook
为
true
时，市场才可以通过 CLOB 进行交易。部分市场可能存在于链上，但不支持订单簿交易。

市场示例
一个简单的市场可能是：
“比特币能否在 2026 年 12 月前达到 $150,000？”
这会产生两种结果代币：
Yes 代币
— 如果比特币达到
150
k
，可兑换
‘
150k，可兑换 `
150
k
，可兑换
‘
1`
No 代币
— 如果比特币未达到
150
k
，可兑换
‘
150k，可兑换 `
150
k
，可兑换
‘
1`

事件
事件
是将一个或多个相关市场组合在一起的容器。事件提供组织结构，并支持多结果预测。

单市场事件
当事件只包含一个市场时，形成一个简单的市场对。事件和市场实质上是等价的。
事件：比特币能否在 2024 年 12 月前达到 $100,000？
└── 市场：比特币能否在 2024 年 12 月前达到 $100,000？（Yes/No）

多市场事件
当事件包含两个或更多市场时，形成一个分组市场对，用于实现互斥的多结果预测。
事件：谁将赢得 2024 年美国总统大选？
├── 市场：Donald Trump？（Yes/No）
├── 市场：Joe Biden？（Yes/No）
├── 市场：Kamala Harris？（Yes/No）
└── 市场：其他？（Yes/No）

市场标识
每个市场和事件都有一个唯一的
slug
，出现在 Polymarket 的 URL 中：
https://polymarket.com/event/fed-decision-in-october
└── slug: fed-decision-in-october
你可以使用 slug 从 API 获取特定的市场或事件：
# 通过 slug 获取事件
curl
"https://gamma-api.polymarket.com/events?slug=fed-decision-in-october"

体育市场
对于体育市场，未成交的限价单会在比赛开始时
自动取消
，在官方开赛时间清空订单簿。但比赛开始时间可能会变动——如果比赛提前开始，订单可能来不及清除。请在临近开赛时密切关注你的订单。

下一步
价格与订单簿
了解价格如何形成以及订单簿的运作方式。
获取市场数据
开始通过 API 查询市场和事件。