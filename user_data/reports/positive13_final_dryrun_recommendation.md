# Positive13 Final Dry-Run Recommendation

## Current Decision

Continue dry-run with **Positive13 + Combined + max_open_trades=3**. Do not change the strategy, remove pairs, disable entry tags, split the bot, or add slots during this observation phase.

- Current risk level: **YELLOW**
- Closed dry-run samples: **0**
- Strategy file: `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py`
- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Config: `D:\test\ft_userdata\user_data\config.dryrun.dualtrend.combined.top50.positive13.max3.json`
- Pair pool: ETH/USDT:USDT, ZEC/USDT:USDT, BTC/USDT:USDT, ADA/USDT:USDT, BNB/USDT:USDT, SOL/USDT:USDT, DOGE/USDT:USDT, XRP/USDT:USDT, TAO/USDT:USDT, SUI/USDT:USDT, PAXG/USDT:USDT, NEAR/USDT:USDT, LINK/USDT:USDT
- max_open_trades: 3
- Keep long: Yes
- Keep both short entry tags: Yes
- Remove pairs: No
- Split bot: No
- Modify strategy: No

## Monitoring Priorities

The highest-priority fields are false breakdown, quick reverse, range-market exposure, actual slippage, fees, funding cost, MAE/MFE and slot saturation. Entry slippage uses requested price when stored; otherwise it is an estimate against the entry 1H close. False-breakdown and false-breakout use pre-entry 12/24-bar extrema because compression custom data is not stored in the trade database.

## Small-Capital Gate

Only consider small-capital live trading after at least 30 closed trades and at least four full observation weeks, with PF >= 1.5, MaxDD < 8%, no persistent pair/tag PF below 0.7, average slippage below 0.05%, no execution/data incidents, and false-breakdown/quick-reverse rates not materially above the historical diagnostic baseline.

## Mandatory Pause Gate

Pause new entries if PF < 1.0, MaxDD > 12%, the loss streak reaches eight trades, actual slippage persistently exceeds 0.10%, a serious API/data anomaly appears, or a single-day loss breaches the operator's approved capital threshold. Existing positions should continue to exit according to the unchanged strategy.
