# DualTrend Positive13 five-year signal collision replay

> Generated 2026-07-24T09:57:54.805676+00:00 from Freqtrade native signal exports.

## Scope

- Constrained strategy: `DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- Counterfactual strategy: `DualTrendPyramidSecondAdd20LongMicroCollisionReplayV1Strategy`
- Constrained timerange: `2021-07-29 16:00:00 -> 2026-06-18 00:00:00`
- Constrained trades: `481`
- Exported max-slot collision candles: `101`
- Distinct counterfactual entry episodes: `80`
- Repeated signals while the same counterfactual trade was open: `18`
- Unresolved collision candles: `3`

The max100 run uses a fixed diagnostic stake and no protections. Its portfolio return is intentionally ignored; only the trade path of a rejected signal is used as a counterfactual outcome.

## Counterfactual Outcome

- Wins / losses: `50 / 30`
- Sum of trade returns: `+84.87%`
- Mean trade return: `+1.06%`
- Profit factor on return ratios: `2.201`

## Blocked Tags

| Tag | Collision candles |
|---|---:|
| `short_pullback_restart` | 79 |
| `short_compression_breakdown` | 21 |
| `long_1d_center_compression` | 1 |

## Outcome By Blocked Tag

| Blocked tag | Episodes | Win | Loss | Sum returns | PF |
|---|---:|---:|---:|---:|---:|
| `long_1d_center_compression` | 1 | 0 | 1 | -0.01% | 0.000 |
| `short_compression_breakdown` | 18 | 11 | 7 | +11.67% | 1.633 |
| `short_pullback_restart` | 61 | 39 | 22 | +73.21% | 2.401 |

## Outcome By Year

| Year | Episodes | Win | Loss | Sum returns | PF |
|---|---:|---:|---:|---:|---:|
| 2021 | 2 | 1 | 1 | -3.94% | 0.003 |
| 2022 | 14 | 8 | 6 | +9.47% | 1.706 |
| 2023 | 13 | 9 | 4 | +57.63% | 8.575 |
| 2024 | 10 | 6 | 4 | -3.82% | 0.581 |
| 2025 | 19 | 10 | 9 | +0.27% | 1.011 |
| 2026 | 22 | 16 | 6 | +25.26% | 3.367 |

## Slot Occupants

| Occupying tag | Collision-candle appearances |
|---|---:|
| `short_pullback_restart` | 225 |
| `short_compression_breakdown` | 59 |
| `long_1d_center_compression` | 18 |
| `long_pullback_restart_1h_body` | 1 |

## Long-Side Squeeze Check

- Rejected long entry episodes: `1`, sum returns `-0.01%`.
- Rejected LongMicro episodes: `0`.
- Collision candles where LongMicro occupied a slot: `1`.
- A slot appearance is not evidence of harmful displacement; inspect the corresponding counterfactual outcome before changing priority.

## Counterfactual Episodes

| Signal time | Pair | Blocked tag | Outcome | Exit | Occupying tags |
|---|---|---|---:|---|---|
| 2021-12-17 15:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | -3.95% | `stop_loss` | `short_pullback_restart|short_compression_breakdown|short_compression_breakdown` |
| 2021-12-29 13:00:00+00:00 | `DOGE/USDT:USDT` | `short_compression_breakdown` | +0.01% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|short_compression_breakdown` |
| 2022-04-23 03:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | +5.04% | `partial_exit` | `short_pullback_restart|short_compression_breakdown|short_compression_breakdown` |
| 2022-04-24 00:00:00+00:00 | `XRP/USDT:USDT` | `short_pullback_restart` | +0.04% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|short_pullback_restart` |
| 2022-04-29 11:00:00+00:00 | `BTC/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `short_compression_breakdown|short_pullback_restart|short_compression_breakdown` |
| 2022-04-29 11:00:00+00:00 | `LINK/USDT:USDT` | `short_compression_breakdown` | +0.02% | `trailing_stop_loss` | `short_compression_breakdown|short_pullback_restart|short_compression_breakdown` |
| 2022-04-29 17:00:00+00:00 | `SOL/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-04-30 14:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | -0.08% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-04-30 15:00:00+00:00 | `ADA/USDT:USDT` | `short_pullback_restart` | -0.00% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-04-30 15:00:00+00:00 | `DOGE/USDT:USDT` | `short_compression_breakdown` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-04-30 15:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +7.76% | `partial_exit` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-04-30 15:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | +10.00% | `roi` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2022-05-03 19:00:00+00:00 | `ADA/USDT:USDT` | `short_pullback_restart` | -4.08% | `stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2022-09-01 15:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | -3.57% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_compression_breakdown` |
| 2022-09-16 14:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | -3.68% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|short_compression_breakdown` |
| 2022-09-18 10:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | -2.01% | `stop_loss` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-03-04 20:00:00+00:00 | `ADA/USDT:USDT` | `short_pullback_restart` | -2.38% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-05-24 04:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | +0.04% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-05-24 04:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +0.04% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 15:00:00+00:00 | `ADA/USDT:USDT` | `short_pullback_restart` | +9.99% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 15:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | +10.00% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 15:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | +10.00% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 15:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +10.03% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 16:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +10.00% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-17 16:00:00+00:00 | `XRP/USDT:USDT` | `short_pullback_restart` | +10.00% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2023-08-24 15:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | -1.38% | `stale_loss_72h` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-08-24 15:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +5.15% | `partial_exit` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-10-12 10:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | -1.75% | `stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2023-10-12 10:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | -2.11% | `stale_loss_72h` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-02-12 00:00:00+00:00 | `LINK/USDT:USDT` | `long_1d_center_compression` | -0.01% | `trailing_stop_loss` | `long_pullback_restart_1h_body|long_1d_center_compression|long_1d_center_compression` |
| 2024-05-12 08:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | +0.02% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-05-13 02:00:00+00:00 | `SUI/USDT:USDT` | `short_pullback_restart` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-05-13 03:00:00+00:00 | `SOL/USDT:USDT` | `short_pullback_restart` | -4.67% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-06-14 16:00:00+00:00 | `ADA/USDT:USDT` | `short_compression_breakdown` | +0.03% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|short_compression_breakdown` |
| 2024-06-14 16:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | +5.07% | `partial_exit` | `short_compression_breakdown|short_compression_breakdown|short_compression_breakdown` |
| 2024-06-27 06:00:00+00:00 | `TAO/USDT:USDT` | `short_pullback_restart` | -4.42% | `stop_loss` | `short_compression_breakdown|short_pullback_restart|short_compression_breakdown` |
| 2024-08-31 17:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +0.15% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-09-01 02:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | -0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2024-09-05 04:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-02-09 22:00:00+00:00 | `SOL/USDT:USDT` | `short_pullback_restart` | -4.34% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-03-09 10:00:00+00:00 | `XRP/USDT:USDT` | `short_pullback_restart` | +10.00% | `roi` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2025-03-09 11:00:00+00:00 | `ETH/USDT:USDT` | `short_pullback_restart` | +5.38% | `partial_exit` | `short_compression_breakdown|short_pullback_restart|short_pullback_restart` |
| 2025-06-14 17:00:00+00:00 | `LINK/USDT:USDT` | `short_compression_breakdown` | -3.60% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|long_1d_center_compression` |
| 2025-08-29 08:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +0.17% | `stale_loss_72h` | `short_pullback_restart|short_pullback_restart|short_compression_breakdown` |
| 2025-09-01 00:00:00+00:00 | `SUI/USDT:USDT` | `short_pullback_restart` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-09-01 00:00:00+00:00 | `XRP/USDT:USDT` | `short_pullback_restart` | -1.65% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-09-24 04:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +5.04% | `partial_exit` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2025-09-25 02:00:00+00:00 | `ETH/USDT:USDT` | `short_pullback_restart` | +5.23% | `partial_exit` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2025-09-28 02:00:00+00:00 | `SUI/USDT:USDT` | `short_pullback_restart` | -2.76% | `trailing_stop_loss` | `long_1d_center_compression|short_compression_breakdown|short_compression_breakdown` |
| 2025-09-28 12:00:00+00:00 | `SOL/USDT:USDT` | `short_pullback_restart` | -2.35% | `trailing_stop_loss` | `long_1d_center_compression|short_compression_breakdown|short_compression_breakdown` |
| 2025-11-06 13:00:00+00:00 | `SOL/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-11-06 15:00:00+00:00 | `ADA/USDT:USDT` | `short_pullback_restart` | -3.90% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-11-06 15:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | -3.44% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-11-06 15:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2025-12-15 15:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +0.36% | `trailing_stop_loss` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2025-12-21 02:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | -1.97% | `stop_loss` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2025-12-21 02:00:00+00:00 | `SUI/USDT:USDT` | `short_pullback_restart` | -1.93% | `trailing_stop_loss` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2025-12-21 03:00:00+00:00 | `TAO/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2026-01-22 15:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | -3.08% | `trailing_stop_loss` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2026-01-22 15:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +5.18% | `partial_exit` | `long_1d_center_compression|short_pullback_restart|short_pullback_restart` |
| 2026-01-25 09:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +5.02% | `partial_exit` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-01-25 15:00:00+00:00 | `DOGE/USDT:USDT` | `short_pullback_restart` | -0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-01-29 12:00:00+00:00 | `ZEC/USDT:USDT` | `short_compression_breakdown` | +0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-01-29 15:00:00+00:00 | `BTC/USDT:USDT` | `short_compression_breakdown` | +10.00% | `roi` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-01-29 15:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | +10.00% | `roi` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-03 18:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | +5.34% | `partial_exit` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-03 18:00:00+00:00 | `XRP/USDT:USDT` | `short_compression_breakdown` | -4.10% | `stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-10 19:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-10 19:00:00+00:00 | `SUI/USDT:USDT` | `short_compression_breakdown` | +0.02% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-10 19:00:00+00:00 | `TAO/USDT:USDT` | `short_compression_breakdown` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-11 05:00:00+00:00 | `BTC/USDT:USDT` | `short_pullback_restart` | -0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-11 05:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.01% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-02-22 13:00:00+00:00 | `SUI/USDT:USDT` | `short_compression_breakdown` | -0.03% | `trailing_stop_loss` | `short_compression_breakdown|short_compression_breakdown|short_pullback_restart` |
| 2026-03-22 00:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.15% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-03-29 11:00:00+00:00 | `NEAR/USDT:USDT` | `short_pullback_restart` | +0.08% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2026-03-29 14:00:00+00:00 | `BNB/USDT:USDT` | `short_pullback_restart` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2026-03-29 14:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.00% | `trailing_stop_loss` | `short_pullback_restart|short_compression_breakdown|short_pullback_restart` |
| 2026-05-31 15:00:00+00:00 | `LINK/USDT:USDT` | `short_pullback_restart` | +0.03% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-05-31 15:00:00+00:00 | `TAO/USDT:USDT` | `short_pullback_restart` | +0.10% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |
| 2026-06-10 09:00:00+00:00 | `SOL/USDT:USDT` | `short_compression_breakdown` | -3.44% | `trailing_stop_loss` | `short_pullback_restart|short_pullback_restart|short_pullback_restart` |

## Interpretation Rules

- A collision candle is not automatically one missed trade; repeated same-pair signals are collapsed by the counterfactual trade path.
- This audit diagnoses opportunity quality. It does not prove which open position should be replaced at collision time.
- Do not promote a ranking rule from a tiny tag or yearly subset. Require stable direction across five-year, yearly, and dry-run shadow evidence.
