# DualTrend 二次加仓失败退出诊断

> **历史状态：** 本文先于同日的 20% 仓位比例定稿，文中的阶段性主候选不是最终答案。最新状态见仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md)，当前研究主候选是 `DualTrendPyramidSecondAdd20V1Strategy`。

日期：2026-07-14

## 目标

在不修改入场、币池、仓位上限、止损主逻辑的前提下，只验证一个想法：

> 二次加仓后，如果短时间没有继续盈利，是否应该单独退出二次加仓腿。

当前主候选：

- `DualTrendPyramidSecondAdd15V1Strategy`

实验版本：

- `DualTrendPyramidSecondAdd15Fail3hFlatV1Strategy`
- `DualTrendPyramidSecondAdd15Fail6hNo05V1Strategy`
- `DualTrendPyramidSecondAdd15Fail6hNo10V1Strategy`

## 三年回测

范围：2023-06-18 -> 2026-06-18

配置：

- pair pool：Positive13
- max_open_trades：3
- timeframe：1h
- timeframe-detail：5m
- config：`config.backtest.dualtrend.combined.top50.positive13.max3.json`

| 策略 | Trades | Profit | Profit Abs | PF | MaxDD | Winrate | 二次加仓交易数 |
|---|---:|---:|---:|---:|---:|---:|---:|
| DualTrendPyramidSecondAdd15V1Strategy | 314 | 198.33% | 1983.31 | 2.677 | 4.82% | 51.27% | 11 |
| Fail3hFlat | 314 | 197.02% | 1970.25 | 2.670 | 4.82% | 51.59% | 11 |
| Fail6hNo05 | 314 | 197.39% | 1973.94 | 2.673 | 4.82% | 51.59% | 11 |
| Fail6hNo10 | 314 | 197.42% | 1974.18 | 2.673 | 4.82% | 51.59% | 11 |

## 结论

三种二次加仓失败退出都没有超过当前主候选：

- `3h 不盈利退出` 比主候选少约 1.31 个百分点。
- `6h 未达到 +0.5% 退出` 比主候选少约 0.94 个百分点。
- `6h 未达到 +1.0% 退出` 比主候选少约 0.91 个百分点。
- MaxDD 没有改善，仍为 4.82%。
- PF 略低于当前主候选。

说明：二次加仓腿的主要收益来自允许它继续跟随趋势，短时间失败退出会提前砍掉部分后续利润；它没有明显降低回撤，因此不是有效增强。

## 处理

已删除失败实验类，保留当前主候选：

- `DualTrendPyramidSecondAdd15V1Strategy`

当前建议：

- 不进入二次加仓快速失败退出方向。
- 继续保留 `SecondAdd15` 作为加仓主候选。
- 下一步如果继续优化加仓，更适合研究“第二腿触发质量”或“二次加仓后的趋势延续识别”，而不是简单按时间退出。
