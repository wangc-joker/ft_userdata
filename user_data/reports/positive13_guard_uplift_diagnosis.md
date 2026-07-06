# Positive13 Guard Uplift Diagnosis

对比：

- Baseline: `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`
- New candidate: `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy`

目标：回答这次 `CompressionFlushGuard` 的提升，主要来自哪些 pair / 哪些 tag。

## 总览

| period | baseline trades | guard trades | baseline profit | guard profit | profit diff | baseline winrate | guard winrate |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3y | 313 | 309 | 328.99% | 341.98% | 12.99% | 49.5% | 50.2% |
| 1y | 114 | 113 | 123.62% | 127.88% | 4.26% | 54.4% | 54.9% |
| pressure | 15 | 15 | 5.73% | 5.73% | 0.00% | 40.0% | 40.0% |

## 3y

### Pair uplift

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| ETH/USDT:USDT | 52.03% | 58.77% | 6.74% | 30 | 28 | -2 |
| BTC/USDT:USDT | 41.88% | 47.86% | 5.97% | 36 | 34 | -2 |
| SOL/USDT:USDT | 8.84% | 12.81% | 3.97% | 27 | 26 | -1 |
| XRP/USDT:USDT | 40.43% | 40.43% | 0.00% | 35 | 35 | 0 |
| LINK/USDT:USDT | -19.07% | -19.07% | 0.00% | 22 | 22 | 0 |
| BNB/USDT:USDT | 50.79% | 50.79% | 0.00% | 22 | 22 | 0 |
| PAXG/USDT:USDT | 7.13% | 7.13% | 0.00% | 6 | 6 | 0 |
| ZEC/USDT:USDT | 41.90% | 41.90% | -0.00% | 13 | 13 | 0 |

### Pair drag

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| ADA/USDT:USDT | 46.70% | 43.01% | -3.69% | 33 | 34 | 1 |
| SUI/USDT:USDT | -2.48% | -2.48% | -0.00% | 19 | 19 | 0 |
| TAO/USDT:USDT | 17.69% | 17.69% | -0.00% | 15 | 15 | 0 |
| NEAR/USDT:USDT | 0.59% | 0.59% | -0.00% | 33 | 33 | 0 |
| DOGE/USDT:USDT | 42.55% | 42.55% | -0.00% | 22 | 22 | 0 |
| ZEC/USDT:USDT | 41.90% | 41.90% | -0.00% | 13 | 13 | 0 |

### Tag uplift

| tag | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | 61.22% | 77.90% | 16.68% | 86 | 81 | -5 |
| long_1d_center_compression | 95.96% | 95.96% | 0.00% | 48 | 48 | 0 |
| short_pullback_restart | 171.81% | 168.12% | -3.69% | 179 | 180 | 1 |

结论：

- 3y 的主要提升来源集中在 `ETH/USDT:USDT, BTC/USDT:USDT, SOL/USDT:USDT`。
- 主要拖累来自 `ADA/USDT:USDT, SUI/USDT:USDT, TAO/USDT:USDT`，说明 guard 不是全域增益，而是集中改善了部分币种。

## 1y

### Pair uplift

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| ETH/USDT:USDT | 20.41% | 24.67% | 4.26% | 11 | 10 | -1 |
| DOGE/USDT:USDT | 2.18% | 2.18% | 0.00% | 6 | 6 | 0 |
| ADA/USDT:USDT | 10.01% | 10.01% | 0.00% | 11 | 11 | 0 |
| PAXG/USDT:USDT | 9.20% | 9.20% | 0.00% | 5 | 5 | 0 |
| TAO/USDT:USDT | 20.49% | 20.49% | 0.00% | 10 | 10 | 0 |
| SUI/USDT:USDT | -1.52% | -1.52% | 0.00% | 6 | 6 | 0 |
| ZEC/USDT:USDT | 10.00% | 10.00% | 0.00% | 1 | 1 | 0 |
| BNB/USDT:USDT | 29.48% | 29.48% | 0.00% | 11 | 11 | 0 |

### Pair drag

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| NEAR/USDT:USDT | 8.16% | 8.16% | -0.00% | 15 | 15 | 0 |
| XRP/USDT:USDT | 19.82% | 19.82% | -0.00% | 14 | 14 | 0 |
| LINK/USDT:USDT | -0.91% | -0.91% | -0.00% | 4 | 4 | 0 |
| SOL/USDT:USDT | -8.75% | -8.75% | -0.00% | 10 | 10 | 0 |
| BTC/USDT:USDT | 5.05% | 5.05% | 0.00% | 10 | 10 | 0 |
| BNB/USDT:USDT | 29.48% | 29.48% | 0.00% | 11 | 11 | 0 |

### Tag uplift

| tag | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| short_compression_breakdown | -2.45% | 1.82% | 4.26% | 31 | 30 | -1 |
| short_pullback_restart | 81.13% | 81.13% | 0.00% | 68 | 68 | 0 |
| long_1d_center_compression | 44.94% | 44.94% | 0.00% | 15 | 15 | 0 |

结论：

- 1y 里，short_pullback_restart 仍然是主收益来源；compression guard 没有改变这条主线，但削弱了部分 flush 型坏单。

## pressure

### Pair uplift

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| ADA/USDT:USDT | -2.43% | -2.43% | 0.00% | 2 | 2 | 0 |
| BNB/USDT:USDT | 2.53% | 2.53% | 0.00% | 2 | 2 | 0 |
| BTC/USDT:USDT | -2.10% | -2.10% | 0.00% | 2 | 2 | 0 |
| NEAR/USDT:USDT | 0.16% | 0.16% | 0.00% | 2 | 2 | 0 |
| SOL/USDT:USDT | -0.04% | -0.04% | 0.00% | 1 | 1 | 0 |
| SUI/USDT:USDT | 0.00% | 0.00% | 0.00% | 1 | 1 | 0 |
| TAO/USDT:USDT | -1.97% | -1.97% | 0.00% | 1 | 1 | 0 |
| XRP/USDT:USDT | -0.43% | -0.43% | 0.00% | 3 | 3 | 0 |

### Pair drag

| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| ADA/USDT:USDT | -2.43% | -2.43% | 0.00% | 2 | 2 | 0 |
| BNB/USDT:USDT | 2.53% | 2.53% | 0.00% | 2 | 2 | 0 |
| BTC/USDT:USDT | -2.10% | -2.10% | 0.00% | 2 | 2 | 0 |
| NEAR/USDT:USDT | 0.16% | 0.16% | 0.00% | 2 | 2 | 0 |
| SOL/USDT:USDT | -0.04% | -0.04% | 0.00% | 1 | 1 | 0 |
| SUI/USDT:USDT | 0.00% | 0.00% | 0.00% | 1 | 1 | 0 |

### Tag uplift

| tag | base profit | guard profit | diff | base trades | guard trades | trade diff |
|---|---:|---:|---:|---:|---:|---:|
| long_1d_center_compression | -2.08% | -2.08% | 0.00% | 1 | 1 | 0 |
| short_compression_breakdown | 2.17% | 2.17% | 0.00% | 7 | 7 | 0 |
| short_pullback_restart | 5.63% | 5.63% | 0.00% | 7 | 7 | 0 |

结论：

- 压力期里，guard 没有把策略推成更激进版本，而是基本维持了原主候选的防守能力。
