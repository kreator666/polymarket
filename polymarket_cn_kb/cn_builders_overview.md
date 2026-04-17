<!-- Source: https://docs.polymarket.com/cn/builders/overview -->

构建者
是指将用户订单路由到 Polymarket 的个人、团体或组织。如果你创建了一个允许用户通过你的系统在 Polymarket 上交易的平台,这个计划就是为你准备的。

计划权益
免 Gas 交易
通过我们的 Relayer,所有链上操作都无需 Gas 费
订单归因
获得订单归属,在构建者排行榜上竞争奖励
收益分成
从你路由的订单中赚取手续费分成

你将获得
权益
说明
Relayer 访问权限
免 Gas 的钱包部署、授权、订单执行和 CTF 操作
交易量追踪
所有订单都归属到你的构建者资料
每周奖励
基于交易量的 USDC 奖励计划(已认证+)
排行榜
在
builders.polymarket.com
上公开展示
技术支持
Telegram 频道和工程支持(已认证+)
EOA 钱包没有 Relayer 访问权限。直接从 EOA 交易的用户需要自己支付 Gas 费。

工作原理
1
用户下单
用户通过你的应用程序下单。
2
签署请求
你的应用使用 Builder API 凭证签署请求。
3
提交到 CLOB
订单被提交到 Polymarket 的 CLOB,并带有归因头信息。
4
执行交易
Polymarket 撮合订单并承担链上操作的 Gas 费。
5
交易量归因
交易量被计入你的构建者账户。

开始使用
1
创建构建者资料
前往
polymarket.com/settings?tab=builder
生成你的 API 密钥。
2
配置归因
设置你的 CLOB 客户端,在每个订单中包含构建者认证头信息。
3
启用免 Gas 交易
使用 Relayer Client 实现免 Gas 的钱包部署和链上操作。
4
跟踪表现
在
构建者排行榜
上监控你的交易量。

SDK 与库
CLOB Client (TypeScript)
下单并进行构建者归因
CLOB Client (Python)
下单并进行构建者归因
Relayer Client (TypeScript)
免 Gas 的链上交易
Relayer Client (Python)
免 Gas 的链上交易
CLOB Client (Rust)
下单并进行构建者归因
Signing SDK (TypeScript)
签署构建者认证头信息
Signing SDK (Python)
签署构建者认证头信息

示例
这些开源演示应用展示了如何集成 Polymarket 的 CLOB Client 和 Builder Relayer Client,实现带构建者订单归因的免 Gas 交易。
身份认证
支持多种钱包提供商
免 Gas 交易
支持 Safe 和 Proxy 钱包
完整集成
订单、仓位、CTF 操作

Safe 钱包示例
为你的用户部署 Gnosis Safe 钱包:
wagmi + Safe
MetaMask、Phantom、Rabby 和其他浏览器钱包
Privy + Safe
Privy 嵌入式钱包
Magic Link + Safe
Magic Link 邮箱/社交登录认证
Turnkey + Safe
Turnkey 嵌入式钱包

Proxy 钱包示例
针对来自 Polymarket.com 的现有 Magic Link 用户:
Magic Link + Proxy
为 Polymarket.com Magic 用户自动部署 Proxy 钱包

每个演示涵盖的内容
身份认证
钱包操作
交易
通过钱包提供商进行用户登录
用户 API 凭证派生(L2 认证)
使用远程签名配置构建者
Safe 和 Proxy 钱包的签名类型
通过 Relayer 部署 Safe 钱包
批量代币授权(USDC.e + 结果代币)
CTF 操作(拆分、合并、兑换)
交易监控
CLOB 客户端初始化
带构建者归因的订单下单
仓位和订单管理
通过 Gamma API 发现市场

下一步
获取 API 密钥
创建和管理你的 Builder API 凭证。
了解等级
了解速率限制以及如何升级。
订单归因
配置你的客户端,将交易归属到你的账户。
免 Gas 指南
为你的用户设置免 Gas 交易。