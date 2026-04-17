<!-- Source: https://docs.polymarket.com/cn/market-data/fetching-markets -->

事件和市场接口均支持分页。详情请参阅
分页
部分。
获取市场数据有三种主要策略，各自适合不同的使用场景：
按 Slug 查询
— 适合获取已知的特定市场或事件
按标签查询
— 适合按分类或体育项目筛选市场
通过事件接口
— 获取所有活跃市场的最高效方式

按 Slug 查询
**适用场景：**需要获取你已知的特定市场或事件。
获取单个市场或事件的最佳方式是使用其唯一的 slug 标识符。slug 可以直接在 Polymarket 前端的 URL 中找到。

如何提取 Slug
从任意 Polymarket URL 中，slug 是
/event/
后面的路径段：
https://polymarket.com/event/fed-decision-in-october
↑
Slug: fed-decision-in-october

示例
# 通过 slug 获取事件（查询参数方式）
curl
"https://gamma-api.polymarket.com/events?slug=fed-decision-in-october"
# 或使用路径接口
curl
"https://gamma-api.polymarket.com/events/slug/fed-decision-in-october"
# 通过 slug 获取市场（查询参数方式）
curl
"https://gamma-api.polymarket.com/markets?slug=fed-decision-in-october"
# 或使用路径接口
curl
"https://gamma-api.polymarket.com/markets/slug/fed-decision-in-october"

按标签查询
**适用场景：**需要按分类、体育项目或主题筛选市场。
标签提供了对市场进行分类和筛选的方式。你可以先发现可用标签，然后使用它们进行筛选。

查看可用标签
通用标签：
GET /tags
（Gamma API）
体育标签和元数据：
GET /sports
（Gamma API）
/sports
接口返回体育项目的元数据，包括标签 ID、图片、判定来源和系列信息。

按标签筛选
获取标签 ID 后，在事件和市场接口中使用
tag_id
参数：
# 获取特定标签的事件
curl
"https://gamma-api.polymarket.com/events?tag_id=100381&limit=10&active=true&closed=false"

其他标签筛选选项
你还可以：
使用
related_tags=true
包含关联标签的市场
使用
exclude_tag_id
排除特定标签
# 包含关联标签
curl
"https://gamma-api.polymarket.com/events?tag_id=100381&related_tags=true&active=true&closed=false"

获取所有活跃市场
**适用场景：**需要获取所有可用的活跃市场，通常用于综合分析或市场发现。
最高效的方法是使用事件接口加上
active=true&closed=false
，因为事件包含其关联的市场。
curl
"https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100"

关键参数
参数
说明
order
排序字段（
volume_24hr
、
volume
、
liquidity
、
start_date
、
end_date
、
competitive
、
closed_time
）
ascending
排序方向（
true
为升序，
false
为降序），默认：
false
active
按活跃状态筛选（
true
为当前可交易的事件）
closed
按已关闭状态筛选，默认：
false
limit
每页返回的结果数
offset
分页跳过的结果数
# 获取交易量最高的活跃事件
curl
"https://gamma-api.polymarket.com/events?active=true&closed=false&order=volume_24hr&ascending=false&limit=100"

分页
所有列表接口都支持通过
limit
和
offset
参数进行分页：
# 第 1 页：前 50 条结果
curl
"https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50&offset=0"
# 第 2 页：接下来 50 条结果
curl
"https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50&offset=50"
# 第 3 页：再接下来 50 条结果
curl
"https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50&offset=100"

最佳实践
**查询单个市场：**使用 slug 方式直接查找
**按分类浏览：**使用标签筛选以减少 API 调用次数
**完整的市场发现：**使用事件接口配合分页
获取活跃市场时
始终加上
active=true
。
closed
参数现在默认为
false
，已关闭的市场会被自动排除——仅在需要历史数据时传入
closed=true
优先使用事件接口
——事件包含其关联市场，可以减少 API 调用次数

下一步
API 参考
完整的接口文档，包含参数和响应结构。