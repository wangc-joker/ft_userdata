# DualTrend 当前权威状态

> **唯一权威入口，更新于 2026-07-17。** 其他带日期的 DualTrend 文档都是当时的实验快照。发生冲突时，以本文和当前代码为准。

## 一眼结论

- 当前研究主候选：`DualTrendPyramidSecondAdd20V1Strategy`
- 策略文件：`user_data/strategies/DualTrendMainStrategies.py`
- 主回测口径：Positive13、`max_open_trades=3`、初始 1000 USDT、`stake_amount=unlimited`、1h + 5m detail、启用 protections
- `+191.75%` 对应较早的 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`，只是历史基线，不再是当前主候选
- 当前 dry-run 启动脚本仍运行 Raw 兼容别名，并未自动升级到 SecondAdd20
- 新增多头扩展没有并入主线；`DualTrendLongExpansionPullbackBodyMicroV1Strategy` 仅保留观察

包含当前主候选代码的已知基线提交是 `04eda83`。读取到本文的提交应当是该提交的后继；若代码中找不到 `DualTrendPyramidSecondAdd20V1Strategy`，先检查分支和同步状态。

## 当前主候选

`DualTrendPyramidSecondAdd20V1Strategy` 在 `DualTrendPyramidSecondAdd15V1Strategy` 基础上，仅把第二次盈利加仓从初始仓位的 15% 提高到 20%。当前两次加仓比例为：

```text
第一笔盈利加仓：25%
第二笔盈利加仓：20%
```

继承主线：

```text
DualTrendPyramidSecondAdd20V1Strategy
  -> DualTrendPyramidSecondAdd15V1Strategy
  -> DualTrendPyramidCloseFloor07V1Strategy
  -> DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy
  -> 更早的 Guard / Baseline / Raw 公共逻辑
```

7 月 14 日实验归档中的临时类名是 `DualTrendPyramidSecondAdd20TestStrategy`。它与最终保留的 `DualTrendPyramidSecondAdd20V1Strategy` 使用相同的 `(0.25, 0.20)` 加仓比例；复现新任务时使用最终 V1 类名。

## 已确认结果

以下为 Positive13/max3 主口径：

| 样本 | Trades | Profit | PF | MaxDD | Winrate | 第二次加仓交易数 |
|---|---:|---:|---:|---:|---:|---:|
| 三年，2023-06-18 -> 2026-06-18 | 314 | +199.22% | 2.682 | 4.82% | 51.27% | 11 |
| 近一年，2025-06-18 -> 2026-06-18 | 123 | +68.02% | 3.395 | 4.75% | 56.10% | 5 |
| 压力期，2026-03-01 -> 2026-05-31 | 15 | +5.11% | 3.077 | 1.75% | 40.00% | 2 |
| 长样本，有效起点 2021-07-29 | 477 | +261.73% | 2.405 | 4.80% | 51.57% | 21 |

长样本从 1000 USDT 开始，对应净利润约 `+2617.27 USDT`。其原始 zip 中保存的配置快照明确为 Positive13、`max_open_trades=3`；不要把这组 `477 / +261.73%` 当成已证实的 20 币/max6 五年结果。

20 币/max6 已可靠保留的是三年、近一年和压力期泛化结果：

| 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 三年 | 339 | +180.62% | 2.445 | 5.29% | 53.10% |
| 近一年 | 135 | +53.55% | 2.751 | 3.07% | 58.52% |
| 压力期 | 18 | +5.43% | 3.454 | 1.50% | 55.56% |

因此 Positive13/max3 仍是主研究口径；20 币/max6 是泛化和压力观察，不替换主口径。精确的 20 币/max6 五年数值需要重新回测并保留归档后再写入权威表。

## 策略角色

| 类名 | 当前角色 |
|---|---|
| `DualTrendPyramidSecondAdd20V1Strategy` | 当前研究主候选 |
| `DualTrendPyramidSecondAdd15V1Strategy` | 稳健对照 |
| `DualTrendPyramidCloseFloor07V1Strategy` | 历史父级/诊断对照 |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 约 `+191.75%` 的历史主候选，仍在继承链中，但不是当前答案 |
| `DualTrendLongExpansionPullbackBodyMicroV1Strategy` | 多头观察版，不替换主线 |
| `DualTrendRawStrategy` / `DualTrendBaselineStrategy` / `DualTrendGuardStrategy` | 原始、保本和 Guard 对照 |
| `DualTrendCombinedShortPullbackShapeV1Strategy` | `DualTrendRawStrategy` 的向后兼容别名，不是 SecondAdd20 |

## 多头结论

当前主线原有多头 tag 为 `long_1d_center_compression`。新增的 `long_pullback_restart_1h` 和 `long_compression_breakout_1h` 没有并入主线：

- `_body` 可作为质量标记，但组合收益不足以替换主线
- `_deep_body` 三年样本不干净，深回踩后的强拉容易成为反弹诱多；不要重复扩展
- 新多头不使用空头专属加仓，只继承全局盈利保护
- 主要问题是与空头共享资金、开仓槽位和复利路径，因而会稀释空头主引擎
- Micro 版新增 tag 只有 7 笔、约 `+75.30 USDT`，但组合总收益仍低于主线，只保留观察

后续若继续研究多头，优先做独立 long 资金槽位或逐笔机会成本对照，不再重复全量 pullback、compression 或 `_deep_body` 路线。

## 配置与运行入口

配置文件中的默认策略和当前研究主候选并未全部对齐。这是另一台机器容易误判的主要原因。

| 入口 | 文件内/实际策略 | 状态 |
|---|---|---|
| Positive13/max3 回测配置 | `DualTrendRawStrategy` | 旧默认；主线回测必须在命令行显式覆盖为 SecondAdd20 |
| Top20/max6 回测配置 | `DualTrendPyramidSecondAdd20V1Strategy` | 类名已对齐，但属于泛化口径 |
| Positive13/max3 dry-run 配置 | `DualTrendGuardStrategy` | 不是当前研究主候选 |
| `start_positive13_max3_dryrun.ps1` | `DualTrendCombinedShortPullbackShapeV1Strategy` | 实际覆盖配置并运行 Raw 兼容别名，不是当前研究主候选 |
| `docker-compose.yml` | 默认 `SampleStrategy` | 只有显式设置策略时才与 DualTrend 有关 |

在没有单独完成 dry-run 升级和风险确认前，不要把“研究主候选”自动解释成“当前模拟盘正在运行的策略”。

## 标准复现命令

Positive13/max3 三年主口径必须显式指定策略，不能依赖配置中的旧默认：

```powershell
docker --context desktop-linux compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json --strategy-path /freqtrade/user_data/strategies --strategy DualTrendPyramidSecondAdd20V1Strategy --timeframe 1h --timeframe-detail 5m --timerange 20230618-20260618 --export trades
```

复现后至少核对输出中的策略类名、pair whitelist、`max_open_trades`、有效起止时间和初始钱包，再引用收益数字。

## 文档读取规则

1. 先读本文，再读当前策略代码。
2. 7 月 14 日的 SecondAdd20 报告和 7 月 15 日的多头/Top20 报告用于理解最近实验。
3. 其他日期型报告按历史快照处理，标题含“当前”“主线”也不代表今天仍有效。
4. 不从单个配置文件或启动脚本反推研究主候选；必须区分研究、泛化回测和 dry-run。
5. 新实验如果替换主候选，必须同时更新本文的类名、结果、运行入口状态和已淘汰方向。

`我的策略/` 和 `user_data/reports/` 目录均已设置入口说明；其中未逐份加标签的旧材料也一律按历史研究记录读取。

关键记录：

- `user_data/reports/dualtrend_second_add20_仓位比例实验_2026-07-14.md`
- `user_data/reports/dualtrend_long_entry_expansion_2026-07-15.md`
- `user_data/reports/dualtrend_top20_max6_backtest_2026-07-15.md`
- `user_data/analysis/pyramid_second_add_size_2026-07-14/five_year-2026-07-14_05-50-14.zip`
