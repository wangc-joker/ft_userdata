# Top30 Max6 Guard Validation

Date: 2026-07-01

## Scope

Compare:

- Baseline: `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`
- Guard: `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy`

Config:

- Pair universe: Top30
- `max_open_trades = 6`
- timeframe: `1h`
- detail timeframe: `5m`

Samples:

- 3Y: `2023-06-18 -> 2026-05-08`
- 1Y: `2025-06-18 -> 2026-05-08`

## Headline Result

The guard branch still beats baseline after expanding from Positive13 to Top30 and increasing slots to 6.

## Summary Table

| Sample | Strategy | Trades | Profit % | Profit Abs | PF | MaxDD % | Winrate % |
|---|---|---:|---:|---:|---:|---:|---:|
| 3Y | Baseline | 381 | 141.04 | 1410.411 | 2.0254 | 4.92 | 47.24 |
| 3Y | Guard | 374 | 148.91 | 1489.139 | 2.0939 | 4.91 | 47.59 |
| 1Y | Baseline | 140 | 36.85 | 368.527 | 2.1787 | 4.86 | 52.14 |
| 1Y | Guard | 139 | 37.97 | 379.672 | 2.2432 | 4.86 | 52.52 |

## Tag Breakdown

### 3Y

| Strategy | short_pullback_restart | Trades | short_compression_breakdown | Trades | long_1d_center_compression | Trades |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 68.57 | 214 | 20.33 | 96 | 52.14 | 71 |
| Guard | 70.37 | 212 | 25.79 | 90 | 52.75 | 72 |

### 1Y

| Strategy | short_pullback_restart | Trades | short_compression_breakdown | Trades | long_1d_center_compression | Trades |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 19.19 | 86 | -0.25 | 39 | 17.91 | 15 |
| Guard | 19.40 | 86 | 0.65 | 38 | 17.93 | 15 |

## Interpretation

1. The uplift survives expansion to a broader universe.
2. The main improvement still comes from `short_compression_breakdown`.
3. `short_pullback_restart` remains the core engine and is not damaged.
4. Drawdown did not worsen in this Top30+Max6 validation.

## Conclusion

`DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy` is the better branch than the previous baseline under:

- broader Top30 universe
- larger slot count
- both 3Y and 1Y samples

At this stage it is reasonable to keep the guard branch as the main candidate for the next round of false-breakdown / bad-signal filtering work.
