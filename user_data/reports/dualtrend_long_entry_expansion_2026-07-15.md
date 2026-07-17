# DualTrend 做多入场扩展验证

> **证据口径说明（2026-07-17）：** 本文“五年 20 币”段落的主线数值 `477 / +2617.27 U` 与现存 Positive13/max3 五年原始归档完全一致，而本文所述 20 币原始 zip 已清理，无法再次核对配置快照。因此该段只保留多头扩展的方向性结论，不能作为 20 币/max6 五年基线；权威口径见仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md)。

日期：2026-07-15

## 目标

当前主候选 `DualTrendPyramidSecondAdd20V1Strategy` 的多头只有：

- `long_1d_center_compression`

本轮不改既有 short 入场、止损、止盈、加仓、币池或 `max_open_trades=3`，只尝试为多头补齐两种 1h/4h 双顺延续形态：

- `long_pullback_restart_1h`
- `long_compression_breakout_1h`

共同约束：

- pair 4H 上升趋势
- 非 BTC 时 BTC 4H 上升趋势
- 1H 重心上移、EMA20 上行、放量有效突破
- 多头 K 线质量与结构止损距离合格
- 不与同一根 K 的 short 或原始日线 long 信号冲突

## 候选定义

### `long_pullback_restart_1h`

4H 上升趋势中的 1H 回踩后重启：回踩深度受限、低点仍在 4H EMA50 附近上方、价格重新突破 1H 压缩上沿。

### `long_compression_breakout_1h`

4H 上升趋势中的 1H 高位压缩突破：压缩区间足够窄、接近上沿、放量收强后突破。

## 近一年结果

窗口：`2025-06-18 -> 2026-06-18`，Positive13，`max_open_trades=3`，1h + 5m detail。

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 当前主候选 `DualTrendPyramidSecondAdd20V1Strategy` | 123 | +68.02% | 3.395 | 4.75% | 56.10% |
| 仅新增 Pullback | 189 | +61.57% | 2.273 | 3.78% | 47.09% |
| 仅新增 Compression | 189 | +55.83% | 2.085 | 7.01% | 45.50% |
| 两种全部启用 | 189 | +62.83% | 2.327 | 4.75% | 47.09% |

## Tag 拆解

| 新 tag | Trades | Profit | PF | Winrate | 判断 |
|---|---:|---:|---:|---:|---|
| `long_pullback_restart_1h` | 71 | +11.33% | 1.598 | 33.8% | 本身为正，但质量不足以覆盖槽位机会成本 |
| `long_compression_breakout_1h` | 68 | +0.83% | 1.036 | 26.5% | 基本无边际收益，且拉高组合回撤 |

同时启用时，Pullback tag 为 69 笔、`+12.97% / PF 1.748`，Compression tag 为 2 笔、`-0.52%`。这是因为两类 long 与原 short、日线 long 共用 3 个开仓槽位，成交顺序会改变。

## 3 年细分结论

后续对 pullback 的强实体、深回踩、成交量和退出方式继续拆分。结论是：

- `_body` 是有效的质量标记，但不能单独证明组合收益会提高。
- `_deep_body` 在三年样本中不干净。“深回踩后再强拉”经常只是反弹诱多。
- 给 `_deep` 增加 1.5 倍强成交量门槛，或在 7% 提前止盈，都不能解决其机会成本问题。
- 新多头不使用空头专属加仓；它只继承全局盈利保护。问题主要来自共享资金和开仓槽位，而不是复用了空头加仓逻辑。

## 5 年扩展实验对比（20 币口径未由现存归档证实）

原记录声称窗口为 `2021-07-29 16:00 -> 2026-06-18 00:00`、20 币、`max_open_trades=6`、初始资金 1000 USDT、1h + 5m detail。由于原始 zip 已清理且主线数值与 Positive13/max3 归档一致，不再把这里的 20 币/max6 标签视为已验证事实。

| 版本 | Trades | Profit | PF | MaxDD | Long | Short | 结论 |
|---|---:|---:|---:|---:|---:|---:|---|
| 主线 `DualTrendPyramidSecondAdd20V1Strategy` | 477 | +2617.27 U | 2.405 | 4.80% | +613.96 U | +2003.32 U | 保留 |
| 全量新多头 | 801 | +2338.76 U | 1.754 | 14.30% | +599.62 U | +1739.14 U | 淘汰 |
| Limited | 664 | +2256.00 U | 1.864 | 12.73% | +520.25 U | +1735.75 U | 淘汰 |
| Micro，仅新增 `long_pullback_restart_1h_body` | 518 | +2538.55 U | 2.269 | 5.29% | +625.30 U | +1913.25 U | 观察，不替换主线 |

Micro 新 tag 只有 7 笔、`+75.30 U`。它本身盈利，但改变了同一时段的资金分配和成交顺序，导致原有 short 及日线 long 的组合收益变化。相对主线总收益仍少 `78.73 U`，PF 更低，回撤略高。

这说明新多头不是简单叠加收益。在无限动态仓位和 6 个槽位下，多头会改变后续订单的仓位规模、并发组合与复利路径。全量扩展因此稀释了空头主引擎，即使 short 成交笔数没有减少。

## 最终结论

1. 做多可以增加形态，两个新 tag 都正确触发，技术实现没有问题。
2. 但本轮不是可并入主策略的增强：三种组合均低于当前主候选的近一年 `+68.02% / PF 3.395`。
3. `long_pullback_restart_1h_body` 是唯一值得保留的观察形态；保留 `DualTrendLongExpansionPullbackBodyMicroV1Strategy` 供未来复核，但不替换主线。
4. `long_compression_breakout_1h` 不值得继续研究，先不保留为候选。
5. 全量、DeepVolume、DeepRoi07 和 Limited 分支均已淘汰，并从策略文件删除，避免误用。
6. 现阶段继续保持 `DualTrendPyramidSecondAdd20V1Strategy` 作为主候选。

如果未来继续做多，优先研究独立 long 资金槽位，或对 Micro 的 7 笔交易做逐笔机会成本对照；不要再重复扩展 `_deep_body`、全量 pullback 或 compression。

## 输出

原始 zip/meta 属于可再生成的临时产物，清理后不长期保留。复现使用：

- 原记录配置：`user_data/config.backtest.dualtrend.combined.top20.max6.pyramid20.json`（现存原始结果不足以验证五年表确实使用该配置）
- 主线：`DualTrendPyramidSecondAdd20V1Strategy`
- 观察版：`DualTrendLongExpansionPullbackBodyMicroV1Strategy`
- 时间范围：`20210618-20260618`
- 时间框架：`1h`，detail `5m`
