# Strategy Name Map 2026-07-01

## New short names

Main public names are now:

- `DualTrendRawStrategy`
- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

## Meaning

- `DualTrendRawStrategy`
  - raw combined strategy
  - equivalent to the old `DualTrendCombinedShortPullbackShapeV1Strategy`

- `DualTrendBaselineStrategy`
  - main baseline branch
  - equivalent to the old `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`

- `DualTrendGuardStrategy`
  - current main candidate with compression flush guard
  - equivalent to the old `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy`

## Backward compatibility

Old names are still kept as compatibility aliases for now:

- `DualTrendCombinedShortPullbackShapeV1Strategy`
- `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`
- `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy`

## Config update

Updated configs:

- `config.backtest.dualtrend.combined.top30.max6.json`
  - strategy -> `DualTrendRawStrategy`

- `config.backtest.dualtrend.combined.top50.positive13.max3.json`
  - strategy -> `DualTrendRawStrategy`

- `config.dryrun.dualtrend.combined.top50.positive13.max3.json`
  - strategy -> `DualTrendGuardStrategy`
