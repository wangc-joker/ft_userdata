# Strategy File Placement Rules

This file is the canonical rule set for strategy file placement in this repository.
Any AI that edits strategy files must read and follow it before making changes.

## Directory Rules

- `myStrage/`
  - Only keep the current main strategy and the two historical benchmark families that we still compare against.
  - Current allowed files:
    - `Top9MainTrendStrategy.py`
    - `Top9MainReversal193Strategy.py`
    - `Top9MainReversalZec216Strategy.py`
    - `Top9MainReversal216ShortAggressiveStrategy.py`
  - Do not place experimental, test-live, or one-off validation strategies here.

- `run/`
  - Only keep strategies that are actively used by running live / test-live bots.
  - If a strategy is not currently running, move it out of `run/`.

- `test/`
  - Put all experimental, comparison, validation, and non-production strategies here.
  - If a strategy is used for a one-off backtest or research branch, it belongs here.
  - Retired test strategies should be removed from the active tree and preserved only in research notes and backtest archives.

- `entrypoints/`
  - Keep Freqtrade-facing implementation entry classes here.
  - These files are not the user-facing strategy homes; they are shared logic entry points.

- `core/`, `signals/`, `pairs/`, `shared/`
  - Keep shared logic, indicators, market-state classification, pair profiles, and constants here.

- `archive/`
  - Keep historical and retired strategy families here.
  - `CombinedTrendCaptureMilestoneV1*` and `CombinedTrendCaptureMilestoneV2*` are archival families.

## Main / 216 Reference Information

- Main baseline:
  - File: `myStrage/Top9MainTrendStrategy.py`
  - Backtest config: `config.backtest.futures.top9.json`
  - Reference口径: `1000 USDT`, `max_open_trades = 3`, `enable_protections = true`, no leverage override
  - Historical benchmark: `169.86%`, `373` trades, `9.07%` max drawdown

- 193 reversal reference:
  - File: `myStrage/Top9MainReversal193Strategy.py`
  - Historical benchmark: `193.48%`, `386` trades, `9.31%` max drawdown

- 216 reference:
  - Base ZEC-only version: `myStrage/Top9MainReversalZec216Strategy.py`
  - Yield-focused version: `myStrage/Top9MainReversal216ShortAggressiveStrategy.py`
  - Keep 216 as a ZEC-focused research line unless a new doc explicitly says otherwise.

## Editing Rules

- Before creating, renaming, or moving strategy files:
  - Check whether the target belongs in `myStrage/`, `run/`, `test/`, or `archive/`.
  - Do not leave experimental strategies in `myStrage/`.
  - Do not leave live-only strategies in `test/`.
- After any strategy file move or rename:
  - Update `README.md`.
  - Update `策略架构说明.md`.
  - Update `策略总览.md` if the visible strategy list or benchmark values changed.
- Keep strategy JSON parameter files next to the strategy file they belong to.
- If a strategy file is moved, its parameter JSON must be moved or recreated with the same basename.

## Non-Production Strategy Note

- The range swing strategy has been retired.
- Keep its思路说明和回测结果 in `research/` and `backtest_results/`.
- Do not keep executable range swing code in `test/`, `myStrage/`, or `run/`.
