<!-- Source: https://docs.polymarket.com/cn/api-reference/clients-sdks -->

Polymarket 提供 TypeScript、Python 和 Rust 的官方开源客户端。三者都支持完整的 CLOB API，包括市场数据、订单管理和身份验证。

安装
TypeScript
Python
Rust
npm
install
@polymarket/clob-client
ethers@5

快速示例
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
,
apiCreds
,
);
const
markets
=
await
client
.
getMarkets
();

源代码
语言
包
仓库
TypeScript
@polymarket/clob-client
github.com/Polymarket/clob-client
Python
py-clob-client
github.com/Polymarket/py-clob-client
Rust
polymarket-client-sdk
github.com/Polymarket/rs-clob-client
每个仓库的
/examples
目录中包含可运行的示例。

Builder SDK
如果你通过
Builder Program
构建应用，还可以使用额外的签名 SDK：
语言
包
仓库
TypeScript
@polymarket/builder-signing-sdk
github.com/Polymarket/builder-signing-sdk
Python
py_builder_signing_sdk
github.com/Polymarket/py-builder-signing-sdk
使用详情请参阅
订单归因
。

Relayer SDK
对于使用代理钱包的
免 Gas 交易
，Relayer 客户端负责通过 Polymarket 的 relayer 提交交易：
语言
包
仓库
TypeScript
@polymarket/builder-relayer-client
github.com/Polymarket/builder-relayer-client
Python
py-builder-relayer-client
github.com/Polymarket/py-builder-relayer-client

下一步
快速开始
设置客户端并下你的第一笔订单。
身份验证
了解 L1/L2 身份验证和 API 凭证。