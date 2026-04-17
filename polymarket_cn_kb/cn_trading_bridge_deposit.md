<!-- Source: https://docs.polymarket.com/cn/trading/bridge/deposit -->

Polymarket 使用 Polygon 上的
USDC.e
(桥接 USDC)作为所有交易的抵押品。Bridge API 允许你从 Ethereum、Solana、Bitcoin 和其他链充值资产——它们会自动转换为 Polygon 上的 USDC.e。

工作原理
为你的 Polymarket 钱包请求充值地址
将资产发送到与你的源链对应的地址
资产会自动桥接并兑换为 USDC.e
USDC.e 会存入你的钱包用于交易

创建充值地址
生成与你的 Polymarket 钱包关联的唯一充值地址。完整的请求和响应架构请参阅
Bridge API Reference
。
curl
-X
POST
https://bridge.polymarket.com/deposit
\
-H
"Content-Type: application/json"
\
-d
'{"address": "0x56687bf447db6ffa42ffe2204a05edaa20f55839"}'

地址类型
地址
用途
evm
Ethereum、Arbitrum、Base、Optimism 及其他 EVM 链
svm
Solana
btc
Bitcoin
tvm
Tron
每个地址都是你钱包独有的。只能从支持的链向正确的地址类型发送资产。

充值流程
1
获取你的充值地址
使用你的 Polymarket 钱包地址调用
POST /deposit
来获取充值地址。
2
检查支持的资产
通过
/supported-assets
验证你的代币是否受支持，以及是否满足最低充值金额。
3
发送资产
从你的源链将代币转账到相应的充值地址。
4
跟踪状态
使用
/status/{address}
监控你的充值进度。

USDC vs USDC.e
你可以向 Polymarket 钱包充值 USDC(原生)或 USDC.e(桥接)。如果你充值原生 USDC，系统会提示你”激活资金”，这会通过费率最低的 Uniswap 池将其兑换为 USDC.e(滑点小于 10bp)。

大额充值
对于来自 Polygon 以外链的超过 50,000 美元的充值，我们建议使用第三方桥接服务以减少滑点:
DeBridge
Across
Portal
直接桥接到你的 Polymarket USDC(Polygon)充值地址。Polymarket 与任何第三方桥接服务无关联，也不对其负责。

最低充值金额
每种资产都有最低充值金额。低于最低金额的充值将不会被处理。请查看
/supported-assets
获取当前的最低金额。

充值恢复
如果你在 Ethereum 或 Polygon 上充值了错误的代币，可以使用这些工具恢复你的资金:
Ethereum 充值
:
recovery.polymarket.com
Polygon 充值
:
matic-recovery.polymarket.com
发送不支持的代币可能会导致
不可恢复的损失
。在充值前务必验证你的代币是否列在
支持的资产
中。

下一步
支持的资产
查看所有支持的链和代币及其最低金额。
检查状态
跟踪你的充值进度直至完成。