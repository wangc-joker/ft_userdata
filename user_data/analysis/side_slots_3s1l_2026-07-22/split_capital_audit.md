# Split-Capital Audit

## Metrics

| portfolio | trades | profit_pct | profit_abs | profit_factor | maxdd_account_pct | cagr_pct |
| --- | --- | --- | --- | --- | --- | --- |
| current_shared_max3 | 481 | 277.368 | 2773.680 | 2.429 | 4.778 | n/a |
| short_only_100pct | 428 | 162.260 | 1622.601 | 2.059 | 8.627 | n/a |
| long_only_100pct | 60 | 39.772 | 397.724 | 3.227 | 4.342 | n/a |
| split_80short_20long | 488 | 137.763 | 1377.625 | 2.092 | 6.780 | 19.387 |

## 80/20 annual realized profit

| year | long | short | combined_profit_abs |
| --- | --- | --- | --- |
| 2021 | -6.694 | -25.521 | -32.215 |
| 2022 | 0.000 | 143.775 | 143.775 |
| 2023 | -0.928 | 88.703 | 87.775 |
| 2024 | 49.790 | 206.217 | 256.007 |
| 2025 | 29.918 | 410.992 | 440.910 |
| 2026 | 7.459 | 473.915 | 481.373 |

## Drawdown interval

- High: 2024-04-12 17:30:00+00:00 at 1313.910 USDT.
- Low: 2024-06-30 22:25:00+00:00 at 1224.823 USDT.
- Absolute drawdown: 89.087 USDT.
- Account drawdown: 6.780%.

The reconstruction scales standalone 1000-USDT engine PnL by fixed 80/20 weights. Existing
minimum long stake remains above the exchange minimum after 20% scaling, so the linear scaling
does not create a minimum-order discontinuity in the observed sample.
