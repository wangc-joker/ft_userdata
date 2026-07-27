# Higher-Low Reclaim Experiment - 2026-07-21

Read `../../../CURRENT_DUALTREND.md` and `../../reports/dualtrend_higher_low_reclaim_experiment_2026-07-21.md` before using these artifacts.

## Artifacts

- `smoke/`: 2026-03-01 through 2026-03-15 engineering smoke test for strategy loading and execution.
- `max100_five_year/backtest-result-2026-07-21_11-28-05.zip`: retained five-year Positive13 diagnostic run using Freqtrade 2026.3, 1h plus 5m detail, protections, and `max_open_trades=100`.

## Status

`long_higher_low_reclaim_1h` is rejected. Its isolated five-year tag result was 452 trades, `-269.154896 USDT`, and profit factor `0.807306`. The add-on also reduced the SecondAdd20 diagnostic portfolio and materially increased drawdown.

The archived `DualTrendHigherLowOnlyV1Strategy` snapshot includes six PAXG parent daily-long trades because the diagnostic clearing step originally ran after the pair-allowlist return. The clearing order was corrected after the run. This does not affect the archived 452-trade higher-low tag row or the add-on strategy result; use tag-level metrics for the pure-pattern conclusion.
