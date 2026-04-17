<!-- Source: https://docs.polymarket.com/cn/trading/overview -->

Polymarket 的 CLOB (Central Limit Order Book) 是一个混合去中心化交易系统——链下订单撮合与链上结算通过
Exchange 合约
实现(
由 Chainsecurity 审计
)。所有交易均为非托管式。订单是
EIP-712
签名消息,撮合后的交易在 Polygon 上原子化结算。运营方无法设定价格或执行未授权交易——用户始终可以独立地在链上取消订单。
我们建议使用开源 SDK 客户端,它们可以处理订单签名、身份验证和提交:
TypeScript Client
npm install @polymarket/clob-client
Python Client
pip install py-clob-client
你也可以直接使用 REST API,但需要自己管理
EIP-712
订单签名
和
HMAC 身份验证头
。
请参阅下方的
REST API 请求头
。

身份验证
CLOB 使用两级身份验证:
级别
方法
用途
L1
EIP-712 签名(私钥)
创建或派生 API 凭证
L2
HMAC-SHA256 (API 凭证)
下单、撤单、查询交易
你需要使用私钥一次来派生
L2 凭证
(API key、secret、passphrase),这些凭证用于验证所有后续的交易请求。
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
// Derive L2 API credentials
const
tempClient
=
new
ClobClient
(
"https://clob.polymarket.com"
,
137
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

签名类型
初始化交易客户端时,你必须指定钱包的
签名类型
和
funder 地址
:
钱包类型
ID
使用场景
Funder 地址
EOA
0
独立钱包——你自己支付 gas 费(使用 POL 支付 gas)
你的 EOA 钱包地址
POLY_PROXY
1
通过 Magic Link 登录的 Polymarket 账户(邮箱/Google 登录)。需要从 Polymarket.com
导出私钥
你的代理钱包地址
GNOSIS_SAFE
2
通过浏览器钱包(MetaMask、Rabby)或嵌入式钱包(Privy、Turnkey)登录的 Polymarket 账户。最常见的类型
你的代理钱包地址
如果你有 Polymarket.com 账户,你的资金存放在个人资料下拉菜单中可见的代理钱包中。
请使用类型
1
或
2
。类型
0
仅适用于独立的 EOA 钱包。

初始化交易客户端
TypeScript
Python
const
client
=
new
ClobClient
(
"https://clob.polymarket.com"
,
137
,
signer
,
apiCreds
,
2
,
// GNOSIS_SAFE
"0x..."
,
// Your proxy wallet address
);

REST API 请求头
如果你直接使用 REST API (不通过 SDK),需要在每个请求中附加身份验证头。
L1 请求头
— 用于创建或派生 API 凭证:
请求头
说明
POLY_ADDRESS
你的钱包地址
POLY_SIGNATURE
EIP-712 签名
POLY_TIMESTAMP
Unix 时间戳
POLY_NONCE
请求随机数
L2 请求头
— 用于所有交易操作(下单、撤单、查询):
请求头
说明
POLY_ADDRESS
你的钱包地址
POLY_SIGNATURE
请求的 HMAC-SHA256 签名
POLY_TIMESTAMP
Unix 时间戳
POLY_API_KEY
你的 API key
POLY_PASSPHRASE
你的 API passphrase
即使使用 L2 身份验证,创建订单的方法仍然需要用户的私钥来进行 EIP-712 订单载荷签名。
L2 凭证用于验证请求本身,但订单必须由密钥签名。

速率限制
CLOB 实施速率限制以确保系统稳定性:
范围
限制
一般限制
每 10 秒 15,000 个请求
POST /order
峰值 500/秒,持续 60/秒
POST /orders
(批量)
峰值 100/秒,持续 25/秒
DELETE /order
峰值 300/秒,持续 50/秒
超过这些限制将返回 HTTP
429
。请在客户端中实现指数退避。

本节内容
快速开始
端到端完成你的第一笔订单
订单簿
读取订单簿、价格、价差和中间价
订单
订单类型、最小价格单位、创建、取消和查询订单
费用
费用结构、启用费用的市场以及做市商回扣
免 Gas 交易
无需支付 gas 即可执行链上操作
CTF Tokens
拆分、合并和赎回结果代币
跨链桥
跨链存入和提取资金