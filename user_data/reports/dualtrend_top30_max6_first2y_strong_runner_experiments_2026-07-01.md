# DualTrend Top30 Max6 前两年强单放行实验记录

日期: 2026-07-01

## 目的

在不改动核心入场的前提下，只针对 `short_pullback_restart` 做一件事:

- 当订单已经走到 `+5%` 浮盈时
- 尝试识别它是不是值得继续冲 `+10%+` 的“强单”

这轮实验的目标不是继续救亏损，而是验证:

- 能不能把 `Baseline / Guard` 里被过早收掉的大盈利单放行出去
- 同时整体结果至少打赢各自父策略

## 实验口径

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 主周期: `1h`
- 细粒度: `5m`
- 时间范围: `2022-11-11 16:00:00` 到 `2024-11-11 00:00:00`
- 模式: Binance Futures, isolated

父策略:

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

实验分支:

- `DualTrendBaselineStrongRunnerAStrategy`
- `DualTrendBaselineStrongRunnerCStrategy`
- `DualTrendGuardStrongRunnerAStrategy`
- `DualTrendGuardStrongRunnerCStrategy`

## 规则来源

前面已经对 `DualTrendRawStrategy` 的 `short_pullback_restart` 做过路径诊断，得到两个可落地候选:

### 候选 A

- 到达 `+5%` 的时间 `<= 28h`
- 入场后最大不利波动 `MAE <= 1.2%`

### 候选 C

- 到达 `+5%` 的时间 `<= 24h`
- 入场后最大不利波动 `MAE <= 1.0%`

本轮实现方式:

- 仅作用于 `short_pullback_restart`
- 且仅在订单先走到 `+5%` 后触发判断
- 若满足强单条件，则继续放行
- 若不满足，则直接止盈退出

## 总结果

| 策略 | 收益率 | PF | MaxDD | Trades | Winrate |
|---|---:|---:|---:|---:|---:|
| DualTrendBaselineStrategy | 51.39% | 1.758 | 7.91% | 218 | 46.33% |
| DualTrendBaselineStrongRunnerAStrategy | 49.49% | 1.730 | 6.78% | 221 | 47.06% |
| DualTrendBaselineStrongRunnerCStrategy | 47.99% | 1.713 | 6.88% | 221 | 47.51% |
| DualTrendGuardStrategy | 55.27% | 1.850 | 7.91% | 213 | 46.48% |
| DualTrendGuardStrongRunnerAStrategy | 53.09% | 1.815 | 6.89% | 216 | 47.22% |
| DualTrendGuardStrongRunnerCStrategy | 51.55% | 1.797 | 6.89% | 216 | 47.69% |

## 结果解读

### 1. 没有任何一个实验分支打赢父策略收益

- `Baseline_A` 比 `Baseline` 少了 `1.90%`
- `Baseline_C` 比 `Baseline` 少了 `3.40%`
- `Guard_A` 比 `Guard` 少了 `2.18%`
- `Guard_C` 比 `Guard` 少了 `3.72%`

也就是说，这轮“强单放行”虽然方向是对着问题去的，但目前这版实现还没有把收益修回来。

### 2. 回撤确实下降了

- `Baseline`: `7.91%` -> `A: 6.78%`, `C: 6.88%`
- `Guard`: `7.91%` -> `A: 6.89%`, `C: 6.89%`

这个下降幅度不算小，说明规则确实更偏防守。

### 3. 胜率略有提升

- `Baseline`: `46.33%` -> `47.06% / 47.51%`
- `Guard`: `46.48%` -> `47.22% / 47.69%`

这和回撤下降是一致的:

- 坏单被更早处理
- 组合更平滑
- 但大盈利单的恢复力度仍然不够

### 4. A 明显优于 C

不管挂在 `Baseline` 还是 `Guard` 上:

- `A` 的收益都高于 `C`
- `A` 的 PF 也高于 `C`
- 两者回撤差不多

说明更宽一点的强单识别阈值比更苛刻的 C 版本更合理。

## 当前结论

### 最优实验分支

这轮里相对最值得保留观察的是:

- `DualTrendGuardStrongRunnerAStrategy`

原因:

- 4 个实验分支里它的收益最高
- PF 也最高
- 同时保留了明显更低的回撤

但它仍然没有超过 `DualTrendGuardStrategy`，所以还不能升级为主线。

### 是否进入主策略

当前不建议。

原因很直接:

- 目标是“至少打赢父策略”
- 现在是“更稳了，但没更赚”

这类分支可以当作低回撤备选观察版，但还不适合作为主策略替代。

## 这轮实验说明了什么

这轮最有价值的地方，不是找到最终答案，而是确认了一个边界:

- 只在“触及 `+5%` 后”再做简单二分判断
- 还不足以把 `Baseline / Guard` 丢掉的大趋势利润完整拿回来

换句话说，真正决定能不能放行大盈利单的，可能不只是:

- 到 `+5%` 的速度
- 早期 `MAE`

还可能需要更强的趋势延续信息，比如:

- 触及 `+5%` 时的结构位置
- 当时的 4H 趋势状态
- BTC 同步方向
- 是否已经进入加速段而不是普通回撤段

## 建议

当前建议分两层看:

### 如果优先收益

继续保留:

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

### 如果优先更低回撤

可以保留一个观察分支:

- `DualTrendGuardStrongRunnerAStrategy`

但它应该被视为“更平滑的防守版”，不是收益升级版。

## 最终结论

本轮“强单放行”实验结论:

- 有效降低回撤
- 略微提高胜率
- 但没有提升总收益
- 因此暂不建议替代当前 `Baseline / Guard`

现阶段更稳妥的结论仍然是:

- 主线继续保留 `Baseline` 和 `Guard`
- `StrongRunnerA` 只作为后续观察分支
