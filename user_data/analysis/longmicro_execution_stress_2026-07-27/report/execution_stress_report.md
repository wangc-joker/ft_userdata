# Corrected LongMicro Execution Stress

## Portfolio Results

| Scenario | Control profit | Candidate profit | Candidate delta | Control PF | Candidate PF | Candidate DD |
|---|---:|---:|---:|---:|---:|---:|
| `baseline` | +261.73% | +277.37% | +15.64% | 2.405 | 2.429 | +4.78% |
| `fee1p5x` | +232.96% | +247.15% | +14.19% | 2.255 | 2.282 | +6.08% |
| `fee2x` | +213.92% | +225.66% | +11.74% | 2.118 | 2.139 | +6.26% |
| `fee2x_slip_light` | +202.27% | +213.67% | +11.40% | 2.014 | 2.035 | +9.08% |
| `fee2x_slip_medium` | +194.51% | +205.68% | +11.17% | 1.949 | 1.970 | +9.37% |
| `fee2x_slip_heavy` | +175.09% | +185.70% | +10.60% | 1.801 | 1.822 | +10.65% |

Freqtrade-reported rows propagate fee effects through callbacks, protections, sizing, and later occupancy. Slippage rows are static post-trade estimates from the fee2x trade lists and do not propagate those state changes.

## Micro Tag

| Scenario | Trades | Wins | Profit | PF |
|---|---:|---:|---:|---:|
| `baseline` | 7 | 3 | +76.26 USDT | 3.364 |
| `fee1p5x` | 7 | 3 | +71.31 USDT | 3.256 |
| `fee2x` | 7 | 3 | +68.95 USDT | 3.177 |
| `fee2x_slip_light` | 7 | 3 | +66.89 USDT | 3.031 |
| `fee2x_slip_medium` | 7 | 3 | +65.52 USDT | 2.940 |
| `fee2x_slip_heavy` | 7 | 3 | +62.09 USDT | 2.731 |

## Micro Tag By Entry Year

| Scenario | Year | Trades | Profit |
|---|---:|---:|---:|
| `baseline` | 2023 | 2 | -1.80 USDT |
| `baseline` | 2024 | 1 | +44.51 USDT |
| `baseline` | 2025 | 4 | +33.55 USDT |
| `fee1p5x` | 2023 | 2 | -2.16 USDT |
| `fee1p5x` | 2024 | 1 | +43.00 USDT |
| `fee1p5x` | 2025 | 4 | +30.46 USDT |
| `fee2x` | 2023 | 2 | -2.49 USDT |
| `fee2x` | 2024 | 1 | +42.39 USDT |
| `fee2x` | 2025 | 4 | +29.05 USDT |
| `fee2x_slip_light` | 2023 | 2 | -2.88 USDT |
| `fee2x_slip_light` | 2024 | 1 | +42.13 USDT |
| `fee2x_slip_light` | 2025 | 4 | +27.65 USDT |
| `fee2x_slip_medium` | 2023 | 2 | -3.15 USDT |
| `fee2x_slip_medium` | 2024 | 1 | +41.95 USDT |
| `fee2x_slip_medium` | 2025 | 4 | +26.72 USDT |
| `fee2x_slip_heavy` | 2023 | 2 | -3.80 USDT |
| `fee2x_slip_heavy` | 2024 | 1 | +41.51 USDT |
| `fee2x_slip_heavy` | 2025 | 4 | +24.39 USDT |

## Fee-induced Path Changes

| Scenario | Strategy | Matched entries | Baseline only | Stress only | Changed exits | Changed order counts |
|---|---|---:|---:|---:|---:|---:|
| `fee1p5x` | `DualTrendPyramidSecondAdd20V1Strategy` | 473 | 4 | 0 | 23 | 7 |
| `fee1p5x` | `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 477 | 4 | 0 | 25 | 7 |
| `fee2x` | `DualTrendPyramidSecondAdd20V1Strategy` | 469 | 8 | 2 | 53 | 18 |
| `fee2x` | `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 473 | 8 | 2 | 55 | 18 |
