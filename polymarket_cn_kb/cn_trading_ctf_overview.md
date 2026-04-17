<!-- Source: https://docs.polymarket.com/cn/trading/ctf/overview -->

Polymarket 上的所有结果都使用
Conditional Token Framework (CTF)
进行代币化，这是由 Gnosis 开发的开放标准。理解 CTF 操作可以实现高级交易策略、做市和直接智能合约交互。

什么是 CTF
Conditional Token Framework 创建代表预测市场结果的
ERC1155 代币
。每个二元市场有两种代币：
代币
兑换为
条件
Yes
$1.00 USDC.e
事件发生
No
$1.00 USDC.e
事件不发生
这些代币始终
完全抵押
——每对 Yes/No 代币都由锁定在 CTF 合约中的 $1.00 USDC.e 支持。

核心操作
CTF 提供三个基本操作：
Split
将 USDC.e 转换为 Yes + No 代币对
Merge
将 Yes + No 代币对转换回 USDC.e
Redeem
判定后将获胜代币兑换为 USDC.e

代币流转

代币标识符
每个结果代币都有一个唯一的
position ID
（也称为 token ID 或 asset ID）。这些是通过三个步骤在链上计算的：
getConditionId(oracle, questionId, outcomeSlotCount)
— oracle 是
UMA CTF Adapter
，
questionId
是 UMA ancillary data 的哈希，
outcomeSlotCount
对于二元市场是
2
getCollectionId(parentCollectionId, conditionId, indexSet)
—
parentCollectionId
对于顶级仓位是
bytes32(0)
，
indexSet
是位掩码（
0b01 = 1
表示第一个结果，
0b10 = 2
表示第二个）
getPositionId(collateralToken, collectionId)
— 将 USDC.e 地址与 collection 结合生成最终的 token ID
你可以通过 Markets API（Gamma API 上的
GET /markets
）或 Events API（Gamma API 上的
GET /events
）找到 token ID。
tokens
数组包含两个结果代币 ID。手动计算它们仅在直接智能合约集成时需要。

标准市场 vs Neg Risk 市场
Polymarket 有两种具有不同 CTF 配置的市场类型：
特性
标准市场
Neg Risk 市场
CTF 合约
ConditionalTokens
ConditionalTokens
Exchange 合约
CTF Exchange
Neg Risk CTF Exchange
多结果
独立市场
通过转换关联
negRisk
标志
false
true
对于 neg risk 市场，额外的
转换
操作允许将一个 No 代币兑换为所有其他结果中的 Yes 代币。详见
Negative Risk Markets
。

合约地址
所有 Polymarket 智能合约地址详见
合约地址
。

资源
CTF Source Code
Gnosis Conditional Tokens 智能合约
Code Examples
链上操作的 Python 和 TypeScript 示例

下一步
Split Tokens
从 USDC.e 创建结果代币对
Merge Tokens
将代币对转换回 USDC.e
Redeem Tokens
判定后领取奖金