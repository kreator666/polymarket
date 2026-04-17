<!-- Source: https://docs.polymarket.com/cn/trading/ctf/redeem -->

兑换
是在市场判定后将获胜的结果代币转换为 USDC.e。每个获胜代币价值正好
1.00
——失败的代币价值
1.00——失败的代币价值
1.00——
失败的代币价值
0。
市场判定为 YES:
100 Yes tokens → $100 USDC.e
100 No tokens  → $0

何时兑换
兑换仅在
市场判定后
可用。一旦预言机报告结果:
获胜代币
可以按每个 $1.00 USDC.e 兑换
失败代币
价值 $0,无法获得赔付
你可以在判定后的任何时间兑换——没有截止日期。你的获胜代币将始终可以兑换。

判定的工作原理
市场的结束条件达成(事件发生、日期过去等)
UMA Adapter 预言机通过
reportPayouts()
报告结果
CTF 合约记录赔付向量
获胜代币的兑换功能变为可用

前置要求
在兑换之前:
市场必须已判定
——检查市场的
resolved
状态
持有获胜代币
——只有获胜的结果可以兑换
知道 condition ID
——兑换调用需要此参数

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
市场的 condition ID

indexSets
uint[]
要兑换的索引集合数组:
[1, 2]
兑换两种结果(只有获胜的有赔付)
兑换会销毁你在该条件下的全部代币余额——没有金额参数。

赔付机制
CTF 使用
赔付向量
来确定兑换价值:
结果
赔付向量
兑换
Yes 获胜
[1, 0]
Yes =
1
,
N
o
=
1, No =
1
,
N
o
=
0
No 获胜
[0, 1]
Yes =
0
,
N
o
=
0, No =
0
,
N
o
=
1
当你调用
redeemPositions()
时:
你的代币余额乘以赔付值
获胜代币被销毁
USDC.e 转移到你的钱包
失败代币也会被销毁,但赔付为 $0

下一步
CTF 概述
了解更多关于 Conditional Token Framework 的信息
判定流程
理解市场如何判定