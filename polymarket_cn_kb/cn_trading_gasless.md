<!-- Source: https://docs.polymarket.com/cn/trading/gasless -->

Polymarket 的
Relayer Client
为你的用户提供免 gas 交易功能。用户无需持有 POL 来支付 gas 费，Polymarket 的基础设施会支付所有交易费用。这创造了一种无缝体验，用户只需要 USDC.e 就能交易。

工作原理
relayer 充当交易赞助者：
你的应用创建一笔交易
用户用私钥签名
你的应用将交易发送到 Polymarket 的 relayer
relayer 将交易提交到链上并支付 gas 费
交易从用户钱包执行
免 gas 交易需要使用
Builder API Keys
或
Relayer API Keys
进行身份验证。

覆盖范围
Polymarket 为通过 relayer 路由的所有操作支付 gas：
操作
说明
Wallet deployment
为新用户部署 Safe 或 Proxy 钱包
Token approvals
授权合约使用 USDC.e 或结果代币
CTF operations
拆分、合并和兑换仓位
Transfers
在地址之间转移代币

身份验证
Relayer 支持两种身份验证方式。选择适合你用例的方式。

使用 Builder API Keys
Builder API Keys 适用于
Builder Program
成员。通过 HMAC-SHA256 签名 header 进行身份验证，使用 relayer SDK 时需要此方式。
所有请求必须包含以下 header：
Header
说明
POLY_BUILDER_API_KEY
你的 Builder API key
POLY_BUILDER_TIMESTAMP
Unix 时间戳
POLY_BUILDER_PASSPHRASE
你的 Builder passphrase
POLY_BUILDER_SIGNATURE
HMAC-SHA256 签名
当你通过
BuilderConfig
提供凭证时，SDK 会自动处理 header 生成。

使用 Relayer API Keys
Relayer API Keys 适用于做市商以及需要更简单方式的用户，无需 HMAC 签名。你可以在 Polymarket 网站的
Settings > API Keys
中创建。
请求中需要包含以下 header：
Header
说明
RELAYER_API_KEY
你的 Relayer API key
RELAYER_API_KEY_ADDRESS
拥有该 key 的地址
RELAYER_API_KEY: <your-api-key>
RELAYER_API_KEY_ADDRESS: 0xC7A2e308Efa0E5424220299Af2d85f05fa51eD2e
如果你想直接使用 Relayer API Key 而不使用 SDK，请参阅
Relayer API Reference
。

前置要求
使用 relayer 之前，你需要：
要求
来源
Builder API 凭证
或
Relayer API key
Builder Profile
或
Settings > API Keys
用户的私钥或签名器
你的钱包集成
USDC.e 余额
用于交易（不是用于 gas）

安装
npm
pip
npm
install
@polymarket/builder-relayer-client
@polymarket/builder-signing-sdk

客户端设置
使用你的签名配置初始化 relayer 客户端：
本地签名
远程签名
当你的后端安全地处理所有交易时，使用本地签名。
TypeScript
Python
import
{
createWalletClient
,
http
,
Hex
}
from
"viem"
;
import
{
privateKeyToAccount
}
from
"viem/accounts"
;
import
{
polygon
}
from
"viem/chains"
;
import
{
RelayClient
}
from
"@polymarket/builder-relayer-client"
;
import
{
BuilderConfig
}
from
"@polymarket/builder-signing-sdk"
;
const
account
=
privateKeyToAccount
(
process
.
env
.
PRIVATE_KEY
as
Hex
);
const
wallet
=
createWalletClient
({
account
,
chain:
polygon
,
transport:
http
(
process
.
env
.
RPC_URL
),
});
const
builderConfig
=
new
BuilderConfig
({
localBuilderCreds:
{
key:
process
.
env
.
POLY_BUILDER_API_KEY
!
,
secret:
process
.
env
.
POLY_BUILDER_SECRET
!
,
passphrase:
process
.
env
.
POLY_BUILDER_PASSPHRASE
!
,
},
});
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
wallet
,
builderConfig
,
);
使用远程签名将凭证保存在你控制的安全服务器上。
你的签名服务器
接收请求详情并返回身份验证 header：
Server (TypeScript)
Server (Python)
import
{
buildHmacSignature
,
BuilderApiKeyCreds
,
}
from
"@polymarket/builder-signing-sdk"
;
const
BUILDER_CREDENTIALS
:
BuilderApiKeyCreds
=
{
key:
process
.
env
.
POLY_BUILDER_API_KEY
!
,
secret:
process
.
env
.
POLY_BUILDER_SECRET
!
,
passphrase:
process
.
env
.
POLY_BUILDER_PASSPHRASE
!
,
};
// POST /sign endpoint
export
async
function
handleSignRequest
(
request
) {
const
{
method
,
path
,
body
}
=
await
request
.
json
();
const
timestamp
=
Date
.
now
().
toString
();
const
signature
=
buildHmacSignature
(
BUILDER_CREDENTIALS
.
secret
,
parseInt
(
timestamp
),
method
,
path
,
body
,
);
return
{
POLY_BUILDER_SIGNATURE:
signature
,
POLY_BUILDER_TIMESTAMP:
timestamp
,
POLY_BUILDER_API_KEY:
BUILDER_CREDENTIALS
.
key
,
POLY_BUILDER_PASSPHRASE:
BUILDER_CREDENTIALS
.
passphrase
,
};
}
你的客户端
指向你的签名服务器：
Client (TypeScript)
Client (Python)
import
{
RelayClient
}
from
"@polymarket/builder-relayer-client"
;
import
{
BuilderConfig
}
from
"@polymarket/builder-signing-sdk"
;
const
builderConfig
=
new
BuilderConfig
({
remoteBuilderConfig:
{
url:
"https://your-server.com/sign"
,
},
});
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
wallet
,
builderConfig
,
);
永远不要在客户端代码中暴露 Builder API 凭证。使用环境变量或密钥管理器。

钱包类型
初始化客户端时选择钱包类型：
类型
部署方式
最适用于
Safe
在首次交易前调用
deploy()
大多数 builder 集成
Proxy
首次交易时自动部署
Magic Link 用户
Safe Wallet (TypeScript)
Safe Wallet (Python)
Proxy Wallet (TypeScript)
Proxy Wallet (Python)
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
wallet
,
builderConfig
,
RelayerTxType
.
SAFE
,
);
// Deploy before first transaction
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

执行交易
使用
execute
方法通过 relayer 发送交易：
interface
Transaction
{
to
:
string
;
// Target contract address
data
:
string
;
// Encoded function call
value
:
string
;
// POL to send (usually "0")
}
const
response
=
await
client
.
execute
(
transactions
,
"Description"
);
const
result
=
await
response
.
wait
();

代币授权
授权合约使用代币：
TypeScript
Python
import
{
encodeFunctionData
,
maxUint256
}
from
"viem"
;
const
USDC
=
"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
;
const
CTF
=
"0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
;
const
approveTx
=
{
to:
USDC
,
data:
encodeFunctionData
({
abi:
[
{
name:
"approve"
,
type:
"function"
,
inputs:
[
{
name:
"spender"
,
type:
"address"
},
{
name:
"amount"
,
type:
"uint256"
},
],
outputs:
[{
type:
"bool"
}],
},
],
functionName:
"approve"
,
args:
[
CTF
,
maxUint256
],
}),
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
"Approve USDC.e for CTF"
);
await
response
.
wait
();

兑换仓位
市场判定后，将获胜代币兑换为 USDC.e：
TypeScript
Python
import
{
encodeFunctionData
}
from
"viem"
;
const
redeemTx
=
{
to:
CTF_ADDRESS
,
data:
encodeFunctionData
({
abi:
[
{
name:
"redeemPositions"
,
type:
"function"
,
inputs:
[
{
name:
"collateralToken"
,
type:
"address"
},
{
name:
"parentCollectionId"
,
type:
"bytes32"
},
{
name:
"conditionId"
,
type:
"bytes32"
},
{
name:
"indexSets"
,
type:
"uint256[]"
},
],
outputs:
[],
},
],
functionName:
"redeemPositions"
,
args:
[
collateralToken
,
parentCollectionId
,
conditionId
,
indexSets
],
}),
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
redeemTx
],
"Redeem positions"
);
await
response
.
wait
();

批量交易
在单次调用中原子性地执行多个操作：
TypeScript
Python
const
approveTx
=
{
to:
USDC
,
data:
encodeFunctionData
({
abi:
erc20Abi
,
functionName:
"approve"
,
args:
[
CTF
,
maxUint256
],
}),
value:
"0"
,
};
const
transferTx
=
{
to:
USDC
,
data:
encodeFunctionData
({
abi:
erc20Abi
,
functionName:
"transfer"
,
args:
[
recipientAddress
,
parseUnits
(
"50"
,
6
)],
}),
value:
"0"
,
};
// Both execute atomically
const
response
=
await
client
.
execute
(
[
approveTx
,
transferTx
],
"Approve and transfer"
,
);
await
response
.
wait
();
批量处理可以减少延迟，并确保所有交易要么全部成功，要么全部失败。

交易状态
通过这些状态跟踪交易进度：
状态
终态
说明
STATE_NEW
否
relayer 已收到交易
STATE_EXECUTED
否
已提交到链上
STATE_MINED
否
已打包进区块
STATE_CONFIRMED
是
成功确认
STATE_FAILED
是
永久失败
STATE_INVALID
是
被拒绝为无效

合约地址
所有 Polymarket 智能合约地址详见
合约地址
。

资源
Builder Relayer Client (TypeScript)
Builder Relayer Client (Python)
Builder Signing SDK (TypeScript)
Builder Signing SDK (Python)

下一步
Negative Risk Markets
了解多结果事件的资本高效交易。
Positions & Tokens
理解拆分、合并和兑换等代币操作。