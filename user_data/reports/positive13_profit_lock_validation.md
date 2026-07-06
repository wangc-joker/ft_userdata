# Positive13 Profit Lock Validation

- Strategy baseline: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Entry sample: fixed Positive13 max_open_trades=3 baseline trades
- Method: offline exit counterfactual using 1H OHLCV inside each original trade window
- Scope: compares profit-lock exits only; entries, stakes, pair pool, ROI, and structural exits stay fixed

## Summary

| Sample | Model | Trades | Profit | PF | MaxDD | Winrate | Lock exits | Partial exits | Activated | Saved | Hurt |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3y | baseline | 291 | 199.34% / 1993.45 | 2.00 | 8.87% | 35.05% | 0 | 0 | 0 | 0 | 0 |
| 3y | breakeven_only | 291 | 187.22% / 1872.22 | 2.36 | 7.30% | 59.11% | 99 | 0 | 172 | 150 | 141 |
| 3y | loose | 291 | 166.28% / 1662.76 | 2.21 | 6.95% | 59.11% | 107 | 0 | 172 | 147 | 144 |
| 3y | medium | 291 | 171.75% / 1717.45 | 2.25 | 8.63% | 59.11% | 117 | 0 | 172 | 142 | 149 |
| 3y | tight | 291 | 163.74% / 1637.41 | 2.19 | 8.16% | 59.11% | 124 | 0 | 172 | 136 | 155 |
| 3y | partial_ladder_a | 291 | 194.26% / 1942.62 | 2.42 | 7.04% | 59.11% | 99 | 33 | 172 | 159 | 132 |
| 3y | partial_ladder_b | 291 | 176.46% / 1764.56 | 2.29 | 7.56% | 59.11% | 103 | 68 | 172 | 109 | 182 |
| 3y | partial_ladder_c | 291 | 191.52% / 1915.22 | 2.40 | 7.19% | 59.11% | 99 | 7 | 172 | 151 | 140 |
| 1y | baseline | 111 | 51.23% / 512.34 | 2.00 | 7.65% | 39.64% | 0 | 0 | 0 | 0 | 0 |
| 1y | breakeven_only | 111 | 53.43% / 534.28 | 2.67 | 4.95% | 67.57% | 46 | 0 | 75 | 56 | 55 |
| 1y | loose | 111 | 47.67% / 476.75 | 2.49 | 4.52% | 67.57% | 49 | 0 | 75 | 56 | 55 |
| 1y | medium | 111 | 52.68% / 526.76 | 2.65 | 4.04% | 67.57% | 52 | 0 | 75 | 55 | 56 |
| 1y | tight | 111 | 49.14% / 491.43 | 2.54 | 3.81% | 67.57% | 56 | 0 | 75 | 52 | 59 |
| 1y | partial_ladder_a | 111 | 54.42% / 544.25 | 2.70 | 4.91% | 67.57% | 46 | 9 | 75 | 60 | 51 |
| 1y | partial_ladder_b | 111 | 50.03% / 500.29 | 2.56 | 5.05% | 67.57% | 47 | 23 | 75 | 42 | 69 |
| 1y | partial_ladder_c | 111 | 53.43% / 534.28 | 2.67 | 4.95% | 67.57% | 46 | 0 | 75 | 56 | 55 |

## Interpretation

- 3y: baseline profit 199.34%, PF 2.00, MaxDD 8.87%. Best PF model is `partial_ladder_a` with profit 194.26%, PF 2.42, MaxDD 7.04%.
- 1y: baseline profit 51.23%, PF 2.00, MaxDD 7.65%. Best PF model is `partial_ladder_a` with profit 54.42%, PF 2.70, MaxDD 4.91%.

## Notes

- This is not a full Freqtrade rerun because Docker could not load Binance futures markets during this pass.
- The test is still useful for this question because it isolates exit behavior on the same baseline trades.
- Intrabar ordering is approximated from 1H OHLCV, so any final candidate should still receive a Docker backtest when exchange access is available.