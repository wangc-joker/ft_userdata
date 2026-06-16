# DualTrend 旧策略 Short Tag 与双顺逻辑借鉴分析

日期：2026-06-16

## 1. 本次做了什么

目标：检查旧策略里的三个 short tag 是否值得迁移到当前 DualTrend Short 主线：

1. `short_1h_center`
2. `short_1d_center_compression`
3. `short_reversal_breakdown`

同时检查旧版“双顺”框架里哪些设计值得借鉴。

参考源码：

| 文件 | 作用 |
|---|---|
| `D:\test\ft_userdata\user_data\strategies\signals\short\entries.py` | 旧 short tag 入场挂载 |
| `D:\test\ft_userdata\user_data\strategies\core\indicators\structure.py` | 旧双顺结构指标 |
| `D:\test\ft_userdata\user_data\strategies\signals\reversal.py` | reversal long/short 逻辑 |
| `D:\test\ft_userdata\user_data\strategies\signals\exit_rules.py` | 旧结构退出 |
| `D:\test\ft_userdata\user_data\strategies\archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeStrategy.py` | 市场状态过滤/仓位权重 |
| `D:\test\ft_userdata\user_data\strategies\archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy.py` | `short_1h_center` 市场状态压仓 |
| `D:\test\ft_userdata\user_data\strategies\archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanEarlyFailStrategy.py` | 旧版早期失败退出 |

## 2. 旧回测表现

使用旧策略 `Top9RegimeMainReversal216Strategy` 已有回测结果。

### max_open_trades = 2

| tag | Trades | Profit | PF | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|
| `short_1h_center` | 106 | +622.22U | 1.93 | 39.6% | 0.63% |
| `short_1d_center_compression` | 22 | +324.81U | 2.15 | 36.4% | 2.00% |
| `short_reversal_breakdown` | 10 | +281.44U | 12.01 | 50.0% | 2.62% |

### max_open_trades = 3

| tag | Trades | Profit | PF | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|
| `short_1h_center` | 118 | +504.00U | 2.17 | 40.7% | 0.81% |
| `short_1d_center_compression` | 26 | +275.96U | 2.49 | 34.6% | 1.83% |
| `short_reversal_breakdown` | 9 | +170.71U | 12.19 | 55.6% | 2.94% |

初步判断：

| tag | 是否值得拿 | 优先级 |
|---|---|---|
| `short_reversal_breakdown` | 值得单独验证 | 高 |
| `short_1d_center_compression` | 值得作为低频大级别补充 | 中高 |
| `short_1h_center` | 不建议原样搬，适合借鉴过滤和形态思想 | 中 |

## 3. `short_1h_center`

### 3.1 逻辑结构

旧逻辑：

```text
daily_short_context = restart_ready_short_1d
+ center_breakout_short
= short_1h_center
```

`center_breakout_short` 来自 1H 结构：

```text
restart_ready_short
+ center_down
+ range_contracting
+ near_low_compression
+ market_center 下移
+ close 跌破 recent_low
+ close < market_center
+ volume_expansion
```

这是一种“日线空头背景 + 1H 中枢下破”的顺势形态。

### 3.2 优点

1. 交易数量最多，是旧 short 收益的主要来源之一；
2. 和当前 DualTrend 的 `short_pullback_restart` 有相似性，都是顺势再启动；
3. 旧逻辑里 `market_center` 比当前 `center_down` 更平滑，能减少单根 K 噪音；
4. 对 ZEC、BTC、SOL、BNB 表现较好。

旧 max2 pair 拆解：

| pair | Trades | Profit |
|---|---:|---:|
| ZEC | 22 | +225.56U |
| BTC | 8 | +152.29U |
| SOL | 12 | +116.72U |
| BNB | 8 | +98.59U |
| XRP | 14 | +26.70U |
| ADA | 20 | +22.22U |
| ETH | 8 | +12.96U |
| DOGE | 13 | -28.19U |

### 3.3 问题

这个 tag 年份稳定性一般：

| year | Trades | Profit |
|---|---:|---:|
| 2023 | 10 | -28.66U |
| 2024 | 32 | +182.66U |
| 2025 | 38 | -28.31U |
| 2026 | 26 | +496.53U |

旧代码后续已经对它做了多次修补：

1. 牛市下压低 `short_1h_center` 仓位；
2. 非熊市压仓；
3. DOGE / ADA / XRP 单独降权；
4. 增加 early-fail exit。

这说明它不是“裸信号很稳”，而是需要市场状态治理。

### 3.4 是否迁移

不建议直接加入当前 Short V1。

更好的借鉴方式：

1. 借 `market_center` 定义，替代或补充当前 `center_down`；
2. 借 `range_contracting + near_low_compression + volume_expansion` 的组合；
3. 作为当前 `short_pullback_restart` 的附加质量分，而不是新 tag 直接开仓；
4. 如果单独验证，必须加 BTC/市场状态过滤和 early-fail。

## 4. `short_1d_center_compression`

### 4.1 逻辑结构

旧逻辑：

```text
daily_short_context = restart_ready_short_1d
+ center_breakout_short_1d
+ rsi_1d < daily_short_rsi
+ daily_short_signal 首次触发
= short_1d_center_compression
```

这和刚验证过的 `long_1d_center_compression` 是镜像结构。

### 4.2 优点

1. 低频；
2. 单笔平均收益高；
3. PF 在 max2/max3 下都高于 `short_1h_center`；
4. 更符合“双顺”的大级别顺势思想。

旧 max2 pair 拆解：

| pair | Trades | Profit |
|---|---:|---:|
| SOL | 2 | +195.62U |
| BTC | 3 | +162.05U |
| XRP | 1 | +72.28U |
| ADA | 3 | +19.27U |
| BNB | 5 | +8.85U |
| ETH | 2 | -20.87U |
| DOGE | 2 | -33.97U |
| TRX | 4 | -78.42U |

### 4.3 问题

年份上并非完全稳定：

| year | Trades | Profit |
|---|---:|---:|
| 2023 | 6 | +55.84U |
| 2024 | 4 | +19.16U |
| 2025 | 10 | +319.88U |
| 2026 | 2 | -70.07U |

问题主要是：

1. 样本少；
2. 对币种敏感；
3. TRX / DOGE / ETH 表现差；
4. 日线信号确认慢，可能在局部反弹后才进场。

### 4.4 是否迁移

值得作为 `ShortDailyCenterV1` 单独验证，不建议直接并入当前 Short V1。

建议验证方式：

```text
ShortDailyCenterV1
只启用 short_1d_center_compression
使用结构止损/结构退出
测试 Top9 / 当前 13 币池 / 去掉 DOGE-TRX-ETH
测试 max_open_trades = 1 / 2
```

## 5. `short_reversal_breakdown`

### 5.1 逻辑结构

旧 reversal short 不是普通顺势突破，而是：

```text
日线反弹衰竭背景
+ 1H 从顶部脱离
+ 低位小平台再分配
+ 放量跌破 72 根 low
= short_reversal_breakdown
```

核心条件包括：

```text
reversal_daily_short_background_ok
+ reversal_short_regime_ok
+ reversal_short_redistribution_ok
+ reversal_short_breakdown_candle_ok
+ reversal_short_risk_filter_ok
```

### 5.2 优点

旧回测里这是质量最高的 short tag：

| 口径 | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| max2 | 10 | +281.44U | 12.01 | 50.0% |
| max3 | 9 | +170.71U | 12.19 | 55.6% |

pair 贡献集中：

| pair | Trades | Profit |
|---|---:|---:|
| ZEC | 4 | +97.56U |
| ADA | 5 | +95.01U |
| XRP | 1 | +88.87U |

年份也比较连贯：

| year | Trades | Profit |
|---|---:|---:|
| 2024 | 4 | +88.85U |
| 2025 | 3 | +172.56U |
| 2026 | 3 | +20.02U |

### 5.3 问题

1. 样本极少；
2. pair 集中，泛化未知；
3. 逻辑更像“衰竭后破位”，不是当前 DualTrend 主线的纯顺势；
4. 旧策略里还给 `short_reversal_breakdown` 做了 1.12 仓位放大，这可能放大了历史收益。

### 5.4 是否迁移

最值得先单独验证。

原因：

1. 和当前 `short_pullback_restart` 重叠较少；
2. 可能补充“反弹衰竭后继续下跌”的场景；
3. 交易少，不太会污染主策略；
4. 如果失效，也容易剔除。

建议做成：

```text
DualTrendShortReversalBreakdownV1
只启用 short_reversal_breakdown
不加仓位放大
先测试旧 pair：ZEC/ADA/XRP
再测试当前 13 币池
再测试和 Short Pullback 合并
```

## 6. 原双顺里值得借鉴的东西

### 6.1 `market_center`

旧双顺用：

```text
market_center = typical_price rolling mean
center_up/down = market_center 与前值比较
```

当前 DualTrend Short V1 的 `center_down` 更像半区 high/close 均值下移：

```text
high_max_last_half < high_max_first_half
close_mean_last_half < close_mean_first_half
```

两者都合理，但旧 `market_center` 更平滑，适合作为假突破过滤。

建议借鉴：

```text
当前 center_down 保留
新增 old_center_down / market_center_slope
要求二者至少一个成立，或把 old_center_down 作为质量加分
```

### 6.2 大级别 tag 走大级别退出

旧双顺根据 tag 是否包含 `_1d_` 选择退出作用域：

```text
_1d_ tag -> structure_stop_short_1d / center_up_1d / uptrend_1d
1h tag -> structure_stop_short / center_up / ema_fast
```

这个非常值得借。

当前 Short V1 主要是：

```text
入场止损 + stale exit + 4H trend flip
```

但如果未来加入 `short_1d_center_compression`，就应该走日线结构退出，而不是当前 72h/120h 的短周期 stale exit。

### 6.3 市场状态过滤/仓位权重

旧逻辑有：

```text
bull: short_1h_center 降权或过滤
bear: short_1h_center / short_1d_center_compression 加权
range: 降权
```

这个思想值得借，但不要照搬旧的 stake multiplier。

当前 DualTrend 更适合变成硬过滤：

```text
非 BTC short:
BTC 4H 不允许强上升
如果 pair/market 日线 bull，禁止 short_1h_center 类信号
如果 pair 日线 bear，允许日线 center short
```

### 6.4 recent_trade_multiplier

旧代码根据最近同 tag / 同 pair 的亏损情况降低仓位。

优点：

1. 能抑制连续失效；
2. 对高频 tag 有帮助。

缺点：

1. 实盘和回测状态依赖更复杂；
2. 对当前风险预算版 DualTrend 来说，会增加归因难度。

建议暂不迁移。

### 6.5 pair-specific trim

旧代码对 DOGE / ADA / XRP / ZEC 等做过 pair-specific 修剪。

这类东西可以作为最终 dry-run 后的治理层，但不适合作为 V1/V2 核心逻辑。

建议：

```text
先用 pair 拆解决定是否剔除
不要一开始写进策略逻辑
```

### 6.6 early-fail exit

旧版对 `short_1h_center` 有早期失败退出：

```text
short_1h_center
+ current_profit < -0.5%
+ 1H close > ema_fast
+ center_up
+ rsi > 52
+ 日线空头动能丢失
= early_fail_short_1h
```

这个思想非常适合当前 DualTrend 的假突破控制。

建议作为后续 Short V2 测试项，而不是立即加入主策略。

## 7. 和当前 DualTrend Short V1 的关系

当前 Short V1 已经有两个主线：

| 当前 tag | 含义 |
|---|---|
| `short_pullback_restart` | 4H 下跌趋势 + 1H 回抽后再跌破 |
| `short_compression_breakdown` | 4H 下跌趋势 + 1H 压缩后破位 |

旧 tag 与当前 tag 的关系：

| 旧 tag | 和当前关系 | 建议 |
|---|---|---|
| `short_1h_center` | 与 `short_pullback_restart` 高度相近 | 不直接加，借过滤 |
| `short_1d_center_compression` | 当前没有对应日线级别 short | 单独验证 |
| `short_reversal_breakdown` | 当前没有对应衰竭破位 | 优先单独验证 |

## 8. 推荐执行顺序

### 第一优先级

实现验证版：

```text
DualTrendShortReversalBreakdownV1
```

验证：

1. 旧 pair：ZEC/ADA/XRP；
2. 当前 13 币池；
3. 全样本与近期；
4. 成本压力；
5. 与 Short Pullback Only 合并。

### 第二优先级

实现验证版：

```text
DualTrendShortDailyCenterV1
```

只启用：

```text
short_1d_center_compression
```

测试结构退出，不先做固定 ROI。

### 第三优先级

对当前 Short V1 加质量对照测试，不改核心入场：

```text
market_center_slope filter
early_fail_short filter
daily bull hard block for 1h short
```

## 9. 当前结论

1. `short_reversal_breakdown` 最值得拿过来先验证；
2. `short_1d_center_compression` 值得作为大级别 short 补充；
3. `short_1h_center` 不建议原样迁移，更适合借鉴它的 `market_center` 和 early-fail 设计；
4. 旧双顺最值得继承的是“多周期作用域”：
   - 1H 信号用 1H 结构退出；
   - 1D 信号用 1D 结构退出；
   - 不同 tag 分开统计，不混在一个标签里。

