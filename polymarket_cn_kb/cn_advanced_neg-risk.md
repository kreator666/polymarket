<!-- Source: https://docs.polymarket.com/cn/advanced/neg-risk -->

Negative Risk
是一种针对”只有一个结果能获胜”的多结果事件的机制。它通过
转换
操作将同一事件内所有结果的持仓关联起来，从而实现资金的高效利用。

运作方式
在标准的多结果事件中，每个市场是独立的。如果你想看空某个结果，必须买入该结果的 No 代币——但这些 No 代币与其他结果没有任何关联。
Negative Risk 改变了这一点。在 neg risk 事件中：
任何市场的
No 份额
都可以转换为
其他所有市场的各 1 份 Yes 份额
转换通过 Neg Risk Adapter 合约完成

示例
假设有一个事件：“谁将赢得 2024 年美国总统大选？“，包含三个结果：
结果
你的持仓
Trump
—
Harris
—
其他
1 No
通过 Negative Risk，那 1 份 “其他” 的 No 可以转换为：
结果
转换后
Trump
1 Yes
Harris
1 Yes
其他
—
这种方式非常高效，因为看空某一个结果在经济上等价于看多所有其他结果。

识别 Neg Risk 市场
Gamma API 在事件和市场上提供了
negRisk
布尔字段：
{
"id"
:
"123"
,
"title"
:
"Who will win the 2024 Presidential Election?"
,
"negRisk"
:
true
,
"markets"
: [
...
]
}
在 neg risk 市场下单时，必须在订单选项中指定：
const
response
=
await
client
.
createAndPostOrder
(
{
tokenID:
"TOKEN_ID"
,
price:
0.5
,
size:
100
,
side:
Side
.
BUY
,
},
{
tickSize:
"0.01"
,
negRisk:
true
,
// Required for neg risk markets
},
);

合约地址
Neg risk 市场使用与标准市场不同的合约：
Neg Risk Adapter 和 Neg Risk CTF Exchange 的地址详见
合约地址
。

增强型 Negative Risk
标准 Negative Risk 要求在市场创建时就确定所有结果。但有时新的结果会在交易开始后出现（例如，新候选人加入竞选）。
增强型 Negative Risk
通过以下方式解决这个问题：
结果类型
说明
命名结果
已知的结果（例如 “Trump”、“Harris”）
占位结果
预留的名额，后续可以明确指定（例如 “Person A”）
显式其他
涵盖所有未被明确命名的结果

占位结果的运作方式
事件上线时包含命名结果 + 占位结果 + “其他”
当新结果出现时，通过公告板明确某个占位结果的身份
随着占位结果被指定，“其他”的定义范围逐渐缩小

增强型 Neg Risk 的交易规则
只交易
命名结果
。占位结果在被命名之前或判定发生之前应忽略。Polymarket 界面不会显示未命名的结果。
如果判定时正确结果未被命名，市场判定为 “其他”
“其他”结果的定义会随着占位结果的指定而变化——避免直接交易

识别增强型 Neg Risk
当以下两个标志同时为 true 时，表示事件为增强型 neg risk：
{
"enableNegRisk"
:
true
,
"negRiskAugmented"
:
true
}
Gamma API 在事件和市场上提供了
negRisk
布尔字段，表示该事件是否使用 negative risk。对于增强型 neg risk 事件，还有一个
enableNegRisk
字段也为
true
。下单时，SDK 选项始终为
negRisk: true
/
neg_risk: True
，无论市场是标准还是增强型 neg risk。

技术细节

转换机制
转换操作是原子性的，通过 Neg Risk Adapter 完成：
你持有结果 A 的 1 个 No 代币
调用 adapter 的转换函数
你获得该事件中每个其他结果各 1 个 Yes 代币

相关资源
Neg Risk Adapter 源代码
Gamma API 文档

下一步
市场与事件
了解多市场事件的组织结构。
持仓与代币
了解拆分、合并和兑换等代币操作。