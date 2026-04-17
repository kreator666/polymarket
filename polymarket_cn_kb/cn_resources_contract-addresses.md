<!-- Source: https://docs.polymarket.com/cn/resources/contract-addresses -->

所有 Polymarket 合约部署在
Polygon 主网
（Chain ID: 137）上。本页是平台所有合约地址的唯一权威来源。

核心交易合约
合约
地址
说明
CTF Exchange
0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E
标准市场的订单撮合和结算
Neg Risk CTF Exchange
0xC5d563A36AE78145C45a50134d48A1215220f80a
Neg risk
（多结果）市场的订单撮合
Neg Risk Adapter
0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296
Neg risk 市场中 No 代币的转换
Conditional Tokens (CTF)
0x4D97DCd97eC945f40cF65F87097ACe5EA0476045
ERC1155 代币存储——拆分、合并和兑换操作

代币合约
合约
地址
说明
USDC.e (Bridged USDC)
0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
所有 Polymarket 交易使用的抵押代币（6 位小数）

钱包工厂合约
合约
地址
说明
Gnosis Safe Factory
0xaacfeea03eb1561c4e67d661e40682bd20e3541b
部署 Safe 钱包
Polymarket Proxy Factory
0xaB45c5A4B0c941a2F231C04C3f49182e1A254052
部署代理钱包

判定合约
合约
地址
说明
UMA Adapter
0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74
连接 Polymarket 和 UMA Optimistic Oracle 的适配器
UMA Optimistic Oracle
0xCB1822859cEF82Cd2Eb4E6276C7916e692995130
处理市场判定提案和争议

流动性
合约
地址
说明
Uniswap v3 USDC.e/USDC Pool
0xd36ec33c8bed5a9f7b6630855f1533455b98a418
提现时用于 USDC.e 和 USDC 之间的转换

源代码
CTF Exchange
订单撮合和结算合约
Conditional Tokens
Gnosis Conditional Token Framework (ERC1155)

代码中使用
TypeScript
Python
const
ADDRESSES
=
{
USDC_E:
"0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
,
CTF:
"0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
,
CTF_EXCHANGE:
"0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
,
NEG_RISK_CTF_EXCHANGE:
"0xC5d563A36AE78145C45a50134d48A1215220f80a"
,
};