<!-- Source: https://docs.polymarket.com/cn/trading/orders/attribution -->

订单归因功能会在通过 CLOB 下单时添加 Builder 身份验证标头,使 Polymarket 能够将交易归因到你的 Builder 账户。这使你能够:
在
Builder 排行榜
上追踪交易量
通过
Builder Program
获得奖励
通过 Data API 监控绩效

Builder API 凭证
每个 Builder 都会从其
Builder Profile
获得 API 凭证:
凭证
描述
key
你的 Builder API 密钥标识符
secret
用于签名请求的密钥
passphrase
附加身份验证密码
Builder API 凭证与用户 API 凭证
不同
。Builder 凭证仅用于订单归因 - 你仍然需要用户凭证进行身份验证。切勿在客户端代码中暴露 Builder 凭证,也不要将其提交到版本控制系统。

远程签名
远程签名将你的 Builder 凭证安全地保存在你控制的服务器上。用户的客户端将订单详细信息发送到你的服务器,服务器添加 Builder 标头后再转发到 CLOB。

服务器实现
你的签名服务器接收请求详细信息并返回身份验证标头:
TypeScript
Python
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
// POST /sign - receives { method, path, body } from the client SDK
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

客户端配置
将 CLOB 客户端指向你的签名服务器:
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
token:
"optional-auth-token"
,
// optional
},
});
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
// signature type
funderAddress
,
undefined
,
false
,
builderConfig
,
);
// Orders automatically include builder headers
const
response
=
await
client
.
createAndPostOrder
(
/* ... */
);

本地签名
当你控制整个订单下单流程时(例如,你的后端代表用户下单),可以在本地签署订单:
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
BuilderConfig
,
BuilderApiKeyCreds
,
}
from
"@polymarket/builder-signing-sdk"
;
const
builderCreds
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
const
builderConfig
=
new
BuilderConfig
({
localBuilderCreds:
builderCreds
,
});
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
funderAddress
,
undefined
,
false
,
builderConfig
,
);
// Orders automatically include builder headers
const
response
=
await
client
.
createAndPostOrder
(
/* ... */
);

身份验证标头
SDK 会自动生成并将这些标头附加到每个请求:
标头
描述
POLY_BUILDER_API_KEY
你的 Builder API 密钥
POLY_BUILDER_TIMESTAMP
签名创建的 Unix 时间戳
POLY_BUILDER_PASSPHRASE
你的 Builder 密码
POLY_BUILDER_SIGNATURE
请求的 HMAC 签名
使用
本地签名
时,SDK 会自动构建并附加这些标头。使用
远程签名
时,你的服务器返回这些标头,然后 SDK 将其附加。

验证归因

获取 Builder 交易
查询归因到你的 Builder 账户的交易以验证归因是否正常工作:
TypeScript
Python
const
trades
=
await
client
.
getBuilderTrades
();
// Filtered by market
const
marketTrades
=
await
client
.
getBuilderTrades
({
market:
"0xbd31dc8a..."
,
});
每个
BuilderTrade
包括:
id
、
market
、
assetId
、
side
、
size
、
price
、
status
、
outcome
、
owner
、
maker
、
transactionHash
、
matchTime
、
fee
和
feeUsdc
。

撤销 Builder API 密钥
如果你的凭证被泄露,请立即撤销:
TypeScript
Python
await
client
.
revokeBuilderApiKey
();
撤销后,从你的
Builder Profile
生成新凭证。

故障排查
无效签名错误
验证请求主体是否正确作为 JSON 传递 - 检查
path
、
body
和
method
是否与客户端发送的内容匹配 - 确保你的服务器和客户端使用相同的 Builder API 凭证
缺少凭证
确保已设置你的环境变量: -
POLY_BUILDER_API_KEY
-
POLY_BUILDER_SECRET
-
POLY_BUILDER_PASSPHRASE
交易量未显示在排行榜上
确认你的 Builder 凭证有效且未被撤销 - 检查订单是否附加了 Builder 配置 - 交易量可能需要最多 24 小时才能在排行榜上显示

下一步
构建者计划
了解 Builder Program 的等级和奖励
创建订单
构建、签名和提交订单