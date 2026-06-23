# Positive13 Extreme Reversal Latched Signal Audit

## Scope And Definitions

- Round-2 signal audit only; no strategy backtest, no live merge, and no order generation.
- Period: 2023-06-18 through 2026-06-18; Positive13 local futures candles.
- An extreme event is one contiguous extreme episode. The watch timer starts after the episode's final candle.
- A later extreme episode supersedes an older unconfirmed watch. Each episode emits at most one signal per combination.
- 4H/1D candles become available only after close. Recent highs/lows and volume MA exclude the current candle.
- PF proxy = gross positive direction-adjusted 72h returns / absolute gross negative 72h returns; it is not trade PF.
- Combination rows overlap across TTL and confirmation variants; their signal counts must not be summed as unique market events.
- Same-candle stop/target ambiguity is resolved conservatively as stop-first.
- Acceptance: fewer than 50 signals is insufficient. A research candidate additionally needs PF proxy >=1.20, 1R-first > stop-first, and avg max-R > |avg min-R|.

## All 36 Combinations

| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| A_24h_weak | 565 | 9 | insufficient | 0.06 | -0.71/-1.43/-4.07% | 2.29/4.40% | 3.30/9.17% | 11.11/0.00/66.67% | 0.75/-1.58 |
| A_24h_medium | 565 | 8 | insufficient | 0.07 | -0.81/-1.71/-3.83% | 2.20/4.69% | 3.25/8.89% | 12.50/0.00/62.50% | 0.74/-1.46 |
| A_24h_strong | 565 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| A_72h_weak | 565 | 11 | insufficient | 0.06 | -0.45/-1.60/-3.42% | 2.38/4.84% | 3.33/8.74% | 9.09/0.00/54.55% | 0.71/-1.42 |
| A_72h_medium | 565 | 9 | insufficient | 0.07 | -0.96/-1.96/-3.46% | 2.09/5.20% | 3.17/8.93% | 11.11/0.00/55.56% | 0.68/-1.36 |
| A_72h_strong | 565 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| A_120h_weak | 565 | 15 | insufficient | 0.13 | -0.32/-1.22/-2.62% | 2.22/4.08% | 3.20/7.69% | 20.00/0.00/53.33% | 0.74/-1.45 |
| A_120h_medium | 565 | 10 | insufficient | 0.06 | -0.77/-1.81/-3.33% | 2.12/4.95% | 3.14/8.96% | 10.00/0.00/60.00% | 0.66/-1.39 |
| A_120h_strong | 565 | 2 | insufficient | 0.07 | -0.08/-2.29/-1.00% | 2.64/4.24% | 2.86/9.11% | 0.00/0.00/100.00% | 0.72/-2.29 |
| A_168h_weak | 565 | 21 | insufficient | 0.78 | 0.01/-0.15/-0.50% | 2.97/3.23% | 4.64/6.30% | 38.10/23.81/42.86% | 1.43/-1.21 |
| A_168h_medium | 565 | 14 | insufficient | 0.68 | -0.28/-0.61/-0.86% | 2.86/3.78% | 4.28/7.38% | 28.57/21.43/50.00% | 1.42/-1.19 |
| A_168h_strong | 565 | 2 | insufficient | 0.07 | -0.08/-2.29/-1.00% | 2.64/4.24% | 2.86/9.11% | 0.00/0.00/100.00% | 0.72/-2.29 |
| B_24h_weak | 375 | 5 | insufficient | 0.06 | -1.94/-2.09/-5.30% | 1.07/5.88% | 2.57/11.50% | 20.00/0.00/60.00% | 0.70/-1.73 |
| B_24h_medium | 375 | 5 | insufficient | 0.06 | -1.94/-2.09/-5.30% | 1.07/5.88% | 2.57/11.50% | 20.00/0.00/60.00% | 0.70/-1.73 |
| B_24h_strong | 375 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| B_72h_weak | 375 | 5 | insufficient | 0.06 | -1.94/-2.09/-5.30% | 1.07/5.88% | 2.57/11.50% | 20.00/0.00/60.00% | 0.70/-1.73 |
| B_72h_medium | 375 | 5 | insufficient | 0.06 | -1.94/-2.09/-5.30% | 1.07/5.88% | 2.57/11.50% | 20.00/0.00/60.00% | 0.70/-1.73 |
| B_72h_strong | 375 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| B_120h_weak | 375 | 6 | insufficient | 0.17 | -1.67/-1.88/-3.90% | 1.13/5.27% | 2.94/10.00% | 33.33/0.00/50.00% | 0.82/-1.56 |
| B_120h_medium | 375 | 5 | insufficient | 0.06 | -1.94/-2.09/-5.30% | 1.07/5.88% | 2.57/11.50% | 20.00/0.00/60.00% | 0.70/-1.73 |
| B_120h_strong | 375 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| B_168h_weak | 375 | 9 | insufficient | 0.42 | -1.17/-0.72/-1.97% | 2.38/4.18% | 4.79/8.48% | 44.44/22.22/44.44% | 1.26/-1.40 |
| B_168h_medium | 375 | 6 | insufficient | 0.06 | -1.92/-1.87/-4.75% | 1.62/5.35% | 2.87/11.75% | 16.67/0.00/66.67% | 0.72/-1.83 |
| B_168h_strong | 375 | 1 | insufficient | inf | -1.14/-4.14/0.15% | 2.88/5.83% | 2.88/8.97% | 0.00/0.00/100.00% | 0.93/-2.89 |
| C_24h_weak | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_24h_medium | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_24h_strong | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_72h_weak | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_72h_medium | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_72h_strong | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_120h_weak | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_120h_medium | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_120h_strong | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_168h_weak | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_168h_medium | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |
| C_168h_strong | 52 | 0 | insufficient | 0.00 | 0.00/0.00/0.00% | 0.00/0.00% | 0.00/0.00% | 0.00/0.00/0.00% | 0.00/0.00 |

## Ranked Candidates

| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| A_168h_weak | 565 | 21 | insufficient | 0.78 | 0.01/-0.15/-0.50% | 2.97/3.23% | 4.64/6.30% | 38.10/23.81/42.86% | 1.43/-1.21 |
| A_120h_weak | 565 | 15 | insufficient | 0.13 | -0.32/-1.22/-2.62% | 2.22/4.08% | 3.20/7.69% | 20.00/0.00/53.33% | 0.74/-1.45 |
| A_168h_medium | 565 | 14 | insufficient | 0.68 | -0.28/-0.61/-0.86% | 2.86/3.78% | 4.28/7.38% | 28.57/21.43/50.00% | 1.42/-1.19 |
| A_72h_weak | 565 | 11 | insufficient | 0.06 | -0.45/-1.60/-3.42% | 2.38/4.84% | 3.33/8.74% | 9.09/0.00/54.55% | 0.71/-1.42 |
| A_120h_medium | 565 | 10 | insufficient | 0.06 | -0.77/-1.81/-3.33% | 2.12/4.95% | 3.14/8.96% | 10.00/0.00/60.00% | 0.66/-1.39 |
| B_168h_weak | 375 | 9 | insufficient | 0.42 | -1.17/-0.72/-1.97% | 2.38/4.18% | 4.79/8.48% | 44.44/22.22/44.44% | 1.26/-1.40 |
| A_72h_medium | 565 | 9 | insufficient | 0.07 | -0.96/-1.96/-3.46% | 2.09/5.20% | 3.17/8.93% | 11.11/0.00/55.56% | 0.68/-1.36 |
| A_24h_weak | 565 | 9 | insufficient | 0.06 | -0.71/-1.43/-4.07% | 2.29/4.40% | 3.30/9.17% | 11.11/0.00/66.67% | 0.75/-1.58 |
| A_24h_medium | 565 | 8 | insufficient | 0.07 | -0.81/-1.71/-3.83% | 2.20/4.69% | 3.25/8.89% | 12.50/0.00/62.50% | 0.74/-1.46 |
| B_120h_weak | 375 | 6 | insufficient | 0.17 | -1.67/-1.88/-3.90% | 1.13/5.27% | 2.94/10.00% | 33.33/0.00/50.00% | 0.82/-1.56 |

- Combinations with >=50 signals: 0 / 36.
- Combinations passing all audit gates: 0 / 36.
- Best ranked combination: `A_168h_weak` (21 signals, PF proxy 0.78).

## Best Combination By Side

| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| long | 205 | 7 | insufficient | 25.74 | 1.73/1.96/4.24% | 4.60/1.75% | 7.51/1.75% | 71.43/71.43/14.29% | 2.87/-0.51 |
| short | 360 | 14 | insufficient | 0.13 | -0.85/-1.21/-2.87% | 2.16/3.97% | 3.21/8.58% | 21.43/0.00/57.14% | 0.71/-1.56 |

## Best Combination By Pair

| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| BTC/USDT:USDT | 58 | 1 | insufficient | inf | -0.01/-1.38/0.42% | 0.51/2.74% | 1.45/2.74% | 0.00/0.00/100.00% | 0.55/-1.04 |
| ADA/USDT:USDT | 42 | 1 | insufficient | inf | 1.77/3.87/7.87% | 4.59/0.30% | 8.18/0.30% | 100.00/100.00/0.00% | 4.72/-0.17 |
| DOGE/USDT:USDT | 61 | 1 | insufficient | inf | -0.09/2.25/4.19% | 4.12/2.51% | 9.97/2.51% | 100.00/100.00/0.00% | 2.85/-0.72 |
| LINK/USDT:USDT | 35 | 3 | insufficient | 5.10 | -0.02/0.38/2.73% | 3.42/1.68% | 5.48/5.23% | 66.67/33.33/33.33% | 1.96/-1.06 |
| PAXG/USDT:USDT | 34 | 2 | insufficient | 2.37 | -0.03/0.09/0.48% | 0.75/0.45% | 1.88/1.15% | 50.00/0.00/0.00% | 1.03/-0.70 |
| NEAR/USDT:USDT | 36 | 2 | insufficient | 1.62 | 1.17/1.42/0.66% | 4.29/1.74% | 6.96/5.03% | 50.00/50.00/50.00% | 1.67/-0.95 |
| SUI/USDT:USDT | 42 | 2 | insufficient | 1.40 | 0.90/2.27/1.18% | 4.20/1.15% | 6.17/5.83% | 50.00/50.00/50.00% | 2.41/-1.32 |
| ETH/USDT:USDT | 64 | 3 | insufficient | 0.75 | 0.20/-1.06/-0.06% | 2.94/3.48% | 3.10/5.00% | 33.33/0.00/66.67% | 1.05/-1.65 |
| ZEC/USDT:USDT | 54 | 2 | insufficient | 0.00 | -3.03/-2.78/-5.74% | 4.35/8.59% | 6.97/11.33% | 0.00/0.00/50.00% | 0.64/-0.97 |
| BNB/USDT:USDT | 47 | 1 | insufficient | 0.00 | -0.56/-1.67/-3.08% | 0.35/2.35% | 0.35/5.25% | 0.00/0.00/100.00% | 0.19/-2.83 |
| TAO/USDT:USDT | 18 | 3 | insufficient | 0.00 | 0.19/-2.07/-7.00% | 2.20/6.89% | 2.62/14.73% | 0.00/0.00/33.33% | 0.40/-1.53 |

## Best Combination By Year

| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 2023 | - | 1 | insufficient | inf | -0.01/-1.38/0.42% | 0.51/2.74% | 1.45/2.74% | 0.00/0.00/100.00% | 0.55/-1.04 |
| 2024 | - | 2 | insufficient | 0.08 | -1.47/-2.44/-0.92% | 3.62/4.26% | 3.62/10.98% | 0.00/0.00/100.00% | 0.86/-2.61 |
| 2025 | - | 10 | insufficient | 2.71 | 0.07/1.28/2.08% | 3.79/2.29% | 6.63/3.12% | 70.00/50.00/10.00% | 2.26/-0.54 |
| 2026 | - | 8 | insufficient | 0.10 | 0.31/-1.21/-3.72% | 2.10/4.22% | 2.82/9.56% | 12.50/0.00/62.50% | 0.64/-1.71 |

## Best Combination Candlestick Descriptors

| Side | Signals | Lower wick | Upper wick | Volume ratio | Low sweep reclaim | High sweep reject |
|---|---:|---:|---:|---:|---:|---:|
| long | 7 | 3.03% | 9.45% | 2.95 | 0.00% | 0.00% |
| short | 14 | 11.32% | 11.80% | 4.79 | 7.14% | 42.86% |

## Required Conclusions

1. **Are conditions still too strict?** Yes. No combination reaches 50 signals.
2. **Which groups deserve a real backtest?** None currently pass every audit gate.
3. **Which side has more edge?** long is directionally better within the best-ranked combination, but has only 7 signals and is not confirmed.
4. **Which pairs are worth retaining?** None meet the six-signal pair screen inside the best-ranked combination.

## Candlestick Pattern Notes

- Signal detail includes lower/upper wick percentage, volume ratio, low-sweep reclaim, and high-sweep rejection.
- These are posterior descriptors only and are not used to filter the current audit.

## Outputs

- `user_data/analysis/positive13_extreme_reversal_latched_signals.csv`
- `user_data/analysis/positive13_extreme_reversal_latched_summary.csv`
- `user_data/analysis/positive13_extreme_reversal_latched_funnel.csv`
- `user_data/analysis/positive13_extreme_reversal_latched_coverage.csv`
- `user_data/reports/positive13_extreme_reversal_latched_audit.md`
