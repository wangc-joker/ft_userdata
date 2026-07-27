# DualTrend LongMicro 参数碰撞与修正后复核

日期：2026-07-20

## 结论

`DualTrendPyramidSecondAdd20LongMicroV1Strategy` 继续保留为研究主候选，`DualTrendPyramidSecondAdd20V1Strategy` 继续作为稳定对照，dry-run 入口不切换。

7 月 17 日 LongMicro 的高收益结果失效。原因不是回测随机波动，而是 `_DualTrendLongExpansionMixin.long_breakout_buffer=0.001` 通过 MRO 覆盖了父级日线多头的 `long_breakout_buffer=0.009`。旧候选同时增加 Micro 入场并放松原日线入场，不能解释为 Micro tag 的单独效果。

修正后使用独立参数 `long_expansion_breakout_buffer=0.001`。候选仍在 Positive13 和 Top20 的三年、五年组合上领先，最大回撤基本不变，但优势缩小且年度表现不连续。

## 根因与控制实验

父级参数：

```text
DualTrendCombinedLongDailyCenterShortV1Strategy.long_breakout_buffer = 0.009
```

旧扩展参数：

```text
_DualTrendLongExpansionMixin.long_breakout_buffer = 0.001
```

修正参数：

```text
_DualTrendLongExpansionMixin.long_expansion_breakout_buffer = 0.001
```

在 2021 窗口、Positive13、`max_open_trades=100` 下做禁用扩展入场控制：

| 策略 | Trades | Profit | PF | MaxDD |
|---|---:|---:|---:|---:|
| SecondAdd20 | 81 | +5.6371% | 1.3195 | 7.6686% |
| 禁用扩展入场诊断类 | 81 | +5.6371% | 1.3195 | 7.6686% |
| 修正后 LongMicro | 81 | +5.6371% | 1.3195 | 7.6686% |

三者 81 笔交易逐笔一致。修复前，即使禁用扩展入场，结果仍为 `+5.6922%` 且只有 79 个开仓键与基线一致，直接证明旧差异来自父级参数被覆盖。

## Positive13 修正后结果

口径：`max_open_trades=3`、1000 USDT、unlimited stake、1h + 5m detail、protections、mainnet 市场元数据。

| 样本 | SecondAdd20 | LongMicro | 候选 PF | 候选 MaxDD | 差值 |
|---|---:|---:|---:|---:|---:|
| 三年，2023-06-18 -> 2026-06-18 | 314 / +199.22% | 318 / +209.59% | 2.685 | 4.80% | +10.37pct |
| 近一年，2025-06-18 -> 2026-06-18 | 123 / +68.02% | 123 / +72.49% | 3.499 | 4.74% | +4.47pct |
| 压力期，2026-03-01 -> 2026-05-31 | 15 / +5.11% | 15 / +5.11% | 3.077 | 1.75% | 0 |
| 五年，有效起点 2021-07-29 | 477 / +261.73% | 481 / +277.37% | 2.429 | 4.78% | +15.64pct |

旧候选的三年 `+216.62%` 和五年 `+281.17%` 作废。

独立年度：

| 窗口 | SecondAdd20 | LongMicro | Micro tag |
|---|---:|---:|---:|
| 2023-06-18 -> 2024-06-18 | +16.36% | +19.76% | 3 笔 / +35.23 USDT |
| 2024-06-18 -> 2025-06-18 | +52.48% | +50.23% | 3 笔 / -20.19 USDT |
| 2025-06-18 -> 2026-06-18 | +68.02% | +72.49% | 1 笔 / +29.15 USDT |

候选在 2024-25 单独启动时落后 `2.25pct`，不能描述为逐年稳定提升。

## Top20/max6 修正后结果

| 样本 | SecondAdd20 | LongMicro | 候选 PF | 候选 MaxDD | 差值 |
|---|---:|---:|---:|---:|---:|
| 三年 | 339 / +180.62% | 342 / +190.23% | 2.454 | 5.284% | +9.61pct |
| 五年 | 511 / +231.17% | 515 / +243.23% | 2.229 | 5.289% | +12.05pct |

旧候选的三年 `+200.99%` 和五年 `+253.85%` 作废。修正后仍领先，但提升约减半。

## 交易路径审计

Positive13 五年同一导出包内对齐 `pair + open_date + is_short`：

| 方向 | 对照 | 候选 | 共同开仓 | 同平仓/退出/订单数 | 对照独有 | 候选独有 |
|---|---:|---:|---:|---:|---:|---:|
| Long | 55 | 59 | 52 | 52 | 3 | 7 |
| Short | 422 | 422 | 422 | 422 | 0 | 0 |

- 7 笔候选独有交易全部为 `long_pullback_restart_1h_body`，合计 `+76.26 USDT`，3 胜 4 负。
- 两笔 `+10%` ROI 单贡献主要利润，其余 5 笔合计为负，收益集中度高。
- 3 笔被替换的日线多头合计约 `+1.44 USDT`。
- 52 笔共同多头因复利仓位变化多约 `+18.46 USDT`。
- 422 笔共同空头交易路径完全相同，候选多约 `+63.12 USDT`，属于复利金额变化，不是空头信号改善。
- 7 笔 Micro 均只有一次入场和一次出场，没有使用空头 tag 专属的两次盈利加仓。

Top20 槽位补充审计：三年候选少 1 笔基线空头，该单利润为 `-0.22 USDT`；五年双方都是 455 笔空头，454 笔路径一致，候选以一笔 `-0.01 USDT` 空头替换一笔 `+0.01 USDT` 空头。新增多头会造成轻微槽位扰动，但没有形成有经济意义的空头利润挤压。

## 元数据一致性

首次重跑遇到 Binance mainnet `exchangeInfo` 451，临时 testnet 元数据覆盖让 Top20 三年基线变为 338 笔、`+180.58%`。mainnet 恢复后重新得到 339 笔、`+180.6155%`，与 7 月 17 日基线逐项一致。

因此 testnet 元数据结果不可用于 mainnet 历史对照。相关覆盖配置只作为失败实验记录，不进入标准命令。

## 决策

保留 LongMicro 研究候选的理由：

- 修正后 Positive13 三年和五年仍分别领先 `10.37pct`、`15.64pct`。
- Top20 三年和五年仍分别领先 `9.61pct`、`12.05pct`。
- 四个主比较的最大回撤都近似不变。
- 空头交易路径没有被新增多头改写。

不切换 dry-run 的理由：

- 五年只有 7 笔，且 3 胜 4 负。
- 收益依赖两笔大赢家。
- 2024-25 独立年度为负贡献。
- 当前 dry-run 仍运行 Raw 兼容别名，需要单独的运行迁移和观察计划。

下一步不继续围绕 7 笔交易做参数微调。优先积累 dry-run 信号观察，或只验证有独立市场逻辑依据的 regime/filter 假设。

## 独立观察入口

同日已增加隔离的 Positive13/max3 LongMicro dry-run 观察入口：

- 配置：`user_data/config.dryrun.dualtrend.longmicro.positive13.max3.json`
- 启动：`start_positive13_longmicro_observation.cmd`
- 状态：`show_positive13_longmicro_observation_status.cmd`
- 报告：`run_positive13_longmicro_observation_report.cmd`
- 停止：`stop_positive13_longmicro_observation.cmd`
- API：`127.0.0.1:8086`
- SQLite：`user_data/tradesv3-positive13-longmicro-observation.sqlite`

该入口不会替换现有 Raw-compatible dry-run，并保证启动前后主 `freqtrade` 容器的状态和身份不变。配置、安全保护和隔离报告路径均已验证。观察容器已于 2026-07-20 15:01（Asia/Shanghai）启动，API 确认为 `dry_run`、LongMicro、13 币、max3；初始为 0 持仓、0 成交，实盘容器保持关闭。

## 证据归档

- `user_data/analysis/long_micro_validation_2026-07-20/corrected_control_2021_max100/backtest-result-2026-07-20_05-12-08.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13/backtest-result-2026-07-20_05-25-10.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13_five_year-2026-07-20_05-54-29.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_rolling_20230618_20240618-2026-07-20_05-58-45.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_rolling_20240618_20250618-2026-07-20_05-59-09.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13_near_year-2026-07-20_05-32-42.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_top20_three_year-2026-07-20_06-05-49.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_top20_five_year-2026-07-20_06-18-23.zip`

目录中的 `rolling_positive13`、`top20_max6_mainnet` 等较早归档是碰撞发现过程，候选数字不可作为最终结果；`metadata_consistency` 是 testnet 元数据失败对照。
