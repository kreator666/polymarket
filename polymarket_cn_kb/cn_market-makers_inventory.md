<!-- Source: https://docs.polymarket.com/cn/market-makers/inventory -->

做市商需要双方的结果代币来报价市场。三个核心库存操作是将 USDC.e
拆分
为 YES/NO 代币对、将代币对
合并
回 USDC.e,以及在判定后
兑换
获胜代币——所有操作都通过 Relayer Client 免 gas 执行。
有关条件代币框架工作原理的完整说明,请参阅
CTF 概述
。本页重点介绍使用 Relayer Client 的做市商工作流程。

将 USDC.e 拆分为代币
拆分将 USDC.e 转换为等量的 YES 和 NO 代币——创建你报价市场双方所需的库存。
TypeScript
Python
import
{
ethers
}
from
"ethers"
;
import
{
Interface
}
from
"ethers/lib/utils"
;
import
{
RelayClient
,
Transaction
}
from
"@polymarket/builder-relayer-client"
;
const
CTF_ADDRESS
=
"0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
;
const
USDCe_ADDRESS
=
"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
;
const
ctfInterface
=
new
Interface
([
"function splitPosition(address collateralToken, bytes32 parentCollectionId, bytes32 conditionId, uint[] partition, uint amount)"
,
]);
// Split $1000 USDCe into YES/NO tokens
const
amount
=
ethers
.
utils
.
parseUnits
(
"1000"
,
6
);
// USDCe has 6 decimals
const
splitTx
:
Transaction
=
{
to:
CTF_ADDRESS
,
data:
ctfInterface
.
encodeFunctionData
(
"splitPosition"
, [
USDCe_ADDRESS
,
// collateralToken
ethers
.
constants
.
HashZero
,
// parentCollectionId (always zero for Polymarket)
conditionId
,
// conditionId from market
[
1
,
2
],
// partition: [YES, NO]
amount
,
]),
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
splitTx
],
"Split USDCe into tokens"
);
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
"Split completed:"
,
result
?.
transactionHash
);
拆分 1000 USDC.e 后,你会收到 1000 个 YES 代币和 1000 个 NO 代币。你的 USDC.e 余额减少 1000。

将代币合并为 USDC.e
合并将等量的 YES 和 NO 代币转换回 USDC.e——适用于减少敞口、退出市场或释放资金。
TypeScript
Python
const
ctfInterface
=
new
Interface
([
"function mergePositions(address collateralToken, bytes32 parentCollectionId, bytes32 conditionId, uint[] partition, uint amount)"
,
]);
// Merge 500 YES + 500 NO back to 500 USDCe
const
amount
=
ethers
.
utils
.
parseUnits
(
"500"
,
6
);
const
mergeTx
:
Transaction
=
{
to:
CTF_ADDRESS
,
data:
ctfInterface
.
encodeFunctionData
(
"mergePositions"
, [
USDCe_ADDRESS
,
ethers
.
constants
.
HashZero
,
conditionId
,
[
1
,
2
],
amount
,
]),
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
mergeTx
],
"Merge tokens to USDCe"
);
await
response
.
wait
();
合并各 500 个后,你的 YES 和 NO 余额各减少 500,USDC.e 余额增加 500。

判定后兑换
市场判定后,将获胜代币兑换为 USDC.e。每个获胜代币价值
1
——失败代币兑换为
1——失败代币兑换为
1——
失败代币兑换为
0。

检查判定状态
TypeScript
Python
const
market
=
await
clobClient
.
getMarket
(
conditionId
);
if
(
market
.
closed
) {
const
winningToken
=
market
.
tokens
.
find
((
t
)
=>
t
.
winner
);
console
.
log
(
"Winning outcome:"
,
winningToken
?.
outcome
);
}

兑换获胜代币
TypeScript
Python
const
ctfInterface
=
new
Interface
([
"function redeemPositions(address collateralToken, bytes32 parentCollectionId, bytes32 conditionId, uint[] indexSets)"
,
]);
const
redeemTx
:
Transaction
=
{
to:
CTF_ADDRESS
,
data:
ctfInterface
.
encodeFunctionData
(
"redeemPositions"
, [
USDCe_ADDRESS
,
ethers
.
constants
.
HashZero
,
conditionId
,
[
1
,
2
],
// Redeem both YES and NO (only winners pay out)
]),
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
"Redeem winning tokens"
);
await
response
.
wait
();

Negative Risk 市场
多结果市场使用 Neg Risk CTF Exchange。拆分和合并的工作方式相同,但使用不同的合约地址:
const
NEG_RISK_ADAPTER
=
"0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
;
const
NEG_RISK_CTF_EXCHANGE
=
"0xC5d563A36AE78145C45a50134d48A1215220f80a"
;
有关多结果代币机制如何不同的详情,请参阅
Negative Risk 市场
。

库存策略

报价前
通过
Gamma API
检查市场元数据
拆分足够的 USDC.e 以覆盖你的预期报价规模
如果尚未完成,设置代币授权(参见
入门
)

交易期间
当库存在某一侧失衡时
倾斜报价
合并多余代币
以释放资金用于其他市场
当任一侧库存不足时
拆分更多

判定后
取消市场中的所有未成交订单
等待判定完成
兑换获胜代币
合并任何剩余的 YES/NO 代币对

批量操作
在单个中继器调用中执行多个库存操作以提高效率:
const
transactions
:
Transaction
[]
=
[
// Split on Market A
{
to:
CTF_ADDRESS
,
data:
ctfInterface
.
encodeFunctionData
(
"splitPosition"
, [
USDCe_ADDRESS
,
ethers
.
constants
.
HashZero
,
conditionIdA
,
[
1
,
2
],
ethers
.
utils
.
parseUnits
(
"1000"
,
6
),
]),
value:
"0"
,
},
// Split on Market B
{
to:
CTF_ADDRESS
,
data:
ctfInterface
.
encodeFunctionData
(
"splitPosition"
, [
USDCe_ADDRESS
,
ethers
.
constants
.
HashZero
,
conditionIdB
,
[
1
,
2
],
ethers
.
utils
.
parseUnits
(
"1000"
,
6
),
]),
value:
"0"
,
},
];
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
"Batch inventory setup"
);
await
response
.
wait
();

下一步
CTF 概述
条件代币框架的底层工作原理
拆分代币
详细的拆分函数参数和前提条件
合并代币
详细的合并函数参数
免 gas 交易
Relayer Client 设置和配置