<!-- Source: https://docs.polymarket.com/cn/trading/ctf/split -->

拆分
将 USDC.e 抵押品转换为完整的结果代币集合。每拆分 $1 USDC.e,你会收到 1 个 Yes 代币和 1 个 No 代币。
$100 USDC.e → 100 Yes tokens + 100 No tokens

前置要求
在拆分之前,确保你有:
USDC.e 余额
在 Polygon 上
USDC.e 授权
给 CTF 合约以使用你的代币
Condition ID
(市场的条件 ID)——该条件必须已通过
prepareCondition
在 CTF 合约上准备好
如果 partition 是无效的,或引用的槽位数超过条件准备的数量,交易将回滚。

工作原理
你授权 CTF 合约使用你的 USDC.e
你调用
splitPosition()
,传入金额和市场详情
CTF 合约从你的钱包转移 USDC.e,并铸造两种结果代币
该操作是原子性的——如果任何步骤失败,整个交易都会回滚。

函数参数

collateralToken
IERC20
USDC.e (Bridged USDC) 合约地址:
0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174

parentCollectionId
bytes32
对于 Polymarket 市场,始终为
0x0000...0000
(32 个零字节)

conditionId
bytes32
市场的 condition ID,可从 Markets API 获取

partition
uint[]
索引集合数组:二元市场使用
[1, 2]
(Yes = 1, No = 2)

amount
uint256
要拆分的抵押品或权益数量。也是将收到的完整集合数量。

下一步
合并代币
将代币对转换回 USDC.e
在订单簿上交易
使用你新拆分的代币下单