# PAIR/BTC Relative-Strength Diagnostic

## Frozen rule

- Scope: existing non-BTC long entries from the corrected five-year LongMicro archive.
- Signal candle: latest completed 1h candle strictly before `open_date`.
- Pass: `EMA24(PAIR/BTC) > EMA72(PAIR/BTC)` and `EMA24` is above its value six hours earlier.
- BTC entries pass through unchanged and are excluded from the pass/reject attribution below.
- Feature availability: 100.00% (42/42).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall non-BTC longs

| rs_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pass | 32 | 10 | 0.312 | 497.362 | 15.543 | 0.650 | 4.677 |
| reject | 10 | 4 | 0.400 | 79.160 | 7.916 | 0.158 | 2.735 |

## By entry tag

| enter_tag | rs_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_1d_center_compression | pass | 30 | 8 | 0.267 | 433.348 | 14.445 | 0.547 | 4.204 |
| long_1d_center_compression | reject | 7 | 3 | 0.429 | 63.882 | 9.126 | 0.101 | 4.896 |
| long_pullback_restart_1h_body | pass | 2 | 2 | 1.000 | 64.015 | 32.007 | 0.104 | inf |
| long_pullback_restart_1h_body | reject | 3 | 1 | 0.333 | 15.278 | 5.093 | 0.057 | 1.523 |

## By entry year

| entry_year | rs_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | pass | 4 | 0 | 0.000 | -18.285 | -4.571 | -0.053 | 0.000 |
| 2021 | reject | 1 | 0 | 0.000 | -7.249 | -7.249 | -0.021 | 0.000 |
| 2023 | pass | 6 | 1 | 0.167 | -35.406 | -5.901 | -0.083 | 0.027 |
| 2023 | reject | 1 | 0 | 0.000 | -8.850 | -8.850 | -0.021 | 0.000 |
| 2024 | pass | 11 | 4 | 0.364 | 214.100 | 19.464 | 0.373 | 16.448 |
| 2024 | reject | 2 | 2 | 1.000 | 83.368 | 41.684 | 0.200 | inf |
| 2025 | pass | 10 | 4 | 0.400 | 238.637 | 23.864 | 0.313 | 4.577 |
| 2025 | reject | 6 | 2 | 0.333 | 11.891 | 1.982 | -0.000 | 1.403 |
| 2026 | pass | 1 | 1 | 1.000 | 98.317 | 98.317 | 0.100 | inf |

## BTC passthrough

| enter_tag | rs_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_1d_center_compression | btc_passthrough | 15 | 4 | 0.267 | 133.748 | 8.917 | 0.288 | 3.022 |
| long_pullback_restart_1h_body | btc_passthrough | 2 | 0 | 0.000 | -3.030 | -1.515 | -0.008 | 0.000 |

## LongMicro trades

| pair | open_date | profit_abs | profit_ratio | rs_ema24 | rs_ema72 | rs_slope_6h | rs_state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BNB/USDT:USDT | 2023-12-21 09:00:00+00:00 | 0.996 | 0.004 | 0.006 | 0.006 | 0.001 | pass |
| BNB/USDT:USDT | 2024-02-07 17:00:00+00:00 | 44.511 | 0.100 | 0.007 | 0.007 | 0.000 | reject |
| BNB/USDT:USDT | 2025-01-17 09:00:00+00:00 | -13.058 | -0.021 | 0.007 | 0.007 | -0.003 | reject |
| BNB/USDT:USDT | 2025-06-10 21:00:00+00:00 | -16.176 | -0.022 | 0.006 | 0.006 | 0.002 | reject |
| BNB/USDT:USDT | 2025-08-07 23:00:00+00:00 | 63.019 | 0.100 | 0.007 | 0.007 | 0.000 | pass |
| BTC/USDT:USDT | 2023-12-16 16:00:00+00:00 | -2.794 | -0.007 | 1.000 | 1.000 | 0.000 | btc_passthrough |
| BTC/USDT:USDT | 2025-01-06 05:00:00+00:00 | -0.236 | -0.000 | 1.000 | 1.000 | 0.000 | btc_passthrough |
