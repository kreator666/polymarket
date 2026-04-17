<!-- Source: https://docs.polymarket.com/cn/trading/matching-engine -->

Polymarket 撮合引擎会定期重启以进行维护和升级。本页介绍重启计划、如何检测和处理停机以及如何获取变更的提前通知。

重启计划
撮合引擎**每周二 7:00 AM ET（美东时间）**进行重启。在重启窗口期间，引擎暂时不可用——通常约
90 秒
。
详情
频率
每周
日期和时间
周二 7:00 AM ET
典型持续时间
约 90 秒
发生情况
订单撮合暂停，API 返回
425
可能会因关键更新或紧急修复而进行计划外重启。这些将尽可能提前通知。

公告
撮合引擎变更——计划重启、更新和维护窗口——会在发生
之前
在以下渠道公告：
Telegram
加入 Polymarket Trading APIs 频道获取实时公告。
Discord
加入 Polymarket Discord 的 #trading-apis 频道。
公告通常包括
变更内容
、
计划时间
和
预计停机窗口
。目标是尽可能提前约 2 天通知。

处理 HTTP 425
在重启窗口期间，CLOB API 在所有订单相关端点上返回
HTTP 425（Too Early）
。这告诉你的客户端撮合引擎正在重启，很快会恢复。

建议的重试策略
1
检测 425
当收到 HTTP
425
响应时，撮合引擎正在重启。不要将其视为永久错误。
2
退避并重试
等待并使用指数退避重试。从 1-2 秒开始，每次重试增加间隔。
3
恢复正常操作
一旦收到成功响应，引擎已恢复在线。恢复正常的订单流程。

代码示例
检查 CLOB API 响应的 HTTP 状态码，在收到
425
时重试：
TypeScript
Python
const
CLOB_HOST
=
"https://clob.polymarket.com"
;
async
function
postWithRetry
(
path
:
string
,
body
:
any
,
headers
:
Record
<
string
,
string
>) {
const
MAX_RETRIES
=
10
;
let
delay
=
1000
;
for
(
let
attempt
=
0
;
attempt
<
MAX_RETRIES
;
attempt
++
) {
const
response
=
await
fetch
(
`
${
CLOB_HOST
}${
path
}
`
, {
method:
"POST"
,
headers:
{
"Content-Type"
:
"application/json"
,
...
headers
},
body:
JSON
.
stringify
(
body
),
});
if
(
response
.
status
===
425
) {
console
.
log
(
`Engine restarting, retrying in
${
delay
/
1000
}
s...`
);
await
new
Promise
((
r
)
=>
setTimeout
(
r
,
delay
));
delay
=
Math
.
min
(
delay
*
2
,
30000
);
continue
;
}
return
response
;
}
throw
new
Error
(
"Engine restart exceeded maximum retry attempts"
);
}

最佳实践
订阅公告渠道
— 在重启发生前获得通知，以便做好准备
优雅处理 425
— 将其视为临时状况而非错误；你的重试逻辑应自动恢复
避免激进重试
— 引擎需要时间重新加载订单簿；快速重试不会加快速度，反而可能在引擎恢复后触发速率限制
记录重启事件
— 跟踪客户端遇到 425 的时间，与公告的维护窗口进行关联