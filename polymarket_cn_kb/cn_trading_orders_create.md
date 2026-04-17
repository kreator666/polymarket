<!-- Source: https://docs.polymarket.com/cn/trading/orders/create -->

Polymarket 上的所有订单都以
限价单
形式表达。市价单通过提交一个具有可成交价格的限价单来实现 — 你的订单将立即以账本上的最佳可用价格执行。
SDK 会为你处理 EIP-712 签名和提交。如果你更喜欢直接使用 REST
API,请参阅
身份验证
以了解如何构建所需的请求头,以及
API 参考
以查看完整的端点文档,包括原始订单对象字段和请求/响应模式。

订单类型
类型
行为
用例
GTC
Good-Til-Cancelled — 在账本上保留,直到成交或取消
限价单的默认类型
GTD
Good-Til-Date — 活跃至指定的到期时间
在已知事件前自动过期
FOK
Fill-Or-Kill — 必须立即完全成交,否则取消
全部成交或全部取消的市价单
FAK
Fill-And-Kill — 立即成交可用部分,取消剩余部分
部分成交的市价单
GTC
和
GTD
是限价单类型 — 它们以你指定的价格在账本上等待成交。
FOK
和
FAK
是市价单类型 — 它们立即对现有流动性执行。
BUY
: 指定你想要花费的美元金额
SELL
: 指定你想要卖出的份额数量

限价单
下单限价单最简单的方式 — 在一次调用中创建、签名并提交:
TypeScript
Python
import
{
ClobClient
,
Side
,
OrderType
}
from
"@polymarket/clob-client"
;
const
response
=
await
client
.
createAndPostOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.5
,
size:
10
,
side:
Side
.
BUY
,
},
{
tickSize:
"0.01"
,
negRisk:
false
,
},
OrderType
.
GTC
,
);
console
.
log
(
"Order ID:"
,
response
.
orderID
);
console
.
log
(
"Status:"
,
response
.
status
);

两步操作 - 先签名再提交
如果需要更多控制,可以将签名和提交分开。这对批量订单或自定义提交逻辑很有用:
TypeScript
Python
// Step 1: Create and sign locally
const
signedOrder
=
await
client
.
createOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.5
,
size:
10
,
side:
Side
.
BUY
,
},
{
tickSize:
"0.01"
,
negRisk:
false
},
);
// Step 2: Submit to the CLOB
const
response
=
await
client
.
postOrder
(
signedOrder
,
OrderType
.
GTC
);

GTD 订单 - 定时过期
GTD 订单会在指定时间自动过期。适用于围绕已知事件进行报价。
TypeScript
Python
// Expire in 1 hour (+ 60s security threshold buffer)
const
expiration
=
Math
.
floor
(
Date
.
now
()
/
1000
)
+
60
+
3600
;
const
response
=
await
client
.
createAndPostOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.5
,
size:
10
,
side:
Side
.
BUY
,
expiration
,
},
{
tickSize:
"0.01"
,
negRisk:
false
},
OrderType
.
GTD
,
);
GTD 过期时间有一分钟的安全阈值。要设置 N 秒的有效生命周期,请使用
now + 60 + N
。例如,对于 30 秒的有效生命周期,将过期时间设置为
now + 60 + 30
。

市价单
市价单使用 FOK 或 FAK 类型立即对现有流动性执行:
TypeScript
Python
import
{
Side
,
OrderType
}
from
"@polymarket/clob-client"
;
// FOK BUY: spend exactly $100 or cancel entirely
const
buyOrder
=
await
client
.
createMarketOrder
(
{
tokenID:
"TOKEN_ID"
,
side:
Side
.
BUY
,
amount:
100
,
// dollar amount
price:
0.5
,
// worst-price limit (slippage protection)
},
{
tickSize:
"0.01"
,
negRisk:
false
},
);
await
client
.
postOrder
(
buyOrder
,
OrderType
.
FOK
);
// FOK SELL: sell exactly 200 shares or cancel entirely
const
sellOrder
=
await
client
.
createMarketOrder
(
{
tokenID:
"TOKEN_ID"
,
side:
Side
.
SELL
,
amount:
200
,
// number of shares
price:
0.45
,
// worst-price limit (slippage protection)
},
{
tickSize:
"0.01"
,
negRisk:
false
},
);
await
client
.
postOrder
(
sellOrder
,
OrderType
.
FOK
);
FOK
— 完全成交或取消整个订单
FAK
— 成交可用部分,取消剩余部分
市价单上的
price
字段作为
最差价格限制
(滑点保护),而不是目标执行价格。

一步市价单
为了方便,
createAndPostMarketOrder
在一次调用中处理创建、签名和提交:
TypeScript
Python
const
response
=
await
client
.
createAndPostMarketOrder
(
{
tokenID:
"TOKEN_ID"
,
side:
Side
.
BUY
,
amount:
100
,
price:
0.5
,
},
{
tickSize:
"0.01"
,
negRisk:
false
},
OrderType
.
FOK
,
);

Post-Only 订单
Post-Only 订单保证你始终是做市方。如果订单会立即匹配(跨越价差),它将被拒绝而不是执行。
TypeScript
Python
const
response
=
await
client
.
postOrder
(
signedOrder
,
OrderType
.
GTC
,
true
);
仅适用于
GTC
和
GTD
订单类型
如果与 FOK 或 FAK 结合使用将被拒绝

批量订单
在单个请求中最多下达
15 个订单
:
TypeScript
Python
import
{
OrderType
,
Side
,
PostOrdersArgs
}
from
"@polymarket/clob-client"
;
const
orders
:
PostOrdersArgs
[]
=
[
{
order:
await
client
.
createOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.48
,
side:
Side
.
BUY
,
size:
500
,
},
{
tickSize:
"0.01"
,
negRisk:
false
},
),
orderType:
OrderType
.
GTC
,
},
{
order:
await
client
.
createOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.52
,
side:
Side
.
SELL
,
size:
500
,
},
{
tickSize:
"0.01"
,
negRisk:
false
},
),
orderType:
OrderType
.
GTC
,
},
];
const
response
=
await
client
.
postOrders
(
orders
);

订单选项
每个订单都需要两个特定于市场的选项:
tickSize
和
negRisk
。有关签名类型(
0
= EOA,
1
= POLY_PROXY,
2
= GNOSIS_SAFE)的详细信息,请参阅
身份验证
。

最小价格变动单位
你的订单价格必须符合市场的最小价格变动单位,否则订单将被拒绝。
Tick Size
Precision
Example Prices
0.1
1 位小数
0.1, 0.2, 0.5
0.01
2 位小数
0.01, 0.50, 0.99
0.001
3 位小数
0.001, 0.500, 0.999
0.0001
4 位小数
0.0001, 0.5000, 0.9999
TypeScript
Python
const
tickSize
=
await
client
.
getTickSize
(
"TOKEN_ID"
);

Negative Risk
多结果事件(3 个及以上结果)使用 Neg Risk CTF Exchange。对于这些市场,请传递
negRisk: true
。
TypeScript
Python
const
isNegRisk
=
await
client
.
getNegRisk
(
"TOKEN_ID"
);
这两个值也可以在市场对象上找到:
minimum_tick_size
和
neg_risk
。

前提条件
在下单之前,你的资金地址必须已批准 Exchange 合约使用相关代币:
BUY 订单
: USDC.e 授权额度 >= 花费金额
SELL 订单
: 条件代币授权额度 >= 卖出金额
订单大小受可用余额限制,需减去现有未完成订单所保留的金额:
maxOrderSize
=
balance
−
∑
(
openOrderSize
−
filledAmount
)
\text{maxOrderSize} = \text{balance} - \sum(\text{openOrderSize} - \text{filledAmount})
maxOrderSize
=
balance
−
∑
(
openOrderSize
−
filledAmount
)
订单会持续监控有效性 — 余额、授权额度和链上取消都会实时跟踪。任何做市方故意滥用这些检查将被列入黑名单。

高级参数
这些可选字段可以在
UserOrder
对象中传递,用于精细控制:
Parameter
Type
Description
feeRateBps
number
以基点表示的费率(默认:市场费率)
nonce
number
用于订单唯一性的自定义随机数
taker
string
将订单限制为特定的吃单方地址

体育市场
体育市场有额外的行为:
比赛开始后,未成交的限价单将
自动取消
,在官方开始时间清空整个订单簿
可成交订单在匹配前有
3 秒的下单延迟
比赛开始时间可能会变动 — 请密切监控你的订单,因为如果开始时间意外变化,订单可能不会被清除

响应
成功下单后返回:
{
"success"
:
true
,
"errorMsg"
:
""
,
"orderID"
:
"0xabc123..."
,
"takingAmount"
:
""
,
"makingAmount"
:
""
,
"status"
:
"live"
,
"transactionsHashes"
: [],
"tradeIDs"
: []
}

状态
Status
Description
live
订单在账本上等待成交
matched
订单立即与现有订单匹配
delayed
可成交订单受匹配延迟影响
unmatched
可成交但延迟失败 — 下单仍然成功

错误消息
Error
Description
INVALID_ORDER_MIN_TICK_SIZE
价格不符合市场的最小价格变动单位
INVALID_ORDER_MIN_SIZE
订单大小低于最小阈值
INVALID_ORDER_DUPLICATED
相同的订单已经下达
INVALID_ORDER_NOT_ENOUGH_BALANCE
余额或授权额度不足
INVALID_ORDER_EXPIRATION
过期时间戳已过期
INVALID_POST_ONLY_ORDER_TYPE
Post-only 与 FOK/FAK 结合使用
INVALID_POST_ONLY_ORDER
Post-only 订单会跨越账本
FOK_ORDER_NOT_FILLED_ERROR
FOK 订单无法完全成交
INVALID_ORDER_ERROR
插入订单时的系统错误
EXECUTION_ERROR
执行交易时的系统错误
ORDER_DELAYED
由于市场条件导致订单匹配延迟
DELAYING_ORDER_ERROR
延迟订单时的系统错误
MARKET_NOT_READY
市场尚未接受订单

心跳
心跳端点维持会话活跃性。如果在
10 秒
内(带 5 秒缓冲)未收到有效心跳,
所有未完成订单将被取消
。
TypeScript
Python
let
heartbeatId
=
""
;
setInterval
(
async
()
=>
{
const
resp
=
await
client
.
postHeartbeat
(
heartbeatId
);
heartbeatId
=
resp
.
heartbeat_id
;
},
5000
);
在每个请求中包含最新的
heartbeat_id
。首次请求使用空字符串。
如果发送过期的 ID,服务器会响应
400
并返回正确的 ID。更新后重试。

下一步
取消订单
取消单个、多个或所有未完成订单
订单归因
将订单归因到你的构建者账户以获得交易量积分