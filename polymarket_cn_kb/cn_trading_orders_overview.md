<!-- Source: https://docs.polymarket.com/cn/trading/orders/overview -->

Polymarket 上的所有订单都以
限价单
形式表达。市价单通过提交一个可成交价格的限价单来实现——你的订单会立即以盘口最优价格成交。
底层订单原语采用
EIP-712
标准进行结构化、哈希和签名,然后通过 Exchange 合约在链上执行。手动准备订单比较复杂,因此我们推荐使用开源的
TypeScript
或
Python
SDK 客户端,它们会为你处理签名和提交。
如果你更喜欢直接使用 REST API,则需要自行管理订单签名。有关构造所需请求头的详细信息,请参阅
身份验证
。

订单类型
类型
行为
使用场景
GTC
(Good-Til-Cancelled)
挂在盘口直到成交或取消
被动限价单的默认选项
GTD
(Good-Til-Date)
在指定过期时间(UTC 秒级时间戳)之前有效,除非先被成交或取消
在已知事件前自动过期订单
FOK
(Fill-Or-Kill)
必须立即完全成交,否则整个订单被取消
全部成交或全部取消
FAK
(Fill-And-Kill)
立即成交尽可能多的份额,然后取消任何未成交的剩余部分
部分立即成交
FOK
和
FAK
是市价单类型——它们立即与挂单流动性成交。
买入
: 指定你想要花费的美元金额
卖出
: 指定你想要出售的份额数量
GTC
和
GTD
是限价单类型——它们以你指定的价格挂在盘口。
GTD 过期时间
: 有一分钟的安全阈值。如果你需要订单在 90 秒后过期,正确的过期值是
现在 + 1 分钟 + 30 秒
。

Post-Only 订单
Post-only 订单是只会挂在盘口而不会在进入时立即匹配的限价单。
如果 post-only 订单会穿过价差(即可立即成交),它将被
拒绝
而不是执行。
Post-only
不能
与市价单类型(FOK 或 FAK)组合使用。如果市价单类型发送
postOnly = true
,订单将被拒绝。
Post-only 只能与
GTC
和
GTD
订单类型一起使用。

最小价格变动单位
市场有不同的最小价格增量(最小价格变动单位)。你的订单价格必须符合市场的最小价格变动单位,否则订单将被拒绝。
最小价格变动单位
价格精度
价格示例
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
使用 SDK 检索市场的最小价格变动单位:
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
tokenID
);
// Returns: "0.1" | "0.01" | "0.001" | "0.0001"
你还可以查看
Markets API
返回的市场对象上的
minimum_tick_size
字段。

Negative Risk
多结果事件(例如”谁会赢得选举?”有 3 个以上候选人)使用不同的交易合约,称为
Neg Risk CTF Exchange
。在这些市场下单时,你必须在订单选项中传递
negRisk: true
。
TypeScript
Python
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
true
,
// Required for multi-outcome markets
},
);
你可以通过 SDK 或市场对象的
neg_risk
字段检查市场是否使用 negative risk:
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
tokenID
);

授权额度
在下单之前,你的资金地址必须已批准 Exchange 合约使用相关代币:
买入
: 资金方必须设置大于或等于支出金额的
USDC.e
授权额度。
卖出
: 资金方必须设置大于或等于出售金额的
条件代币
授权额度。
这允许 Exchange 合约根据你签名的订单指令执行结算。

有效性检查
系统会持续监控订单以确保它们保持有效。这包括跟踪:
底层余额
授权额度
链上订单取消
任何被发现故意滥用这些检查的 maker 将被列入黑名单。
每个市场的订单下单也有限制。你只能下总额小于或等于每个市场可用余额的订单。例如,如果你的资金钱包中有 500 USDC.e,你可以下一个以 $0.50 买入 1000 YES 的订单——但该市场中的任何额外买入订单都会被拒绝,因为你的全部余额已为第一个订单预留。
你可以下单的最大规模是:
maxOrderSize
=
underlyingAssetBalance
−
∑
(
orderSize
−
orderFillAmount
)
\text{maxOrderSize} = \text{underlyingAssetBalance} - \sum(\text{orderSize} - \text{orderFillAmount})
maxOrderSize
=
underlyingAssetBalance
−
∑
(
orderSize
−
orderFillAmount
)

订单查询
所有查询端点都需要
L2 身份验证
。
Builder 身份验证
的客户端也可以使用相同的方法查询归属于其 builder 账户的订单。

获取单个订单
通过订单 ID 检索特定订单的详细信息:
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
);

获取未成交订单
检索你的未成交订单,可选择按市场或资产筛选:
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
// Filtered by asset
const
assetOrders
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
每个返回的订单包含以下字段:
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
市场 ID (条件 ID)
asset_id
string
代币 ID
side
string
BUY
或
SELL
original_size
string
下单时的原始订单规模
size_matched
string
已成交数量
price
string
限价
outcome
string
可读结果(例如 “Yes”、“No”)
order_type
string
订单类型 (GTC、GTD、FOK、FAK)
maker_address
string
资金地址
owner
string
订单所有者的 API 密钥
expiration
string
订单过期的 Unix 时间戳(无过期时间为
0
)
associate_trades
string[]
此订单部分参与的交易 ID
created_at
string
订单创建的 Unix 时间戳

交易历史
当订单被匹配时,会创建一笔交易。交易经历以下状态:
状态
是否终态?
描述
MATCHED
否
已匹配并发送到执行器服务以进行链上提交
MINED
否
观察到已在链上挖出,但尚未达到最终性阈值
CONFIRMED
是
达到强概率最终性——交易成功
RETRYING
否
交易失败(回滚或重组)——运营商正在重试
FAILED
是
交易永久失败且不再重试

Trade 对象
每笔交易包含以下字段:
字段
类型
描述
id
string
交易 ID
taker_order_id
string
Taker 订单 ID (哈希)
market
string
市场 ID (条件 ID)
asset_id
string
代币 ID
side
string
BUY
或
SELL
size
string
交易规模
fee_rate_bps
string
以基点表示的费率
price
string
交易价格
status
string
交易状态(见上表)
match_time
string
交易匹配的 Unix 时间戳
last_update
string
最后状态更新的 Unix 时间戳
outcome
string
可读结果(例如 “Yes”、“No”)
owner
string
交易所有者的 API 密钥 ID
maker_address
string
资金地址
trader_side
string
你在此交易中是
TAKER
还是
MAKER
transaction_hash
string
链上交易哈希(挖矿后可用)
maker_orders
array
与此交易匹配的 maker 订单数组(见下文)

MakerOrder 字段
maker_orders
数组中的每个条目包含:
字段
类型
描述
order_id
string
Maker 订单 ID (哈希)
owner
string
Maker 的 API 密钥 ID
maker_address
string
Maker 的资金地址
matched_amount
string
此交易中匹配的数量
price
string
Maker 订单价格
fee_rate_bps
string
Maker 费率(基点)
asset_id
string
代币 ID
outcome
string
结果名称
side
string
BUY
或
SELL
使用 SDK 检索你的交易:
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
// With pagination
const
paginatedTrades
=
await
client
.
getTradesPaginated
({
market:
"0xbd31dc8a..."
,
});

心跳
心跳端点维护会话存活以确保订单安全。如果在
10 秒
内(最多有 5 秒缓冲)未收到有效心跳,
你的所有未成交订单将被取消
。
TypeScript
Python
// Send heartbeats in a loop
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
在每个请求中,包含你收到的最新
heartbeat_id
。对于你的第一个请求,使用空字符串。
如果你发送无效或过期的
heartbeat_id
,服务器会响应
400 Bad Request
并在响应中提供正确的
heartbeat_id
。更新你的客户端并重试。

订单评分
检查你的挂单是否符合
maker 返佣
评分条件:
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
console
.
log
(
scoring
);
// { scoring: true }
// Multiple orders
const
batchScoring
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

链上订单信息
当交易在链上结算时,Exchange 合约会发出
OrderFilled
事件,包含以下字段:
字段
描述
orderHash
已成交订单的唯一哈希
maker
生成订单和资金来源的用户
taker
成交订单的用户,或在成交多个限价单时为 Exchange 合约
makerAssetId
给出的资产 ID。如果为
0
,订单是
买入
(用 USDC.e 换取结果代币)
takerAssetId
收到的资产 ID。如果为
0
,订单是
卖出
(用结果代币换取 USDC.e)
makerAmountFilled
给出的资产数量
takerAmountFilled
收到的资产数量
fee
订单 maker 支付的费用

错误消息
下单时,如果无法下单,响应可能包含
errorMsg
。如果
success
为
false
,则发生服务器端错误:
错误
描述
INVALID_ORDER_MIN_TICK_SIZE
价格不符合市场的最小价格变动单位
INVALID_ORDER_MIN_SIZE
订单规模低于最小阈值
INVALID_ORDER_DUPLICATED
相同的订单已经下过
INVALID_ORDER_NOT_ENOUGH_BALANCE
资金方没有足够的余额或授权额度
INVALID_ORDER_EXPIRATION
过期时间戳在过去
INVALID_ORDER_ERROR
插入订单时的系统错误
INVALID_POST_ONLY_ORDER_TYPE
Post-only 标志与市价单类型(FOK/FAK)一起使用
INVALID_POST_ONLY_ORDER
Post-only 订单会穿过盘口
EXECUTION_ERROR
执行交易时的系统错误
ORDER_DELAYED
由于市场条件订单下单延迟
DELAYING_ORDER_ERROR
延迟订单时的系统错误
FOK_ORDER_NOT_FILLED_ERROR
FOK 订单无法完全成交
MARKET_NOT_READY
市场尚未接受订单

插入状态
当订单成功下单时,响应包含
status
字段:
状态
描述
matched
订单已下单并与挂单匹配
live
订单已下单并挂在盘口
delayed
订单可成交但受匹配延迟限制
unmatched
订单可成交但延迟失败——下单仍然成功

安全性
Polymarket 的 Exchange 合约已由 Chainsecurity 审计(
查看审计报告
)。
运营商的权限仅限于订单匹配和确保正确排序。运营商无法设置价格或执行未经授权的交易。如果出现信任问题,用户可以独立地在链上取消订单。

下一步
创建订单
构建、签名和提交订单
取消订单
取消单个、多个或所有订单