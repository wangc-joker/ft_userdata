# Positive13 Dry-Run Weekly Report - 2026-06-23

## Overview

- Period: 2026-06-17 to 2026-06-23
- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Database: `not found`
- Closed trades: 0; open positions: 0
- Profit: 0.0000 (0.00% sum)
- PF: N/A; MaxDD: N/A; Win rate: N/A
- Average profit: N/A; average duration: N/A h
- Long: 0 trades / 0.0000 profit
- Short: 0 trades / 0.0000 profit

## Backtest Guardrails

Reference: 3y baseline PF 2.00 / MaxDD 7.66%; fee2x + heavy PF 1.72 / MaxDD 10.89%; recent-year PF 2.00.

| Check | Result |
| --- | --- |
| PF below 1.5 | insufficient |
| MaxDD near/above 10% | insufficient |
| Average slippage at heavy level | insufficient |
| Cost exceeds fee2x + heavy proxy (0.20%) | insufficient |

## Pair x Entry Tag x Side

| Pair | Entry tag | Side | Trades | Profit | PF | Win rate | Avg MAE | Avg MFE | Quick reverse | False down | Range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No data |  |  |  |  |  |  |  |  |  |  |  |

## Risk Features

| Metric | Value |
| --- | --- |
| Quick reverse rate | N/A |
| False breakdown rate | N/A |
| False breakout rate | N/A |
| Range market rate | N/A |
| Average slippage | N/A |
| Maximum slippage | N/A |
| Total fee rate | 0.00% |
| Total funding fee | 0.0000 |

BTC 4H regime distribution: {}

Pair 4H regime distribution: {}

## Anomalies

- Worst pair: {}
- Worst entry tag: {}
- Highest average-slippage pair: {}
- Highest funding-cost pair: {}
- Risk events: {}

## Weekly Decision

- Risk level: **YELLOW**
- Continue dry-run: **Yes**
- Pause new entries: **No**
- Manual inspection required: **No**
- Return to offline optimization: **No**
- Consider small-capital live trading: **No until sample and execution gates are met**
- Action: **Continue dry-run; do not add capital.**
- Only 0 closed trades; statistical sample is insufficient.
- There are 1 data/config warnings.

Current dry-run sample is insufficient for statistical conclusions.

## Warnings

- No Positive13 dry-run database found. Old NFI databases were intentionally ignored; use --db-path when the bot database exists.
