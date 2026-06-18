# DualTrend Top50 正贡献13池 成本压力与槽位验证

日期: 2026-06-18

## 1. 目标

基于前一轮 top50 子池收敛验证，当前最值得继续推进的是：

- `Positive13` 正贡献 13 币池

这轮继续验证两件事：

1. 成本上升后，这版策略是否还稳
2. `max_open_trades` 从 `3` 放宽到 `4/5` 是否值得

本轮策略保持不变：

- `DualTrendCombinedShortPullbackShapeV1Strategy`

## 2. 基线配置

使用配置：

- [config.backtest.dualtrend.combined.top50.positive13.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json)

对照基线结果来自上一轮：

### 2.1 三年基线

- 区间: `2023-06-18 -> 2026-06-18`
- 结果: [backtest-result-2026-06-18_06-49-31.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-31.zip)

| 指标 | 基线结果 |
|---|---:|
| Pairs | 13 |
| Trades | 294 |
| Profit | +1907.86U / +190.79% |
| Profit Factor | 1.97 |
| Max Drawdown | 7.68% |
| Winrate | 34.69% |
| Long / Short | 46 / 248 |

### 2.2 近一年基线

- 区间: `2025-06-18 -> 2026-06-18`
- 结果: [backtest-result-2026-06-18_06-51-00.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-51-00.zip)

| 指标 | 基线结果 |
|---|---:|
| Pairs | 13 |
| Trades | 111 |
| Profit | +512.35U / +51.23% |
| Profit Factor | 2.00 |
| Max Drawdown | 7.65% |
| Winrate | 39.64% |
| Long / Short | 14 / 97 |

## 3. 成本压力测试

本轮先测试最常见的两档手续费压力：

1. 手续费 `1.5x`
2. 手续费 `2.0x`

说明：

- 这里用提高 `fee` 的方式做压力验证
- 还没有额外叠加滑点

### 3.1 三年样本

区间：

- `2023-06-18 -> 2026-06-18`

结果文件：

- 手续费 1.5x: [backtest-result-2026-06-18_07-08-59.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-08-59.zip)
- 手续费 2.0x: [backtest-result-2026-06-18_06-59-24.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-59-24.zip)

| 方案 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 294 | +1907.86U / +190.79% | 1.97 | 7.68% | 34.69% |
| fee 1.5x | 294 | +1840.85U / +184.08% | 1.93 | 7.93% | 34.4% |
| fee 2.0x | 294 | +1769.11U / +176.91% | 1.89 | 8.24% | 34.4% |

观察：

1. 成本抬升后，收益和 PF 有正常回落，但没有结构性崩塌。
2. 即使手续费到 `2x`，三年 PF 仍有 `1.89`。
3. MaxDD 从 `7.68%` 增到 `8.24%`，放大可接受。

### 3.2 近一年样本

区间：

- `2025-06-18 -> 2026-06-18`

结果文件：

- 手续费 1.5x: [backtest-result-2026-06-18_06-58-57.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-58-57.zip)
- 手续费 2.0x: [backtest-result-2026-06-18_06-58-58.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-58-58.zip)

| 方案 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 111 | +512.35U / +51.23% | 2.00 | 7.65% | 39.64% |
| fee 1.5x | 111 | +496.74U / +49.67% | 1.95 | 7.94% | 38.7% |
| fee 2.0x | 111 | +482.28U / +48.23% | 1.91 | 8.25% | 38.7% |

观察：

1. 近一年样本在成本压力下也没有塌。
2. PF 仍明显高于 `1.9`，说明主逻辑的边际优势足以覆盖更高费用。
3. 这对后续 dry-run 很重要，因为实盘一定比理想回测更贵。

## 4. 槽位测试

新增配置：

- [config.backtest.dualtrend.combined.top50.positive13.max4.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max4.json)
- [config.backtest.dualtrend.combined.top50.positive13.max5.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max5.json)

测试目标：

- `max_open_trades = 3 / 4 / 5`

## 5. 三年样本槽位对照

区间：

- `2023-06-18 -> 2026-06-18`

结果文件：

- max4: [backtest-result-2026-06-18_07-01-58.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-01-58.zip)
- max5: [backtest-result-2026-06-18_07-02-00.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-02-00.zip)

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 294 | +1907.86U / +190.79% | 1.97 | 7.68% | 34.69% | 46 / 248 |
| 4 | 325 | +1893.36U / +189.34% | 1.89 | 9.53% | 32.9% | 46 / 279 |
| 5 | 338 | +1897.53U / +189.75% | 1.84 | 10.23% | 33.4% | 46 / 292 |

观察：

1. 放大槽位后，交易数明显增加，但总收益几乎没有增加。
2. `max4`、`max5` 都没有超过基线 `max3` 的收益质量。
3. PF 和胜率下降，回撤明显变差。

结论：

- 三年样本下，`max_open_trades = 3` 明显优于 `4/5`

## 6. 近一年样本槽位对照

区间：

- `2025-06-18 -> 2026-06-18`

结果文件：

- max4: [backtest-result-2026-06-18_07-01-32.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-01-32.zip)
- max5: [backtest-result-2026-06-18_07-01-33.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_07-01-33.zip)

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 111 | +512.35U / +51.23% | 2.00 | 7.65% | 39.64% | 14 / 97 |
| 4 | 128 | +525.87U / +52.59% | 1.90 | 9.55% | 36.7% | 14 / 114 |
| 5 | 136 | +500.13U / +50.01% | 1.80 | 10.25% | 36.0% | 14 / 122 |

观察：

1. 近一年里 `max4` 的绝对收益略高于 `max3`，但优势很小。
2. 为了多出这点收益，PF 从 `2.00` 降到 `1.90`，MaxDD 从 `7.65%` 升到 `9.55%`。
3. `max5` 已经出现“交易更多、质量更差、收益还回落”的情况。

结论：

- 如果目标是更稳，不该为了那一点点绝对收益去放宽到 `4/5`

## 7. 这轮验证的核心结论

### 7.1 对成本压力的判断

`Positive13` 币池下，这版主策略在：

- 三年样本
- 近一年样本

都能承受手续费抬升到 `1.5x` 和 `2x` 的压力，说明它不是“只在理想手续费里成立”的脆弱版本。

### 7.2 对槽位的判断

当前这版策略更像是：

- 需要挑信号
- 不需要堆仓位

它的 alpha 质量主要来自：

1. 币池收敛
2. 形态过滤
3. 只接更像样的结构

而不是靠“多开几单”硬堆出来。

### 7.3 当前最优工作结论

如果现在要为 dry-run 做准备，最合理的主候选仍然是：

- `Positive13`
- `max_open_trades = 3`

## 8. 本轮已完成事项

本轮已完成：

1. 对 `Positive13` 跑三年与近一年基线对照
2. 跑手续费 `1.5x / 2.0x` 成本压力测试
3. 跑 `max_open_trades = 3 / 4 / 5` 对照
4. 输出稳定性判断

## 9. 下一步建议

如果我们继续往实盘准备推进，建议顺序是：

1. 先以 `Positive13 + max3` 作为 dry-run 主候选
2. 再检查 long / short 同币近距离反向冲突情况
3. 最后再决定是否需要做 side-specific slot 或双 bot 拆分
