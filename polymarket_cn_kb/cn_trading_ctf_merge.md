<!-- Source: https://docs.polymarket.com/cn/trading/ctf/merge -->

合并
是拆分的逆操作——它将完整的结果代币集合转换回 USDC.e 抵押品。每合并 1 个 Yes 代币和 1 个 No 代币,你会收到 $1 USDC.e。该条件必须已通过
prepareCondition
在 CTF 合约上准备好。
100 Yes tokens + 100 No tokens → $100 USDC.e

前置要求
在合并之前,你需要:
相等数量
的 Yes 和 No 代币
市场的
Condition ID
交易所需的
足够 gas

工作原理
你调用
mergePositions()
,传入金额和市场详情
完整集合中每个仓位的一个单位被销毁,换取 1 个抵押品单位
CTF 合约将 USDC.e 释放回你的钱包
该操作是原子性的——如果你没有足够的两种代币,交易将回滚。

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

amount
uint256
要合并的完整集合数量。也是将收到的抵押品数量。

下一步
兑换代币
判定后将获胜代币兑换为 USDC.e
CTF 概述
了解更多关于 Conditional Token Framework 的信息