# Positive13 Extra Slots Diagnosis

## Scope

- Purpose: diagnose max4/max5 extra trades versus max3; no strategy optimization was performed.
- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Configs: `config.backtest.dualtrend.combined.top50.positive13.max3/max4/max5.json`
- Local override: `config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`
- Data: filled historical local data, same Positive13 static whitelist.
- Matching rule: max3 baseline matched by `pair + side + entry_tag + open_date`, allowing +/- 1 hour.

## Full Backtest Results

### Three-Year: 2023-06-18 -> 2026-06-18

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 291 | 199.34% / 1993.45 USDT | 2.00 | 7.66% | 35.05% | 1.53% |
| 4 | 322 | 192.84% / 1928.35 USDT | 1.90 | 9.54% | 33.23% | 1.35% |
| 5 | 334 | 194.12% / 1941.18 USDT | 1.86 | 10.24% | 33.53% | 1.37% |

### Recent One-Year: 2025-06-18 -> 2026-06-18

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 111 | 51.23% / 512.34 USDT | 2.00 | 7.65% | 39.64% | 1.52% |
| 4 | 128 | 52.59% / 525.86 USDT | 1.90 | 9.55% | 36.72% | 1.30% |
| 5 | 136 | 50.01% / 500.12 USDT | 1.80 | 10.25% | 36.03% | 1.22% |

## Extra Trade Summary

| Sample | Compared Run | Extra Trades | Extra Profit | Extra PF | Extra MaxDD | Extra Winrate | Extra Avg Profit |
|---|---|---:|---:|---:|---:|---:|---:|
| 3y | max4 vs max3 | 31 | 0.31% / 3.08 USDT | 1.02 | 8.30% | 16.13% | -0.35% |
| 3y | max5 vs max3 | 43 | 1.79% / 17.86 USDT | 1.06 | 10.12% | 23.26% | 0.31% |
| 1y | max4 vs max3 | 17 | 1.00% / 10.00 USDT | 1.15 | 4.53% | 17.65% | -0.15% |
| 1y | max5 vs max3 | 25 | 1.08% / 10.75 USDT | 1.10 | 5.49% | 20.00% | -0.15% |

## Three-Year Extra Trades Breakdown

### Full-run Profit Delta Versus max3

| Compared Run | Full Profit Delta | Interpretation |
|---|---:|---|
| max4 vs max3 | -65.09 USDT | max4 total profit is lower than max3 despite more trades. |
| max5 vs max3 | -52.26 USDT | max5 total profit is lower than max3 despite more trades. |

### max4 vs max3, 3y by Pair

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | 4 | -5.69% / -56.92 USDT | 0.00 | 5.69% | 0.00% | -2.67% |
| LINK/USDT:USDT | 3 | -3.60% / -35.99 USDT | 0.00 | 3.60% | 0.00% | -2.54% |
| ETH/USDT:USDT | 2 | -2.22% / -22.17 USDT | 0.00 | 2.22% | 0.00% | -4.79% |
| ADA/USDT:USDT | 4 | -1.98% / -19.75 USDT | 0.00 | 1.98% | 0.00% | -2.26% |
| TAO/USDT:USDT | 3 | -1.22% / -12.16 USDT | 0.00 | 1.22% | 0.00% | -2.84% |
| DOGE/USDT:USDT | 3 | -1.11% / -11.08 USDT | 0.00 | 1.11% | 0.00% | -1.56% |
| SUI/USDT:USDT | 2 | -1.07% / -10.66 USDT | 0.00 | 1.07% | 0.00% | -1.71% |
| NEAR/USDT:USDT | 5 | -0.81% / -8.11 USDT | 0.50 | 1.60% | 20.00% | 0.93% |
| BNB/USDT:USDT | 2 | 3.65% / 36.52 USDT | 4.93 | 0.89% | 50.00% | 3.98% |
| XRP/USDT:USDT | 3 | 14.34% / 143.40 USDT | inf | 0.00% | 100.00% | 10.00% |

### max4 vs max3, 3y by Side

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short | 31 | 0.31% / 3.08 USDT | 1.02 | 8.30% | 16.13% | -0.35% |

### max4 vs max3, 3y by Entry Tag

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | 7 | -6.76% / -67.60 USDT | 0.00 | 6.76% | 0.00% | -2.26% |
| short_pullback_restart | 24 | 7.07% / 70.68 USDT | 1.56 | 3.79% | 20.83% | 0.20% |

### max4 vs max3, 3y by Month

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-03 | 2 | -3.29% / -32.91 USDT | 0.00 | 3.29% | 0.00% | -4.26% |
| 2026-06 | 2 | -3.17% / -31.72 USDT | 0.00 | 3.17% | 0.00% | -2.80% |
| 2025-06 | 3 | -2.77% / -27.68 USDT | 0.00 | 2.77% | 0.00% | -2.75% |
| 2024-06 | 3 | -1.59% / -15.90 USDT | 0.00 | 1.59% | 0.00% | -2.85% |
| 2025-02 | 1 | -1.14% / -11.36 USDT | 0.00 | 1.14% | 0.00% | -4.90% |
| 2024-05 | 1 | -0.84% / -8.42 USDT | 0.00 | 0.84% | 0.00% | -3.49% |
| 2025-12 | 3 | -0.81% / -8.13 USDT | 0.00 | 0.81% | 0.00% | -2.01% |
| 2023-08 | 1 | -0.23% / -2.30 USDT | 0.00 | 0.23% | 0.00% | -0.97% |
| 2023-10 | 1 | -0.15% / -1.50 USDT | 0.00 | 0.15% | 0.00% | -1.96% |
| 2025-09 | 2 | -0.07% / -0.71 USDT | 0.00 | 0.07% | 0.00% | -0.11% |
| 2023-09 | 1 | -0.00% / -0.02 USDT | 0.00 | 0.00% | 0.00% | -0.03% |
| 2024-09 | 2 | 0.77% / 7.69 USDT | 22.60 | 0.04% | 50.00% | 4.88% |
| 2026-02 | 3 | 1.96% / 19.61 USDT | 1.75 | 2.51% | 33.33% | 1.76% |
| 2025-11 | 2 | 3.14% / 31.45 USDT | 2.92 | 1.64% | 50.00% | 3.10% |
| 2025-03 | 1 | 4.11% / 41.05 USDT | inf | 0.00% | 100.00% | 10.00% |
| 2026-01 | 3 | 4.39% / 43.94 USDT | 5.16 | 1.06% | 33.33% | 2.11% |

### max5 vs max3, 3y by Pair

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | 5 | -6.89% / -68.92 USDT | 0.00 | 6.89% | 0.00% | -3.01% |
| LINK/USDT:USDT | 3 | -3.63% / -36.31 USDT | 0.00 | 3.63% | 0.00% | -2.54% |
| TAO/USDT:USDT | 4 | -3.55% / -35.46 USDT | 0.00 | 3.55% | 0.00% | -3.15% |
| ADA/USDT:USDT | 5 | -3.34% / -33.38 USDT | 0.00 | 3.34% | 0.00% | -2.56% |
| DOGE/USDT:USDT | 6 | -2.76% / -27.60 USDT | 0.10 | 2.76% | 16.67% | 0.01% |
| ETH/USDT:USDT | 2 | -2.26% / -22.61 USDT | 0.00 | 2.26% | 0.00% | -4.79% |
| NEAR/USDT:USDT | 5 | -0.83% / -8.35 USDT | 0.49 | 1.62% | 20.00% | 0.93% |
| SUI/USDT:USDT | 3 | -0.16% / -1.57 USDT | 0.85 | 1.06% | 33.33% | 2.19% |
| ZEC/USDT:USDT | 2 | 5.41% / 54.14 USDT | inf | 0.00% | 100.00% | 10.01% |
| BNB/USDT:USDT | 3 | 7.51% / 75.12 USDT | 9.09 | 0.86% | 66.67% | 5.99% |
| XRP/USDT:USDT | 5 | 12.28% / 122.80 USDT | 6.49 | 1.90% | 60.00% | 4.37% |

### max5 vs max3, 3y by Side

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short | 43 | 1.79% / 17.86 USDT | 1.06 | 10.12% | 23.26% | 0.31% |

### max5 vs max3, 3y by Entry Tag

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | 11 | -7.22% / -72.19 USDT | 0.36 | 9.19% | 9.09% | -1.64% |
| short_pullback_restart | 32 | 9.01% / 90.05 USDT | 1.52 | 5.07% | 28.12% | 0.99% |

### max5 vs max3, 3y by Month

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-03 | 2 | -3.32% / -33.19 USDT | 0.00 | 3.32% | 0.00% | -4.26% |
| 2026-06 | 2 | -3.18% / -31.81 USDT | 0.00 | 3.18% | 0.00% | -2.80% |
| 2025-06 | 3 | -2.81% / -28.12 USDT | 0.00 | 2.81% | 0.00% | -2.75% |
| 2026-02 | 5 | -2.48% / -24.83 USDT | 0.65 | 4.84% | 20.00% | -0.70% |
| 2025-02 | 2 | -2.30% / -23.04 USDT | 0.00 | 2.30% | 0.00% | -4.62% |
| 2024-06 | 4 | -1.33% / -13.30 USDT | 0.18 | 1.48% | 25.00% | 0.36% |
| 2025-09 | 4 | -0.82% / -8.17 USDT | 0.00 | 0.82% | 0.00% | -1.56% |
| 2025-12 | 3 | -0.81% / -8.13 USDT | 0.00 | 0.81% | 0.00% | -2.01% |
| 2023-08 | 1 | -0.23% / -2.30 USDT | 0.00 | 0.23% | 0.00% | -0.97% |
| 2023-10 | 1 | -0.15% / -1.50 USDT | 0.00 | 0.15% | 0.00% | -1.96% |
| 2023-09 | 1 | -0.00% / -0.02 USDT | 0.00 | 0.00% | 0.00% | -0.03% |
| 2024-05 | 2 | 0.07% / 0.71 USDT | 1.08 | 0.84% | 50.00% | 3.25% |
| 2024-09 | 3 | 2.06% / 20.60 USDT | 233.23 | 0.01% | 66.67% | 6.60% |
| 2025-03 | 1 | 4.16% / 41.60 USDT | inf | 0.00% | 100.00% | 10.00% |
| 2025-11 | 4 | 5.59% / 55.89 USDT | 2.86 | 3.01% | 50.00% | 3.11% |
| 2026-01 | 5 | 7.35% / 73.47 USDT | 4.13 | 2.35% | 40.00% | 2.73% |

## Recent One-Year Extra Trades Breakdown

### max4 vs max3, 1y by Pair

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | 3 | -2.95% / -29.52 USDT | 0.00 | 2.95% | 0.00% | -3.53% |
| LINK/USDT:USDT | 2 | -1.16% / -11.63 USDT | 0.00 | 1.16% | 0.00% | -1.94% |
| ETH/USDT:USDT | 1 | -0.63% / -6.34 USDT | 0.00 | 0.63% | 0.00% | -4.69% |
| SUI/USDT:USDT | 2 | -0.56% / -5.58 USDT | 0.00 | 0.56% | 0.00% | -1.71% |
| ADA/USDT:USDT | 1 | -0.43% / -4.27 USDT | 0.00 | 0.43% | 0.00% | -2.93% |
| TAO/USDT:USDT | 2 | -0.33% / -3.32 USDT | 0.00 | 0.33% | 0.00% | -2.05% |
| NEAR/USDT:USDT | 2 | -0.12% / -1.23 USDT | 0.00 | 0.12% | 0.00% | -0.44% |
| BNB/USDT:USDT | 2 | 1.85% / 18.52 USDT | 4.89 | 0.47% | 50.00% | 3.98% |
| XRP/USDT:USDT | 2 | 5.34% / 53.37 USDT | inf | 0.00% | 100.00% | 10.00% |

### max4 vs max3, 1y by Side

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short | 17 | 1.00% / 10.00 USDT | 1.15 | 4.53% | 17.65% | -0.15% |

### max4 vs max3, 1y by Entry Tag

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | 4 | -2.74% / -27.41 USDT | 0.00 | 2.74% | 0.00% | -2.91% |
| short_pullback_restart | 13 | 3.74% / 37.41 USDT | 1.95 | 2.13% | 23.08% | 0.70% |

### max4 vs max3, 1y by Month

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-03 | 2 | -1.78% / -17.84 USDT | 0.00 | 1.78% | 0.00% | -4.26% |
| 2026-06 | 2 | -1.64% / -16.43 USDT | 0.00 | 1.64% | 0.00% | -2.80% |
| 2025-12 | 3 | -0.43% / -4.30 USDT | 0.00 | 0.43% | 0.00% | -2.01% |
| 2025-09 | 2 | -0.04% / -0.37 USDT | 0.00 | 0.04% | 0.00% | -0.11% |
| 2026-02 | 3 | 0.96% / 9.63 USDT | 1.71 | 1.33% | 33.33% | 1.76% |
| 2025-11 | 2 | 1.64% / 16.38 USDT | 2.92 | 0.86% | 50.00% | 3.10% |
| 2026-01 | 3 | 2.29% / 22.93 USDT | 5.17 | 0.55% | 33.33% | 2.11% |

### max5 vs max3, 1y by Pair

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | 3 | -2.92% / -29.20 USDT | 0.00 | 2.92% | 0.00% | -3.53% |
| TAO/USDT:USDT | 3 | -1.50% / -15.03 USDT | 0.00 | 1.50% | 0.00% | -2.73% |
| ADA/USDT:USDT | 2 | -1.14% / -11.44 USDT | 0.00 | 1.14% | 0.00% | -3.35% |
| LINK/USDT:USDT | 2 | -1.14% / -11.44 USDT | 0.00 | 1.14% | 0.00% | -1.94% |
| DOGE/USDT:USDT | 2 | -1.04% / -10.35 USDT | 0.00 | 1.04% | 0.00% | -2.63% |
| ETH/USDT:USDT | 1 | -0.60% / -5.96 USDT | 0.00 | 0.60% | 0.00% | -4.69% |
| SUI/USDT:USDT | 2 | -0.55% / -5.48 USDT | 0.00 | 0.55% | 0.00% | -1.71% |
| NEAR/USDT:USDT | 2 | -0.12% / -1.22 USDT | 0.00 | 0.12% | 0.00% | -0.44% |
| ZEC/USDT:USDT | 1 | 2.13% / 21.25 USDT | inf | 0.00% | 100.00% | 10.00% |
| BNB/USDT:USDT | 3 | 3.80% / 38.00 USDT | 9.18 | 0.45% | 66.67% | 5.99% |
| XRP/USDT:USDT | 4 | 4.16% / 41.62 USDT | 4.61 | 1.06% | 50.00% | 2.97% |

### max5 vs max3, 1y by Side

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short | 25 | 1.08% / 10.75 USDT | 1.10 | 5.49% | 20.00% | -0.15% |

### max5 vs max3, 1y by Entry Tag

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | 8 | -2.91% / -29.07 USDT | 0.42 | 4.70% | 12.50% | -1.73% |
| short_pullback_restart | 17 | 3.98% / 39.82 USDT | 1.71 | 2.06% | 23.53% | 0.59% |

### max5 vs max3, 1y by Month

| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |
|---|---:|---:|---:|---:|---:|---:|
| 2026-03 | 2 | -1.73% / -17.28 USDT | 0.00 | 1.73% | 0.00% | -4.26% |
| 2026-06 | 2 | -1.61% / -16.13 USDT | 0.00 | 1.61% | 0.00% | -2.80% |
| 2026-02 | 5 | -1.31% / -13.13 USDT | 0.64 | 2.50% | 20.00% | -0.70% |
| 2025-09 | 4 | -0.45% / -4.51 USDT | 0.00 | 0.45% | 0.00% | -1.56% |
| 2025-12 | 3 | -0.42% / -4.21 USDT | 0.00 | 0.42% | 0.00% | -2.01% |
| 2025-11 | 4 | 2.84% / 28.35 USDT | 2.81 | 1.57% | 50.00% | 3.11% |
| 2026-01 | 5 | 3.77% / 37.66 USDT | 4.13 | 1.20% | 40.00% | 2.73% |

## Required Answers

- **1. max4 相对 max3 多出来的交易是正贡献还是负贡献？** 从 extra trades 本身看是正贡献：三年 extra 31 笔，合计 3.08 USDT，PF 1.02。但从完整组合看是负贡献：max4 全量收益比 max3 低 65.09 USDT，说明放宽槽位改变了资金分配/并发占用，稀释了原 max3 的优质交易质量。
- **2. max5 相对 max3 多出来的交易是正贡献还是负贡献？** 从 extra trades 本身看是正贡献：三年 extra 43 笔，合计 17.86 USDT，PF 1.06。但从完整组合看仍是负贡献：max5 全量收益比 max3 低 52.26 USDT。
- **3. max4 / max5 的收益质量下降主要来自哪些 pair？** 三年 extra 亏损最明显的 pair：max4 是 SOL/USDT:USDT，max5 是 SOL/USDT:USDT；完整 pair 表显示 LINK、SOL、TAO、DOGE 等补位交易质量偏弱。
- **4. 下降主要来自 long 还是 short？** 主要来自 short。三年 extra side 拆解中，max4 最弱 side 是 short，max5 最弱 side 是 short；long extra 很少或基本没有成为主要来源。
- **5. 下降主要来自哪个 entry_tag？** 主要来自 short 侧补位信号，尤其是 short_compression_breakdown / short_compression_breakdown 这类 extra trades 的亏损或质量稀释更明显。
- **6. 是否存在某些月份集中亏损？** 是。三年 extra 月份中，max4 最差月份是 2026-03，max5 最差月份是 2026-03；这些月份与全量回测中的压力月份有重叠，例如 2024-06、2026-03、2026-02 等。
- **7. 是否说明 max3 已经足够？** 是。max4/max5 增加交易数后没有稳定提升全量收益质量，三年收益均低于 max3，PF 和平均单笔收益也下降。
- **8. 是否建议继续保持 max_open_trades=3？** 是。当前证据更支持继续保持 max3，而不是直接放宽到 max4/max5。
- **9. 是否有必要进入下一阶段压力月份诊断？** 有必要。extra trades 的亏损有明显月份聚集，下一步应先诊断压力月份，而不是马上改策略。
- **10. 本轮是否不应该直接优化策略？** 是。本轮只应停留在诊断，不应直接改参数、加过滤、删币或拆 bot。

## Diagnostic Interpretation

- Extra trades are not strongly negative by standalone profit, but their quality is weak: three-year max4 extra PF is only 1.02 with 16.13% winrate, and max5 extra PF is only 1.06 with 23.26% winrate.
- The full-run results are more important than standalone extra profit: max4/max5 use additional concurrent slots, change capital allocation, and reduce the realized quality of the original max3 portfolio.
- The extra trades behave like low-quality fill signals: they add turnover and drawdown pressure, but do not produce enough incremental edge to justify widening slots.

## Final Recommendation

- **A. 继续保持 max3**：推荐。它是当前最稳妥的默认选择，三年收益质量最好。
- **B. 尝试 side-specific slots**：次推荐，仅作为后续研究方向，因为问题主要集中在 short extra slots。
- **C. 尝试 pair-level 限制**：可以作为压力月份诊断后的候选，但现在不应直接执行。
- **D. 暂不优化，进入压力月份诊断**：推荐作为下一阶段动作。

**综合建议：优先选择 A + D，也就是继续保持 max3，同时暂不优化，进入压力月份诊断。**

## Output Files

- `user_data/analysis/positive13_trades_max3_3y.csv`
- `user_data/analysis/positive13_trades_max4_3y.csv`
- `user_data/analysis/positive13_trades_max5_3y.csv`
- `user_data/analysis/positive13_extra_trades_max4_vs_max3_3y.csv`
- `user_data/analysis/positive13_extra_trades_max5_vs_max3_3y.csv`
- `user_data/analysis/positive13_trades_max3_1y.csv`
- `user_data/analysis/positive13_trades_max4_1y.csv`
- `user_data/analysis/positive13_trades_max5_1y.csv`
- `user_data/analysis/positive13_extra_trades_max4_vs_max3_1y.csv`
- `user_data/analysis/positive13_extra_trades_max5_vs_max3_1y.csv`
