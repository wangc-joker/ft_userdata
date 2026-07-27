# BTC Daily Bear-Regime Guard Diagnostic

## Frozen rule

- Pass all existing long entries except during a confirmed BTC daily bear regime.
- Bear regime: `BTC close < EMA50 < EMA200` and EMA50 below its value three daily bars earlier.
- Timing: latest daily candle whose close is strictly before the archived trade `open_date`.
- Feature availability: 89.83% (53/59).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall longs

| btc_bear_guard_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pass | 52 | 17 | 0.327 | 699.294 | 13.448 | 1.143 | 4.229 |
| reject | 1 | 1 | 1.000 | 41.418 | 41.418 | 0.043 | inf |
| nan | 6 | 0 | 0.000 | -33.473 | -5.579 | -0.098 | 0.000 |

## By entry tag

| enter_tag | btc_bear_guard_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| long_1d_center_compression | pass | 45 | 14 | 0.311 | 623.033 | 13.845 | 0.990 | 4.380 |
| long_1d_center_compression | reject | 1 | 1 | 1.000 | 41.418 | 41.418 | 0.043 | inf |
| long_1d_center_compression | nan | 6 | 0 | 0.000 | -33.473 | -5.579 | -0.098 | 0.000 |
| long_pullback_restart_1h_body | pass | 7 | 3 | 0.429 | 76.262 | 10.895 | 0.153 | 3.364 |

## By entry year

| entry_year | btc_bear_guard_state | trades | wins | win_rate | profit_abs | profit_abs_mean | profit_ratio_sum | profit_factor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | nan | 6 | 0 | 0.000 | -33.473 | -5.579 | -0.098 | 0.000 |
| 2023 | pass | 11 | 2 | 0.182 | -7.715 | -0.701 | -0.012 | 0.841 |
| 2024 | pass | 19 | 8 | 0.421 | 358.200 | 18.853 | 0.708 | 8.693 |
| 2025 | pass | 20 | 6 | 0.300 | 274.517 | 13.726 | 0.368 | 3.813 |
| 2025 | reject | 1 | 1 | 1.000 | 41.418 | 41.418 | 0.043 | inf |
| 2026 | pass | 2 | 1 | 0.500 | 74.292 | 37.146 | 0.079 | 4.092 |

## Rejected trades

| pair | open_date | enter_tag | profit_abs | profit_ratio | btc_regime_date | btc_daily_close | btc_daily_ema50 | btc_daily_ema200 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PAXG/USDT:USDT | 2025-12-12 00:00:00+00:00 | long_1d_center_compression | 41.418 | 0.043 | 2025-12-11 00:00:00+00:00 | 91977.500 | 96767.406 | 103664.942 |
