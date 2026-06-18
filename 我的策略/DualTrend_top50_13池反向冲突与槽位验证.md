# DualTrend Top50 正贡献13池 反向冲突与槽位验证

日期: 2026-06-18

## 1. 目标

在 `Positive13 + max_open_trades=3` 已经确认是当前主候选后，这一轮继续回答两个实盘前问题：

1. long / short 会不会在同一币上近距离反手互打
2. long 是否只是占用 short 主引擎槽位，还是确实带来增益

本轮主对象：

- `DualTrendCombinedShortPullbackShapeV1Strategy`

对照对象：

- `DualTrendCompressionRestartShortV1Strategy`（short-only）

## 2. 主候选基线

配置：

- [config.backtest.dualtrend.combined.top50.positive13.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json)

combined 基线结果：

### 2.1 三年

- 结果: [backtest-result-2026-06-18_06-49-31.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-31.zip)

| 指标 | Combined |
|---|---:|
| Trades | 294 |
| Profit | +1907.86U / +190.79% |
| PF | 1.97 |
| MaxDD | 7.68% |
| Winrate | 34.69% |
| Long / Short | 46 / 248 |

### 2.2 近一年

- 结果: [backtest-result-2026-06-18_06-51-00.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-51-00.zip)

| 指标 | Combined |
|---|---:|
| Trades | 111 |
| Profit | +512.35U / +51.23% |
| PF | 2.00 |
| MaxDD | 7.65% |
| Winrate | 39.64% |
| Long / Short | 14 / 97 |

### 2.3 最长可得样本

你这轮要求补一遍“5年回测”，但需要明确一点：

- 当前这组 Binance futures 历史里，老币大多从 `2022-10-01` 左右才有
- 再扣掉 `startup_candle_count = 1000`
- 所以这次实际有效回测区间为：
  - `2022-11-11 16:00:00 -> 2026-06-18 00:00:00`

结果文件：

- [backtest-result-2026-06-18_07-44-29.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-44-29.zip)

| 指标 | Combined |
|---|---:|
| Trades | 345 |
| Profit | +2411.57U / +241.16% |
| PF | 1.96 |
| MaxDD | 7.67% |
| Winrate | 33.9% |
| Long / Short | 48 / 297 |
| CAGR | 40.62% |

entry_tag 拆解：

| entry_tag | Trades | Profit Abs | Profit % |
|---|---:|---:|---:|
| `short_pullback_restart` | 205 | +1393.66U | +139.37% |
| `short_compression_breakdown` | 92 | +476.18U | +47.62% |
| `long_1d_center_compression` | 48 | +541.73U | +54.17% |

主要贡献 pair：

- `ETH` +383.93U
- `ADA` +356.03U
- `ZEC` +286.19U
- `DOGE` +278.45U
- `BNB` +259.02U
- `BTC` +203.84U

这组最长样本的意义很直接：

1. 这版策略在可获得的最长正式样本里依然稳定
2. `PF` 仍接近 `2.0`
3. `MaxDD` 仍控制在 `8%` 附近
4. short 仍是主引擎，但 long 继续是正增益

## 3. same-pair 近距离反向冲突

检查方式：

按 pair 拆开逐笔排序，统计：

1. 前一笔与后一笔是否方向相反
2. 前一笔平仓到后一笔开仓间隔是否 `<= 24h`
3. 是否 `<= 72h`

### 3.1 三年样本

结果：

- 同 pair 方向切换总次数：`49`
- `24h` 内反向冲突：`0`
- `72h` 内反向冲突：`0`
- 最短反向切换间隔：`147h`

结论：

- 虽然同一币在更长周期内会出现 long / short 切换，但没有出现近距离互打。
- 这说明当前 combined 版本不是靠“刚做多就反手做空”这类高摩擦行为堆收益。

### 3.2 近一年样本

结果：

- 同 pair 方向切换总次数：`9`
- `24h` 内反向冲突：`0`
- `72h` 内反向冲突：`0`
- 最短反向切换间隔：`147h`

结论：

- 近一年口径下同样没有 same-pair 快速反手问题。

## 4. 槽位占用观察

这里不直接推断“漏掉了多少信号”，而是先看事实层面的持仓并发结构：

1. long-only 持仓时间占比
2. short-only 持仓时间占比
3. long/short 混合持仓时间占比
4. 总持仓数 `>= 3` 时，long 出现在其中的时间占比

### 4.1 三年样本

| 观察项 | 占比 |
|---|---:|
| long-only 持仓时间 | 8.60% |
| short-only 持仓时间 | 22.56% |
| long/short 混合持仓时间 | 2.70% |
| 空仓时间 | 66.15% |
| 总持仓数 >= 3 的时间 | 6.90% |
| 总持仓数 >= 3 且其中有 long 的时间 | 1.92% |

解释：

- 三年样本里，大部分时间根本没有到满槽。
- 即使到了 `>= 3` 槽位的时段，其中 long 参与的时间也很小。

### 4.2 近一年样本

| 观察项 | 占比 |
|---|---:|
| long-only 持仓时间 | 12.64% |
| short-only 持仓时间 | 23.51% |
| long/short 混合持仓时间 | 6.74% |
| 空仓时间 | 57.12% |
| 总持仓数 >= 3 的时间 | 11.37% |
| 总持仓数 >= 3 且其中有 long 的时间 | 3.77% |

解释：

- 近一年里 long 活跃度更高一些，但它在满槽场景中的占比仍不算大。
- 从占用事实看，long 并没有大规模挤占 short 的主战场。

## 5. short-only 对照回测

为了回答“long 值不值得保留”，用同一个 13 币池、同样 `max_open_trades=3`，跑 short-only 对照。

### 5.1 short-only 三年结果

- 结果: [backtest-result-2026-06-18_07-36-57.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-36-57.zip)

| 指标 | Short-only |
|---|---:|
| Trades | 296 |
| Profit | +1022.64U / +102.26% |
| PF | 1.60 |
| MaxDD | 9.32% |
| Winrate | 33.4% |
| Long / Short | 0 / 296 |

### 5.2 short-only 近一年结果

- 结果: [backtest-result-2026-06-18_07-36-39.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-36-39.zip)

| 指标 | Short-only |
|---|---:|
| Trades | 126 |
| Profit | +148.74U / +14.87% |
| PF | 1.29 |
| MaxDD | 9.24% |
| Winrate | 33.3% |
| Long / Short | 0 / 126 |

## 6. Combined vs Short-only

### 6.1 三年样本对照

| 指标 | Combined | Short-only |
|---|---:|---:|
| Trades | 294 | 296 |
| Profit | +1907.86U / +190.79% | +1022.64U / +102.26% |
| PF | 1.97 | 1.60 |
| MaxDD | 7.68% | 9.32% |
| Winrate | 34.69% | 33.4% |

观察：

1. combined 的总收益远高于 short-only。
2. 更关键的是，combined 不是“收益更高但回撤更烂”，而是 **收益更高、PF 更高、MaxDD 反而更低**。
3. 这说明 long 部分不是无效占位，而是对组合有真实改善。

### 6.2 近一年样本对照

| 指标 | Combined | Short-only |
|---|---:|---:|
| Trades | 111 | 126 |
| Profit | +512.35U / +51.23% | +148.74U / +14.87% |
| PF | 2.00 | 1.29 |
| MaxDD | 7.65% | 9.24% |
| Winrate | 39.64% | 33.3% |

观察：

1. 近一年差距更明显。
2. combined 不仅收益大幅领先，收益质量也明显更强。
3. 如果把 long 完全去掉，当前这版主策略的组合表现会明显退化。

## 7. 当前判断

### 7.1 是否存在 same-pair 近距离反向冲突

结论：

- 没有。
- 三年和近一年样本里，`24h / 72h` 口径下都是 `0`。

### 7.2 long 是否只是占槽

结论：

- 不是。
- 如果只看槽位占用，long 在满槽时段里的参与度本来就不高。
- 如果看组合贡献，long 明显是增益项，而不是噪音项。

### 7.3 是否必须立刻做 side-specific slots

当前判断：

- **不是必须项。**

理由：

1. 没有 same-pair 快速反手冲突
2. long 在满槽时段的占比不高
3. combined 明显优于 short-only

也就是说，当前主候选并没有表现出“long 把 short 拖坏了”的证据。

### 7.4 最长样本下主候选是否仍成立

结论：

- 仍成立。

因为在 `2022-11-11 -> 2026-06-18` 的最长可得样本里，这版主候选依然表现出：

1. 明显正收益
2. 接近 `2.0` 的 PF
3. 没有明显恶化的回撤
4. short / long 分工清晰

## 8. 更实用的结论

如果下一步要进 dry-run，当前更合理的推进方式是：

1. 先保留 combined 版本
2. 维持 `Positive13 + max_open_trades=3`
3. 不急着拆成双 bot
4. 先在 dry-run 里继续观察：
   - 满槽时长
   - missed signal 体感
   - long / short 资金分配是否有现实摩擦

如果 dry-run 里真的出现“short 信号很多但总被 long 占位”的现象，再升级到 side-specific slots 或双 bot，更顺手也更有根据。

## 9. 本轮已完成事项

本轮已完成：

1. `Positive13` 主候选 same-pair `24h / 72h` 反向冲突检查
2. 持仓并发与满槽时段占比统计
3. short-only 三年 / 近一年 Docker 正式回测
4. combined vs short-only 对照结论输出
5. `Positive13` 最长可得样本正式回测补充
