# Positive13 Extreme Reversal Signal Audit

## Scope And Method

- Independent signal audit only. No orders, no strategy merge, no live configuration changes.
- Pair pool: Positive13; interval: 2023-06-18 through 2026-06-18.
- RSI/ATR use Wilder smoothing with period 14; EMA20 uses standard exponential smoothing.
- 4H and 1D values are shifted to their candle close time to prevent lookahead bias.
- An extreme episode may wait up to 72 completed 1H candles for confirmation; one signal is emitted per episode.
- Breakout levels use the preceding 6 candles; stops use the preceding 12 candles plus 0.3 ATR.
- Forward path is 72h. If stop and target touch in the same OHLC candle, stop is conservatively counted first.
- A/B/C are overlapping condition sets and must not be added together.

## Variant Results

### A / B / C Comparison

| Group | Signals | Ret 6h | Ret 24h | Ret 72h | MFE/MAE 72h | 1R first | 2R first | Stop first | Avg max/min R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0 | 0.00% | 0.00% | 0.00% | 0.00/0.00% | 0.00% | 0.00% | 0.00% | 0.00/0.00 |
| B | 0 | 0.00% | 0.00% | 0.00% | 0.00/0.00% | 0.00% | 0.00% | 0.00% | 0.00/0.00 |
| C | 0 | 0.00% | 0.00% | 0.00% | 0.00/0.00% | 0.00% | 0.00% | 0.00% | 0.00/0.00 |

### By Side

| Group | Signals | Ret 6h | Ret 24h | Ret 72h | MFE/MAE 72h | 1R first | 2R first | Stop first | Avg max/min R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### By Year

| Group | Signals | Ret 6h | Ret 24h | Ret 72h | MFE/MAE 72h | 1R first | 2R first | Stop first | Avg max/min R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### Variant A By Pair

| Group | Signals | Ret 6h | Ret 24h | Ret 72h | MFE/MAE 72h | 1R first | 2R first | Stop first | Avg max/min R |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### Condition Funnel

| Variant | Side | Extreme candles | Extreme episodes | Confirmations anywhere | Confirmed <=72h | Auditable signals |
|---|---|---:|---:|---:|---:|---:|
| A | long | 6 | 6 | 0 | 0 | 0 |
| A | short | 22 | 12 | 4 | 0 | 0 |
| B | long | 1 | 1 | 0 | 0 | 0 |
| B | short | 11 | 7 | 4 | 0 | 0 |
| C | long | 0 | 0 | 0 | 0 | 0 |
| C | short | 0 | 0 | 4 | 0 | 0 |

## Conclusions

- **Does extreme reversal show a statistical edge?** 样本不足. Variant A has 0 signals; the conclusion is based on forward returns, first-hit rates, and R excursion together rather than return alone.
- **Which side is better?** 无法判断, based on Variant A's combined 24h/72h return and average max-R score. This remains an audit conclusion, not a trading recommendation.
- **Which pairs look effective?** None meet the minimum six-signal directional screen. Pairs below six signals are observation-only.
- **Should it enter strategy backtesting?** Not yet: collect more evidence or revise the audit hypothesis before strategy backtesting.
- RSI 1D 10/90 is used only in super-extreme Variant C, never as the default condition.

## Output Files

- `user_data/analysis/positive13_extreme_reversal_signals.csv`
- `user_data/analysis/positive13_extreme_reversal_summary.csv`
- `user_data/analysis/positive13_extreme_reversal_data_coverage.csv`
- `user_data/analysis/positive13_extreme_reversal_funnel.csv`
- `user_data/reports/positive13_extreme_reversal_signal_audit.md`
