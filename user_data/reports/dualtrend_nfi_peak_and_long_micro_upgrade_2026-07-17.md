# DualTrend NFI 退出借鉴与 Long Micro 升级实验

> **失效说明（2026-07-20）：** 本报告的 LongMicro、Micro 仓位缩放及 Top20 收益包含参数名碰撞：扩展 mixin 的 `long_breakout_buffer=0.001` 意外覆盖了父级日线多头的 `0.009`。因此 `+216.62%`、`+281.17%`、`+200.99%`、`+253.85%` 及相关缩放比较不可再作为候选证据。参数隔离后的权威结果见 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md) 和 `dualtrend_long_micro_parameter_collision_audit_2026-07-20.md`。NFI 方向性结论与历史实验记录继续保留。

日期：2026-07-17

## 目标与口径

在稳定对照 `DualTrendPyramidSecondAdd20V1Strategy` 上验证两条升级方向：

1. 参考 `D:\test\NostalgiaForInfinityX7.py` 的 max-profit / pullback 分层退出，减少强趋势盈利回吐。
2. 对已发现的稀有非深回踩强实体多头做仓位和跨窗口验证，判断它是否仍会挤压空头主引擎。

统一主口径为 Positive13、`max_open_trades=3`、初始 1000 USDT、`stake_amount=unlimited`、1h + 5m detail、启用 protections。SecondAdd20 三年对照为 `314 笔 / +199.22% / PF 2.682 / MaxDD 4.82%`。

## NFI 退出实验

### 峰值追踪锁盈

只针对 `short_pullback_restart`，在峰值达到 `+5%/+6%` 后按固定回撤距离抬高止损：

| 规则 | 三年收益 | PF | 结论 |
|---|---:|---:|---|
| 峰值 5%，回撤 3.0% | +176.20% | 2.53 | 淘汰 |
| 峰值 5%，回撤 2.5% | +173.20% | 2.51 | 淘汰 |
| 峰值 6%，回撤 2.5% | +176.79% | 2.55 | 淘汰 |
| 5%/7%/9% 分层 | +174.92% | 2.53 | 淘汰 |

这些规则确实减少了部分账面回吐，但也过早切断原本能走到 ROI 或部分止盈的赢家，组合损失明显。

### 峰值回撤加反转确认

进一步要求峰值达到 `+7%/+8%`、回撤 4%，并出现 6h 上涨及价格重回 EMA20，才退出空头。两版三年均约为 `314 笔 / +197.00% / PF 2.67 / MaxDD 4.82%`，只触发 2 笔，仍未超过对照。

对原 `long_1d_center_compression` 做同类反转退出也失败：

| 规则 | Trades | 三年收益 | PF | MaxDD |
|---|---:|---:|---:|---:|
| 峰值 5%，回撤 3% | 315 | +185.34% | 2.61 | 9.78% |
| 峰值 7%，回撤 4% | 314 | +185.18% | 2.61 | 5.28% |

结论：只借鉴 NFI 的研究思想，不移植其峰值退出形态。DualTrend 当前退出链更适合这批趋势单。

原始归档位于：

- `user_data/analysis/runner_peak_trail_2026-07-17/`
- `user_data/analysis/long_peak_reversal_2026-07-17/`

失败实验类已从正式策略文件删除，避免被误当候选；原始 zip 和本文继续保留实验记录。

## Long Micro 仓位梯度

Micro 只允许精确 tag `long_pullback_restart_1h_body`，排除 `_deep_body` 和其他 1h 多头。三年仓位梯度：

| Micro 仓位比例 | Trades | Profit | PF | MaxDD |
|---|---:|---:|---:|---:|
| 25% | 325 | +208.33% | 2.679 | 5.68% |
| 50% | 325 | +210.90% | 2.679 | 5.68% |
| 75% | 325 | +214.80% | 2.687 | 5.68% |
| 100% | 325 | +216.62% | 2.687 | 5.68% |

收益随仓位单调提高，降低仓位没有换来可见的回撤改善，因此采用完整风险仓位。临时仓位测试类已删除。

## 跨窗口验证

| 样本 | SecondAdd20 | Long Micro | PF | MaxDD | 判断 |
|---|---:|---:|---:|---:|---|
| 三年 | 314 / +199.22% | 325 / +216.62% | 2.687 | 5.68% | 收益 +17.40pct，回撤 +0.86pct |
| 近一年 | 123 / +68.02% | 128 / +76.63% | 3.473 | 4.02% | 收益提高且回撤下降 |
| 压力期 | 15 / +5.11% | 16 / +5.13% | 3.083 | 1.75% | 基本持平，无额外压力损伤 |
| 五年 | 477 / +261.73% | 490 / +281.17% | 2.420 | 5.68% | 收益 +19.44pct，回撤 +0.88pct |

五年 Long Micro 净利润 `+2811.71 USDT`。其中 long `+746.40 USDT`、short `+2065.32 USDT`；SecondAdd20 分别为 long `+613.96`、short `+2003.32 USDT`。因此这次扩展没有在五年结果中挤压空头利润。

Micro tag 自身三年为 7 笔、`+62.19 USDT`、PF `3.327`；五年仍为 7 笔、`+75.60 USDT`、PF `3.376`。组合成交比对照多 13 笔，说明共享槽位和资金路径改变了其他成交，不能把总差额只归因于 tag 自身利润。

五年归档中的配置快照已核对为 Positive13、`max_open_trades=3`、1000 USDT、无限 stake；有效窗口为 `2021-07-29 16:00 -> 2026-06-18`。

## 20 币/max6 泛化

为消除旧报告中五年币池口径无法核验的问题，使用 `config.backtest.dualtrend.combined.top20.max6.pyramid20.json` 对两策略同批重跑。zip 配置快照确认 pair whitelist 为 20、`max_open_trades=6`、初始钱包 1000 USDT。

| 样本 | 策略 | Trades | Profit | PF | MaxDD | Long / Short Profit |
|---|---|---:|---:|---:|---:|---:|
| 三年 | SecondAdd20 | 339 | +180.62% | 2.445 | 5.287% | +422.97 / +1383.18 U |
| 三年 | LongMicro | 344 | +200.99% | 2.515 | 5.285% | +566.55 / +1443.33 U |
| 五年 | SecondAdd20 | 511 | +231.17% | 2.208 | 5.286% | +465.54 / +1846.19 U |
| 五年 | LongMicro | 518 | +253.85% | 2.269 | 5.285% | +625.30 / +1913.25 U |

Micro tag 三年为 7 笔、`+63.94 USDT`、PF `3.354`；五年为 7 笔、`+75.30 USDT`、PF `3.367`。组合总收益、PF、long 利润和 short 利润均改善，MaxDD 基本持平且略低。因此 Positive13 的升级不是单一小币池偶然结果。

## 决策

正式提升为研究主候选：

```text
DualTrendPyramidSecondAdd20LongMicroV1Strategy
```

`DualTrendPyramidSecondAdd20V1Strategy` 继续保留为稳定对照。此次提升不代表 dry-run 自动切换：现有 Positive13 dry-run 仍运行 Raw 兼容别名。

风险边界：新增 tag 只有 7 笔；Positive13 三年/五年最大回撤增加约 0.9 个百分点，虽然 20 币/max6 回撤未增加，样本稀少的风险仍然存在。下一步优先验证滚动样本外、20 币近一年/压力期及模拟盘信号，不再扩展 `_deep_body`、全量 pullback、compression breakout 或峰值追踪退出。

## 关键归档

- 三年仓位梯度：`user_data/analysis/micro_long_stake_2026-07-17/backtest-result-2026-07-17_10-09-34.zip`
- 近一年：`user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-16-47.zip`
- 压力期：`user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-18-07.zip`
- 五年：`user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-29-41.zip`
- 20 币/max6 三年：`user_data/analysis/long_micro_top20_max6_2026-07-17/backtest-result-2026-07-17_10-52-30.zip`
- 20 币/max6 五年：`user_data/analysis/long_micro_top20_max6_2026-07-17/backtest-result-2026-07-17_11-10-20.zip`
- 正式类压力冒烟：`user_data/analysis/long_micro_promoted_2026-07-17/`
