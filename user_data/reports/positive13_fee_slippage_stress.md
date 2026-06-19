# Positive13 Fee2x + Slippage Stress

## Scope

- Only Codex execution checklist steps 1-7 were performed.
- No strategy optimization, no parameter changes, no max4/max5 diagnostics, no pressure-month diagnostics, no long/tag diagnostics.
- Fee2x was run with Freqtrade `--fee 0.001`.
- Slippage was estimated post-trade from fee2x exported trades.
- Slippage levels are per side: light 0.03%, medium 0.05%, heavy 0.10%.

## Three-Year Sample

| 方案 | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Worst Month | Worst Pair |
|---|---:|---:|---:|---:|---:|---:|---|---|
| baseline | 241 | 151.13% / 1511.33 USDT | 2.01 | 7.24% | 34.44% | 1.59% | 2026-03 (-49.81) | NEAR/USDT:USDT (-23.61) |
| fee2x | 241 | 140.75% / 1407.53 USDT | 1.92 | 7.84% | 34.02% | 1.53% | 2026-03 (-51.59) | NEAR/USDT:USDT (-26.01) |
| fee2x + light slippage | 241 | 134.62% / 1346.16 USDT | 1.85 | 9.87% | 33.61% | 1.47% | 2026-03 (-53.96) | NEAR/USDT:USDT (-28.46) |
| fee2x + medium slippage | 241 | 130.52% / 1305.24 USDT | 1.81 | 10.21% | 33.61% | 1.43% | 2026-03 (-55.54) | NEAR/USDT:USDT (-30.10) |
| fee2x + heavy slippage | 241 | 120.29% / 1202.95 USDT | 1.72 | 11.06% | 33.61% | 1.33% | 2026-03 (-59.49) | NEAR/USDT:USDT (-34.18) |

## Recent One-Year Sample

| 方案 | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Worst Month | Worst Pair |
|---|---:|---:|---:|---:|---:|---:|---|---|
| baseline | 101 | 38.78% / 387.78 USDT | 1.86 | 7.17% | 35.64% | 1.40% | 2025-06 (-30.00) | DOGE/USDT:USDT (-33.39) |
| fee2x | 101 | 36.18% / 361.80 USDT | 1.77 | 7.74% | 34.65% | 1.33% | 2025-06 (-30.83) | DOGE/USDT:USDT (-35.22) |
| fee2x + light slippage | 101 | 34.34% / 343.44 USDT | 1.71 | 8.18% | 34.65% | 1.27% | 2025-06 (-31.36) | DOGE/USDT:USDT (-36.64) |
| fee2x + medium slippage | 101 | 33.12% / 331.21 USDT | 1.68 | 8.48% | 34.65% | 1.23% | 2025-06 (-31.71) | DOGE/USDT:USDT (-37.60) |
| fee2x + heavy slippage | 101 | 30.06% / 300.62 USDT | 1.59 | 9.23% | 34.65% | 1.13% | 2026-03 (-33.36) | DOGE/USDT:USDT (-39.98) |

## Required Answers

1. Baseline 是否复现成功：是。三年 151.13%，PF 2.01，MaxDD 7.24%；近一年 38.78%，PF 1.86，MaxDD 7.17%。
2. fee2x + light / medium / heavy slippage 后，三年和近一年是否仍然稳定：light/medium 稳定；heavy 下两个样本仍保持正收益且 MaxDD 小于 12%，但近一年 PF 1.59，严格低于 1.6，属于边缘压力结果。
3. PF 是否仍大于 1.6：不是全部。light/medium 均大于 1.6；heavy 下三年 PF 1.72，近一年 PF 1.59。
4. MaxDD 是否仍小于 12%：是。medium 压力下三年 MaxDD 10.21%，近一年 MaxDD 8.48%。
5. 是否建议进入下一阶段诊断：建议。当前已经通过文档 4.5 的 medium slippage 通过标准，但下一阶段应只做诊断，不要直接优化。
6. 是否暂时不要改策略：是，暂时不要改策略。当前目标是验证成本承受力，结果没有显示必须立刻改策略的证据。

## Output Files

- `user_data/analysis/positive13_fee_slippage_stress.py`
- `user_data/analysis/positive13_fee_slippage_stress.csv`
- `user_data/reports/positive13_baseline_recheck.md`
- `user_data/reports/positive13_fee_slippage_stress.md`
