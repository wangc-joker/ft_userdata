# Positive13 Current Exit Logic Summary

## Effective Baseline Settings

- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Hard fallback stoploss: `-0.06` (-6%).
- `use_custom_stoploss=True`: short uses entry structure high + 0.2 ATR, long uses daily structure stop; both are capped to no more than 5% price risk.
- Standard trailing stop enabled: `False`.
- `trailing_stop_positive=None`.
- `trailing_stop_positive_offset=0.0`.
- `trailing_only_offset_is_reached=False`.
- Minimal ROI: `{"0": 0.1}`; 10% ROI is available immediately.
- `custom_stoploss` exists for both directions through the inheritance chain.
- `custom_exit` exists: shorts use stale-loss/flat/low-profit time exits and 4H trend flip; longs use daily trend flip, center/EMA structure exit, and swing exit.
- `populate_exit_trend` emits no explicit dataframe exit signal. `force_exit` remains a framework/manual terminal reason; emergency exit uses Freqtrade defaults because the strategy does not override it.
- Freqtrade labels custom-stop updates as `trailing_stop_loss` even though standard trailing is disabled.

## How Exits Trigger

- Loss control: the entry structural stop is converted to an absolute custom stop; the -6% setting is the fallback only.
- Profit taking: ROI exits at 10%, plus custom structural/time exits. There is no configured standard profit trailing curve.
- Short custom exits: loss after 72h, below 1% after 120h, below 3% after 240h, or 4H trend flips up while profit is below 3%.
- Long custom exits: daily downtrend, daily center below fast EMA, or close below daily swing structure stop.

## Three-Year Exit Reason Distribution

| Exit reason | Trades | Share |
|---|---:|---:|
| stop_loss | 119 | 40.89% |
| roi | 89 | 30.58% |
| trailing_stop_loss | 33 | 11.34% |
| stale_loss_72h | 33 | 11.34% |
| stale_flat_120h | 10 | 3.44% |
| swing_exit_long_1d | 5 | 1.72% |
| stale_low_profit_240h | 1 | 0.34% |
| force_exit | 1 | 0.34% |
