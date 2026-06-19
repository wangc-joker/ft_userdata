# Positive13 Pressure Months Diagnosis

## Scope

- Diagnostic only: no strategy optimization, no parameter change, no pair deletion, no bot split.
- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Pair pool: Positive13
- max_open_trades: 3
- Baseline source: `backtest-result-2026-06-19_03-17-28.zip`
- Main pressure window: `2026-03-01 -> 2026-05-31`
- Control windows: `2026-01-01 -> 2026-02-28`, `2026-06-01 -> 2026-06-18`

## Period Summary

| Period | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-01-01 -> 2026-02-28 | 24 | 40.92% / 409.16 USDT | 3.33 | 5.69% | 50.00% | 2.98% |
| 2026-03-01 -> 2026-05-31 | 17 | -12.92% / -129.23 USDT | 0.39 | 17.25% | 17.65% | -1.05% |
| 2026-06-01 -> 2026-06-18 | 12 | 24.07% / 240.71 USDT | 3.14 | 7.44% | 50.00% | 3.02% |

## Pressure Window Breakdown

### Long / Short

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short | 16 | -11.00% / -110.01 USDT | 0.43 | 15.43% | 18.75% | -0.98% |
| long | 1 | -1.92% / -19.22 USDT | 0.00 | 1.92% | 0.00% | -2.08% |

### Entry Tag

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short_pullback_restart | 8 | -5.88% / -58.82 USDT | 0.33 | 8.69% | 25.00% | -1.30% |
| short_compression_breakdown | 8 | -5.12% / -51.19 USDT | 0.51 | 9.84% | 12.50% | -0.66% |
| long_1d_center_compression | 1 | -1.92% / -19.22 USDT | 0.00 | 1.92% | 0.00% | -2.08% |

### Pair

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | 2 | -4.20% / -42.05 USDT | 0.00 | 4.20% | 0.00% | -3.65% |
| ADA/USDT:USDT | 2 | -2.35% / -23.46 USDT | 0.00 | 2.35% | 0.00% | -1.28% |
| SUI/USDT:USDT | 1 | -2.22% / -22.17 USDT | 0.00 | 2.22% | 0.00% | -4.04% |
| XRP/USDT:USDT | 5 | -2.16% / -21.56 USDT | 0.53 | 4.43% | 20.00% | -0.69% |
| BTC/USDT:USDT | 2 | -2.00% / -20.00 USDT | 0.00 | 2.00% | 0.00% | -1.09% |
| NEAR/USDT:USDT | 1 | -1.98% / -19.83 USDT | 0.00 | 1.98% | 0.00% | -4.10% |
| BNB/USDT:USDT | 2 | -1.71% / -17.08 USDT | 0.24 | 2.25% | 50.00% | -1.08% |
| TAO/USDT:USDT | 1 | -1.54% / -15.43 USDT | 0.00 | 1.54% | 0.00% | -1.97% |
| ZEC/USDT:USDT | 1 | 5.23% / 52.34 USDT | inf | 0.00% | 100.00% | 10.00% |

### Month

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-03 | 7 | -5.99% / -59.86 USDT | 0.47 | 10.66% | 14.29% | -0.91% |
| 2026-04 | 6 | -3.32% / -33.17 USDT | 0.47 | 4.11% | 33.33% | -0.87% |
| 2026-05 | 4 | -3.62% / -36.20 USDT | 0.00 | 3.62% | 0.00% | -1.54% |

## Loss Labels

| Label | Losing Trades | Share of Losing Trades |
|---|---:|---:|
| false_breakdown | 5 | 35.71% |
| range_market | 3 | 21.43% |
| normal_loss | 3 | 21.43% |
| stop_too_tight | 2 | 14.29% |
| btc_regime_conflict | 1 | 7.14% |

## Loss Behavior Indicators

- Pressure losing trades: 14
- Average MAE on losing trades: 2.82%
- Average MFE before/inside loss window: 2.85%
- Quick reverse within 1-5 1H candles: 5 / 14
- BTC range regime: 5 / 14
- BTC regime conflict: 1 / 14
- ATR spike: 0 / 14
- Range market: 5 / 14
- Late trend chase: 0 / 14
- False breakout/breakdown labels: 5 / 14
- Overlap with max4/max5 extra loss months: 2026-03

## Losing Trade Details

| Pair | Open Date | Side | Entry Tag | Profit | MAE | MFE | Label |
|---|---|---|---|---:|---:|---:|---|
| SOL/USDT:USDT | 2026-03-07 20:00:00 | short | short_compression_breakdown | -22.52 | 3.93% | 2.78% | false_breakdown |
| BNB/USDT:USDT | 2026-03-22 00:00:00 | short | short_pullback_restart | -22.48 | 3.24% | 1.63% | false_breakdown |
| XRP/USDT:USDT | 2026-03-22 00:00:00 | short | short_pullback_restart | -22.44 | 3.41% | 3.36% | range_market |
| SUI/USDT:USDT | 2026-03-22 00:00:00 | short | short_pullback_restart | -22.17 | 4.14% | 4.50% | false_breakdown |
| XRP/USDT:USDT | 2026-03-24 17:00:00 | short | short_compression_breakdown | -21.81 | 3.40% | 0.53% | false_breakdown |
| BTC/USDT:USDT | 2026-03-27 09:00:00 | short | short_compression_breakdown | -0.78 | 0.40% | 4.36% | stop_too_tight |
| ADA/USDT:USDT | 2026-03-27 09:00:00 | short | short_compression_breakdown | -1.20 | 1.07% | 7.78% | stop_too_tight |
| NEAR/USDT:USDT | 2026-04-02 02:00:00 | short | short_pullback_restart | -19.83 | 4.44% | 2.74% | normal_loss |
| ADA/USDT:USDT | 2026-04-13 00:00:00 | short | short_compression_breakdown | -22.26 | 2.54% | 0.08% | btc_regime_conflict |
| BTC/USDT:USDT | 2026-04-18 00:00:00 | long | long_1d_center_compression | -19.22 | 2.12% | 0.45% | normal_loss |
| TAO/USDT:USDT | 2026-04-30 15:00:00 | short | short_compression_breakdown | -15.43 | 2.50% | 0.17% | range_market |
| SOL/USDT:USDT | 2026-05-23 08:00:00 | short | short_compression_breakdown | -19.53 | 5.91% | 0.68% | false_breakdown |
| XRP/USDT:USDT | 2026-05-22 07:00:00 | short | short_pullback_restart | -0.32 | 1.15% | 4.77% | range_market |
| XRP/USDT:USDT | 2026-05-25 23:00:00 | short | short_pullback_restart | -0.92 | 1.28% | 6.03% | normal_loss |

## Required Answers

- **1. 2026-03 到 2026-05 是否是当前策略的主要压力期？** 是。该窗口 17 笔，收益 -129.23 USDT，PF 0.39，明显弱于 2026-01~02 和 2026-06 对照期。
- **2. 压力期亏损主要来自 long 还是 short？** 主要来自 short。
- **3. 压力期亏损主要来自哪个 entry_tag？** 主要来自 `short_pullback_restart`。
- **4. 压力期亏损主要集中在哪些 pair？** 主要集中在 SOL/USDT:USDT, ADA/USDT:USDT, SUI/USDT:USDT, XRP/USDT:USDT。
- **5. 压力期亏损是否主要是假突破/假跌破？** 不是主要来源。false breakout/breakdown 共 5 笔，占亏损单 35.71%。
- **6. 压力期亏损是否主要是震荡市导致？** 不是单一主因。range_market 触发 5 笔。
- **7. 压力期亏损是否主要是 BTC 大盘环境冲突？** 不是主要来源。BTC regime conflict 触发 1 笔。
- **8. 压力期亏损是否主要是 ATR 极端波动导致？** 不是主要来源。ATR spike 触发 0 笔。
- **9. 这些亏损是否属于正常策略回撤？** 大部分属于正常策略回撤，但存在可诊断的行情类型聚集，尤其是 short 侧、特定 entry_tag、部分 pair 和压力月份重叠。
- **10. 是否有必要进入 long 模块诊断？** 暂时不是最高优先级；除非 long 在明细表中显示为主要亏损来源，否则应先看 entry_tag/压力月份。
- **11. 是否有必要进入 entry_tag 级别优化？** 有必要进入 entry_tag 级别诊断，但本轮不要优化，只定位问题来源。
- **12. 是否暂时仍然保持 max_open_trades=3？** 是，继续保持 max3。
- **13. 是否继续不改策略？** 是，继续不改策略；下一步只做更细诊断。

## Follow-Up Recommendation

- 保持 `max_open_trades=3`。
- 暂不优化策略、不删币、不拆 bot。
- 下一阶段建议优先做 `entry_tag` 级别诊断，并把 2026-03、2026-04、2026-05 与 max4/max5 extra loss months 交叉看。
- 如果后续必须排序，优先级建议为：entry_tag 诊断 > pair 诊断 > long 模块诊断。

## Output Files

- `user_data/reports/positive13_pressure_months_diagnosis.md`
- `user_data/analysis/positive13_trades_202603_202605.csv`
- `user_data/analysis/positive13_trades_202601_202602.csv`
- `user_data/analysis/positive13_trades_202606.csv`
