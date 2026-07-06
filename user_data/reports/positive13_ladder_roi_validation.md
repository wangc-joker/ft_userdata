# Positive13 分批阶梯止盈 / 保本保护 Docker 验证

生成时间：2026-06-29

## 当前验证对象

- 基线：`DualTrendCombinedShortPullbackShapeV1Strategy`
- 只保本：`DualTrendCombinedShortPullbackShapeBreakevenOnlyV1Strategy`
- 阶梯分批：`DualTrendCombinedShortPullbackShapePartialLadderA1Roi50Strategy`
- 分段移动止损：`DualTrendCombinedShortPullbackShapePartialLadderA2BandTrailRoi50Strategy`
- 币池：Positive13
- 资金槽位：`max_open_trades = 3`
- 阶梯语义：
  - 盈利超过 2% 后启用保本保护；
  - 盈利 10% 时卖出当前剩余仓位 50%；
  - 之后每再多盈利 10%，继续卖出当前剩余仓位 50%；
  - 第一次止盈后锁 5%，第二次锁 5.5%，第三次锁 6%，逐级上调，最高锁到 8%。

## 重要说明

普通 1H 回测无法准确验证分批止盈，因为 `adjust_trade_position()` 主要按 candle close 触发，而 ROI / stoploss 可能在 candle 内部高低点先触发。

因此分批止盈必须看 `--timeframe-detail 5m` 的结果。当前本地 5m 数据主要覆盖到 2026-05-08 左右，所以更公平的对比区间使用：

`2025-06-18 -> 2026-05-08`

## 官方 Docker 回测结果：5m-detail 可比区间

命令核心：

```text
docker compose run --rm freqtrade backtesting
--config /freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json
--config /freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json
--strategy-path /freqtrade/user_data/strategies
--timeframe 1h
--timeframe-detail 5m
--timerange 20250618-20260508
--export trades
--cache none
```

| 版本 | Trades | Profit | PF | MaxDD | Winrate | 多出口交易 | 额外分批出口 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 97 | 40.31% / 403.137 | 1.90 | 5.88% | 38.1% | 0 | 0 |
| Breakeven Only | 112 | 31.77% / 317.668 | 2.21 | 4.84% | 53.6% | 0 | 0 |
| Partial Ladder A1 ROI50 | 85 | 32.38% / 323.802 | 2.57 | 4.83% | 55.3% | 14 | 25 |
| Partial Ladder A1 FourStep Lock765 ROI50 | 85 | 32.44% / 324.392 | 2.57 | 4.83% | 55.3% | 14 | 25 |
| Partial Ladder A1 FourStep Lock876 ROI50 | 85 | 32.44% / 324.392 | 2.57 | 4.83% | 55.3% | 14 | 25 |
| Partial Ladder A1 FourStep Prelock ROI50 | 114 | 21.89% / 218.908 | 1.79 | 6.81% | 55.3% | 11 | 14 |
| Partial Ladder A2 BandTrail ROI50 | 115 | 22.23% / 222.273 | 1.86 | 4.76% | 61.7% | 5 | 6 |
| Partial Ladder A2 WideBandTrail ROI50 | 114 | 29.39% / 293.854 | 2.09 | 5.26% | 57.9% | 10 | 13 |
| Partial Ladder A2 UltraWideBandTrail ROI50 | 114 | 21.92% / 219.165 | 1.78 | 6.81% | 51.8% | 11 | 14 |

## 和基线相比

`Breakeven Only`：

- 收益下降：40.31% -> 31.77%
- PF 提升：1.90 -> 2.21
- 回撤降低：5.88% -> 4.84%
- 胜率提升：38.1% -> 53.6%

`Partial Ladder A1 ROI50`：

- 收益下降：40.31% -> 32.38%
- PF 提升：1.90 -> 2.57
- 回撤降低：5.88% -> 4.83%
- 胜率提升：38.1% -> 55.3%
- 真实触发了分批止盈：14 笔交易有多次退出，共 25 次额外分批退出。

`Partial Ladder A1 FourStep Lock765 ROI50`：

- 收益基本持平并小幅提升：32.38% -> 32.44%
- PF 持平：2.57
- MaxDD 持平：4.83%
- Winrate 持平：55.3%
- 分批触发数持平：14 笔交易有多次退出，共 25 次额外分批退出。
- 最大退出订单数为 4，说明“四次分批上限”已生效。
- 当前是 A1 系列里更干净的一版：分批更少，但没有牺牲收益和风险指标。

`Partial Ladder A1 FourStep Lock876 ROI50`：

- 和 `Lock765` 在这段样本上表现完全一致：32.44% / PF 2.57 / MaxDD 4.83%
- 说明这两个锁盈阶梯在当前 5m-detail 公平区间内没有改变实际触发路径
- 在这个样本里，`5% / 6% / 7% / 8%` 和 `5% / 6% / 6.5% / 7%` 的差异还不足以改变最终结果

`Partial Ladder A1 FourStep Prelock ROI50`：

- 收益下降：40.31% -> 21.89%
- PF 下降：1.90 -> 1.79
- 回撤扩大：5.88% -> 6.81%
- 胜率提升：38.1% -> 56.9%
- 5.1% 到 10% 之间使用 5% 回撤空间后，分批触发恢复：11 笔交易有多次退出，共 14 次额外分批退出。
- 但这版收益和回撤都变差，说明 5% 回撤空间虽然语义正确，却让部分已盈利订单回吐过多。

`Partial Ladder A2 BandTrail ROI50`：

- 收益下降：40.31% -> 22.23%
- PF 下降：1.90 -> 1.86
- 回撤降低：5.88% -> 4.76%
- 胜率提升：38.1% -> 61.7%
- 真实触发分批止盈仍少：5 笔交易有多次退出，共 6 次额外分批退出。
- 当前 A2 已改为 4 次分批：50%、25%、12.5%、12.5%。
- 10% 以上已改为阶梯放宽回撤空间：5%、5.5%、6%...，最高 10%。

`Partial Ladder A2 WideBandTrail ROI50`：

- 收益下降：40.31% -> 29.39%
- PF 提升：1.90 -> 2.09
- 回撤降低：5.88% -> 5.26%
- 胜率提升：38.1% -> 57.9%
- 额外分批触发 13 次，是 A2 系列里最均衡的一档。

`Partial Ladder A2 UltraWideBandTrail ROI50`：

- 收益下降：40.31% -> 21.92%
- PF 下降：1.90 -> 1.78
- 回撤扩大：5.88% -> 6.81%
- 胜率提升到 51.8%，但整体性价比最差。

## 和只保本相比

`Partial Ladder A1 ROI50` 相比 `Breakeven Only`：

- 收益小幅提升：31.77% -> 32.38%
- PF 明显提升：2.21 -> 2.57
- MaxDD 基本持平：4.84% -> 4.83%
- Trades 减少：112 -> 85

这说明阶梯分批确实有一点增益，但主要优势仍然是风险形态更好；绝大多数改善来自“盈利后不再让订单变成亏损”的止损保护，而不是分批止盈本身大幅增加收益。

`Partial Ladder A2 BandTrail ROI50` 相比 `Breakeven Only`：

- 收益下降：31.77% -> 22.23%
- PF 下降：2.21 -> 1.86
- MaxDD 基本持平：4.84% -> 4.76%
- 胜率提升：53.6% -> 61.7%

`Partial Ladder A2 WideBandTrail ROI50` 相比 `Breakeven Only`：

- 收益下降：31.77% -> 29.39%
- PF 下降：2.21 -> 2.09
- MaxDD 增加：4.84% -> 5.26%
- 胜率提升：53.6% -> 57.9%

这说明 10% 以内移动止损放宽后，确实能恢复一部分收益，但仍然不如 A1。

## 1H 全区间结果为何不作为最终结论

在普通 1H 回测中，分批止盈基本不会正确触发，结果会退化成保本止损或被 ROI 抢先退出。

近一年 `2025-06-18 -> 2026-06-18` 的 1H-only 结果：

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Baseline | 111 | 51.23% | 2.00 | 7.65% | 39.64% |
| Breakeven Only | 129 | 14.58% | 1.50 | 6.47% | 47.29% |
| Partial Ladder A1 ROI50 | 111 | 15.42% | 1.63 | 5.38% | 45.05% |

三年 `2023-06-18 -> 2026-06-18` 的 1H-only 结果也显示收益大幅下降：

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Baseline | 294 | 190.79% | 1.97 | 7.68% | 34.69% |
| Breakeven Only | 324 | 36.69% | 1.40 | 14.57% | 43.52% |
| Partial Ladder A1 ROI50 | 283 | 24.41% | 1.31 | 14.50% | 41.34% |

这些结果可以说明“规则会显著改变订单路径和仓位竞争”，但不能精确评估分批止盈质量。

## 结论

1. 只加保本保护，不是单纯小修，它会改变退出时间、释放槽位顺序和后续入场路径。
2. 在 5m-detail 公平区间内，保本和阶梯分批都降低回撤、提高 PF 和胜率，但牺牲了总收益。
3. 阶梯分批相对于只保本有轻微正增益，收益从 31.77% 提升到 32.38%，PF 从 2.21 提升到 2.57。
4. `A1 FourStep Lock765` 和 `A1 FourStep Lock876` 在当前样本里结果完全一致，都是 32.44% / PF 2.57 / MaxDD 4.83%。
5. A2 分段移动止损放宽后，最好的是 `A2 WideBandTrail`，收益 29.39%，PF 2.09，但仍低于 A1 FourStep 的收益 32.44%、PF 2.57。
6. `A1 FourStep Prelock` 把分批减少到 4 次，并在 5.1% 后给 5% 回撤空间，但收益只有 21.89%，明显低于原 A1。
7. 相对于当前基线，阶梯分批还不能作为主策略替换版本，因为总收益明显低于基线。
8. 如果目标是 dry-run 更平滑、减少“盈利单变亏损”的心理和资金回撤压力，可以把 `A1 FourStep Lock765` 作为观察版本单独跑。
9. 如果目标仍然是最大化当前 Positive13 主候选收益，暂时继续保持 Baseline 主策略。

## A1 FourStep 5%-10% 回吐后是否再到 10%

诊断对象：

- 交易内最高浮盈达到 5.1%-10%
- 最后通过 trailing stop 出场
- 出场收益低于 2%，也就是接近保本出场

结果：

| 样本 | 数量 |
|---|---:|
| 符合条件交易 | 15 |
| 出场后 24h 内重新达到 +10% | 2 |
| 出场后 72h 内重新达到 +10% | 5 |
| 出场后 120h 内重新达到 +10% | 8 |

按 tag：

| tag | 120h 内重新达到 +10% |
|---|---:|
| short_pullback_restart | 7 |
| long_1d_center_compression | 1 |
| short_compression_breakdown | 0 |

结论：

- 是的，确实有不少单子在 5%-10% 浮盈后回吐到接近保本，但后面又重新走到 10% 以上。
- 15 笔中有 8 笔在 120h 内重新达到 +10%，其中 7 笔来自 `short_pullback_restart`。
- 这说明 5.1% 后用 5% 回撤空间，会让一部分趋势单被过早洗出去；但另一部分并没有重新走强，所以不能简单取消保护。
- 后续如果继续优化，重点应该放在 `short_pullback_restart` 的“回吐后是否仍处于趋势结构内”，而不是直接统一加宽或收紧止损。

明细输出：

`user_data/analysis/a1_fourstep_prelock_reentry_10pct_check.csv`

## 建议

当前主策略继续保持：

`Positive13 + Combined + max_open_trades=3 + Baseline exits`

可选观察版本：

`DualTrendCombinedShortPullbackShapePartialLadderA1FourStepLock765Roi50Strategy`
`DualTrendCombinedShortPullbackShapePartialLadderA1FourStepLock876Roi50Strategy`

不建议作为主线的高胜率版本：

`DualTrendCombinedShortPullbackShapePartialLadderA2BandTrailRoi50Strategy`

原因：A2 系列虽然按 4 次分批执行了 50%、25%、12.5%、12.5%，但 10% 以内的移动止损仍会提前截断趋势单。最佳 A2 Wide 的分批触发 13 次，仍少于 A1 的 25 次。

观察重点：

- 实盘 / dry-run 中是否频繁把原本大盈利单提前保护出场；
- 是否减少大回撤；
- 是否明显减少“盈利 4% 以后最后亏损”的订单；
- 是否因为提前释放仓位而引入更多低质量新单。

## A1 只放宽 TP1 之后的锁盈验证

目标：

- 不改 TP1 之前的保护逻辑
- 只放宽 TP1 之后的锁盈，减少大盈利单被过早削掉

验证区间：

- `2023-06-18 -> 2026-05-08`
- 使用 `1h + 5m detail`

验证版本：

| 版本 | 锁盈阶梯 |
|---|---|
| A1 当前版 | `5% / 6% / 7% / 8%` |
| LooseA | `5% / 6.5% / 8% / 9%` |
| LooseB | `5% / 7% / 8.5% / 10%` |

结果：

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| A1 当前版 | 262 | 90.58% / 905.757 | 2.01 | 7.85% | 48.5% |
| LooseA | 270 | 96.71% / 967.104 | 2.03 | 7.85% | 48.9% |
| LooseB | 271 | 95.36% / 953.595 | 2.01 | 7.85% | 48.7% |

结论先看总表：

- `LooseA` 是这轮最好的版本。
- `LooseB` 也比当前 A1 略好，但不如 `LooseA` 稳。
- 放宽 TP1 后续锁盈，确实能回收一部分被过早砍掉的大盈利单，但改善幅度还不算颠覆性。

### 同开仓对照

以当前 A1 为基准，按 `pair + open_date + enter_tag` 对齐同一笔开仓。

`LooseA`：

- 共同交易：`260`
- 仅 A1 有：`2`
- 仅 LooseA 有：`10`
- 净变化：`+13.017 USDT`

分类：

| 类型 | 数量 |
|---|---:|
| 大盈利变更大 | 9 |
| 大盈利变更小 | 5 |
| 普通盈利变更大 | 28 |
| 普通盈利变更小 | 28 |
| 亏损变小 | 36 |
| 亏损变更差 | 33 |
| 基本不变 | 116 |

`LooseB`：

- 共同交易：`260`
- 仅 A1 有：`2`
- 仅 LooseB 有：`11`
- 净变化：`+7.785 USDT`

分类：

| 类型 | 数量 |
|---|---:|
| 大盈利变更大 | 10 |
| 大盈利变更小 | 5 |
| 普通盈利变更大 | 31 |
| 普通盈利变更小 | 35 |
| 亏损变小 | 39 |
| 亏损变更差 | 35 |
| 基本不变 | 99 |

解释：

- 两个放宽版都确实多救回了一部分大盈利单。
- 但 `LooseB` 虽然放大的大盈利单略多，普通盈利和亏损两侧的扰动也更大，所以净收益反而不如 `LooseA`。
- `LooseA` 的特点是改动更小，但结果更干净。

### 分批触发情况

三版在三年样本中的四档分批触发情况：

| 版本 | TP1 | TP2 | TP3 | TP4 | 多次减仓交易数 |
|---|---:|---:|---:|---:|---:|
| A1 当前版 | 36 | 11 | 7 | 0 | 36 |
| LooseA | 38 | 12 | 7 | 0 | 38 |
| LooseB | 38 | 12 | 7 | 0 | 38 |

这里能看到：

- 放宽后，TP1/TP2 的触发略有增加。
- 但 TP3/TP4 仍然很少，说明当前样本里真正能走到深层分批的单子本来就不多。
- 所以这轮优化的本质，不是把分批层数吃得更深，而是减少 TP1 之后被太早扫掉。

### 这一步的结论

1. 只放宽 TP1 之后的锁盈，方向是对的。
2. `LooseA` 比当前 A1 有确定性改善：收益更高，PF 略高，回撤基本不变。
3. `LooseB` 太激进，虽然也有改善，但不如 `LooseA` 平衡。
4. 如果继续在 A1 路线上优化“大盈利单被过早削掉”，当前最值得保留的候选是：

`DualTrendCombinedShortPullbackShapePartialLadderA1FourStepPostTp1LooseA1Roi50Strategy`

明细文件：

- `user_data/analysis/a1_vs_loose_post_tp1_compare.csv`

## Baseline + 保本 + 10%减半 + 剩余 5%移动止损

本轮新验证目标：

- 不采用 A1 的多次阶梯分批
- 尽量贴近原 Baseline 的风格
- 只增加两个动作：
  - 盈利超过 `2%` 后保本
  - 盈利到 `10%` 时卖出当前仓位 `50%`
- 剩余仓位不再继续分批，改为按最高浮盈回撤 `5%` 的移动止损离场

策略类：

`DualTrendCombinedShortPullbackShapeBaselineBreakevenTp10Trail5Roi50Strategy`

说明：

- 为了让 10% 减半真实生效，固定 ROI 提高到 `50%`
- 否则原 Baseline 的 `roi 10%` 会先把整单直接平掉

验证区间：

- `2023-06-18 -> 2026-05-08`
- 使用 `1h + 5m detail`

结果：

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Baseline | 280 | 178.48% / 1784.771 | 1.96 | 5.89% | 33.9% |
| Baseline + Breakeven + TP10 Half + Trail5 | 301 | 116.08% / 1160.794 | 2.06 | 7.85% | 48.5% |

直接结论：

- 相比 Baseline：
  - 收益明显下降：`178.48% -> 116.08%`
  - PF 小幅提升：`1.96 -> 2.06`
  - 胜率明显提升：`33.9% -> 48.5%`
  - MaxDD 反而扩大：`5.89% -> 7.85%`
- 相比之前的 A1 四档分批版本：
  - 收益明显更高：`90.58% -> 116.08%`
  - PF 略高：`2.01 -> 2.06`
  - 风格上也更接近 Baseline

### 分批触发情况

- 触发 10% 减半的交易数：`35`
- 额外部分减仓订单数：`35`

也就是说：

- 三年样本里，只有 `35` 笔交易真正走到了这一步
- 大部分订单最终还是由 `trailing_stop_loss` 或 `stop_loss` 离场

退出分布：

| Exit reason | Trades | Profit USDT |
|---|---:|---:|
| trailing_stop_loss | 213 | 1920.327 |
| stop_loss | 80 | -812.986 |
| stale_flat_120h | 3 | 8.941 |
| stale_loss_72h | 3 | -3.684 |
| stale_low_profit_240h | 1 | 18.560 |
| swing_exit_long_1d | 1 | 29.637 |

这里最关键的一点是：

- 原 Baseline 中大量 `roi 10%` 的确定性落袋利润，被改造成了“先减半，再等 trailing stop”
- 这确实提高了胜率和 PF
- 但也让不少原本完整兑现的 10% 盈利单，后半仓位在回撤里吐回去了

### 与 Baseline 的共同开仓对照

按 `pair + open_date + enter_tag` 对齐同一笔开仓：

- 共同交易：`270`
- 仅 Baseline 有：`10`
- 仅新版本有：`31`

分类：

| 类型 | 数量 |
|---|---:|
| 亏损变小 | 72 |
| 亏损翻盈 | 49 |
| 亏损变更差 | 45 |
| 盈利变更大 | 26 |
| 盈利变更小 | 56 |
| 盈利翻亏 | 8 |
| 基本不变 | 11 |

聚合变化：

- 变好的绝对收益合计：`+963.698 USDT`
- 变差的绝对收益合计：`-1413.639 USDT`
- 净变化：`-449.942 USDT`

这说明：

1. 这个版本确实救回了很多亏损单。
2. 但它仍然削掉了更多原本由 Baseline `roi 10%` 直接兑现的大盈利。
3. 所以它比 A1 好很多，但还是没法超过 Baseline。

明细文件：

- `user_data/analysis/baseline_vs_breakeven_tp10_trail5_compare.csv`
