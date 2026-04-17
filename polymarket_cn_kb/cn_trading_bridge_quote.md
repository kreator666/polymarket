<!-- Source: https://docs.polymarket.com/cn/trading/bridge/quote -->

在执行充值或提现前获取预估报价。报价包括预估输出金额、结算时间和详细的费用明细。

获取报价
curl
-X
POST
https://bridge.polymarket.com/quote
\
-H
"Content-Type: application/json"
\
-d
'{
"fromAmountBaseUnit": "10000000",
"fromChainId": "137",
"fromTokenAddress": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
"recipientAddress": "0x17eC161f126e82A8ba337f4022d574DBEaFef575",
"toChainId": "137",
"toTokenAddress": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
}'

请求参数
参数
类型
描述
fromAmountBaseUnit
string
要发送的金额(基本单位)，例如
"10000000"
代表 10 USDC
fromChainId
string
源链 ID，例如
"137"
代表 Polygon
fromTokenAddress
string
源链上的代币合约地址
recipientAddress
string
接收资金的目标钱包地址
toChainId
string
目标链 ID
toTokenAddress
string
目标链上的代币合约地址

响应
报价响应包括:
字段
类型
描述
estCheckoutTimeMs
number
预估结算时间(毫秒)
estInputUsd
number
预估输入价值(美元)
estOutputUsd
number
预估输出价值(美元)
estToTokenBaseUnit
string
预估输出金额(基本单位)
quoteId
string
此报价的唯一标识符
estFeeBreakdown
object
详细费用明细(见下文)

费用明细
estFeeBreakdown
对象包含:

gasUsd
number
Gas 费(美元)

appFeeLabel
string
应用费用标签

appFeePercent
number
应用费用占总金额的百分比

appFeeUsd
number
应用费用(美元)

fillCostPercent
number
执行成本占总金额的百分比

fillCostUsd
number
执行成本(美元)

maxSlippage
number
最大潜在滑点百分比

minReceived
number
扣除滑点后收到的最小金额

swapImpact
number
兑换影响占总金额的百分比

swapImpactUsd
number
兑换影响(美元)

totalImpact
number
总影响占总金额的百分比

totalImpactUsd
number
总影响成本(美元)
报价仅为预估值。由于市场条件变化，实际金额可能会略有不同。

下一步
创建充值
执行充值到 Polymarket。
提现
从 Polymarket 提现到其他链。