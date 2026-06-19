# Positive13 Pair / Tag / Regime Diagnosis

## Scope

- Diagnostic only: no strategy optimization, no parameter changes, no pair deletion, no bot split.
- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`
- Pair pool: Positive13
- max_open_trades: 3
- Uses filled historical data and the aligned max3 baseline.
- Rule applied: pair/tag with sample < 6 is observation only, not deletion/disable evidence.

## Matrix Outputs

- `positive13_pair_tag_regime_matrix.csv`: pair × entry_tag plus period / BTC regime / range / false_breakdown / quick_reverse / duration matrices.
- `positive13_pair_tag_pressure_matrix.csv`: pressure-window focused pair/tag/regime matrix.
- `positive13_pair_tag_quick_reverse_matrix.csv`: quick_reverse / false_breakdown / range focused matrix.

### Worst Pair × Entry Tag Rows, 3y

| Pair | Entry Tag | Trades | Profit | PF | Winrate | Avg Profit | Avg MAE/MFE |
|---|---|---:|---:|---:|---:|---:|---:|
| LINK/USDT:USDT | short_compression_breakdown | 7 | -40.44 | 0.3775 | 14.29% | -1.39% | 3.76/2.78 |
| NEAR/USDT:USDT | long_1d_center_compression | 2 | -16.73 | 0.0000 | 0.00% | -2.21% | 2.68/4.43 |
| SOL/USDT:USDT | short_compression_breakdown | 9 | -15.36 | 0.7888 | 22.22% | 0.12% | 2.77/5.19 |
| SUI/USDT:USDT | long_1d_center_compression | 1 | -8.87 | 0.0000 | 0.00% | -2.15% | 3.20/4.32 |
| LINK/USDT:USDT | long_1d_center_compression | 1 | -7.17 | 0.0000 | 0.00% | -2.14% | 2.02/0.76 |
| NEAR/USDT:USDT | short_compression_breakdown | 6 | 5.20 | 1.0834 | 16.67% | -0.66% | 2.66/4.77 |
| XRP/USDT:USDT | short_compression_breakdown | 10 | 11.38 | 1.1313 | 30.00% | 0.25% | 3.00/4.99 |
| BNB/USDT:USDT | short_compression_breakdown | 1 | 17.72 | inf | 100.00% | 10.00% | 1.20/13.38 |
| TAO/USDT:USDT | short_compression_breakdown | 4 | 19.97 | 1.4444 | 25.00% | 0.51% | 3.09/4.58 |
| XRP/USDT:USDT | long_1d_center_compression | 3 | 26.63 | 2.3210 | 33.33% | 1.90% | 1.90/7.73 |
| SUI/USDT:USDT | short_compression_breakdown | 7 | 30.92 | 1.9569 | 42.86% | 1.69% | 2.66/5.81 |
| BTC/USDT:USDT | short_pullback_restart | 17 | 31.66 | 1.2485 | 29.41% | 0.46% | 2.16/4.20 |
| DOGE/USDT:USDT | short_pullback_restart | 13 | 33.46 | 1.3005 | 30.77% | 1.10% | 2.61/5.54 |
| DOGE/USDT:USDT | long_1d_center_compression | 2 | 34.34 | 5.8117 | 50.00% | 3.95% | 1.69/5.75 |
| ADA/USDT:USDT | long_1d_center_compression | 2 | 40.18 | 6.6183 | 50.00% | 3.96% | 2.20/5.80 |
| ADA/USDT:USDT | short_compression_breakdown | 13 | 45.69 | 1.5693 | 30.77% | 1.10% | 2.39/5.61 |
| XRP/USDT:USDT | short_pullback_restart | 23 | 55.37 | 1.3804 | 21.74% | 0.09% | 2.00/4.08 |
| BNB/USDT:USDT | short_pullback_restart | 11 | 57.27 | 1.6794 | 45.45% | 1.17% | 2.56/5.45 |

### Worst Pair × Entry Tag Rows, Pressure Window

| Pair | Entry Tag | Trades | Profit | PF | Winrate | Avg Profit | Avg MAE/MFE |
|---|---|---:|---:|---:|---:|---:|---:|
| SOL/USDT:USDT | short_compression_breakdown | 2 | -42.05 | 0.0000 | 0.00% | -3.65% | 4.92/1.73 |
| ADA/USDT:USDT | short_compression_breakdown | 2 | -23.46 | 0.0000 | 0.00% | -1.28% | 1.81/3.93 |
| SUI/USDT:USDT | short_pullback_restart | 1 | -22.17 | 0.0000 | 0.00% | -4.04% | 4.14/4.50 |
| XRP/USDT:USDT | short_compression_breakdown | 1 | -21.81 | 0.0000 | 0.00% | -3.37% | 3.40/0.53 |
| NEAR/USDT:USDT | short_pullback_restart | 1 | -19.83 | 0.0000 | 0.00% | -4.10% | 4.44/2.74 |
| BTC/USDT:USDT | long_1d_center_compression | 1 | -19.22 | 0.0000 | 0.00% | -2.08% | 2.12/0.45 |
| BNB/USDT:USDT | short_pullback_restart | 2 | -17.08 | 0.2403 | 50.00% | -1.08% | 2.32/4.14 |
| TAO/USDT:USDT | short_compression_breakdown | 1 | -15.43 | 0.0000 | 0.00% | -1.97% | 2.50/0.17 |
| BTC/USDT:USDT | short_compression_breakdown | 1 | -0.78 | 0.0000 | 0.00% | -0.10% | 0.40/4.36 |
| XRP/USDT:USDT | short_pullback_restart | 4 | 0.26 | 1.0108 | 25.00% | -0.02% | 1.54/5.54 |
| ZEC/USDT:USDT | short_compression_breakdown | 1 | 52.34 | inf | 100.00% | 10.00% | 0.26/12.62 |

## Diagnosis Lists

- 全局稳定正贡献 pair: ADA/USDT:USDT, BNB/USDT:USDT, BTC/USDT:USDT, ETH/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT, ZEC/USDT:USDT
- 全局弱贡献或负贡献 pair: DOGE/USDT:USDT, SUI/USDT:USDT
- 更偏 short_pullback_restart 的 pair: ADA/USDT:USDT, DOGE/USDT:USDT, LINK/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT, ZEC/USDT:USDT
- 更偏 short_compression_breakdown 的 pair: BTC/USDT:USDT
- 更适合 long_1d_center_compression 的 pair: BNB/USDT:USDT
- 压力期拖累 pair: SOL/USDT:USDT, ADA/USDT:USDT, SUI/USDT:USDT, XRP/USDT:USDT, BTC/USDT:USDT, NEAR/USDT:USDT, BNB/USDT:USDT, TAO/USDT:USDT
- quick_reverse / false_breakdown 占比较高 pair: ADA/USDT:USDT, DOGE/USDT:USDT, ETH/USDT:USDT, LINK/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, SUI/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT
- 满足禁用候选硬条件的 pair/tag: none
- 样本不足仅观察 pair/tag: LINK/USDT:USDT × long_1d_center_compression, NEAR/USDT:USDT × long_1d_center_compression, SUI/USDT:USDT × long_1d_center_compression

## Required Answers

- **1. 哪些 pair 是全局稳定正贡献？** ADA/USDT:USDT, BNB/USDT:USDT, BTC/USDT:USDT, ETH/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT, ZEC/USDT:USDT。
- **2. 哪些 pair 是全局弱贡献或负贡献？** DOGE/USDT:USDT, SUI/USDT:USDT。
- **3. 哪些 pair 只适合 short_pullback_restart？** 没有足够证据支持“只适合”；相对偏好候选为 ADA/USDT:USDT, DOGE/USDT:USDT, LINK/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT, ZEC/USDT:USDT。
- **4. 哪些 pair 只适合 short_compression_breakdown？** 没有足够证据支持“只适合”；相对偏好候选为 BTC/USDT:USDT。
- **5. 哪些 pair 适合 long_1d_center_compression？** pair-level 达到当前偏好规则的是 BNB/USDT:USDT；其余样本不足以作 pair-level 强判断，但 long tag 整体仍是组合增益。
- **6. 哪些 pair 在压力期集中拖累？** SOL/USDT:USDT, ADA/USDT:USDT, SUI/USDT:USDT, XRP/USDT:USDT, BTC/USDT:USDT, NEAR/USDT:USDT, BNB/USDT:USDT, TAO/USDT:USDT。
- **7. 压力期拖累是否只是小样本偶然？** 部分是小样本，但不是完全偶然；压力期总样本只有 17 笔，pair/tag 层面多数不足 6 笔，因此只能标记压力敏感，不能直接禁用。
- **8. 哪些 pair 的 quick_reverse/false_breakdown 占比明显偏高？** ADA/USDT:USDT, DOGE/USDT:USDT, ETH/USDT:USDT, LINK/USDT:USDT, NEAR/USDT:USDT, SOL/USDT:USDT, SUI/USDT:USDT, TAO/USDT:USDT, XRP/USDT:USDT。
- **9. 是否存在 pair-level 禁用某个 entry_tag 的证据？** 不存在。没有 pair/tag 同时满足三年和近一年 PF < 1 且压力期拖累的硬条件。
- **10. 是否存在只在某个 BTC 4H regime 下启用某 pair/tag 的证据？** 还不充分。BTC 4H regime 有诊断价值，但不能单独作为启用条件，需要和 pair、range_market、false_breakdown 交叉验证。
- **11. 是否存在只在 range_market=false 时启用某 pair/tag 的证据？** 有方向性证据，特别是 short tag 在 range_market/反抽环境下质量下降，但还不足以直接实现过滤。
- **12. 是否存在 false_breakdown 前置特征，能用于未来过滤？** 当前 false_breakdown 是事后标签；可作为寻找前置特征的线索，建议继续研究入场前区间、ATR、EMA slope 和 BTC regime 的组合，但本轮不实现。
- **13. 是否有足够证据做第一个最小优化版本？** 证据还不够稳。按照规则，尚无明确 pair/tag 禁用候选。
- **14. 如果有，推荐哪个最小优化方向？** 暂不推荐实现版本；若后续必须做，方向应是 short tag 的 range/false_breakdown 前置特征验证，而不是删 pair。
- **15. 如果没有，是否继续保持当前主策略进入 dry-run 观察？** 是。继续保持当前主策略与 max3，进入 dry-run/实盘观察，同时保留诊断监控。

## Final Recommendation

- 不删 pair，不禁用 tag，不加过滤，不拆 bot。
- 保持 `max_open_trades=3`。
- 当前最合理动作是继续 dry-run/实盘观察，并追加监控：pair × tag × range_market/quick_reverse/false_breakdown 的月度统计。
- 如果后续要做最小优化，应先把 false_breakdown 的前置特征找出来，再用独立回测验证。

## Output Files

- `user_data/reports/positive13_pair_tag_regime_diagnosis.md`
- `user_data/analysis/positive13_pair_tag_regime_matrix.csv`
- `user_data/analysis/positive13_pair_tag_pressure_matrix.csv`
- `user_data/analysis/positive13_pair_tag_quick_reverse_matrix.csv`
