# Guard 强单放行同开仓对照
生成时间: 2026-07-03
## 本轮目的
只比较同一笔开仓在基线 `DualTrendRawBreakevenGuardStrategy` 与候选 `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy` 下的结果，重点看 `short_pullback_restart`。
## 3y
- 基线总交易数: 321
- 候选总交易数: 335
- 同开仓可直接对照: 321
- 仅基线存在: 0
- 仅候选存在: 14

### short_pullback_restart 同开仓对照
- 对照笔数: 193
- 候选更好: 68 笔
- 候选更差: 68 笔
- 基本一致: 57 笔
- 平均单笔收益: 基线 0.89% / 候选 0.82% / 差值 -0.07%
- 退出原因发生变化: 62 笔

### 只看候选里 MFE >= 5% 的 short_pullback_restart
- 笔数: 70
- 候选更好: 28 笔
- 候选更差: 36 笔
- 基本一致: 6 笔
- 平均单笔收益: 基线 5.07% / 候选 4.86% / 差值 -0.2%

### 观察
- 候选主要改变的是这些退出路径：
  - `roi` -> `partial_exit`: 34 笔
  - `trailing_stop_loss` -> `partial_exit`: 25 笔
  - `stale_flat_120h` -> `partial_exit`: 2 笔
  - `stale_low_profit_240h` -> `partial_exit`: 1 笔

### 共享交易 vs 新增交易贡献
- 共享交易总利润变化: `+20.94 USDT`
- 候选新增 14 笔交易总利润: `+83.00 USDT`
- 结论：三年提升不主要来自“同一笔强单明显多赚”，而更主要来自**更早释放仓位后拿到的新增交易**。
- 新增交易 tag 贡献：
  - `short_compression_breakdown`: `5` 笔 / `+50.48 USDT`
  - `short_pullback_restart`: `9` 笔 / `+32.53 USDT`

### 候选改善最多的 5 笔 short_pullback_restart
- 2024-09-03 14:00:00+00:00 / ZEC/USDT:USDT: 0.01% -> 6.41% (`trailing_stop_loss` -> `partial_exit`)
- 2025-03-09 03:00:00+00:00 / ZEC/USDT:USDT: -0.02% -> 5.7% (`trailing_stop_loss` -> `partial_exit`)
- 2024-09-05 04:00:00+00:00 / BTC/USDT:USDT: -0.03% -> 5.66% (`trailing_stop_loss` -> `partial_exit`)
- 2025-02-27 15:00:00+00:00 / BNB/USDT:USDT: -0.03% -> 5.47% (`trailing_stop_loss` -> `partial_exit`)
- 2025-02-26 14:00:00+00:00 / BTC/USDT:USDT: 0.02% -> 5.49% (`trailing_stop_loss` -> `partial_exit`)

### 候选变差最多的 5 笔 short_pullback_restart
- 2024-11-02 13:00:00+00:00 / TAO/USDT:USDT: 10.0% -> 5.01% (`roi` -> `partial_exit`)
- 2024-08-30 12:00:00+00:00 / ADA/USDT:USDT: 10.01% -> 5.04% (`roi` -> `partial_exit`)
- 2025-01-26 22:00:00+00:00 / ZEC/USDT:USDT: 10.0% -> 5.03% (`roi` -> `partial_exit`)
- 2025-02-16 14:00:00+00:00 / SOL/USDT:USDT: 10.0% -> 5.03% (`roi` -> `partial_exit`)
- 2025-01-26 21:00:00+00:00 / SUI/USDT:USDT: 10.0% -> 5.04% (`roi` -> `partial_exit`)

## 1y
- 基线总交易数: 127
- 候选总交易数: 135
- 同开仓可直接对照: 127
- 仅基线存在: 0
- 仅候选存在: 8

### short_pullback_restart 同开仓对照
- 对照笔数: 82
- 候选更好: 34 笔
- 候选更差: 28 笔
- 基本一致: 20 笔
- 平均单笔收益: 基线 1.12% / 候选 1.11% / 差值 -0.0%
- 退出原因发生变化: 27 笔

### 只看候选里 MFE >= 5% 的 short_pullback_restart
- 笔数: 30
- 候选更好: 14 笔
- 候选更差: 15 笔
- 基本一致: 1 笔
- 平均单笔收益: 基线 4.83% / 候选 4.82% / 差值 -0.01%

### 观察
- 候选主要改变的是这些退出路径：
  - `roi` -> `partial_exit`: 14 笔
  - `trailing_stop_loss` -> `partial_exit`: 10 笔
  - `stale_flat_120h` -> `partial_exit`: 2 笔
  - `stale_low_profit_240h` -> `partial_exit`: 1 笔

### 共享交易 vs 新增交易贡献
- 共享交易总利润变化: `+43.10 USDT`
- 候选新增 8 笔交易总利润: `+17.20 USDT`
- 结论：近一年提升既有共享交易改善，也有新增交易贡献，但两者里**共享交易改善更重要**。
- 新增交易 tag 贡献：
  - `short_compression_breakdown`: `5` 笔 / `+27.01 USDT`
  - `short_pullback_restart`: `3` 笔 / `-9.81 USDT`

### 候选改善最多的 5 笔 short_pullback_restart
- 2025-06-21 18:00:00+00:00 / SOL/USDT:USDT: 0.01% -> 5.48% (`trailing_stop_loss` -> `partial_exit`)
- 2026-02-10 07:00:00+00:00 / DOGE/USDT:USDT: -0.02% -> 5.35% (`trailing_stop_loss` -> `partial_exit`)
- 2026-01-25 05:00:00+00:00 / TAO/USDT:USDT: -0.0% -> 5.29% (`trailing_stop_loss` -> `partial_exit`)
- 2026-04-01 14:00:00+00:00 / BNB/USDT:USDT: 0.01% -> 5.25% (`trailing_stop_loss` -> `partial_exit`)
- 2026-02-22 13:00:00+00:00 / XRP/USDT:USDT: -0.05% -> 5.18% (`trailing_stop_loss` -> `partial_exit`)

### 候选变差最多的 5 笔 short_pullback_restart
- 2026-01-31 09:00:00+00:00 / BNB/USDT:USDT: 10.0% -> 5.05% (`roi` -> `partial_exit`)
- 2026-05-31 15:00:00+00:00 / SOL/USDT:USDT: 10.0% -> 5.11% (`roi` -> `partial_exit`)
- 2026-06-05 03:00:00+00:00 / ETH/USDT:USDT: 10.0% -> 5.15% (`roi` -> `partial_exit`)
- 2025-11-20 16:00:00+00:00 / ETH/USDT:USDT: 10.0% -> 5.19% (`roi` -> `partial_exit`)
- 2025-11-20 16:00:00+00:00 / XRP/USDT:USDT: 10.0% -> 5.22% (`roi` -> `partial_exit`)

## 总结
- 这份对照只回答“同一笔开仓”被候选改成什么结果，不讨论新增/减少交易带来的资金占用变化。
- 从结果看，当前候选的优势并不单纯是“reach5 强单单笔利润更大”。
- 三年里，它更像是：**把一部分原本会走到 10% ROI 的单子，改成了 5% 左右的 partial_exit，然后靠更早腾出槽位拿到后续新增交易，最后总收益反而更高。**
- 近一年里，共享交易本身也有改善，但 `short_pullback_restart` 的同单平均收益并没有明显抬高。
- 这意味着下一步如果继续优化，重点不该是继续放大“更早 partial_exit”，而应该是：
  1. 保留它释放槽位的优点
  2. 尽量少砍掉原本能稳定走到 10% ROI 的真强单
