<!-- Source: https://docs.polymarket.com/cn/trading/bridge/withdraw -->

从你的 Polymarket 钱包提现 USDC.e 到任何支持的链和代币。资金会自动桥接并兑换为你在目标链上所需的代币。

工作原理
指定你的目标链、代币和接收地址
接收每个目标链(EVM、Solana、Bitcoin)的充值地址
从你的 Polymarket 钱包将 USDC.e 发送到相应的充值地址
资金会自动桥接并兑换为你所需的代币
资金到达你的目标钱包
不要预先生成提现地址。只在准备执行提现时生成。每个地址都为特定目标配置。
提现时，USDC.e(桥接 USDC)会通过
Uniswap v3 池
兑换为 USDC(原生)。界面强制输出金额差异小于 10bp。有时此池可能会枯竭。如果遇到提现问题，请尝试将提现拆分成更小的金额，或等待池重新平衡。或者，你可以直接提现 USDC.e，这不需要 Uniswap 流动性——但要注意某些交易所不再直接接受 USDC.e 充值。
对于非常大额的提现(超过 50,000 美元)，考虑将提现拆分成更小的金额，或使用第三方桥接服务以减少滑点。

创建提现地址
生成为你的提现目标配置的充值地址。完整的请求和响应架构请参阅
Bridge API Reference
。
curl
-X
POST
https://bridge.polymarket.com/withdraw
\
-H
"Content-Type: application/json"
\
-d
'{
"address": "0x9156dd10bea4c8d7e2d591b633d1694b1d764756",
"toChainId": "1",
"toTokenAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
"recipientAddr": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
}'

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
提现是
即时
且
免费
的——Polymarket 不收取提现费用。

提现流程
1
检查支持的资产
通过
/supported-assets
验证你的目标链和代币是否受支持。
2
获取报价
通过
POST /quote
预览费用和预估输出。
3
创建提现地址
使用你的钱包地址、目标链、代币和接收地址调用
POST /withdraw
。
4
发送 USDC.e
从你的 Polymarket 钱包将 USDC.e 转账到相应的充值地址。
5
跟踪状态
使用
/status/{address}
监控进度。

下一步
获取报价
在提现前预览费用和预估输出。
检查状态
跟踪你的提现进度。