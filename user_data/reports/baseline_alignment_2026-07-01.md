# Baseline Alignment 2026-07-01

## Why the numbers looked inconsistent

Several different "baselines" were discussed in the thread, but they are not the same test line.

The most confusing numbers were:

- `187.22%`
- `151.13%`
- `141.04%`

They come from different universes and, in one case, a different evaluation method.

## Aligned reference table

| Label | Strategy | Universe / Slots | Sample | Method | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| Positive13 raw baseline recheck | `DualTrendCombinedShortPullbackShapeV1Strategy` | Positive13 / max3 | 2023-06-18 -> 2026-06-18 | Full Docker backtest | 241 | 151.13% | 2.01 | 7.24% | 34.44% |
| Positive13 old profit-lock report baseline | `DualTrendCombinedShortPullbackShapeV1Strategy` | Positive13 / max3 | 3Y sample in report | Offline exit-model comparison | 291 | 199.34% | 2.00 | 8.87% | 35.05% |
| Positive13 old profit-lock report breakeven-only | `DualTrendCombinedShortPullbackShapeV1Strategy` + BE-only exit model | Positive13 / max3 | 3Y sample in report | Offline exit-model comparison | 291 | 187.22% | 2.36 | 7.30% | 59.11% |
| Positive13 current baseline branch | `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy` | Positive13 / max3 | 2023-06-18 -> 2026-05-08 | Full Docker backtest | not preserved in current note | not restated here | not restated here | not restated here | not restated here |
| Positive13 current guard branch | `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy` | Positive13 / max3 | 2023-06-18 -> 2026-05-08 | Full Docker backtest | 309 | 138.34% | 2.20 | 5.77% | 50.16% |
| Top30 expanded baseline branch | `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy` | Top30 / max6 | 2023-06-18 -> 2026-05-08 | Full Docker backtest | 381 | 141.04% | 2.03 | 4.92% | 47.24% |
| Top30 expanded guard branch | `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy` | Top30 / max6 | 2023-06-18 -> 2026-05-08 | Full Docker backtest | 374 | 148.91% | 2.09 | 4.91% | 47.59% |

## The key conclusion

### `187.22%` is **not** comparable to `141.04%`

Because:

1. `187.22%` came from `positive13_profit_lock_validation.md`
2. that report was an **offline exit counterfactual**, not a fresh full Docker rerun
3. it used the `Positive13 / max3` line
4. `141.04%` came from `Top30 / max6`

So those two values were never the same baseline.

### The closest comparable full-Docker values are:

- Positive13 raw baseline recheck: `151.13%`
- Top30 expanded baseline branch: `141.04%`

Those are still different test lines, but at least both are full Docker backtests.

## Practical reading order going forward

When we discuss the strategy now, use this order:

1. `Top30 / max6` baseline branch
2. `Top30 / max6` guard branch
3. `Positive13 / max3` only as a smaller-universe validation line

That keeps future comparisons on the same branch family and same style of test.
