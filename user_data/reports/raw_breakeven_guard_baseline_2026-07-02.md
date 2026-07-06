# Raw / Breakeven / Guard Baseline

本轮把止盈研究基线切换为 3 条独立主线：

1. `DualTrendRawStrategy`
2. `DualTrendRawBreakevenStrategy`
3. `DualTrendRawBreakevenGuardStrategy`

说明：

- `Raw`：只保留当前 raw 入场，不带旧 `reach5` 分流。
- `Raw + Breakeven`：只加 `+2% -> 锁 0.1%` 的保本止损。
- `Raw + Breakeven + Guard`：在上一条基础上，再加 `short_compression_breakdown` 的 flush guard。

## 三年

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| DualTrendRawStrategy | 373 | 189.66% | 1.77 | 9.76% | 31.4% |
| DualTrendRawBreakevenStrategy | 395 | 132.50% | 1.95 | 5.47% | 47.3% |
| DualTrendRawBreakevenGuardStrategy | 387 | 140.52% | 2.02 | 5.47% | 47.5% |

结论：

- `Raw` 收益最高，但 PF 和回撤控制最弱。
- 单加保本，收益明显下降，但 PF / 胜率 / MaxDD 明显改善。
- `Breakeven + Guard` 比 `Breakeven` 多拿回一部分收益，同时 PF 继续略优，是更平衡的研究底座。

## 近一年

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| DualTrendRawStrategy | 145 | 42.59% | 1.68 | 9.75% | 33.1% |
| DualTrendRawBreakevenStrategy | 156 | 35.32% | 2.03 | 5.49% | 51.9% |
| DualTrendRawBreakevenGuardStrategy | 154 | 36.31% | 2.08 | 5.49% | 51.9% |

结论：

- 近一年同样是 `Raw` 收益最高，但代价是 PF 和 MaxDD 更差。
- `Breakeven + Guard` 是三条里最均衡的一条：收益只比 `Breakeven` 略高，但 PF 最好。

## 后续研究口径

从这一轮开始，止盈实验默认使用以下口径：

- baseline：`DualTrendRawStrategy`
- candidate 1：`DualTrendRawBreakevenStrategy`
- candidate 2：`DualTrendRawBreakevenGuardStrategy`

如果目标是“在不过度牺牲收益的前提下，提高稳健性”，更建议后续止盈研究优先挂在：

- `DualTrendRawBreakevenGuardStrategy`

如果目标是“纯追求利润上限”，则继续以：

- `DualTrendRawStrategy`

作为绝对收益对照线。
