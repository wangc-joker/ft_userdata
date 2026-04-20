# NFI Candidate: Top10 + 1000U + Max2 + 3Y

## Purpose

This file records the current best completed result from the 3-year volume-ranked Binance futures screening for `NostalgiaForInfinityX7`.

Candidate config:

- `user_data/config.backtest.nfi.candidate.top10.1000u.max2.3y.json`

Source test workspace:

- `user_data/tests/nfi_top_volume_3y_1000u`

## Rules Used

- Strategy: `NostalgiaForInfinityX7`
- Exchange universe source: Binance USDT perpetual futures
- Ranking basis: current 24h `quoteVolume`
- Exclusions: leveraged-style symbols such as `*BULL`, `*BEAR`, `*UP`, `*DOWN`
- History requirement: pair must have a complete local backtest data window across `5m`, `15m`, `1h`, `4h`, `1d`
- Effective complete 3-year window in local data: `2023-04-16 -> 2026-04-16`

## Selected Top10 Pool

1. `BTC/USDT:USDT`
2. `ETH/USDT:USDT`
3. `SOL/USDT:USDT`
4. `XRP/USDT:USDT`
5. `DOGE/USDT:USDT`
6. `ZEC/USDT:USDT`
7. `HIGH/USDT:USDT`
8. `AAVE/USDT:USDT`
9. `BNB/USDT:USDT`
10. `ENJ/USDT:USDT`

## Completed Result

Completed backtest:

- Pair count: `10`
- Max open trades: `2`
- Starting balance: `1000 USDT`
- Final balance: `7177.844706 USDT`
- Profit: `6177.844706 USDT`
- Total return: `617.78%`
- CAGR: `93.0155%`
- Max drawdown: `47.4362%`
- Trades: `126`
- Win rate: `99.2063%`

This is currently the best completed result, not yet the confirmed global optimum for `10/20/30/40/60 x 2/3/4/5/6`.

## Current Limitation

The larger combinations starting from `Top20` are not completed yet on this machine. The backtest process is being terminated during computation, which currently looks like an environment resource limit rather than a strategy/config error.

Relevant working directory:

- `user_data/tests/nfi_top_volume_3y_1000u/backtest_runs`

## Re-run Command

```powershell
docker compose run --rm freqtrade backtesting `
  --config /freqtrade/user_data/config.backtest.nfi.candidate.top10.1000u.max2.3y.json `
  --strategy NostalgiaForInfinityX7 `
  --timerange 20230416-20260416 `
  --cache none `
  --export trades `
  --backtest-directory /freqtrade/user_data/backtest_results
```

## Notes

- This candidate file does not modify `NostalgiaForInfinityX7`.
- This candidate file does not replace the broader screening configs under `user_data/tests/nfi_top_volume_3y_1000u`.
- If the remaining `Top20+` combinations are completed later, this candidate should be re-validated against the full result table.
