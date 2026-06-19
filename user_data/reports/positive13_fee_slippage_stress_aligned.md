# Positive13 Fee2x + Slippage Stress Aligned

## Scope

- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Config: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json`
- Local override: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`
- Pair pool: Positive13 static whitelist
- Max open trades: 3
- Baseline uses the filled local historical data.
- Fee2x uses Freqtrade `--fee 0.001`.
- Slippage is estimated from the new fee2x trade list, per side: light 0.03%, medium 0.05%, heavy 0.10%.
- Not performed: max4/max5 diagnostics, pressure-month diagnostics, long-module diagnostics, strategy parameter changes.

## Three-Year Result

- Timerange: `2023-06-18 -> 2026-06-18`

| Scenario | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Source |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline | 291 | 199.34% / 1993.45 USDT | 2.00 | 7.66% | 35.05% | 1.53% | `backtest-result-2026-06-19_03-08-28.zip` |
| fee2x | 291 | 181.25% / 1812.47 USDT | 1.91 | 8.23% | 34.71% | 1.46% | `backtest-result-2026-06-19_03-10-59.zip` |
| fee2x + light slippage | 291 | 173.64% / 1736.36 USDT | 1.85 | 9.61% | 34.36% | 1.40% | `backtest-result-2026-06-19_03-10-59.zip` |
| fee2x + medium slippage | 291 | 168.56% / 1685.61 USDT | 1.81 | 9.82% | 34.36% | 1.36% | `backtest-result-2026-06-19_03-10-59.zip` |
| fee2x + heavy slippage | 291 | 155.88% / 1558.75 USDT | 1.72 | 10.89% | 34.36% | 1.26% | `backtest-result-2026-06-19_03-10-59.zip` |

## Recent One-Year Result

- Timerange: `2025-06-18 -> 2026-06-18`

| Scenario | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Source |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline | 111 | 51.23% / 512.34 USDT | 2.00 | 7.65% | 39.64% | 1.52% | `backtest-result-2026-06-19_03-09-26.zip` |
| fee2x | 111 | 48.23% / 482.27 USDT | 1.91 | 8.25% | 38.74% | 1.45% | `backtest-result-2026-06-19_03-11-58.zip` |
| fee2x + light slippage | 111 | 46.15% / 461.54 USDT | 1.85 | 8.71% | 38.74% | 1.39% | `backtest-result-2026-06-19_03-11-58.zip` |
| fee2x + medium slippage | 111 | 44.77% / 447.72 USDT | 1.81 | 9.02% | 38.74% | 1.35% | `backtest-result-2026-06-19_03-11-58.zip` |
| fee2x + heavy slippage | 111 | 41.32% / 413.18 USDT | 1.72 | 9.81% | 38.74% | 1.25% | `backtest-result-2026-06-19_03-11-58.zip` |

## Required Answers

- **1. 补齐数据后的 baseline 是否和旧基线基本对齐？** 是。三年为 291 trades / +199.34% / PF 2.00 / MaxDD 7.66%；近一年为 111 trades / +51.23% / PF 2.00 / MaxDD 7.65%。
- **2. fee2x + medium slippage 是否仍然通过？** 是。三年 PF 1.81、MaxDD 9.82%；近一年 PF 1.81、Profit +44.77%。
- **3. fee2x + heavy slippage 是否仍然可接受？** 是，但属于更保守压力假设下的边际通过。三年 PF 1.72、MaxDD 10.89%；近一年 PF 1.72、Profit +41.32%。
- **4. 三年 PF 是否仍 >= 1.60？** 是。三年 medium PF 1.81，heavy PF 1.72。
- **5. 三年 MaxDD 是否仍 <= 12%？** 是。三年 medium MaxDD 9.82%，heavy MaxDD 10.89%。
- **6. 近一年 PF 是否仍 >= 1.50？** 是。近一年 medium PF 1.81，heavy PF 1.72。
- **7. 近一年 Profit 是否仍 > 0？** 是。近一年 medium Profit +44.77%，heavy Profit +41.32%。
- **8. 是否建议进入第 8～10 步？** 建议进入，但只进入诊断，不建议直接改策略。当前 baseline 已对齐，medium 与 heavy 压力测试均通过核心门槛，可以继续做 max4/max5 多余交易诊断等第 8～10 步。

## Output Files

- `user_data/analysis/positive13_fee_slippage_stress_aligned.csv`
- `user_data/reports/positive13_fee_slippage_stress_aligned.md`
