<!-- Source: https://docs.polymarket.com/cn/market-makers/liquidity-rewards -->

通过发布限价挂单，流动性提供者（maker）会自动获得参与 Polymarket 激励计划的资格。奖励每天在 UTC 午夜时分直接分发到 maker 地址。
该计划旨在：
促进所有市场的流动性
鼓励在市场整个生命周期中提供流动性
激励在市场中间价附近被动、平衡地报价
鼓励交易活动
阻止明显的剥削行为
该计划深受
dYdX 的流动性提供者奖励
启发。方法论本质上是 dYdX 方法的复制，并针对二元合约市场进行了调整——独立订单簿、无质押机制、修改的订单效用相对深度函数，以及按市场隔离的奖励金额。

方法论
流动性提供者根据一个公式获得奖励，该公式奖励市场参与度，提升双边深度（单边订单仍然计分），以及相对于规模截止调整后中间价更紧的价差。每个市场配置一个最大价差和最小规模截止，在此范围内的订单才会被考虑。奖励的平均值由每个参与者在市场 m 中的 Q
n
相对份额决定。

变量
Variable
Description
S
订单位置评分函数
v
与中间价的最大价差（以美分计）
s
与规模截止调整后中间价的价差
b
游戏内乘数
m
市场
m’
市场补充（即如果 m = YES，则为 NO）
n
交易者索引
u
样本索引
c
缩放因子（目前所有市场均为 3.0）
Q
ne
样本中第一个订单簿的总分
Q
no
样本中第二个订单簿的总分
Spread%
市场 m 中订单 n 与中间价的距离（基点或相对值）
BidSize
以份额计价的买单数量
AskSize
以份额计价的卖单数量

公式

1. 订单评分函数
基于调整后中间价和最小合格价差之间位置的订单二次评分规则：
S
(
v
,
s
)
=
(
v
−
s
v
)
2
⋅
b
S(v,s)= (\frac{v-s}{v})^2 \cdot b
S
(
v
,
s
)
=
(
v
v
−
s

)
2
⋅
b

2. 第一市场边分数
Q
o
n
e
=
S
(
v
,
S
p
r
e
a
d
m
1
)
⋅
B
i
d
S
i
z
e
m
1
+
S
(
v
,
S
p
r
e
a
d
m
2
)
⋅
B
i
d
S
i
z
e
m
2
+
…
Q_{one}= S(v,Spread_{m_1}) \cdot BidSize_{m_1} + S(v,Spread_{m_2}) \cdot BidSize_{m_2} + \dots
Q
o
n
e

=
S
(
v
,
Sp
re
a
d
m
1

)
⋅
B
i
d
S
i
z
e
m
1

+
S
(
v
,
Sp
re
a
d
m
2

)
⋅
B
i
d
S
i
z
e
m
2

+
…
+
S
(
v
,
S
p
r
e
a
d
m
1
′
)
⋅
A
s
k
S
i
z
e
m
1
′
+
S
(
v
,
S
p
r
e
a
d
m
2
′
)
⋅
A
s
k
S
i
z
e
m
2
′
+ S(v, Spread_{m^\prime_1}) \cdot AskSize_{m^\prime_1} + S(v, Spread_{m^\prime_2}) \cdot AskSize_{m^\prime_2}
+
S
(
v
,
Sp
re
a
d
m
1
′

)
⋅
A
s
k
S
i
z
e
m
1
′

+
S
(
v
,
Sp
re
a
d
m
2
′

)
⋅
A
s
k
S
i
z
e
m
2
′

3. 第二市场边分数
Q
t
w
o
=
S
(
v
,
S
p
r
e
a
d
m
1
)
⋅
A
s
k
S
i
z
e
m
1
+
S
(
v
,
S
p
r
e
a
d
m
2
)
⋅
A
s
k
S
i
z
e
m
2
+
…
Q_{two}= S(v,Spread_{m_1}) \cdot AskSize_{m_1} + S(v,Spread_{m_2}) \cdot AskSize_{m_2} + \dots
Q
tw
o

=
S
(
v
,
Sp
re
a
d
m
1

)
⋅
A
s
k
S
i
z
e
m
1

+
S
(
v
,
Sp
re
a
d
m
2

)
⋅
A
s
k
S
i
z
e
m
2

+
…
+
S
(
v
,
S
p
r
e
a
d
m
1
′
)
⋅
B
i
d
S
i
z
e
m
1
′
+
S
(
v
,
S
p
r
e
a
d
m
2
′
)
⋅
B
i
d
S
i
z
e
m
2
′
+ S(v, Spread_{m^\prime_1}) \cdot BidSize_{m^\prime_1} + S(v, Spread_{m^\prime_2}) \cdot BidSize_{m^\prime_2}
+
S
(
v
,
Sp
re
a
d
m
1
′

)
⋅
B
i
d
S
i
z
e
m
1
′

+
S
(
v
,
Sp
re
a
d
m
2
′

)
⋅
B
i
d
S
i
z
e
m
2
′

4. 最小分数
通过取 Q
ne
和 Q
no
的最小值来提升双边流动性，同时仍以降低的比率（除以 c）奖励单边流动性。
如果中间价在 [0.10, 0.90] 范围内
——单边流动性可以计分：
Q
min
⁡
=
max
⁡
(
min
⁡
(
Q
o
n
e
,
Q
t
w
o
)
,
max
⁡
(
Q
o
n
e
/
c
,
Q
t
w
o
/
c
)
)
Q_{\min} = \max(\min({Q_{one}, Q_{two}}), \max(Q_{one}/c, Q_{two}/c))
Q
m
i
n

=
max
(
min
(
Q
o
n
e

,
Q
tw
o

)
,
max
(
Q
o
n
e

/
c
,
Q
tw
o

/
c
))
如果中间价在 [0, 0.10) 或 (0.90, 1.0] 范围内
——流动性必须是双边的才能计分：
Q
min
⁡
=
min
⁡
(
Q
o
n
e
,
Q
t
w
o
)
Q_{\min} = \min({Q_{one}, Q_{two}})
Q
m
i
n

=
min
(
Q
o
n
e

,
Q
tw
o

)

5. 标准化分数
做市商的 Q
min
除以给定样本中所有做市商的 Q
min
总和：
Q
n
o
r
m
a
l
=
Q
m
i
n
∑
n
=
1
N
(
Q
m
i
n
)
n
Q_{normal} = \frac{Q_{min}}{\sum_{n=1}^{N}{(Q_{min})_n}}
Q
n
or
ma
l

=
∑
n
=
1
N

(
Q
min

)
n

Q
min

6. 时期分数
交易者在一个时期中所有样本的 Q
normal
总和：
Q
e
p
o
c
h
=
∑
u
=
1
10
,
080
(
Q
n
o
r
m
a
l
)
u
Q_{epoch} = \sum_{u=1}^{10,080}{(Q_{normal})_u}
Q
e
p
oc
h

=
∑
u
=
1
10
,
080

(
Q
n
or
ma
l

)
u

7. 最终分数
通过除以给定时期中所有做市商的 Q
epoch
总和来标准化 Q
epoch
。该值乘以市场可用奖励即可得到交易者的奖励：
Q
f
i
n
a
l
=
Q
e
p
o
c
h
∑
n
=
1
N
(
Q
e
p
o
c
h
)
n
Q_{final}=\frac{Q_{epoch}}{\sum_{n=1}^{N}{(Q_{epoch})_n}}
Q
f
ina
l

=
∑
n
=
1
N

(
Q
e
p
oc
h

)
n

Q
e
p
oc
h

实例演示
假设调整后的市场中间价为 0.50，m 和 m’ 的最大价差配置均为 3 美分。

步骤 2 - 第一边分数
交易者有以下未成交订单：
在 m 上以 0.49 价格买入 100Q（价差 = 1 美分）
在 m 上以 0.48 价格买入 200Q（价差 = 2 美分）
在 m’ 上以 0.51 价格卖出 100Q（价差 = 1 美分）
Q
n
e
=
(
(
3
−
1
)
3
)
2
⋅
100
+
(
(
3
−
2
)
3
)
2
⋅
200
+
(
(
3
−
1
)
3
)
2
⋅
100
Q_{ne} = \left( \frac{(3-1)}{3} \right)^2 \cdot 100 + \left( \frac{(3-2)}{3} \right)^2 \cdot 200 + \left( \frac{(3-1)}{3} \right)^2 \cdot 100
Q
n
e

=
(
3
(
3
−
1
)

)
2
⋅
100
+
(
3
(
3
−
2
)

)
2
⋅
200
+
(
3
(
3
−
1
)

)
2
⋅
100
Q
ne
使用随机采样每分钟计算一次。

步骤 3 - 第二边分数
同一交易者还有：
在 m 上以 0.485 价格买入 100Q（价差 = 1.5 美分）
在 m’ 上以 0.48 价格买入 100Q（价差 = 2 美分）
在 m’ 上以 0.505 价格卖出 200Q（价差 = 0.5 美分）
Q
n
o
=
(
(
3
−
1.5
)
3
)
2
⋅
100
+
(
(
3
−
2
)
3
)
2
⋅
100
+
(
(
3
−
.
5
)
3
)
2
⋅
200
Q_{no} = \left( \frac{(3-1.5)}{3} \right)^2 \cdot 100 + \left( \frac{(3-2)}{3} \right)^2 \cdot 100 + \left( \frac{(3-.5)}{3} \right)^2 \cdot 200
Q
n
o

=
(
3
(
3
−
1.5
)

)
2
⋅
100
+
(
3
(
3
−
2
)

)
2
⋅
100
+
(
3
(
3
−
.5
)

)
2
⋅
200
Q
no
使用随机采样每分钟计算一次。

步骤 4-7
取 Q
ne
和 Q
no
的最小值（如果中间价在 [0.10, 0.90] 范围内则进行单边调整）
对样本中的所有其他做市商进行标准化
对时期中的所有 10,080 个样本求和
再次标准化以获得最终奖励份额
最低奖励支付金额为
$1
；低于此金额的奖励将不会支付。
min_incentive_size
和
max_incentive_spread
都可以通过 CLOB API 和
Markets API
与完整的市场对象一起获取。时期的奖励分配也可以通过 Markets API 获取。

下一步
交易
订单输入和报价最佳实践
Maker 返利
在 15 分钟加密货币市场上赚取 USDC 返利