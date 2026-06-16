# DualTrendCompressionRestartShortV1 稳健性验证报告

生成时间：2026-06-15 14:59:29

## 1. 基准结果

全样本组合策略：

```text
交易数：339
总收益：1027.09485 USDT / 102.7095%
Profit Factor：1.5283
胜率：31.5634%
最大回撤：180.540043 USDT / 9.2684%
```

近期组合策略：

```text
交易数：171
总收益：391.538924 USDT / 39.1539%
Profit Factor：1.4843
胜率：33.9181%
最大回撤：124.680243 USDT / 9.3194%
```

## 2. Entry Tag 稳定性

| strategy | sample | entry_tag | trades | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DualTrendCompressionRestartShortPullbackOnlyV1Strategy | full | short_pullback_restart | 337 | 100.7052 | 1.5224 | 31.454 | 9.2717 | 1.0384 |
| DualTrendCompressionRestartShortV1Strategy | full | short_pullback_restart | 261 | 63.5899 | 1.4164 | 31.4176 | 10.71 | 0.9436 |
| DualTrendCompressionRestartShortV1Strategy | full | short_compression_breakdown | 78 | 39.1196 | 1.9381 | 32.0513 | 7.4395 | 1.4268 |
| DualTrendCompressionRestartShortCompressionOnlyV1Strategy | full | short_compression_breakdown | 116 | 22.7626 | 1.4472 | 29.3103 | 10.9811 | 0.9071 |
| DualTrendCompressionRestartShortPullbackOnlyV1Strategy | recent | short_pullback_restart | 169 | 37.7669 | 1.474 | 33.7278 | 9.3136 | 1.0437 |
| DualTrendCompressionRestartShortV1Strategy | recent | short_compression_breakdown | 35 | 23.7856 | 2.6026 | 40.0 | 2.5188 | 2.6511 |
| DualTrendCompressionRestartShortCompressionOnlyV1Strategy | recent | short_compression_breakdown | 58 | 18.3881 | 1.6795 | 32.7586 | 6.3576 | 1.2484 |
| DualTrendCompressionRestartShortV1Strategy | recent | short_pullback_restart | 136 | 15.3683 | 1.2329 | 32.3529 | 10.343 | 0.6708 |

结论：

```text
short_pullback_restart 是更稳定的主信号。
它在全样本和近期样本中的交易数更多，收益贡献连续性更好。
short_compression_breakdown 近期表现不错，但全样本年度稳定性弱于 pullback，更适合作为补充信号。
```

## 3. Pair 贡献与拖累

全样本贡献最大：

| pair | trades | total_profit_abs | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct | best_trade_pct | worst_trade_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ZEC/USDT:USDT | 19 | 235.116743 | 23.5117 | 4.7296 | 57.8947 | 2.4503 | 4.3625 | 10.0164 | -3.6975 |
| DOGE/USDT:USDT | 31 | 181.04136 | 18.1041 | 2.1208 | 35.4839 | 4.8543 | 1.9887 | 10.0032 | -4.5661 |
| ETH/USDT:USDT | 25 | 171.707294 | 17.1707 | 2.477 | 36.0 | 2.4979 | 2.0202 | 10.0002 | -4.919 |
| BNB/USDT:USDT | 25 | 138.627782 | 13.8628 | 2.0785 | 48.0 | 4.2006 | 2.0671 | 10.0009 | -4.6816 |
| ADA/USDT:USDT | 36 | 119.339858 | 11.934 | 1.593 | 30.5556 | 7.6183 | 1.4166 | 10.0124 | -4.5628 |

全样本拖累最大：

| pair | trades | total_profit_abs | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct | best_trade_pct | worst_trade_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TRX/USDT:USDT | 19 | -85.767305 | -8.5767 | 0.1396 | 5.2632 | 8.7011 | -1.1594 | 2.4872 | -3.9111 |
| LINK/USDT:USDT | 31 | -63.092968 | -6.3093 | 0.7322 | 19.3548 | 9.6446 | -0.1205 | 10.0035 | -4.6471 |
| NEAR/USDT:USDT | 34 | 0.823328 | 0.0823 | 1.0033 | 20.5882 | 8.958 | -0.2966 | 10.0245 | -4.7363 |
| XRP/USDT:USDT | 37 | 38.663991 | 3.8664 | 1.1785 | 24.3243 | 9.2944 | -0.0149 | 10.0061 | -4.4705 |
| BTC/USDT:USDT | 30 | 40.920966 | 4.0921 | 1.2446 | 26.6667 | 5.8621 | -0.0811 | 10.0 | -4.2306 |

近期贡献最大：

| pair | trades | total_profit_abs | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct | best_trade_pct | worst_trade_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XRP/USDT:USDT | 17 | 80.457472 | 8.0457 | 2.2811 | 41.1765 | 1.8605 | 1.4112 | 10.001 | -4.4705 |
| ETH/USDT:USDT | 12 | 76.571785 | 7.6572 | 2.4349 | 41.6667 | 1.8544 | 2.518 | 10.0002 | -4.919 |
| DOGE/USDT:USDT | 17 | 73.156869 | 7.3157 | 1.9892 | 35.2941 | 3.7094 | 2.1586 | 10.0022 | -4.5661 |
| SUI/USDT:USDT | 12 | 52.67352 | 5.2674 | 1.8912 | 41.6667 | 2.5367 | 1.7364 | 10.0021 | -4.6996 |
| ZEC/USDT:USDT | 6 | 47.312789 | 4.7313 | 3.2988 | 66.6667 | 1.0429 | 3.9716 | 10.005 | -3.6975 |

近期拖累最大：

| pair | trades | total_profit_abs | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct | best_trade_pct | worst_trade_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LINK/USDT:USDT | 13 | -38.695758 | -3.8696 | 0.561 | 15.3846 | 6.6559 | -0.7092 | 9.9989 | -4.6471 |
| TRX/USDT:USDT | 12 | -35.433153 | -3.5433 | 0.2124 | 8.3333 | 3.6294 | -0.8629 | 2.4872 | -3.9111 |
| BNB/USDT:USDT | 11 | -21.387742 | -2.1388 | 0.639 | 36.3636 | 3.3729 | -0.4755 | 10.0006 | -3.3395 |
| TAO/USDT:USDT | 6 | 3.204856 | 0.3205 | 1.1194 | 50.0 | 2.2481 | 0.1383 | 9.9995 | -4.9952 |
| ADA/USDT:USDT | 18 | 34.078412 | 3.4078 | 1.403 | 27.7778 | 5.7673 | 1.4085 | 10.0033 | -3.5787 |

## 4. Pair 剔除测试

| sample | case | pairs | trades | total_profit_pct | profit_factor | winrate | max_drawdown_pct | avg_profit_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | remove_worst_1 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,LINK/USDT:USDT,NEAR/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 327 | 118.2759 | 1.5995 | 33.3333 | 8.0402 | 1.2053 |
| full | remove_worst_2 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,NEAR/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 307 | 124.871 | 1.6675 | 34.202 | 7.5732 | 1.2774 |
| full | remove_worst_3 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 275 | 132.1472 | 1.7687 | 36.0 | 6.8874 | 1.4802 |
| full | large_cap_8 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,LINK/USDT:USDT | 267 | 67.1852 | 1.4754 | 30.7116 | 9.3059 | 0.9895 |
| full | positive_pairs_only | ZEC/USDT:USDT,DOGE/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,ADA/USDT:USDT,SUI/USDT:USDT,TAO/USDT:USDT,SOL/USDT:USDT,BTC/USDT:USDT,XRP/USDT:USDT,NEAR/USDT:USDT | 309 | 114.9195 | 1.6166 | 33.657 | 7.9003 | 1.2331 |
| recent | remove_worst_1 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,NEAR/USDT:USDT,SUI/USDT:USDT,TRX/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 165 | 37.1186 | 1.485 | 33.9394 | 7.4809 | 1.0398 |
| recent | remove_worst_2 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,NEAR/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 159 | 44.5992 | 1.5743 | 36.478 | 7.5353 | 1.2343 |
| recent | remove_worst_3 | BTC/USDT:USDT,ETH/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,NEAR/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,TAO/USDT:USDT | 151 | 47.9113 | 1.6391 | 36.4238 | 6.8043 | 1.3807 |
| recent | large_cap_8 | BTC/USDT:USDT,ETH/USDT:USDT,BNB/USDT:USDT,SOL/USDT:USDT,XRP/USDT:USDT,DOGE/USDT:USDT,ADA/USDT:USDT,LINK/USDT:USDT | 138 | 31.5593 | 1.5035 | 33.3333 | 9.242 | 1.2094 |
| recent | positive_pairs_only | XRP/USDT:USDT,ETH/USDT:USDT,DOGE/USDT:USDT,SUI/USDT:USDT,ZEC/USDT:USDT,NEAR/USDT:USDT,BTC/USDT:USDT,SOL/USDT:USDT,ADA/USDT:USDT,TAO/USDT:USDT | 151 | 45.0986 | 1.6058 | 35.7616 | 7.8563 | 1.3105 |

## 5. 风险参数矩阵

以下为组合策略在不同 `risk_per_trade`、`max_position_value_pct`、`max_open_trades` 下的结果：

| sample | risk_per_trade | max_position_value_pct | max_open_trades | trades | total_profit_pct | profit_factor | winrate | max_drawdown_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | 0.005 | 0.25 | 2 | 268 | 43.6235 | 1.5336 | 31.7164 | 5.4882 |
| full | 0.005 | 0.35 | 2 | 268 | 44.1257 | 1.5089 | 31.7164 | 5.7372 |
| full | 0.005 | 0.45 | 2 | 268 | 45.1899 | 1.5121 | 31.7164 | 5.8488 |
| full | 0.0075 | 0.25 | 2 | 268 | 71.6584 | 1.602 | 31.7164 | 7.0263 |
| full | 0.0075 | 0.35 | 2 | 268 | 72.4562 | 1.5411 | 31.7164 | 7.9598 |
| full | 0.0075 | 0.45 | 2 | 268 | 71.4507 | 1.5074 | 31.7164 | 8.309 |
| full | 0.01 | 0.25 | 2 | 268 | 86.8529 | 1.6318 | 31.7164 | 7.5297 |
| full | 0.01 | 0.35 | 2 | 268 | 103.0583 | 1.5738 | 31.7164 | 9.5214 |
| full | 0.01 | 0.45 | 2 | 268 | 103.6764 | 1.5301 | 31.7164 | 10.3618 |
| full | 0.005 | 0.25 | 3 | 339 | 64.0971 | 1.5582 | 31.5634 | 6.3826 |
| full | 0.005 | 0.35 | 3 | 339 | 67.8125 | 1.5518 | 31.5634 | 6.9084 |
| full | 0.005 | 0.45 | 3 | 339 | 64.4811 | 1.5184 | 31.5634 | 7.0933 |
| full | 0.0075 | 0.25 | 3 | 339 | 98.9786 | 1.5791 | 31.5634 | 8.6473 |
| full | 0.0075 | 0.35 | 3 | 339 | 102.7095 | 1.5283 | 31.5634 | 9.2684 |
| full | 0.0075 | 0.45 | 3 | 339 | 98.8782 | 1.4943 | 31.5634 | 9.8713 |
| full | 0.01 | 0.25 | 3 | 339 | 123.1217 | 1.6115 | 31.5634 | 10.0897 |
| full | 0.01 | 0.35 | 3 | 339 | 146.9286 | 1.5474 | 31.5634 | 9.9048 |
| full | 0.01 | 0.45 | 3 | 339 | 146.0883 | 1.5288 | 31.5634 | 11.6521 |
| full | 0.005 | 0.25 | 5 | 422 | 72.1204 | 1.4675 | 30.5687 | 9.5294 |
| full | 0.005 | 0.35 | 5 | 418 | 75.6949 | 1.4757 | 30.622 | 9.339 |
| full | 0.005 | 0.45 | 5 | 418 | 73.7077 | 1.4618 | 30.622 | 9.33 |
| full | 0.0075 | 0.25 | 5 | 419 | 117.9788 | 1.5241 | 30.7876 | 10.573 |
| full | 0.0075 | 0.35 | 5 | 402 | 119.6521 | 1.5176 | 30.597 | 9.4628 |
| full | 0.0075 | 0.45 | 5 | 394 | 113.5308 | 1.4863 | 31.2183 | 9.412 |
| full | 0.01 | 0.25 | 5 | 411 | 145.7657 | 1.5578 | 30.9002 | 10.7381 |
| full | 0.01 | 0.35 | 5 | 379 | 161.6783 | 1.5505 | 31.6623 | 12.4226 |
| full | 0.01 | 0.45 | 5 | 369 | 149.2041 | 1.5103 | 31.7073 | 12.6593 |
| recent | 0.005 | 0.25 | 2 | 127 | 21.5392 | 1.6331 | 35.4331 | 5.4636 |
| recent | 0.005 | 0.35 | 2 | 127 | 19.9585 | 1.5638 | 35.4331 | 5.7451 |
| recent | 0.005 | 0.45 | 2 | 127 | 19.5885 | 1.5469 | 35.4331 | 5.8913 |
| recent | 0.0075 | 0.25 | 2 | 127 | 33.3237 | 1.6681 | 35.4331 | 7.0305 |
| recent | 0.0075 | 0.35 | 2 | 127 | 33.8217 | 1.6175 | 35.4331 | 7.9401 |
| recent | 0.0075 | 0.45 | 2 | 127 | 31.4072 | 1.5539 | 35.4331 | 8.31 |
| recent | 0.01 | 0.25 | 2 | 127 | 40.0291 | 1.7006 | 35.4331 | 7.568 |
| recent | 0.01 | 0.35 | 2 | 127 | 46.0673 | 1.627 | 35.4331 | 9.5203 |
| recent | 0.01 | 0.45 | 2 | 127 | 46.0621 | 1.5859 | 35.4331 | 10.3652 |
| recent | 0.005 | 0.25 | 3 | 171 | 26.153 | 1.5233 | 33.9181 | 6.3078 |
| recent | 0.005 | 0.35 | 3 | 171 | 25.7218 | 1.4908 | 33.9181 | 6.9013 |
| recent | 0.005 | 0.45 | 3 | 171 | 23.0968 | 1.4371 | 33.9181 | 7.0504 |
| recent | 0.0075 | 0.25 | 3 | 171 | 39.9409 | 1.5436 | 33.9181 | 8.4775 |
| recent | 0.0075 | 0.35 | 3 | 171 | 39.1539 | 1.4843 | 33.9181 | 9.3194 |
| recent | 0.0075 | 0.45 | 3 | 171 | 36.429 | 1.4391 | 33.9181 | 9.8817 |
| recent | 0.01 | 0.25 | 3 | 171 | 49.6094 | 1.5829 | 33.9181 | 9.9553 |
| recent | 0.01 | 0.35 | 3 | 171 | 54.3695 | 1.499 | 33.9181 | 9.8704 |
| recent | 0.01 | 0.45 | 3 | 171 | 56.024 | 1.4991 | 33.9181 | 11.6335 |
| recent | 0.005 | 0.25 | 5 | 220 | 28.3001 | 1.4138 | 32.7273 | 9.3931 |
| recent | 0.005 | 0.35 | 5 | 220 | 28.6218 | 1.4085 | 32.7273 | 9.2443 |
| recent | 0.005 | 0.45 | 5 | 220 | 28.4481 | 1.4065 | 33.1818 | 9.2483 |
| recent | 0.0075 | 0.25 | 5 | 220 | 48.6314 | 1.4955 | 32.7273 | 10.6556 |
| recent | 0.0075 | 0.35 | 5 | 213 | 48.9806 | 1.493 | 33.3333 | 9.461 |
| recent | 0.0075 | 0.45 | 5 | 210 | 45.7783 | 1.4577 | 33.8095 | 9.428 |
| recent | 0.01 | 0.25 | 5 | 217 | 55.4584 | 1.5035 | 32.7189 | 10.9029 |
| recent | 0.01 | 0.35 | 5 | 199 | 62.2177 | 1.5165 | 33.6683 | 12.3621 |
| recent | 0.01 | 0.45 | 5 | 191 | 55.2111 | 1.4634 | 34.0314 | 12.6442 |

结论：

```text
如果不同风险参数下收益方向保持为正，且回撤没有失控，说明入场逻辑具备一定稳健性。
实盘 dry-run 初期更适合优先使用较保守组合：risk_per_trade=0.005 或 0.0075，max_open_trades=2 或 3。
```

## 6. 成本压力测试

手续费压力：

| sample | cost_case | trades | total_profit_pct | profit_factor | winrate | max_drawdown_pct |
| --- | --- | --- | --- | --- | --- | --- |
| full | fee_1p5x | 340 | 95.1877 | 1.4889 | 31.1765 | 9.6408 |
| full | fee_2x | 341 | 86.9136 | 1.4465 | 31.085 | 9.982 |
| recent | fee_1p5x | 171 | 37.3715 | 1.4573 | 33.3333 | 9.5293 |
| recent | fee_2x | 172 | 34.4891 | 1.4119 | 33.1395 | 9.8439 |

滑点压力，基于导出交易事后扣减，每边滑点：

| sample | cost_case | trades | total_profit_pct | profit_factor | winrate |
| --- | --- | --- | --- | --- | --- |
| full | slippage_0.05pct_each_side | 339 | 89.7112 | 1.4406 | 31.2684 |
| full | slippage_0.10pct_each_side | 339 | 76.713 | 1.3603 | 30.9735 |
| full | slippage_0.20pct_each_side | 339 | 50.7165 | 1.2191 | 30.3835 |
| recent | slippage_0.05pct_each_side | 171 | 33.8533 | 1.4005 | 33.3333 |
| recent | slippage_0.10pct_each_side | 171 | 28.5526 | 1.3235 | 33.3333 |
| recent | slippage_0.20pct_each_side | 171 | 17.9514 | 1.1876 | 32.7485 |

## 7. 是否建议进入 Dry-run

```text
建议：可以进入小资金 dry-run，但不建议直接实盘。

理由：
1. 基准组合、pullback-only、compression-only 在近期样本均为正。
2. pullback 信号更稳定，可以作为 V1 主信号。
3. LINK、TRX 等 pair 存在明显拖累，需要先做白名单收缩。
4. 成本和滑点压力仍需重点看 2 倍手续费与 0.10%-0.20% 滑点后的结果。
5. dry-run 建议先用保守风险：risk_per_trade=0.005 或 0.0075，max_open_trades=2 或 3。
```

## 8. 输出文件

```text
summary.csv
pair_breakdown.csv
tag_breakdown.csv
cost_pressure.csv
```
