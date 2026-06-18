# DualTrend Combined 使用 top40_302u 币池回测记录

## 1. 输入

用户指定币池文件：

```text
D:/test/real_trade/user_data/generated/pairs.dynamic.top40.302u.balanced.json
```

文件名为 top40，但实际内容为 30 个 pair。

已生成本地回测配置：

```text
user_data/config.backtest.dualtrend.combined.top40_302u.max3.json
```

策略：

```text
DualTrendCombinedLongDailyCenterShortV1Strategy
```

参数：

```text
dry_run_wallet = 1000 USDT
max_open_trades = 3
timeframe = 1h
trading_mode = futures
margin_mode = isolated
```

## 2. 总结果

| 样本 | 时间 | Trades | Profit | PF | MaxDD | Winrate | Best pair | Worst pair |
|---|---|---:|---:|---:|---:|---:|---|---|
| 1 年 | 2025-05-07 至 2026-05-07 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% | ETH | LINK |
| 3 年 | 2023-05-14 至 2026-05-07 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% | ETH | LTC |

## 3. Entry Tag 拆解

### 1 年

| entry_tag | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| `long_1d_center_compression` | 23 | +129.69U / +12.97% | 2.29 | 34.8% |
| `short_compression_breakdown` | 24 | +111.90U / +11.19% | 2.03 | 37.5% |
| `short_pullback_restart` | 93 | +54.30U / +5.43% | 1.13 | 31.2% |
| TOTAL | 140 | +295.88U / +29.59% | 1.48 | 32.9% |

### 3 年

| entry_tag | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| `long_1d_center_compression` | 68 | +468.70U / +46.87% | 2.04 | 32.4% |
| `short_pullback_restart` | 224 | +458.56U / +45.86% | 1.31 | 29.5% |
| `short_compression_breakdown` | 67 | +450.71U / +45.07% | 2.21 | 37.3% |
| TOTAL | 359 | +1377.96U / +137.80% | 1.60 | 31.5% |

## 4. 年度拆解

### 1 年样本

| 年份 | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| 2025 部分 | 95 | +229.12U | 1.56 | 33.7% |
| 2026 部分 | 45 | +66.76U | 1.32 | 31.1% |

### 3 年样本

| 年份 | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| 2023 部分 | 66 | +10.43U | 1.03 | 19.7% |
| 2024 | 100 | +470.82U | 1.93 | 35.0% |
| 2025 | 148 | +773.08U | 1.72 | 34.5% |
| 2026 部分 | 45 | +123.64U | 1.32 | 31.1% |

说明：

2023 从 2023-05-14 开始，不是完整自然年；2026 截止 2026-05-07，也不是完整自然年。

## 5. Pair 拆解

### 1 年主要贡献

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| ETH | 11 | +77.21U | 2.61 | 36.4% |
| ADA | 17 | +72.36U | 2.24 | 35.3% |
| XRP | 16 | +55.50U | 1.94 | 37.5% |
| SOL | 11 | +45.28U | 1.81 | 36.4% |
| BNB | 10 | +25.20U | 1.55 | 40.0% |
| BTC | 14 | +24.35U | 1.51 | 35.7% |
| TRX | 14 | +20.35U | 1.48 | 28.6% |
| NEAR | 10 | +18.58U | 1.31 | 30.0% |

### 1 年拖累

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| LINK | 8 | -29.35U | 0.42 | 12.5% |
| BCH | 2 | -14.82U | 0.00 | 0.0% |
| SUI | 12 | -12.95U | 0.79 | 33.3% |
| LTC | 1 | -8.13U | 0.00 | 0.0% |

### 3 年主要贡献

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| ETH | 30 | +272.14U | 2.70 | 36.7% |
| ZEC | 19 | +247.47U | 5.21 | 57.9% |
| ADA | 34 | +206.81U | 2.04 | 35.3% |
| BNB | 23 | +189.57U | 2.38 | 47.8% |
| SOL | 30 | +173.06U | 1.88 | 36.7% |
| BTC | 41 | +142.56U | 1.61 | 29.3% |
| XRP | 37 | +81.69U | 1.33 | 27.0% |
| DOGE | 23 | +81.21U | 1.51 | 30.4% |

### 3 年拖累

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| LTC | 3 | -30.48U | 0.00 | 0.0% |
| BCH | 2 | -28.38U | 0.00 | 0.0% |
| LINK | 24 | -28.08U | 0.85 | 20.8% |
| DOT | 2 | -20.10U | 0.00 | 0.0% |
| NEAR | 32 | -16.76U | 0.93 | 18.8% |
| FIL | 1 | -9.75U | 0.00 | 0.0% |
| APE | 1 | -9.18U | 0.00 | 0.0% |
| AVAX | 1 | -7.75U | 0.00 | 0.0% |

## 6. 观察

1. 这个 30 币池下，Combined 仍然是正收益，3 年 PF 1.60，MaxDD 8.62%。
2. 1 年样本明显弱于原 13 币池 combined：+29.59%，PF 1.48。
3. 多出来的小币大多没有贡献，很多 pair 交易数为 0 或很少。
4. 主要收益仍集中在 ETH、ZEC、ADA、BNB、SOL、BTC、XRP、DOGE。
5. LINK 仍然是稳定拖累；LTC/BCH/DOT 交易少但负贡献明显。

## 7. 下一步建议

不建议直接把这个 30 币池全量用于 dry-run。

建议先做两个过滤版：

1. 去掉 LINK/LTC/BCH/DOT/NEAR；
2. 只保留 3 年正贡献 pair；
3. 再跑 1 年、3 年、成本压力和 max_open_trades 3/4/5。
