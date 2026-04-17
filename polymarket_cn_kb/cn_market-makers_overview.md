<!-- Source: https://docs.polymarket.com/cn/market-makers/overview -->

Polymarket 上的 Market Maker(做市商)是指通过持续发布买单和卖单来为预测市场提供流动性的交易者。通过设置价差,做市商让其他用户能够高效交易,同时赚取价差作为承担风险的补偿。
做市商对 Polymarket 生态系统至关重要——他们为市场提供流动性、收紧价差以改善用户体验、通过持续报价实现价格发现,并吸收来自散户和机构用户的交易流。
不是 Market Maker?
如果你正在构建为用户路由订单的应用程序,请查看
Builder Program
。

入门指南
1
完成设置
部署钱包,充值 USDC.e,并设置代币授权。请参阅
入门指南
。
2
连接数据源
使用 WebSocket 获取实时订单簿更新,使用 Gamma API 获取市场元数据。请参阅
市场数据
。
3
开始报价
通过 CLOB REST API 发布订单。请参阅
交易
。

快速参考
操作
工具
文档
充值 USDC.e
Bridge API
Bridge
授权代币
Relayer Client
入门指南
发布限价单
CLOB REST API
创建订单
监控订单簿
WebSocket
WebSocket
将 USDC.e 拆分为代币
CTF / Relayer
库存管理
将代币合并为 USDC.e
CTF / Relayer
库存管理

本节内容
入门指南
充值、代币授权、钱包部署、API 密钥
交易
报价最佳实践、策略和风险控制
库存管理
拆分、合并和兑换结果代币
流动性奖励
通过提供流动性赚取奖励

风险提示
注意价差管理——如果你的买入价高于卖出价(即”负价差”或”交叉市场”),每次成交都会亏损。提交报价前务必验证价格。

支持
如需做市商入驻和支持,请联系
support@polymarket.com
。