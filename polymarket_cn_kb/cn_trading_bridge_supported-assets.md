<!-- Source: https://docs.polymarket.com/cn/trading/bridge/supported-assets -->

Bridge API 支持从多条链和多种代币充值。所有充值都会自动转换为
Polygon 上的 USDC.e
，用作 Polymarket 上交易的抵押品。

获取支持的资产
检索支持的链和代币完整列表及其最低充值金额。
curl
https://bridge.polymarket.com/supported-assets

支持的链
桥接服务支持从以下区块链网络充值:
链
地址类型
最低充值
示例代币
Ethereum
EVM
$7
ETH, USDC, USDT, WBTC, DAI, LINK, UNI, AAVE
Polygon
EVM
$2
POL, USDC, USDT, DAI, WETH, SAND
Arbitrum
EVM
$2
ETH, ARB, USDC, USDT, DAI, WBTC, USDe
Base
EVM
$2
ETH, USDC, USDT, DAI, cbBTC, AERO, USDS
Optimism
EVM
$2
ETH, OP, USDC, USDT, DAI, USDe
BNB Smart Chain
EVM
$2
BNB, USDC, USDT, DAI, ETH, BTCB, BUSD
Solana
SVM
$2
SOL, USDC, USDT, USDe, TRUMP
Bitcoin
BTC
$9
BTC
Tron
TVM
$9
USDT
HyperEVM
EVM
$2
HYPE, USDC, USDe, stHYPE, UBTC, UETH
Abstract
EVM
$2
ETH, USDC, USDT
Monad
EVM
$2
MON, USDC, USDT
Ethereal
EVM
$2
USDe, WUSDe
Katana
EVM
$2
AUSD
Lighter
EVM
$2
USDC
支持的资产会随时间变化。在发起充值前，务必调用
/supported-assets
获取当前列表。

最低金额
每种资产都有一个
minCheckoutUsd
值——以美元等值计算的最低充值金额。低于此阈值的充值可能无法处理。
大多数 L2 链(Polygon、Arbitrum、Base、Optimism)的最低金额为 2 美元，而 Ethereum 充值要求最低 7 美元。由于桥接成本较高，Bitcoin 和 Tron 的最低金额为 9 美元。

下一步
创建充值
为你的钱包生成充值地址。
检查状态
跟踪你的充值进度。