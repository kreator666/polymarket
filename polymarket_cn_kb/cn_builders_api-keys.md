<!-- Source: https://docs.polymarket.com/cn/builders/api-keys -->

Builder API keys 用于验证你的应用程序与 Polymarket relayer 的连接,并启用订单归因。你需要这些凭证来访问免 Gas 交易和追踪交易量。

访问你的 Builder 个人资料
1
直接链接
前往
polymarket.com/settings?tab=builder
2
从菜单进入
点击你的头像 → 选择 “Builders”

创建 API Keys
在你个人资料的
Builder Keys
部分:
点击
”+ Create New”
生成新的 API key
立即复制全部三个值
— secret 和 passphrase 只会显示一次
将它们安全地存储在你的密钥管理器或环境变量中
每个 API key 包含三个组成部分:
Component
Description
Example
key
你的 builder 账户的公开标识符
abc123-def456-...
secret
用于签名请求的密钥
base64-encoded-secret
passphrase
额外的身份验证值
your-passphrase
secret
和
passphrase
只在创建时显示一次。如果你丢失了它们,需要生成新的 key。

管理 Keys
为不同环境创建独立的 keys:
Environment
Purpose
Development
测试和本地开发
Staging
预生产环境测试
Production
实盘交易

个人资料设置
你的 builder 个人资料包含可自定义的设置:
Setting
Description
Profile Picture
显示在
Builder Leaderboard
上
Builder Name
排行榜上显示的公开名称
Builder Address
你的唯一 builder 标识符(只读)
Current Tier
你的速率限制等级: Unverified、Verified 或 Partner

环境变量
将你的凭证存储为环境变量:
Bash
TypeScript
Python
.env
POLY_BUILDER_API_KEY
=
your-api-key
POLY_BUILDER_SECRET
=
your-secret
POLY_BUILDER_PASSPHRASE
=
your-passphrase
import
{
BuilderApiKeyCreds
}
from
"@polymarket/builder-signing-sdk"
;
const
builderCreds
:
BuilderApiKeyCreds
=
{
key:
process
.
env
.
POLY_BUILDER_API_KEY
!
,
secret:
process
.
env
.
POLY_BUILDER_SECRET
!
,
passphrase:
process
.
env
.
POLY_BUILDER_PASSPHRASE
!
,
};
import
os
from
py_builder_signing_sdk
import
BuilderApiKeyCreds
builder_creds
=
BuilderApiKeyCreds(
key
=
os.environ[
"POLY_BUILDER_API_KEY"
],
secret
=
os.environ[
"POLY_BUILDER_SECRET"
],
passphrase
=
os.environ[
"POLY_BUILDER_PASSPHRASE"
],
)

安全最佳实践
Practice
Description
绝不提交凭证
使用
.gitignore
排除
.env
文件
使用环境变量
从环境变量加载凭证,而不是硬编码字符串
使用密钥管理器
生产环境使用 AWS Secrets Manager、HashiCorp Vault 等
分离环境
为开发、预发布和生产环境使用不同的 keys
监控使用情况
检查排行榜是否有异常的交易量变化
绝不要在客户端代码中暴露 Builder API 凭证。
你的 secret 和 passphrase 必须保留在服务器端。

故障排查
超出速率限制
原因:
你已超出所在等级的每日交易限制。
解决方案:
等待每日限制重置
联系 Polymarket
升级你的等级
丢失 secret 或 passphrase
原因:
secret 和 passphrase 只在创建时显示一次。
解决方案:
创建新的 API key。你无法恢复原始值。

后续步骤
归因订单
配置你的客户端以将交易归因到你的账户。
了解等级
了解速率限制以及如何升级。