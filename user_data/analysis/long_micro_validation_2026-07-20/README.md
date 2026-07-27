# LongMicro validation artifacts - 2026-07-20

This directory preserves the parameter-collision diagnosis and the corrected backtests. Read `../../../CURRENT_DUALTREND.md` and `../../reports/dualtrend_long_micro_parameter_collision_audit_2026-07-20.md` before using any archive here.

## Corrected evidence

- `corrected_control_2021_max100/`: disabled-entry control proving the parent daily-long behavior is unchanged after parameter isolation.
- `corrected_positive13/`: Positive13/max3 three-year baseline and corrected candidate.
- `corrected_positive13_five_year-*`: Positive13/max3 five-year baseline and corrected candidate.
- `corrected_positive13_near_year-*` and `corrected_positive13_pressure-*`: corrected short windows.
- `corrected_rolling_*`: independent annual windows with executed Micro entries.
- `corrected_top20_three_year-*` and `corrected_top20_five_year-*`: corrected Top20/max6 candidate runs.
- `metadata_consistency_mainnet/`: mainnet baseline reproduction used for the Top20 three-year control.

## Diagnostic or invalid candidate evidence

- `disabled_control_2021_max100/`: pre-fix disabled-entry control that exposed the parent-parameter override.
- `signal_audit_2021*`, `rolling_positive13/`, and `top20_max6_mainnet/`: pre-fix LongMicro results; candidate metrics are invalid, while unchanged baseline rows remain diagnostic evidence.
- `metadata_consistency/` and `config.exchange-metadata-testnet.json`: rejected testnet metadata comparison. It produced a different market universe and is not comparable with mainnet results.

Do not promote figures from a path lacking the `corrected_` prefix unless the 2026-07-20 audit explicitly identifies that row as a valid control.
