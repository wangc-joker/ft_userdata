# DualTrend 当前权威状态

> **唯一权威入口，更新于 2026-07-17。** 其他带日期的 DualTrend 文档都是当时的实验快照。发生冲突时，以本文和当前代码为准。

## 一眼结论

- 当前研究主候选：`DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- 稳定对照：`DualTrendPyramidSecondAdd20V1Strategy`
- 策略文件：`user_data/strategies/DualTrendMainStrategies.py`
- 主回测口径：Positive13、`max_open_trades=3`、初始 1000 USDT、`stake_amount=unlimited`、1h + 5m detail、启用 protections
- 新候选只在 SecondAdd20 上增加稀有的非深回踩强实体多头 `long_pullback_restart_1h_body`；空头、加仓和盈利保护逻辑不变
- 三年收益由 `+199.22%` 提高到 `+216.62%`，五年由 `+261.73%` 提高到 `+281.17%`；五年最大回撤由 `4.80%` 增至 `5.68%`
- 20 币/max6 也通过：三年 `+180.62% -> +200.99%`，五年 `+231.17% -> +253.85%`，回撤均未增加
- 新 tag 五年只有 7 笔，属于有风险边际改善的研究升级，尚未切换 dry-run
- 历史 `+191.75%` Window05To15 策略不是当前候选

读取到本文的提交必须同时包含 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`。若代码中找不到该类，说明分支或同步状态不完整，不要回退推断旧候选。

## 当前主候选

继承关系：

```text
DualTrendPyramidSecondAdd20LongMicroV1Strategy
  -> DualTrendLongExpansionPullbackBodyMicroV1Strategy
  -> DualTrendLongExpansionPullbackBodyOnlyV1Strategy
  -> _DualTrendLongExpansionMixin
  -> DualTrendPyramidSecondAdd20V1Strategy
  -> DualTrendPyramidSecondAdd15V1Strategy
  -> DualTrendPyramidCloseFloor07V1Strategy
  -> DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy
  -> 更早的 Guard / Baseline / Raw 公共逻辑
```

SecondAdd20 的两次盈利加仓比例仍是：

```text
第一笔盈利加仓：25%
第二笔盈利加仓：20%
```

新增多头必须精确命中 `long_pullback_restart_1h_body`。`_deep_body`、无强实体 pullback 和 compression breakout 均被过滤。新多头沿用全局风险管理，但不使用空头 tag 专属的加仓资格。

## 已确认结果

以下均为 Positive13/max3 主口径：

| 样本 | 新候选 Trades | 新候选 Profit | PF | MaxDD | Winrate | SecondAdd20 Profit | SecondAdd20 MaxDD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 三年，2023-06-18 -> 2026-06-18 | 325 | +216.62% | 2.687 | 5.68% | 51.38% | +199.22% | 4.82% |
| 近一年，2025-06-18 -> 2026-06-18 | 128 | +76.63% | 3.473 | 4.02% | 57.81% | +68.02% | 4.75% |
| 压力期，2026-03-01 -> 2026-05-31 | 16 | +5.13% | 3.083 | 1.75% | 43.75% | +5.11% | 1.75% |
| 长样本，有效起点 2021-07-29 | 490 | +281.17% | 2.420 | 5.68% | 51.43% | +261.73% | 4.80% |

五年从 1000 USDT 开始，新候选净利润 `+2811.71 USDT`，相对 SecondAdd20 多 `+194.44 USDT`。拆分结果：

| 方向 | 新候选五年利润 | SecondAdd20 五年利润 | 差值 |
|---|---:|---:|---:|
| Long | +746.40 USDT | +613.96 USDT | +132.44 USDT |
| Short | +2065.32 USDT | +2003.32 USDT | +62.00 USDT |

这次多头没有在五年总账上挤压空头利润；不过总成交从 477 增至 490，而新 tag 本身只有 7 笔，说明共享槽位和复利路径仍会改变其他成交，不能把组合差值简单归因于 7 笔 tag 盈亏。

新 tag 的三年结果为 7 笔、`+62.19 USDT`、PF `3.327`；五年为 7 笔、`+75.60 USDT`、PF `3.376`。样本量仍小，是当前最大不确定性。

旧归档中的五年 SecondAdd20 类名为 `DualTrendPyramidSecondAdd20TestStrategy`，参数与最终 V1 的 `(0.25, 0.20)` 一致。其配置快照已核实为 Positive13/max3，不是 20 币/max6。

20 币/max6 已重新用同一命令直接对照，并保留配置快照：

| 样本 | 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| 三年 | SecondAdd20 | 339 | +180.62% | 2.445 | 5.287% | 53.10% |
| 三年 | LongMicro | 344 | +200.99% | 2.515 | 5.285% | 53.49% |
| 五年，有效起点 2021-07-29 | SecondAdd20 | 511 | +231.17% | 2.208 | 5.286% | 53.03% |
| 五年，有效起点 2021-07-29 | LongMicro | 518 | +253.85% | 2.269 | 5.285% | 53.09% |

20 币五年 LongMicro 的 long/short 利润为 `+625.30 / +1913.25 USDT`，SecondAdd20 为 `+465.54 / +1846.19 USDT`。新增多头同样没有压低空头总利润。近一年和压力期当前仍只保留 SecondAdd20 的历史泛化值；不要拿 Positive13 数字替代它们。

## 策略角色

| 类名 | 当前角色 |
|---|---|
| `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 当前研究主候选 |
| `DualTrendPyramidSecondAdd20V1Strategy` | 稳定对照；不含新增 1h 多头 |
| `DualTrendLongExpansionPullbackBodyMicroV1Strategy` | 新候选的实现父级；历史实验类名 |
| `DualTrendPyramidSecondAdd15V1Strategy` | 仓位比例对照 |
| `DualTrendPyramidCloseFloor07V1Strategy` | 历史父级/诊断对照 |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 约 `+191.75%` 的历史候选，不是当前答案 |
| `DualTrendRawStrategy` / `DualTrendBaselineStrategy` / `DualTrendGuardStrategy` | 原始、保本和 Guard 对照 |
| `DualTrendCombinedShortPullbackShapeV1Strategy` | Raw 的向后兼容别名，不是当前候选 |

## 本轮淘汰方向

参考 `D:\test\NostalgiaForInfinityX7.py` 的分层盈利回撤思想后，已完成并淘汰：

- 空头强趋势单达到 `+5%/+6%` 后按峰值回撤锁盈：三年收益降至 `+173.20% ~ +176.79%`
- 空头峰值达到 `+7%/+8%` 后，等待 6h 反转和 EMA20 确认退出：三年约 `+197.00%`，仍低于对照
- 原日线多头达到 `+5%/+7%` 后等待反转退出：三年约 `+185.18% ~ +185.34%`，其中一版 MaxDD 升至 `9.78%`
- Micro 多头仓位缩放 25%/50%/75%：三年收益依次 `+208.33% / +210.90% / +214.80%`，均低于完整仓位的 `+216.62%`

结论：当前 ROI、结构止损、部分止盈和保本链对强趋势单更合适，不再重复增加峰值追踪退出。NFI 可继续借鉴市场状态过滤和风险分层思路，但不直接移植其超长 custom-exit 规则树。

## 多头结论

- 全量 `long_pullback_restart_1h` 和 `long_compression_breakout_1h` 会稀释主引擎，继续淘汰
- `_deep_body` 三年不干净，深回踩后的强拉容易成为反弹诱多，继续淘汰
- 只保留非深回踩强实体 `long_pullback_restart_1h_body`
- 新多头不使用空头专属加仓；SecondAdd20 的盈利加仓仍只给既有合格空头
- 下一步优先做滚动样本外、20 币近一年/压力期补充和 dry-run 观察，不继续扩宽多头 tag

## 配置与运行入口

配置和启动脚本没有随研究候选自动切换：

| 入口 | 文件内/实际策略 | 状态 |
|---|---|---|
| Positive13/max3 回测配置 | `DualTrendRawStrategy` | 旧默认；回测必须命令行显式覆盖新候选 |
| Top20/max6 回测配置 | `DualTrendPyramidSecondAdd20V1Strategy` | 仍是稳定对照，不是新候选 |
| Positive13/max3 dry-run 配置 | `DualTrendGuardStrategy` | 不是研究候选 |
| `start_positive13_max3_dryrun.ps1` | `DualTrendCombinedShortPullbackShapeV1Strategy` | 实际运行 Raw 兼容别名 |
| `docker-compose.yml` | 默认 `SampleStrategy` | 仅显式设置后才与 DualTrend 有关 |

因此“当前研究候选”不等于“当前模拟盘策略”。在完成独立 dry-run 风险确认前，不改运行入口。

## 标准复现命令

```powershell
docker --context desktop-linux compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json --strategy-path /freqtrade/user_data/strategies --strategy DualTrendPyramidSecondAdd20LongMicroV1Strategy --timeframe 1h --timeframe-detail 5m --timerange 20230618-20260618 --enable-protections --export trades
```

复现后至少核对策略类名、pair whitelist、`max_open_trades=3`、有效起止时间、初始钱包和 protections，再引用收益数字。

## 文档读取规则

1. 先读本文，再读当前策略代码。
2. 最新升级依据是 `user_data/reports/dualtrend_nfi_peak_and_long_micro_upgrade_2026-07-17.md`。
3. 7 月 14 日 SecondAdd20 与 7 月 15 日多头/Top20 报告用于理解父级和已淘汰方向。
4. 其他日期型报告按历史快照处理，标题含“当前”“主线”也不代表今天仍有效。
5. 不从单个配置或启动脚本反推研究候选。
6. 新实验若替换主候选，必须在同一变更中更新本文、`AGENTS.md`、结果、运行状态和淘汰方向。

关键证据：

- `user_data/reports/dualtrend_nfi_peak_and_long_micro_upgrade_2026-07-17.md`
- `user_data/reports/dualtrend_second_add20_仓位比例实验_2026-07-14.md`
- `user_data/reports/dualtrend_long_entry_expansion_2026-07-15.md`
- `user_data/analysis/micro_long_stake_2026-07-17/backtest-result-2026-07-17_10-09-34.zip`
- `user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-16-47.zip`
- `user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-18-07.zip`
- `user_data/analysis/micro_long_validation_2026-07-17/backtest-result-2026-07-17_10-29-41.zip`
- `user_data/analysis/long_micro_top20_max6_2026-07-17/backtest-result-2026-07-17_10-52-30.zip`
- `user_data/analysis/long_micro_top20_max6_2026-07-17/backtest-result-2026-07-17_11-10-20.zip`
- `user_data/analysis/pyramid_second_add_size_2026-07-14/five_year-2026-07-14_05-50-14.zip`
