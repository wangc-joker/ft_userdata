# Range Swing Research Retired

This note preserves the last iteration of the Top9 range swing idea for future reference.
The executable strategy code has been removed from the active tree.

## Idea Summary

- Only consider entries when the **daily timeframe** is already in a range / sideways state.
- Require the range to be meaningful enough to justify a trade:
  - do not trade tiny ranges
  - avoid mid-range entries
  - only trade near the range high or low
- Use the **1h timeframe** for the actual trigger:
  - at the range high: look for reversal structure, descending triangle, or center-of-gravity compression / lower center
  - at the range low: use the mirrored bullish structure
  - require breakout or breakout-retest confirmation before entry
- Stoploss should be based on the 1h structure or nearby swing extreme, capped around 2%.
- If the range has already been touched many times, reduce size and tighten conditions because breakout risk increases.

## Final Test Setup

- Initial capital: `500 USDT`
- `max_open_trades = 3`
- No leverage
- Futures, isolated margin

## Final Outcome

The range swing idea improved during iteration, but it never turned into a stable positive strategy.

Latest recorded result:

- Trades: `19`
- Total profit: `-0.23%`
- Final balance: `498.863 USDT`
- Max drawdown: `0.89%`
- Win rate: `6 / 19`
- Profit factor: `0.8769`

Earlier broader version:

- Trades: `44`
- Total profit: `-0.59%`
- Final balance: `497.031 USDT`
- Max drawdown: `3.15%`

## Reference Results

- Latest result archive:
  - [backtest-result-2026-04-14_09-15-20.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-04-14_09-15-20.zip)
  - [backtest-result-2026-04-14_09-15-20.meta.json](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-04-14_09-15-20.meta.json)
- Earlier broader version:
  - [backtest-result-2026-04-14_08-49-57.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-04-14_08-49-57.zip)
  - [backtest-result-2026-04-14_08-49-57.meta.json](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-04-14_08-49-57.meta.json)

## Why It Was Retired

- The entry logic became too specific for the reward it produced.
- Even after tightening the daily range filter and weighting the better pairs more heavily, the strategy still failed to produce a stable positive edge.
- The idea is kept here as a research reference only.
