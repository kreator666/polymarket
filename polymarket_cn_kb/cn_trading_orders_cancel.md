<!-- Source: https://docs.polymarket.com/cn/trading/orders/cancel -->

所有取消端点都需要
L2 身份验证
。响应始终包含
canceled
(已取消订单 ID 列表)和
not_canceled
(订单 ID 到失败原因的映射)。

取消单个订单
TypeScript
Python
REST
const
resp
=
await
client
.
cancelOrder
(
"0xb816482a..."
);
console
.
log
(
resp
);
// { canceled: ["0xb816482a..."], not_canceled: {} }

取消多个订单
TypeScript
Python
REST
const
resp
=
await
client
.
cancelOrders
([
"0xb816482a..."
,
"0xc927593b..."
]);

取消所有订单
取消所有市场中的每个未完成订单:
TypeScript
Python
REST
const
resp
=
await
client
.
cancelAll
();

按市场取消
取消特定市场的所有订单,可选择性地筛选到单个代币。
market
和
asset_id
都是可选的——同时省略两者将取消所有订单。
TypeScript
Python
REST
const
resp
=
await
client
.
cancelMarketOrders
({
market:
"0xbd31dc8a..."
,
// optional: condition ID
asset_id:
"52114319501245..."
,
// optional: specific token
});

链上取消
如果 API 不可用,你可以直接在
Exchange 合约
上通过调用链上的
cancelOrder(Order order)
来取消订单。传递下单时签名的完整订单结构。
根据市场类型使用
CTFExchange
或
NegRiskCTFExchange
合约。地址详见
合约地址
。
这是一种回退机制——API 取消是即时的,而链上取消需要一笔交易。

查询订单

获取单个订单
TypeScript
Python
const
order
=
await
client
.
getOrder
(
"0xb816482a..."
);
console
.
log
(
order
.
status
,
order
.
size_matched
);

获取未完成订单
检索所有未完成订单,可选择性地按市场或代币筛选:
TypeScript
Python
// All open orders
const
orders
=
await
client
.
getOpenOrders
();
// Filtered by market
const
marketOrders
=
await
client
.
getOpenOrders
({
market:
"0xbd31dc8a..."
,
});
// Filtered by token
const
tokenOrders
=
await
client
.
getOpenOrders
({
asset_id:
"52114319501245..."
,
});

OpenOrder 对象
字段
类型
描述
id
string
订单 ID
status
string
当前订单状态
market
string
Condition ID
asset_id
string
Token ID
side
string
BUY
或
SELL
original_size
string
下单时的数量
size_matched
string
已成交数量
price
string
限价
outcome
string
人类可读的结果(例如,“Yes”,“No”)
order_type
string
订单类型(GTC, GTD, FOK, FAK)
maker_address
string
资金提供者地址
owner
string
订单所有者的 API key
associate_trades
string[]
此订单包含的交易 ID
expiration
string
Unix 过期时间戳(如果没有则为
0
)
created_at
string
Unix 创建时间戳

交易历史
当订单匹配时,会创建一笔交易。交易经历以下状态:
Status
Terminal
Description
MATCHED
No
已匹配并发送至链上提交
MINED
No
已在链上挖出,尚未最终确认
CONFIRMED
Yes
已达到最终性——交易成功
RETRYING
No
交易失败——正在重试
FAILED
Yes
永久失败
TypeScript
Python
// All trades
const
trades
=
await
client
.
getTrades
();
// Filtered by market
const
marketTrades
=
await
client
.
getTrades
({
market:
"0xbd31dc8a..."
,
});
其他筛选参数:
id
,
maker_address
,
asset_id
,
before
,
after
。
对于大型结果集,使用分页变体:
TypeScript
Python
const
page
=
await
client
.
getTradesPaginated
({
market:
"0xbd31dc8a..."
});
console
.
log
(
page
.
trades
,
page
.
count
);
// trades array + total count

Trade 对象
字段
类型
描述
id
string
交易 ID
taker_order_id
string
Taker 订单哈希
market
string
Condition ID
asset_id
string
Token ID
side
string
BUY
或
SELL
size
string
交易数量
price
string
执行价格
fee_rate_bps
string
费率(基点)
status
string
交易状态(见上表)
match_time
string
匹配时的 Unix 时间戳
last_update
string
最后状态更改的 Unix 时间戳
outcome
string
人类可读的结果(例如,“Yes”)
maker_address
string
Maker 的资金提供者地址
owner
string
交易所有者的 API key
transaction_hash
string
链上交易哈希
bucket_index
number
用于交易对账的索引
trader_side
string
TAKER
或
MAKER
maker_orders
MakerOrder[]
填充此交易的 Maker 订单
由于 gas 限制,单笔交易可能会被拆分到多个链上交易中。使用
bucket_index
和
match_time
将相关交易对账回单个逻辑交易。

订单评分
检查你的挂单是否符合
maker 返利
评分资格:
TypeScript
Python
// Single order
const
scoring
=
await
client
.
isOrderScoring
({
orderId:
"0x..."
});
// Multiple orders
const
batch
=
await
client
.
areOrdersScoring
({
orderIds:
[
"0x..."
,
"0x..."
],
});

下一步
订单归因
将订单归属到你的 Builder 账户以获得交易量信用
费用
了解费用结构和 Maker 返利