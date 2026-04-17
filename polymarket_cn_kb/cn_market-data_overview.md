<!-- Source: https://docs.polymarket.com/cn/market-data/overview -->

所有市场数据都通过公开的 REST 接口提供。无需 API 密钥、无需身份验证、无需钱包。
curl
"https://gamma-api.polymarket.com/events?limit=5"

数据模型
Polymarket 使用两种组织模型来组织数据。最基本的元素始终是市场——事件只是提供额外的组织层级。
1
事件 - Event
一个顶层对象，代表一个问题（例如”谁将赢得 2024 年美国总统大选？”）。包含一个或多个市场。
2
市场 - Market
事件中一个具体的可交易二元结果。对应一对 CLOB token ID、一个市场地址、一个 question ID 和一个 condition ID。

单市场事件 vs 多市场事件
类型
示例
单市场事件
”比特币能否达到 $100k？” → 1 个市场（Yes/No）
多市场事件
”Barron Trump 会去哪所大学？” → Georgetown、NYU、UPenn、Harvard、其他 等多个市场

结果与价格
每个市场都有
outcomes
和
outcomePrices
数组，两者一一对应。价格代表隐含概率：
{
"outcomes"
:
"[
\"
Yes
\"
,
\"
No
\"
]"
,
"outcomePrices"
:
"[
\"
0.20
\"
,
\"
0.80
\"
]"
}
// Index 0: "Yes" → 0.20（20% 概率）
// Index 1: "No" → 0.80（80% 概率）
当
enableOrderBook
为
true
时，市场可以通过 CLOB 进行交易。

可用数据
接口分布在三个 API 中。完整的接口文档（包含参数和响应结构）请参阅
API 参考
。

Gamma API - 事件 市场与发现
接口
说明
GET /events
列出事件，支持筛选和分页
GET /events/{id}
通过 ID 获取单个事件
GET /markets
列出市场，支持筛选和分页
GET /markets/{id}
通过 ID 获取单个市场
GET /public-search
搜索事件、市场和用户
GET /tags
标签/分类排行
GET /series
系列（关联事件组）
GET /sports
体育元数据
GET /teams
队伍信息

CLOB API - 价格与订单簿
接口
说明
GET /price
单个代币的价格
GET /prices
多个代币的价格
GET /book
单个代币的订单簿
POST /books
多个代币的订单簿
GET /prices-history
代币的历史价格数据
GET /midpoint
代币的中间价
GET /spread
代币的价差

Data API - 持仓 交易与分析
接口
说明
GET /positions?user={address}
用户的当前持仓
GET /closed-positions?user={address}
用户的已平仓持仓
GET /activity?user={address}
用户的链上活动
GET /value?user={address}
持仓总价值
GET /oi
市场的未平仓合约
GET /holders
市场的前几大持有者
GET /trades
交易历史

下一步
获取市场数据
三种发现和查询市场的策略。
API 参考
完整的接口文档，包含参数和响应结构。