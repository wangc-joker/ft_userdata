# DualTrend Phase 1A Early-Fail Exit 验证结果

日期：2026-07-06

## 本轮完成内容

1. 为研究版补上 `_DualTrendEarlyFailExitMixin` 内部的 `_supports_trade_direction()`，修复继承链缺失导致的 `custom_exit` 异常。
2. 使用 docker 重新回测：
   - 3 年样本：`2023-06-18 -> 2026-06-18`
   - 压力期：`2026-03-01 -> 2026-05-31`
3. 对比对象保持为当前主策略：
   - `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`
4. 本轮只研究 short 早退，不修改入场、币池、仓位、杠杆、stoploss、reach5。

## 策略版本

- 基线：
  - `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`
- 研究版：
  - `DualTrendEarlyFailPhase1AStrategy`

## 回测结果对比

### 3 年样本

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 335 | 155.07% | 2.22 | 5.77% | 52.8% |
| Phase 1A | 349 | 138.46% | 2.18 | 7.79% | 46.4% |

结论：

- Phase 1A 3 年总收益明显低于基线，下降约 `16.61` 个百分点。
- PF 也略低。
- 回撤反而变大，从 `5.77%` 上升到 `7.79%`。
- 胜率明显下降。

### 压力期

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 20 | 1.91% | 1.38 | 3.30% | 35.0% |
| Phase 1A | 20 | 3.51% | 2.03 | 2.04% | 35.0% |

结论：

- Phase 1A 在压力期确实更好。
- 收益更高，PF 更高，回撤更小。
- 说明“坏 breakdown / 快速反转”这条思路不是错的，方向是有效的。

## 按 tag 观察

### 3 年样本 tag 汇总

- 基线：
  - `short_pullback_restart`: `75.49%`
  - `short_compression_breakdown`: `26.76%`
  - `long_1d_center_compression`: `52.82%`
- Phase 1A：
  - `short_pullback_restart`: `76.02%`
  - `short_compression_breakdown`: `12.13%`
  - `long_1d_center_compression`: `50.32%`

结论：

- `short_pullback_restart` 基本持平。
- 真正被打坏的是 `short_compression_breakdown`，从 `26.76%` 掉到 `12.13%`。
- 这说明目前的早退条件对 compression breakdown 过于敏感，误杀了后续本可走开的单子。

## Exit Reason 观察

3 年样本中，Phase 1A 新增退出原因的损益如下：

- `early_fail_short_pullback_reclaim`: `-19.90%`
- `early_fail_short_breakdown_reclaim`: `-13.79%`
- `early_fail_short_breakdown_ema_reclaim`: `-5.13%`
- `early_fail_short_pullback_btc_flip`: `-0.25%`
- `early_fail_short_breakdown_btc_flip`: `-1.13%`

解读：

- 这些早退本身都是小亏退出，逻辑上是在“提前认错”。
- 压力期里它们有效减少了更差的 stoploss。
- 但在 3 年总样本里，当前阈值明显太紧，导致大量本可恢复的 `short_compression_breakdown` 被过早砍掉。

## 本轮结论

### 可以确认的事

1. Phase 1A 的方向是有价值的：
   - 在压力期能改善收益和回撤。
2. 但当前实现不适合直接替换主策略：
   - 3 年收益下降
   - PF 略降
   - MaxDD 变差
3. 目前最需要收紧研究范围的是：
   - 不要同时对 `short_pullback_restart` 和 `short_compression_breakdown` 用同样激进的早退框架
   - 尤其不能继续用当前强度去砍 `short_compression_breakdown`

### 是否进入主线

- 结论：**暂不进入主线**
- 当前主策略保持不变：
  - `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

## 下一步建议

如果继续做 Phase 1A，建议只做更窄的一步：

1. 只保留 `short_compression_breakdown` 的“最弱 reclaim 退出”或只保留 BTC flip 版本。
2. 暂时不要对 `short_pullback_restart` 动手。
3. 或者只把 early-fail 限定在：
   - 开仓后 `<= 3h`
   - `current_profit <= 0`
   - reclaim 并且 center 明显上移

这样更像“只砍最坏的假 breakdown”，而不是普遍提前止损。
