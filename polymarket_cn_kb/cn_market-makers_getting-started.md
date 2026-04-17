<!-- Source: https://docs.polymarket.com/cn/market-makers/getting-started -->

在开始做市之前,你需要完成这些一次性设置步骤——向 Polygon 充值 USDC.e、部署钱包、授权代币交易并生成 API 凭证。
1
充值 USDC.e
做市商需要在 Polygon 上有 USDC.e 来为交易操作提供资金。
方式
适用场景
文档
Bridge API
从其他链自动充值
Bridge 充值
直接 Polygon 转账
已经在 Polygon 上有 USDC.e
N/A
跨链桥
从 Ethereum 大额充值
支持的资产

使用 Bridge API
// Get deposit addresses for your Polymarket wallet
const
deposit
=
await
fetch
(
"https://bridge.polymarket.com/deposit"
, {
method:
"POST"
,
headers:
{
"Content-Type"
:
"application/json"
},
body:
JSON
.
stringify
({
address:
"YOUR_POLYMARKET_WALLET_ADDRESS"
,
}),
});
// Returns deposit addresses for EVM, SVM, and BTC networks
const
addresses
=
await
deposit
.
json
();
// Send USDC to the appropriate address for your source chain
2
部署钱包

EOA - 外部拥有账户
标准的 Ethereum 钱包。你需要为所有链上交易支付费用(授权、拆分、合并、交易执行)。

Safe 钱包 - 推荐
通过 Polymarket 的 relayer 部署的基于 Gnosis Safe 的钱包。优势:
免 gas 交易
— Polymarket 为链上操作支付 gas 费用
合约钱包
— 支持批量交易等高级功能
使用 Relayer Client 部署 Safe 钱包:
TypeScript
Python
import
{
RelayClient
,
RelayerTxType
}
from
"@polymarket/builder-relayer-client"
;
const
client
=
new
RelayClient
(
"https://relayer-v2.polymarket.com/"
,
137
,
// Polygon mainnet
signer
,
builderConfig
,
RelayerTxType
.
SAFE
,
);
// Deploy the Safe wallet
const
response
=
await
client
.
deploy
();
const
result
=
await
response
.
wait
();
console
.
log
(
"Safe Address:"
,
result
?.
proxyAddress
);
完整的 Relayer Client 设置(包括本地和远程签名配置)请参阅
免 Gas 交易
。
3
授权代币
交易前,你必须授权交易所合约使用你的代币。

所需授权
代币
被授权方
用途
USDC.e
CTF Contract
将 USDC.e 拆分为结果代币
CTF (结果代币)
CTF Exchange
交易结果代币
CTF (结果代币)
Neg Risk CTF Exchange
交易 neg-risk 市场代币

合约地址 - Polygon 主网
const
ADDRESSES
=
{
USDCe:
"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
,
CTF:
"0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
,
CTF_EXCHANGE:
"0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
,
NEG_RISK_CTF_EXCHANGE:
"0xC5d563A36AE78145C45a50134d48A1215220f80a"
,
NEG_RISK_ADAPTER:
"0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
,
};

通过 Relayer Client 授权
TypeScript
Python
import
{
ethers
}
from
"ethers"
;
import
{
Interface
}
from
"ethers/lib/utils"
;
const
erc20Interface
=
new
Interface
([
"function approve(address spender, uint256 amount) returns (bool)"
,
]);
// Approve USDCe for CTF contract
const
approveTx
=
{
to:
ADDRESSES
.
USDCe
,
data:
erc20Interface
.
encodeFunctionData
(
"approve"
, [
ADDRESSES
.
CTF
,
ethers
.
constants
.
MaxUint256
,
]),
value:
"0"
,
};
const
response
=
await
client
.
execute
([
approveTx
],
"Approve USDCe for CTF"
);
await
response
.
wait
();
4
生成 API 凭证
要下单和访问需要认证的端点,你需要从钱包派生 L2 API 凭证。
TypeScript
Python
import
{
ClobClient
}
from
"@polymarket/clob-client"
;
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
);
// Derive API credentials from your wallet
const
credentials
=
await
client
.
createOrDeriveApiKey
();
console
.
log
(
"API Key:"
,
credentials
.
key
);
console
.
log
(
"Secret:"
,
credentials
.
secret
);
console
.
log
(
"Passphrase:"
,
credentials
.
passphrase
);
获得凭证后,初始化客户端以进行需要认证的操作:
TypeScript
Python
const
tradingClient
=
new
ClobClient
(
"https://clob.polymarket.com"
,
137
,
wallet
,
credentials
,
);
有关签名类型和 REST API 请求头的完整详情,请参阅
身份验证
。

下一步
交易
发布限价单并管理报价
市场数据
连接到实时市场数据