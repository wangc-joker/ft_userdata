# LongMicro Sample Concentration Audit

## Sample Uncertainty

- Trades / wins / losses: `7 / 3 / 4`
- Win rate: `42.86%`; Wilson 95% interval: `15.82% -> 74.95%`
- IID trade bootstrap probability of a positive seven-trade sum: `89.16%` baseline, `85.79%` under heavy execution stress
- Baseline bootstrap 95% interval for seven-trade return-ratio sum: `-8.36% -> +40.68%`

The bootstrap interval includes losses. It also assumes the seven observations are independent and identically distributed, which is optimistic because five trades come from one pair.

## Profit Concentration

- Baseline net Micro profit: `+76.26 USDT`
- Best single trade: `+63.02 USDT`, `82.63%` of net profit
- Two ROI trades: `+107.53 USDT`; all five non-ROI trades: `-31.27 USDT`
- Return-ratio sum after capping winners at +5%: `+5.30%`; at +3%: `+1.30%`
- Removing the best single trade leaves `+13.24 USDT`
- Heavy execution stress still leaves `+62.09 USDT`, but non-ROI trades remain `-35.74 USDT`

## Pair Leave-out

| Removed pair | Removed trades | Removed profit | Remaining profit | Remaining return-ratio sum |
|---|---:|---:|---:|---:|
| `BNB/USDT:USDT` | 5 | +79.29 USDT | -3.03 USDT | -0.77% |
| `BTC/USDT:USDT` | 2 | -3.03 USDT | +79.29 USDT | +16.08% |

## Year Leave-out

| Removed year | Removed trades | Removed profit | Remaining profit |
|---:|---:|---:|---:|
| 2023 | 2 | -1.80 USDT | +78.06 USDT |
| 2024 | 1 | +44.51 USDT | +31.75 USDT |
| 2025 | 4 | +33.55 USDT | +42.71 USDT |

## Cross-universe Duplication

- Top20/max6 Micro trades: `7`, profit `+76.25 USDT`
- All seven Top20/max6 Micro entries are the same pair and timestamp entries as Positive13/max3.
- Top20 therefore confirms that the surrounding portfolio stays profitable, but it does not add an independent Micro signal observation or reduce the BNB concentration risk.

## Decision

Execution-cost robustness does not remove sample uncertainty. The candidate remains observation-only until independent out-of-sample trades broaden the pair and market-period distribution. Do not create a BNB-only rule from this audit; that would fit the only profitable historical cluster.
