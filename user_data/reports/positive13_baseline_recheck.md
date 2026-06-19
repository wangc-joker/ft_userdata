# Positive13 Baseline Recheck

- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Config: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json`
- Local schema override: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`
- Pair pool: Positive13 from config pair whitelist
- max_open_trades: 3
- Trading mode: futures / isolated
- Timeframes used by strategy: 1h, with 4h/1d informative data
- Data note: local data was extended to `2026-06-18` for this recheck.

## Results

| Sample | Timerange | Trades | Profit | PF | MaxDD | Winrate | Worst Month | Worst Pair |
|---|---|---:|---:|---:|---:|---:|---|---|
| 3y | 2023-06-18 -> 2026-06-18 | 241 | 151.13% / 1511.33 USDT | 2.01 | 7.24% | 34.44% | 2026-03 (-49.81) | NEAR/USDT:USDT (-23.61) |
| 1y | 2025-06-18 -> 2026-06-18 | 101 | 38.78% / 387.78 USDT | 1.86 | 7.17% | 35.64% | 2025-06 (-30.00) | DOGE/USDT:USDT (-33.39) |

## Baseline Reproduction

Baseline reproduced successfully for both required timeranges in the current local environment. The result remains positive, PF stays above 1.6, and MaxDD stays below 12% in both samples.
