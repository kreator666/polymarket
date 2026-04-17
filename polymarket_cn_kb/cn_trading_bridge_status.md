<!-- Source: https://docs.polymarket.com/cn/trading/bridge/status -->

在将资产发送到充值地址后，使用状态端点跟踪进度，直到资金到达你的 Polymarket 钱包。

检查状态
查询发送到特定充值地址的所有充值状态。
curl
https://bridge.polymarket.com/status/0x23566f8b2E82aDfCf01846E54899d110e97AC053
使用
/deposit
响应中的充值地址(EVM、SVM 或 BTC)，而不是你的 Polymarket 钱包地址。

交易状态
每笔充值都会经历以下状态:
状态
终态
描述
DEPOSIT_DETECTED
否
在源链上检测到资金，尚未处理
PROCESSING
否
交易正在路由和兑换中
ORIGIN_TX_CONFIRMED
否
源链交易已确认
SUBMITTED
否
已提交到目标链(Polygon)
COMPLETED
是
资金已到账——交易成功
FAILED
是
交易遇到错误

响应
有活跃充值的响应:
{
"transactions"
: [
{
"fromChainId"
:
"1"
,
"fromTokenAddress"
:
"0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
,
"fromAmountBaseUnit"
:
"1000000000"
,
"toChainId"
:
"137"
,
"toTokenAddress"
:
"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
,
"status"
:
"COMPLETED"
,
"txHash"
:
"0xabc123..."
,
"createdTimeMs"
:
1697875200000
}
]
}
字段
描述
fromChainId
源链 ID
fromTokenAddress
发送的代币
fromAmountBaseUnit
金额(基本单位)
toChainId
目标链(137 代表 Polygon)
toTokenAddress
接收的代币
status
当前状态(见上表)
txHash
目标交易哈希(仅在
COMPLETED
时)
createdTimeMs
Unix 时间戳(毫秒)，仅在交易开始处理后出现

空响应
空的
transactions
数组表示此地址还没有检测到充值:
{
"transactions"
: []
}
交易通常会在几分钟内完成，但根据网络状况可能需要更长时间。每 10-30 秒轮询一次，直到状态变为
COMPLETED
或
FAILED
。

下一步
创建充值
为你的钱包生成充值地址。
支持的资产
检查支持的链和最低金额。