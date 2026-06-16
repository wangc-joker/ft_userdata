# DualTrend Long V1 稳健性验证报告

- 生成时间：2026-06-15 17:43:14
- 全样本：2022-10-01 至 2026-05-07；因 `startup_candle_count=1000`，实际可交易起点约为 2022-11-11。
- 近期样本：2025-01-01 至 2026-05-07。
- 资金和基础配置：1000 USDT、max_open_trades=3、1h、Binance USDT 永续、保护开启。
- Top8 测试使用 13-pair 配置加载数据，策略内部 allowlist 限定为 BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK。

## 1. 入场过滤一致性修正

- 已修正：`custom_stoploss()` 取入场信号 K 线时，使用 `date < trade.open_date_utc` 锚定信号 candle，避免 Freqtrade 下一根 K 开仓导致止损和图表信号错位。
- 已同步：画图脚本的 `return_24h`、ATR EWM 和 `atr_ref=atr.shift(1)` 与策略一致。
- `close_position >= 0.72` 在 `candle_quality_long` 中生效；修正后逐笔验证无违规。
- `max_stop_distance=0.05` 在入场信号和 `custom_stake_amount()` 中双层生效；修正后逐笔验证无超过 5% 的信号风险。

| 验证项 | 结果 |
| --- | --- |
| 交易数 | 95 |
| 最小 close_position | 0.7250 |
| close_position < 0.72 违规数 | 0 |
| 最大 signal_risk_pct | 4.95% |
| signal_risk_pct > 5% 违规数 | 0 |
| 最大实际开仓风险 | 4.93% |
| 实际开仓风险 > 5% 数 | 0 |

修正前后 Long V1 回测：

| 样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate |
| --- | --- | --- | --- | --- | --- | --- |
| 修正前 全样本 | 95 | 160.87 | 16.09% | 1.42 | 7.09% | 45.26% |
| 修正后 全样本 | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% |
| 修正前 近期 | 30 | 94.48 | 9.45% | 1.95 | 4.85% | 50.00% |
| 修正后 近期 | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% |

结论：修正后全样本利润从 160.87 降到 158.38 USDT，但 MaxDD 从 7.09% 降到 6.98%；近期利润从 94.48 提高到 97.12 USDT，MaxDD 从 4.85% 降到 4.46%。修正是必要的，且没有破坏策略表现。

## 2. Entry Tag 拆分

全样本汇总：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pullback Only | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| Compression Only | 28 | -36.61 | -3.66% | 0.74 | 5.95% | 32.14% | -0.52% | ZEC/USDT:USDT 5.01% | XRP/USDT:USDT -4.65% |
| Combined | 96 | 170.38 | 17.04% | 1.44 | 5.77% | 45.83% | 0.70% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |

近期汇总：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pullback Only | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| Compression Only | 7 | -7.32 | -0.73% | 0.81 | 2.94% | 28.57% | -0.88% | BNB/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| Combined | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |

按年份：

| 策略 | Year | Trades | Profit USDT | PF | Winrate |
| --- | --- | --- | --- | --- | --- |
| Pullback Only | 2023 | 40 | 54.70 | 1.34 | 45.00% |
| Pullback Only | 2024 | 25 | 0.61 | 1.01 | 40.00% |
| Pullback Only | 2025 | 25 | 99.85 | 2.18 | 48.00% |
| Pullback Only | 2026 | 5 | 3.23 | 1.18 | 60.00% |
| Compression Only | 2023 | 13 | -9.33 | 0.85 | 38.46% |
| Compression Only | 2024 | 8 | -20.27 | 0.55 | 25.00% |
| Compression Only | 2025 | 6 | 0.38 | 1.01 | 33.33% |
| Compression Only | 2026 | 1 | -7.40 | 0.00 | 0.00% |
| Combined | 2023 | 41 | 46.50 | 1.27 | 43.90% |
| Combined | 2024 | 25 | 20.77 | 1.18 | 44.00% |
| Combined | 2025 | 25 | 99.77 | 2.17 | 48.00% |
| Combined | 2026 | 5 | 3.34 | 1.19 | 60.00% |
| Pullback Only | 2025 | 25 | 94.09 | 2.17 | 48.00% |
| Pullback Only | 2026 | 5 | 3.02 | 1.18 | 60.00% |
| Compression Only | 2025 | 6 | 0.30 | 1.01 | 33.33% |
| Compression Only | 2026 | 1 | -7.62 | 0.00 | 0.00% |
| Combined | 2025 | 25 | 94.09 | 2.17 | 48.00% |
| Combined | 2026 | 5 | 3.02 | 1.18 | 60.00% |

按 pair：

| 策略 | Pair | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pullback Only | BNB/USDT:USDT | 39 | 92.84 | 9.28% | 1.59 | 5.99% | 41.03% |
| Pullback Only | DOGE/USDT:USDT | 11 | 58.25 | 5.82% | 3.39 | 1.58% | 72.73% |
| Pullback Only | ZEC/USDT:USDT | 17 | 7.97 | 0.80% | 1.11 | 3.79% | 47.06% |
| Pullback Only | XRP/USDT:USDT | 28 | -0.67 | -0.07% | 0.99 | 4.07% | 39.29% |
| Compression Only | DOGE/USDT:USDT | 6 | 8.73 | 0.87% | 1.37 | 1.56% | 50.00% |
| Compression Only | XRP/USDT:USDT | 7 | 4.28 | 0.43% | 1.14 | 1.47% | 42.86% |
| Compression Only | ZEC/USDT:USDT | 7 | -14.39 | -1.44% | 0.62 | 3.70% | 28.57% |
| Compression Only | BNB/USDT:USDT | 8 | -35.23 | -3.52% | 0.32 | 4.48% | 12.50% |
| Combined | BNB/USDT:USDT | 39 | 91.98 | 9.20% | 1.58 | 6.06% | 41.03% |
| Combined | DOGE/USDT:USDT | 12 | 70.68 | 7.07% | 3.90 | 1.58% | 75.00% |
| Combined | ZEC/USDT:USDT | 17 | 7.93 | 0.79% | 1.11 | 3.81% | 47.06% |
| Combined | XRP/USDT:USDT | 28 | -0.22 | -0.02% | 1.00 | 4.07% | 39.29% |
| Pullback Only | BNB/USDT:USDT | 15 | 48.22 | 4.82% | 1.91 | 3.71% | 40.00% |
| Pullback Only | XRP/USDT:USDT | 10 | 21.36 | 2.14% | 1.59 | 2.72% | 50.00% |
| Pullback Only | DOGE/USDT:USDT | 2 | 18.70 | 1.87% | 0.00 | 0.00% | 100.00% |
| Pullback Only | ZEC/USDT:USDT | 3 | 8.84 | 0.88% | 2.08 | 0.82% | 66.67% |
| Compression Only | BNB/USDT:USDT | 2 | 9.79 | 0.98% | 2.43 | 0.67% | 50.00% |
| Compression Only | ZEC/USDT:USDT | 1 | -7.75 | -0.77% | 0.00 | 0.77% | 0.00% |
| Compression Only | XRP/USDT:USDT | 4 | -9.36 | -0.94% | 0.60 | 1.54% | 25.00% |
| Combined | BNB/USDT:USDT | 15 | 48.22 | 4.82% | 1.91 | 3.71% | 40.00% |
| Combined | XRP/USDT:USDT | 10 | 21.36 | 2.14% | 1.59 | 2.72% | 50.00% |
| Combined | DOGE/USDT:USDT | 2 | 18.70 | 1.87% | 0.00 | 0.00% | 100.00% |
| Combined | ZEC/USDT:USDT | 3 | 8.84 | 0.88% | 2.08 | 0.82% | 66.67% |

## 3. BTC 过滤强度

全样本：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BTC B 允许非下跌 | 115 | 145.71 | 14.57% | 1.32 | 10.05% | 43.48% | 0.56% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| BTC A 当前 4H uptrend | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| BTC C 4H up + 1D>EMA50 | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |

近期：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BTC B 允许非下跌 | 36 | 174.31 | 17.43% | 2.76 | 3.94% | 58.33% | 1.87% | ZEC/USDT:USDT 5.01% | XRP/USDT:USDT -4.65% |
| BTC A 当前 4H uptrend | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| BTC C 4H up + 1D>EMA50 | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |

结论：全样本仍是当前 BTC 4H uptrend 更稳，利润和回撤比更好；近期样本中“允许 BTC 非下跌”明显放大收益，但全样本 2024 拖累加重，说明它更激进，暂不适合作为主线默认。BTC 4H + 1D>EMA50 在本轮样本里与当前过滤结果相同，说明这些 Long 信号出现时 BTC 日线基本已经站上 EMA50，新增条件没有带来额外过滤价值。

## 4. 止损距离

全样本：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stop 3% | 54 | 119.98 | 12.00% | 1.54 | 5.20% | 42.59% | 0.76% | ZEC/USDT:USDT 5.01% | BNB/USDT:USDT -2.98% |
| Stop 4% | 79 | 101.35 | 10.13% | 1.30 | 7.74% | 40.51% | 0.42% | ZEC/USDT:USDT 5.01% | XRP/USDT:USDT -4.02% |
| Stop 5% | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |

近期：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stop 3% | 22 | 70.25 | 7.02% | 1.92 | 4.46% | 45.45% | 0.98% | XRP/USDT:USDT 5.00% | BNB/USDT:USDT -2.98% |
| Stop 4% | 25 | 69.75 | 6.98% | 1.79 | 4.46% | 44.00% | 0.87% | XRP/USDT:USDT 5.00% | ZEC/USDT:USDT -3.30% |
| Stop 5% | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |

结论：3% 止损在全样本 PF 和 DD 更好，但近期利润低于 5%；5% 保留更多有效 pullback 交易，是当前收益主线。若目标优先控制回撤，可用 3%-4% 再做独立 dry-run 对照。

## 5. 退出方式

全样本：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ROI 5% | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| ROI 3% | 97 | 37.79 | 3.78% | 1.11 | 7.97% | 51.55% | 0.15% | ZEC/USDT:USDT 4.45% | ZEC/USDT:USDT -5.10% |
| ROI 4% | 97 | 63.31 | 6.33% | 1.17 | 8.55% | 46.39% | 0.28% | ZEC/USDT:USDT 4.45% | ZEC/USDT:USDT -5.10% |
| ROI 6% | 91 | 184.60 | 18.46% | 1.47 | 6.05% | 41.76% | 0.81% | XRP/USDT:USDT 6.38% | ZEC/USDT:USDT -5.10% |
| 1R平50%+结构止损 | 83 | 107.42 | 10.74% | 1.29 | 6.65% | 36.14% | 0.61% | BNB/USDT:USDT 14.08% | ZEC/USDT:USDT -5.10% |
| 1R平30%/2R平30%+结构止损 | 83 | 80.63 | 8.06% | 1.22 | 8.75% | 36.14% | 0.48% | BNB/USDT:USDT 15.10% | ZEC/USDT:USDT -5.10% |

近期：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ROI 5% | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| ROI 3% | 30 | 69.49 | 6.95% | 1.81 | 3.73% | 60.00% | 0.85% | ZEC/USDT:USDT 4.45% | XRP/USDT:USDT -4.65% |
| ROI 4% | 30 | 91.14 | 9.11% | 2.03 | 3.93% | 56.67% | 1.16% | ZEC/USDT:USDT 4.45% | XRP/USDT:USDT -4.65% |
| ROI 6% | 29 | 98.73 | 9.87% | 1.94 | 4.46% | 44.83% | 1.21% | XRP/USDT:USDT 6.38% | XRP/USDT:USDT -4.65% |
| 1R平50%+结构止损 | 25 | 104.68 | 10.47% | 2.00 | 4.46% | 36.00% | 1.54% | BNB/USDT:USDT 13.65% | XRP/USDT:USDT -4.65% |
| 1R平30%/2R平30%+结构止损 | 25 | 122.55 | 12.26% | 2.16 | 4.46% | 36.00% | 1.78% | BNB/USDT:USDT 14.76% | XRP/USDT:USDT -4.65% |

结论：全样本看固定 ROI 6% 的收益、PF、DD 都最好，但胜率更低、交易数更少；固定 ROI 5% 是更保守的基准版本。ROI 3% 胜率更高但全样本收益显著下降；分批止盈近期表现好，但全样本明显弱于 ROI 5%/6%，暂不建议并入主线。

## 6. Pair 拆解和剔除测试

Pullback Only pair 拆解，全样本 + 近期：

| 样本 | Pair | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 全样本 Pullback | BNB/USDT:USDT | 39 | 92.84 | 9.28% | 1.59 | 5.99% | 41.03% |
| 全样本 Pullback | DOGE/USDT:USDT | 11 | 58.25 | 5.82% | 3.39 | 1.58% | 72.73% |
| 全样本 Pullback | ZEC/USDT:USDT | 17 | 7.97 | 0.80% | 1.11 | 3.79% | 47.06% |
| 全样本 Pullback | XRP/USDT:USDT | 28 | -0.67 | -0.07% | 0.99 | 4.07% | 39.29% |
| 近期 Pullback | BNB/USDT:USDT | 15 | 48.22 | 4.82% | 1.91 | 3.71% | 40.00% |
| 近期 Pullback | XRP/USDT:USDT | 10 | 21.36 | 2.14% | 1.59 | 2.72% | 50.00% |
| 近期 Pullback | DOGE/USDT:USDT | 2 | 18.70 | 1.87% | 0.00 | 0.00% | 100.00% |
| 近期 Pullback | ZEC/USDT:USDT | 3 | 8.84 | 0.88% | 2.08 | 0.82% | 66.67% |

剔除/保留组合，全样本：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pullback Only | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| 去掉最差1个pair | 67 | 156.55 | 15.66% | 1.61 | 5.00% | 47.76% | 0.96% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| 去掉最差2个pair | 51 | 161.58 | 16.16% | 1.88 | 5.05% | 49.02% | 1.20% | DOGE/USDT:USDT 5.00% | BNB/USDT:USDT -4.38% |
| 只保留全样本为正 | 67 | 156.55 | 15.66% | 1.61 | 5.00% | 47.76% | 0.96% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| 只保留近期为正 | 95 | 158.38 | 15.84% | 1.41 | 6.98% | 45.26% | 0.67% | ZEC/USDT:USDT 5.01% | ZEC/USDT:USDT -5.10% |
| 只保留Top8主流 | 234 | 32.70 | 3.27% | 1.03 | 21.32% | 35.47% | 0.12% | ADA/USDT:USDT 5.01% | SOL/USDT:USDT -5.10% |

剔除/保留组合，近期：

| 策略/样本 | Trades | Profit USDT | Profit % | PF | MaxDD | Winrate | AvgProfit | Best trade | Worst trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pullback Only | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| 去掉最差1个pair | 20 | 71.46 | 7.15% | 2.19 | 3.71% | 50.00% | 1.52% | DOGE/USDT:USDT 5.00% | ZEC/USDT:USDT -3.30% |
| 去掉最差2个pair | 17 | 62.54 | 6.25% | 2.20 | 3.71% | 47.06% | 1.39% | DOGE/USDT:USDT 5.00% | BNB/USDT:USDT -2.98% |
| 只保留全样本为正 | 20 | 71.46 | 7.15% | 2.19 | 3.71% | 50.00% | 1.52% | DOGE/USDT:USDT 5.00% | ZEC/USDT:USDT -3.30% |
| 只保留近期为正 | 30 | 97.12 | 9.71% | 2.00 | 4.46% | 50.00% | 1.23% | DOGE/USDT:USDT 5.00% | XRP/USDT:USDT -4.65% |
| 只保留Top8主流 | 69 | -73.45 | -7.34% | 0.75 | 11.83% | 27.54% | -0.39% | ADA/USDT:USDT 5.00% | LINK/USDT:USDT -4.95% |

结论：全样本拖累最明显的是 XRP，其次 ZEC 贡献较弱但仍为正；BNB 是最大贡献，DOGE 的交易数少但质量高。近期四个 pair 全为正，所以“只保留近期为正”与原始 Pullback 一致。Top8 扩展后收益低于原始四币集合，说明当前 Long 形态不是主流大币普适信号。

## 7. 总结判断

- Long 值得继续，但不建议直接大规模并入主策略；更适合作为 Pullback-only 小仓位模块观察。
- 主线 entry_tag 是 `long_pullback_restart`。Compression-only 全样本和近期都为负，不建议作为独立做多主线；Combined 全样本略优于 Pullback，但增量交易很少，不能证明 compression 分支已经稳健。
- 最好退出方式：全样本优先固定 ROI 6%；更保守基准用固定 ROI 5%。分批止盈逻辑可以保留为研究分支，但本轮不建议进主策略。
- 有效过滤：`close_position >= 0.72`、`max_stop_distance <= 5%`、当前 BTC 4H uptrend。BTC 非下跌过滤近期更强但全样本不稳；BTC 4H + 1D>EMA50 在本轮没有新增过滤效果。
- Pair 建议：主线保留 BNB/DOGE/ZEC/XRP 做观察；如果追求更稳，可先剔除 XRP，只跑 BNB/DOGE/ZEC 对照。
- Dry-run 建议：可以进入小仓位 dry-run，但只建议 Pullback Only、ROI 5%、当前 BTC 过滤、max_stop_distance 5%，并单独记录是否剔除 XRP 的 A/B。

## 8. 本轮文件记录

- 修正策略：`D:\test\ft_userdata\user_data\strategies\DualTrendCompressionRestartLongV1Strategy.py`
- 验证变体：`D:\test\ft_userdata\user_data\strategies\DualTrendCompressionRestartLongV1ValidationStrategies.py`
- 入场一致性验证 CSV：`D:\test\ft_userdata\user_data\strategies\research\long_v1_validation\long_v1_entry_filter_validation.csv`
- 本报告：`D:\test\ft_userdata\我的策略\DualTrend_LongV1_稳健性验证报告.md`

主要回测 zip：
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_full-2026-06-15_07-50-50.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_recent-2026-06-15_07-50-45.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_fixed_full-2026-06-15_09-29-41.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_fixed_recent-2026-06-15_09-29-35.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task2_tags_full-2026-06-15_09-31-39.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task2_tags_recent-2026-06-15_09-31-26.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task3_btc_full_v2-2026-06-15_09-34-48.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task3_btc_recent_v2-2026-06-15_09-34-27.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task4_stop_full-2026-06-15_09-33-01.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task4_stop_recent-2026-06-15_09-32-48.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task5_exit_full-2026-06-15_09-35-31.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task5_exit_recent-2026-06-15_09-34-53.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task6_pairs_full-2026-06-15_09-39-21.zip`
- `D:\test\ft_userdata\user_data\backtest_results\long_v1_task6_pairs_recent-2026-06-15_09-40-18.zip`
