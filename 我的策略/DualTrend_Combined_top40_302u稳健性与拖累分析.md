# DualTrend Combined top40_302u 稳健性与拖累分析

## 1. 范围

使用策略：

```text
DualTrendCombinedLongDailyCenterShortV1Strategy
```

币池文件：

```text
D:/test/real_trade/user_data/generated/pairs.dynamic.top40.302u.balanced.json
```

注意：

这个文件名叫 top40，但实际内容为 30 个 pair。

本轮验证目标：

1. `max_open_trades = 3 / 4 / 5`
2. 成本压力测试
3. 检查 long / short 是否存在同 pair 近距离反向冲突
4. 分析 `LTC/BCH/LINK/DOT/NEAR` 拖累原因

## 2. max_open_trades 验证

### 1 年样本：2025-05-07 至 2026-05-07

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 3 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% |
| 4 | 161 | +276.27U / +27.63% | 1.40 | 10.00% | 31.1% |
| 5 | 169 | +301.39U / +30.14% | 1.42 | 10.00% | 31.4% |

### 3 年样本：2023-05-14 至 2026-05-07

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 3 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% |
| 4 | 400 | +1520.75U / +152.08% | 1.58 | 10.01% | 30.8% |
| 5 | 417 | +1556.13U / +155.61% | 1.58 | 10.01% | 30.7% |

结论：

1. `max_open_trades` 从 3 提到 4/5，收益会增加，但 PF 会下降，回撤显著升到约 10%。
2. 对这个 top40_302u 币池，`3` 是更平衡的稳健值。
3. `5` 虽然收益最高，但并没有比 `4` 好多少，更多像是用更高资金同时暴露换来的。

## 3. 成本压力测试

基准费率：

```text
fee = 0.0005
```

测试口径：

1. `1.5x fee` => `0.00075`
2. `2x fee` => `0.0010`
3. `slippage 0.10%` => 用每侧额外成本折算为 `fee = 0.0015`
4. `slippage 0.20%` => 用每侧额外成本折算为 `fee = 0.0025`

说明：

若按“每侧 0.05% 滑点”口径折算，则等价于 `2x fee`，所以不单独重复跑一遍。

### 1 年样本

| 场景 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% |
| 手续费 1.5x | 140 | +279.06U / +27.91% | 1.44 | 8.79% | 32.1% |
| 手续费 2x | 140 | +260.75U / +26.07% | 1.41 | 9.11% | 32.1% |
| 滑点 0.10% | 143 | +203.51U / +20.35% | 1.30 | 9.75% | 30.1% |
| 滑点 0.20% | 142 | +111.04U / +11.10% | 1.16 | 10.60% | 29.6% |

### 3 年样本

| 场景 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% |
| 手续费 1.5x | 360 | +1293.39U / +129.34% | 1.56 | 8.93% | 31.1% |
| 手续费 2x | 360 | +1233.44U / +123.34% | 1.54 | 9.28% | 31.1% |
| 滑点 0.10% | 363 | +1038.89U / +103.89% | 1.45 | 9.81% | 29.8% |
| 滑点 0.20% | 361 | +586.71U / +58.67% | 1.27 | 10.56% | 29.1% |

结论：

1. 手续费放大到 1.5x / 2x 后，策略仍然稳定为正。
2. 0.10% 滑点压力下，策略仍然有效，但 PF 明显下降。
3. 0.20% 滑点压力下，3 年仍为正，但优势已经被明显侵蚀，1 年样本只剩 +11.10%。
4. 所以这个组合对成本并不脆弱，但也不是“完全不怕滑点”。

## 4. 同 pair 近距离反向冲突

检查方式：

按 pair 排序逐笔交易，统计：

1. 前一笔和平后一笔是否方向相反；
2. 前一笔平仓到后一笔开仓间隔是否 <= 24h；
3. 是否 <= 72h。

结果：

```text
24h 内反向冲突：0
72h 内反向冲突：0
```

结论：

当前 combined 版本没有出现“同一币种刚做完 long 很快反手 short”或“刚做完 short 很快反手 long”的近距离冲突。也就是说，这个合并版不是靠高频反手堆出来的，long / short 逻辑彼此基本分时段工作。

## 5. 拖累币种分析

## 5.1 LTC

| 指标 | 数值 |
|---|---:|
| Trades | 3 |
| Profit | -30.48U |
| Short / Long | 0 / 3 |
| Win / Loss | 0 / 3 |

结论：

1. `LTC` 的拖累完全来自 `long_1d_center_compression`。
2. 3 笔全是 `stop_loss`，没有一笔盈利。
3. 这不是 short 出错，而是旧 long daily center 在 LTC 上完全不适配。

## 5.2 BCH

| 指标 | 数值 |
|---|---:|
| Trades | 2 |
| Profit | -28.38U |
| Short / Long | 0 / 2 |
| Win / Loss | 0 / 2 |

结论：

1. `BCH` 也是纯 `long_1d_center_compression` 拖累。
2. 2 笔全是 `stop_loss`，没有任何正反馈。
3. 与 LTC 一样，是 long daily center 的不适配，不是 short 主线的问题。

## 5.3 DOT

| 指标 | 数值 |
|---|---:|
| Trades | 2 |
| Profit | -20.10U |
| Short / Long | 0 / 2 |
| Win / Loss | 0 / 2 |

结论：

1. `DOT` 也是纯 long daily center 亏损。
2. 2 笔全部 `stop_loss`。
3. 说明这类 1D center breakout 在 DOT 上样本太少，而且触发质量差。

## 5.4 LINK

| 指标 | 数值 |
|---|---:|
| Trades | 24 |
| Profit | -28.08U |
| Short / Long | 24 / 0 |
| Win / Loss | 5 / 19 |

按 tag：

| Tag | Trades | Profit | Winrate |
|---|---:|---:|---:|
| `short_compression_breakdown` | 6 | -24.04U | 16.7% |
| `short_pullback_restart` | 18 | -4.04U | 22.2% |

按 exit：

| Exit | Trades | Profit |
|---|---:|---:|
| `stop_loss` | 9 | -121.37U |
| `trailing_stop_loss` | 7 | -61.91U |
| `stale_loss_72h` | 3 | -1.54U |
| `roi` | 5 | +156.75U |

结论：

1. `LINK` 的问题不是“没有赢家”，而是亏损笔数太多。
2. `short_compression_breakdown` 在 LINK 上尤其差，亏损集中。
3. 这更像是 LINK 的短空经常出现假跌破或跌不动后反抽，把止损和 trailing 都吃掉。

## 5.5 NEAR

| 指标 | 数值 |
|---|---:|
| Trades | 32 |
| Profit | -16.76U |
| Short / Long | 30 / 2 |
| Win / Loss | 6 / 26 |

按 tag：

| Tag | Trades | Profit | Winrate |
|---|---:|---:|---:|
| `long_1d_center_compression` | 2 | -17.54U | 0.0% |
| `short_pullback_restart` | 22 | -3.00U | 22.7% |
| `short_compression_breakdown` | 8 | +3.78U | 12.5% |

按 exit：

| Exit | Trades | Profit |
|---|---:|---:|
| `stop_loss` | 19 | -203.08U |
| `trailing_stop_loss` | 3 | -39.74U |
| `stale_loss_72h` | 4 | -9.23U |
| `roi` | 6 | +235.28U |

结论：

1. `NEAR` 的 long 侧 2 笔全亏，说明 long daily center 同样不适合。
2. `short_compression_breakdown` 在 NEAR 上反而是正的。
3. 真正拖累 NEAR 的是 `short_pullback_restart`，它总体接近打平但略亏，而且会频繁吃止损。
4. 这说明 NEAR 更适合“加速下破型”的 short，而不适合“回抽失败再下”这一类 short。

## 6. 最终结论

1. `max_open_trades=3` 仍然是这个币池下最稳妥的值。
2. 提高到 `4/5` 可以增收，但会明显抬高回撤，不像是优先选择。
3. 成本压力下策略仍有效，但对 0.10% 以上滑点开始明显敏感。
4. 当前 combined 版本没有发现同 pair 近距离 long/short 反向冲突。
5. `LTC/BCH/DOT` 的拖累本质上都是 long daily center 完全失效。
6. `LINK` 的拖累主要来自 short 假跌破，特别是 `short_compression_breakdown`。
7. `NEAR` 的拖累主要来自：
   - long daily center 失效
   - `short_pullback_restart` 质量偏差

## 7. 下一步建议

最值得先测的不是继续调参数，而是做币种过滤：

1. 去掉 `LTC/BCH/DOT`；
2. 去掉 `LINK`；
3. 对 `NEAR`：
   - 先整体去掉测试；
   - 或只禁用 `short_pullback_restart` 与 long；
4. 再回测 1 年、3 年和成本压力。
