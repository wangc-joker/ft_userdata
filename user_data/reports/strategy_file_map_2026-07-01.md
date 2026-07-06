# Strategy File Map 2026-07-01

## Main strategy file

The main active strategy file has been renamed to:

- `user_data/strategies/DualTrendMainStrategies.py`

## Why

The old filename was too long:

- `DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py`

The new filename is shorter and easier to remember while still clearly marking it as the main DualTrend strategy file.

## Backward compatibility

The old filename is still kept as a compatibility shim:

- `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py`

It now only re-exports everything from:

- `user_data/strategies/DualTrendMainStrategies.py`

This means:

1. old references do not immediately break
2. new work should use `DualTrendMainStrategies.py`
3. future documentation should point to the new file

## Current important files

- main active strategy file:
  - `user_data/strategies/DualTrendMainStrategies.py`

- combined long/short base:
  - `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1Strategy.py`

- short-only structural base:
  - `user_data/strategies/DualTrendCompressionRestartShortV1Strategy.py`
