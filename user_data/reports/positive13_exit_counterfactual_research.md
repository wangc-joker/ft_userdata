# Positive13 Exit Counterfactual Research

## Scope And Caveats

- Offline research only. Main strategy, dry-run/live configuration, pair pool, tags, and max3 are unchanged.
- Entries and stakes are fixed to the aligned baseline. A candidate replaces the exit only when its profit trigger occurred before the original exit; otherwise the original trade is retained.
- Original structural stop remains active after model activation; maximum holding time is 14 days.
- Extended exits can overlap later fixed entries and do not recalculate max3 slot contention or wallet sizing. Results are screening evidence, not a replacement backtest.
- Candidate returns use candle OHLC and baseline open/close fees; funding and intrabar path are approximate. Stop hits are evaluated conservatively.
- Candidate MaxDD is a close-balance proxy over fixed trades. Its baseline is 8.87%, while Freqtrade's full equity-aware baseline MaxDD is 7.66%; compare proxy values only within the counterfactual table.
- Model E assumption: after +5%, protect breakeven until age 24h, then use 60% giveback with a 1.5% minimum lock.

## Baseline Reproduction

- 3Y export: 291 trades / 1993.45 USDT / PF 2.00 / MaxDD 7.66%.
- 1Y export: 111 trades / 512.34 USDT / PF 2.00 / MaxDD 7.65%.

## Three-Year Trailing Counterfactuals

| Model | Trades | Profit | PF | MaxDD proxy | Winrate | Avg/Med Profit | Avg/Med/Max Hours | Activated | Top5 winner share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 291 | 1993.45 (199.34%) | 2.00 | 8.87% | 35.05% | 1.53/-1.59% | 49.42/31.00/429.00 | 0 | 11.18% |
| A_giveback50_floor1 | 291 | 215.39 (21.54%) | 1.15 | 15.39% | 57.04% | 0.11/1.48% | 22.34/12.00/336.00 | 166 | 11.58% |
| B_giveback60_floor1.5 | 291 | 1313.78 (131.38%) | 1.73 | 12.97% | 44.33% | 0.74/-1.15% | 44.93/24.00/336.00 | 127 | 29.04% |
| C_giveback70_floor2 | 291 | 1547.12 (154.71%) | 1.80 | 14.03% | 37.80% | 0.97/-1.47% | 71.71/39.00/429.00 | 98 | 27.63% |
| D_atr1h_1.5 | 291 | 792.89 (79.29%) | 1.44 | 12.68% | 44.33% | 0.46/-1.15% | 29.00/19.00/325.00 | 127 | 9.95% |
| D_atr1h_2.0 | 291 | 663.90 (66.39%) | 1.37 | 13.00% | 44.33% | 0.40/-1.15% | 29.80/19.00/327.00 | 127 | 9.94% |
| D_atr1h_2.5 | 291 | 827.58 (82.76%) | 1.46 | 12.36% | 44.33% | 0.54/-1.15% | 31.42/22.00/335.00 | 127 | 13.24% |
| D_atr1h_3.0 | 291 | 915.61 (91.56%) | 1.51 | 11.09% | 43.30% | 0.62/-1.15% | 33.63/24.00/336.00 | 127 | 14.05% |
| D_atr4h_1.5 | 291 | 926.34 (92.63%) | 1.51 | 13.38% | 43.99% | 0.65/-1.15% | 31.99/22.00/336.00 | 127 | 11.74% |
| D_atr4h_2.0 | 291 | 1047.16 (104.72%) | 1.58 | 11.13% | 41.24% | 0.70/-1.15% | 35.76/24.00/336.00 | 127 | 17.16% |
| D_atr4h_2.5 | 291 | 1383.31 (138.33%) | 1.76 | 12.11% | 39.18% | 0.92/-1.15% | 42.65/31.00/336.00 | 127 | 22.25% |
| D_atr4h_3.0 | 291 | 1444.85 (144.48%) | 1.80 | 13.96% | 37.46% | 0.91/-1.15% | 49.41/33.00/336.00 | 127 | 26.90% |
| E_min24h_profit_protect | 291 | 1585.10 (158.51%) | 1.87 | 13.79% | 39.18% | 0.91/-1.15% | 51.76/29.00/336.00 | 127 | 28.72% |

## One-Year Trailing Counterfactuals

| Model | Trades | Profit | PF | MaxDD proxy | Winrate | Avg/Med Profit | Avg/Med/Max Hours | Activated | Top5 winner share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 111 | 512.34 (51.23%) | 2.00 | 7.65% | 39.64% | 1.52/-1.21% | 60.13/37.00/429.00 | 0 | 21.86% |
| A_giveback50_floor1 | 111 | 116.30 (11.63%) | 1.33 | 4.22% | 63.96% | 0.28/1.51% | 25.38/15.00/336.00 | 71 | 17.53% |
| B_giveback60_floor1.5 | 111 | 546.13 (54.61%) | 2.18 | 6.70% | 49.55% | 1.44/-0.03% | 59.38/27.00/336.00 | 53 | 45.34% |
| C_giveback70_floor2 | 111 | 608.36 (60.84%) | 2.21 | 9.87% | 41.44% | 1.67/-1.02% | 92.51/48.00/429.00 | 35 | 43.71% |
| D_atr1h_1.5 | 111 | 272.23 (27.22%) | 1.59 | 4.45% | 49.55% | 0.60/-0.03% | 35.41/22.00/325.00 | 53 | 17.68% |
| D_atr1h_2.0 | 111 | 211.08 (21.11%) | 1.45 | 4.61% | 49.55% | 0.42/-0.03% | 36.27/22.00/327.00 | 53 | 18.35% |
| D_atr1h_2.5 | 111 | 303.06 (30.31%) | 1.65 | 4.31% | 49.55% | 0.81/-0.03% | 38.51/24.00/335.00 | 53 | 22.11% |
| D_atr1h_3.0 | 111 | 300.32 (30.03%) | 1.65 | 4.42% | 48.65% | 0.77/-0.10% | 40.57/27.00/336.00 | 53 | 24.46% |
| D_atr4h_1.5 | 111 | 301.81 (30.18%) | 1.65 | 4.29% | 49.55% | 0.80/-0.03% | 39.19/24.00/336.00 | 53 | 21.01% |
| D_atr4h_2.0 | 111 | 358.54 (35.85%) | 1.77 | 4.39% | 45.95% | 0.97/-0.10% | 43.79/30.00/336.00 | 53 | 29.27% |
| D_atr4h_2.5 | 111 | 459.76 (45.98%) | 1.99 | 4.67% | 43.24% | 1.18/-0.10% | 50.14/32.00/336.00 | 53 | 38.33% |
| D_atr4h_3.0 | 111 | 525.34 (52.53%) | 2.12 | 5.80% | 41.44% | 1.28/-0.10% | 57.89/35.00/336.00 | 53 | 44.51% |
| E_min24h_profit_protect | 111 | 667.42 (66.74%) | 2.43 | 6.36% | 44.14% | 1.78/-0.10% | 67.22/33.00/336.00 | 53 | 43.57% |

## Answers: Profit Trailing

1. Highest candidate total profit: `E_min24h_profit_protect` at 1585.10 USDT, still below baseline 1993.45 USDT.
2. Highest candidate PF: `E_min24h_profit_protect` at 1.87, still below baseline 2.00.
3. Lowest candidate MaxDD proxy: `D_atr1h_3.0` at 11.09%, above baseline proxy 8.87%.
4. Models improving profit without material drawdown expansion: none.
5. Pressure period did not worsen for the highest-profit candidate: baseline -129.23 vs `E_min24h_profit_protect` -84.83 USDT; this local improvement does not offset its three-year degradation.
6. Baseline average duration is 49.42h; the longest candidate average is 71.71h.
7. Highest-profit model top-five winners contribute 28.72% of gross winning profit.
8. Entry-tag beneficiaries under `E_min24h_profit_protect`: `long_1d_center_compression` +57.26 USDT; both short tags deteriorated.
9. Positive pair deltas under `E_min24h_profit_protect`: `ADA/USDT:USDT` +236.21, `BNB/USDT:USDT` +134.17, `TAO/USDT:USDT` +69.76, `PAXG/USDT:USDT` +44.01, `ETH/USDT:USDT` +12.27, `SOL/USDT:USDT` +11.85. These are exploratory and do not justify pair-specific exits.
10. Real strategy version warranted now: no.

## Exit-Forward Outcomes

| Window | Stops too early | Takes too early | Hold helps | Hold hurts | Avg favorable | Avg adverse |
|---:|---:|---:|---:|---:|---:|---:|
| 6h | 13.82% | 33.33% | 54.98% | 45.02% | 2.08% | 1.66% |
| 12h | 21.05% | 43.14% | 50.86% | 49.14% | 2.75% | 2.18% |
| 24h | 36.84% | 52.48% | 49.31% | 50.69% | 3.56% | 2.94% |
| 48h | 49.34% | 64.36% | 50.34% | 49.66% | 4.96% | 4.28% |
| 72h | 60.53% | 68.32% | 53.45% | 46.55% | 6.14% | 5.14% |
| 168h | 77.63% | 74.26% | 52.25% | 47.75% | 9.59% | 8.44% |
| 336h | 83.11% | 79.59% | 56.03% | 43.97% | 13.97% | 11.87% |

## Answers: Are Current Exits Too Early?

1. Losing stop trades labelled stopped_too_early: 36.84% by 24h and 49.34% by 48h.
2. Long losing stops recovering by the 24h label: 48.15%.
3. Short losing stops recovering by the 24h label: 34.40%.
4. Winning trades labelled took_profit_too_early by 72h: 68.32%.
5. Hold-help rates at 24/48/72/168h: 49.31% / 50.34% / 53.45% / 52.25%.
6. Highest 24h stop-recovery tag: `long_1d_center_compression` (48.15%)
7. Highest 72h continued-profit tag: `short_compression_breakdown` (74.07%)
8. Highest early-stop pair with >=3 stops: `SUI/USDT:USDT` (50.00%)
9. Highest early-profit pair with >=3 wins: `SOL/USDT:USDT` (87.50%)
10. Current stoploss clearly too tight: not proven.
11. Current take-profit/trailing clearly too early: not globally proven. Post-exit favorable excursions are frequent, but fixed-hold improvement is near 50% and every global widening model loses three-year quality.
12. Change stoploss now: no.
13. Change trailing now: no.
14. Entry-tag-specific exits: worth further offline study for `long_1d_center_compression`, but not implementation yet; both short tags reject global widening.
15. Pair-specific exits: not recommended without independent validation.

## Final Recommendation

1. Current exit logic clearly early: not globally. Many exits leave later favorable excursion, but the tested widening rules fail to monetize it across three years.
2. Current stoploss clearly tight: no clear evidence.
3. Wider post-profit trailing deserves continuation: not as a global rule; only a long-tag-specific diagnostic is justified.
4. Develop a real strategy version next: no.
5. Next direction: keep current exits; if research continues, isolate `long_1d_center_compression` profit protection before considering `DualTrendCombinedShortPullbackShapeV1ExitResearchStrategy`.
6. Keep the current main strategy unchanged: yes.

## Outputs

- `user_data/reports/positive13_exit_logic_current_summary.md`
- `user_data/analysis/positive13_baseline_trades_3y_exit_analysis.csv`
- `user_data/analysis/positive13_baseline_trades_1y_exit_analysis.csv`
- `user_data/analysis/positive13_exit_forward_outcome_3y.csv`
- `user_data/analysis/positive13_exit_forward_outcome_1y.csv`
- `user_data/analysis/positive13_trailing_stop_models_3y.csv`
- `user_data/analysis/positive13_trailing_stop_models_1y.csv`
- `user_data/analysis/positive13_exit_reason_summary.csv`
- `user_data/analysis/positive13_exit_entry_tag_summary.csv`
- `user_data/analysis/positive13_exit_pair_summary.csv`
- `user_data/analysis/positive13_exit_trade_level_details.csv`
