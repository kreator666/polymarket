<!-- Source: https://docs.polymarket.com/cn -->

Polymarket 开发文档
基于全球最大的预测市场进行构建。为预测市场开发者提供 API、SDK 和工具。
开发者快速入门
几分钟内发出你的第一个 API 请求。了解 Polymarket 平台的基础知识，获取市场数据，下单交易，并兑换盈利仓位。
开始使用 →
TypeScript
Python
import
{
ClobClient
,
Side
}
from
"@polymarket/clob-client"
;
const
client
=
new
ClobClient
(
host
,
chainId
,
signer
,
creds
);
const
order
=
await
client
.
createAndPostOrder
(
{
tokenID
,
price:
0.50
,
size:
10
,
side:
Side
.
BUY
},
{
tickSize:
"0.01"
,
negRisk:
false
}
);
了解 Polymarket
学习基础知识，探索我们的 API，并开始在全球最大的预测市场上构建应用。
快速入门
设置你的开发环境，几分钟内完成第一个 API 调用。
核心概念
了解市场、事件、代币以及交易机制。
API 参考
浏览 REST 端点、WebSocket 数据流和身份验证。
SDK
官方 Python 和 TypeScript 库，加速你的开发。