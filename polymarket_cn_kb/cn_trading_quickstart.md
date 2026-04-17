<!-- Source: https://docs.polymarket.com/cn/trading/quickstart -->

本指南将带你完整体验在 Polymarket 上下达订单的全过程。
1
安装 SDK
TypeScript
Python
npm
install
@polymarket/clob-client
ethers@5
2
设置你的客户端
生成你的 API 凭证并初始化交易客户端。本示例使用 EOA 钱包(类型
0
)——你的钱包支付自己的 gas 费用并充当资金账户:
TypeScript
Python
import
{
ClobClient
}
from
"@polymarket/clob-client"
;
import
{
Wallet
}
from
"ethers"
;
// v5.8.0
const
HOST
=
"https://clob.polymarket.com"
;
const
CHAIN_ID
=
137
;
// Polygon mainnet
const
signer
=
new
Wallet
(
process
.
env
.
PRIVATE_KEY
);
// Derive API credentials
const
tempClient
=
new
ClobClient
(
HOST
,
CHAIN_ID
,
signer
);
const
apiCreds
=
await
tempClient
.
createOrDeriveApiKey
();
// Initialize trading client
const
client
=
new
ClobClient
(
HOST
,
CHAIN_ID
,
signer
,
apiCreds
,
0
,
// EOA
signer
.
address
,
);
如果你有 Polymarket.com 账户,你的资金在代理钱包中——请改用签名类型
1
或
2
。详情请见
签名类型
。
在交易之前,你的资金账户地址需要
USDC.e
(用于购买结果代币)和
POL
(用于 gas,如果使用 EOA 类型
0
)。代理钱包用户(类型
1
和
2
)可以改用 Polymarket 的无 gas 中继器。
3
下达订单
从
Markets API
获取代币 ID,然后创建并提交你的订单:
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
"YOUR_TOKEN_ID"
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
// Set to true for multi-outcome markets
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
使用 SDK 的
getTickSize()
和
getNegRisk()
方法,或从 API 返回的市场对象中查询市场的
tickSize
和
negRisk
值。
4
查看你的订单
TypeScript
Python
// View all open orders
const
openOrders
=
await
client
.
getOpenOrders
();
console
.
log
(
`You have
${
openOrders
.
length
}
open orders`
);
// View your trade history
const
trades
=
await
client
.
getTrades
();
console
.
log
(
`You've made
${
trades
.
length
}
trades`
);
// Cancel an order
await
client
.
cancelOrder
(
response
.
orderID
);

问题排查
L2 AUTH NOT AVAILABLE - Invalid Signature
生成的 API 凭证使用了错误的私钥、签名类型或资金账户地址。
检查
signatureType
是否与你的账户类型匹配(
0
、
1
或
2
)
确保
funder
与你的钱包类型正确对应
如果不确定,请使用
createOrDeriveApiKey()
重新生成凭证
Order rejected - insufficient balance
你的资金账户地址没有足够的代币:
买单(BUY)
: 需要在资金账户地址中有 USDC.e
卖单(SELL)
: 需要在资金账户地址中有结果代币
确保你的 USDC.e 余额大于未完成订单中已锁定的金额
Order rejected - insufficient allowance
你需要批准 Exchange 合约使用你的代币。这通常在你首次交易时通过 Polymarket UI 完成,或使用 CTF 合约的
setApprovalForAll()
方法完成。
什么是我的资金账户地址
你的资金账户地址是持有你资金的钱包:
EOA(类型 0)
: 直接是你的钱包地址
代理钱包(类型 1 或 2)
: 前往
polymarket.com/settings
在个人资料下拉菜单中查找钱包地址
如果代理钱包不存在,请先登录 Polymarket.com(钱包在首次登录时部署)。
Blocked by Cloudflare or Geoblock
你正在尝试从受限制的地区下达交易。详情请见
地理限制
。

下一步
创建订单
订单类型、价格精度和错误处理
订单归属
将订单归属到你的构建者账户以获得交易量积分