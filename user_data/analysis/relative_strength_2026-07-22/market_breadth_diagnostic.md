# Positive13 4H Market-Breadth Diagnostic

## Frozen rule

- Universe: the 13 pairs in the standard Positive13/max3 config.
- Per-pair uptrend: `close > EMA50 > EMA200` and EMA50 above its value three 4h bars earlier, matching the existing strategy definition.
- Pass: at least 7 of 13 configured pairs are in that uptrend state.
- Timing: latest 4h candle whose close is strictly before the archived trade `open_date`.
- Feature availability: 100.00% (59/59).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall longs

| breadth_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pass | 37 | 8 | 0.216 | 280.947 | 7.593 | 0.361 | 2.628 |
| reject | 22 | 10 | 0.455 | 426.293 | 19.377 | 0.728 | 6.503 |

## By entry tag

| enter_tag | breadth_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_1d_center_compression | pass | 35 | 7 | 0.200 | 218.164 | 6.233 | 0.261 | 2.266 |
| long_1d_center_compression | reject | 17 | 8 | 0.471 | 412.814 | 24.283 | 0.674 | 10.084 |
| long_pullback_restart_1h_body | pass | 2 | 1 | 0.500 | 62.783 | 31.391 | 0.100 | 266.721 |
| long_pullback_restart_1h_body | reject | 5 | 2 | 0.400 | 13.479 | 2.696 | 0.053 | 1.421 |

## By entry year

| entry_year | breadth_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | pass | 6 | 0 | 0.000 | -33.473 | -5.579 | -0.098 | 0.000 |
| 2023 | pass | 8 | 1 | 0.125 | -5.839 | -0.730 | -0.008 | 0.872 |
| 2023 | reject | 3 | 1 | 0.333 | -1.876 | -0.625 | -0.004 | 0.347 |
| 2024 | pass | 11 | 3 | 0.273 | 135.954 | 12.359 | 0.232 | 4.950 |
| 2024 | reject | 8 | 5 | 0.625 | 222.246 | 27.781 | 0.476 | 19.309 |
| 2025 | pass | 10 | 3 | 0.300 | 110.013 | 11.001 | 0.156 | 4.132 |
| 2025 | reject | 11 | 4 | 0.364 | 205.923 | 18.720 | 0.256 | 4.297 |
| 2026 | pass | 2 | 1 | 0.500 | 74.292 | 37.146 | 0.079 | 4.092 |

## LongMicro trades

| pair | open_date | profit_abs | profit_ratio | market_state_date | breadth_up_count | breadth_available_count | breadth_state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BTC/USDT:USDT | 2023-12-16 16:00:00+00:00 | -2.794 | -0.007 | 2023-12-16 12:00:00+00:00 | 4 | 11 | reject |
| BNB/USDT:USDT | 2023-12-21 09:00:00+00:00 | 0.996 | 0.004 | 2023-12-21 08:00:00+00:00 | 6 | 11 | reject |
| BNB/USDT:USDT | 2024-02-07 17:00:00+00:00 | 44.511 | 0.100 | 2024-02-07 16:00:00+00:00 | 4 | 11 | reject |
| BTC/USDT:USDT | 2025-01-06 05:00:00+00:00 | -0.236 | -0.000 | 2025-01-06 04:00:00+00:00 | 8 | 12 | pass |
| BNB/USDT:USDT | 2025-01-17 09:00:00+00:00 | -13.058 | -0.021 | 2025-01-17 08:00:00+00:00 | 6 | 12 | reject |
| BNB/USDT:USDT | 2025-06-10 21:00:00+00:00 | -16.176 | -0.022 | 2025-06-10 20:00:00+00:00 | 4 | 13 | reject |
| BNB/USDT:USDT | 2025-08-07 23:00:00+00:00 | 63.019 | 0.100 | 2025-08-07 20:00:00+00:00 | 7 | 13 | pass |
