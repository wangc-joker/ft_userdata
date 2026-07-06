# DualTrend Top30 Max6 前两年结构型强单放行回测

日期: 2026-07-01

## 目的

在前面的 `reach5` 结构诊断基础上，验证一个更窄的真实回测分支：

- 只作用于 `short_pullback_restart`
- 只在订单先达到 `+5%` 后触发判断
- 保留原来的 `adverse <= 1.25%` 思路
- 再叠加两个当下结构条件：
  - `pair_1h_ret_6h <= -2%`
  - `pair_4h_ema50_slope_3 <= -0.5%`

核心问题：

- 这能不能比父策略更好地识别“应该继续冲 `+10%+`”的真强单？

## 回测口径

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 周期: `1h + 5m detail`
- 区间: `2022-11-11 16:00:00 -> 2024-11-11 00:00:00`
- 模式: Binance Futures, isolated

父策略:

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

新分支:

- `DualTrendBaselineStrongRunnerStructureStrategy`
- `DualTrendGuardStrongRunnerStructureStrategy`

## 总结果

| 策略 | 收益率 | PF | MaxDD | Trades | Winrate |
|---|---:|---:|---:|---:|---:|
| DualTrendBaselineStrategy | 51.39% | 1.7580 | 7.91% | 218 | 46.33% |
| DualTrendBaselineStrongRunnerStructureStrategy | 53.48% | 1.7602 | 7.18% | 225 | 48.44% |
| DualTrendGuardStrategy | 55.27% | 1.8495 | 7.91% | 213 | 46.48% |
| DualTrendGuardStrongRunnerStructureStrategy | 57.39% | 1.8487 | 7.05% | 220 | 48.64% |

## 相对父策略变化

### Baseline -> Baseline Structure

- 收益: `51.39% -> 53.48%`，提升 `+2.09%`
- PF: `1.7580 -> 1.7602`，基本持平，略有改善
- MaxDD: `7.91% -> 7.18%`，下降 `0.73%`
- Winrate: `46.33% -> 48.44%`
- Trades: `218 -> 225`

### Guard -> Guard Structure

- 收益: `55.27% -> 57.39%`，提升 `+2.12%`
- PF: `1.8495 -> 1.8487`，几乎持平
- MaxDD: `7.91% -> 7.05%`，下降 `0.86%`
- Winrate: `46.48% -> 48.64%`
- Trades: `213 -> 220`

## short_pullback_restart 变化

| 策略 | short_pullback_profit_abs | trades | winrate |
|---|---:|---:|---:|
| Baseline | 330.70 | 125 | 52.00% |
| Baseline Structure | 359.70 | 131 | 55.73% |
| Guard | 332.87 | 123 | 51.22% |
| Guard Structure | 362.55 | 129 | 55.04% |

观察：

- 这次收益改善，主要就来自 `short_pullback_restart`
- 不只是利润变高，命中率也更高
- 说明这条结构条件并不是“更保守地少做单”，而是在 `+5%` 节点更合理地区分了该放和不该放的单

## 和上一轮 A / C 的区别

上一轮 A / C 方案结论是：

- 回撤下降
- 胜率提升
- 但总收益没有打赢父策略

这一轮结构版的区别在于：

- 不再依赖 `hours_to_5pct`
- 更重视 `+5%` 当下是否仍在趋势加速段
- 结果上第一次出现了“收益和回撤同时变好”的情况

## 当前结论

这轮结果是正面的，而且比上一轮更有升级价值。

### 1. 结构型强单放行，比单纯 A / C 候选更靠谱

原因：

- `Baseline Structure` 打赢了 `Baseline`
- `Guard Structure` 打赢了 `Guard`
- 两条线上都不是只赢一个指标，而是：
  - 收益更高
  - 回撤更低
  - 胜率更高

### 2. 当前最值得继续推进的是 Guard Structure

因为它在这轮里综合最好：

- 收益最高：`57.39%`
- 回撤最低：`7.05%`
- PF 基本维持住父策略水平

### 3. 这说明“5% 节点时趋势是否仍在加速”确实有信息量

目前最有效的两个附加条件是：

- 最近 `6h` 仍然明显下行
- `4H EMA50` 仍明显向下

这比只看“到 5% 的时间快不快”更接近我们真正想抓的东西。

## 建议

下一步建议不要再大范围乱扩，而是围绕这个结构版继续做两件事中的一件：

1. 先做 `3年 / 5年` 稳健性验证，看这个提升是不是只出现在前两年。
2. 或者只对 `Guard Structure` 做更小步的阈值微调，比如：
   - `ret_6h` 从 `-2%` 微调到 `-1.5% / -2.5%`
   - `4h ema50 slope` 从 `-0.5%` 微调到 `-0.25% / -0.75%`

## 最终结论

这轮是到目前为止第一版真正值得继续推进的“强单放行”升级分支。

如果只看前两年样本：

- `DualTrendBaselineStrongRunnerStructureStrategy` 优于 `Baseline`
- `DualTrendGuardStrongRunnerStructureStrategy` 优于 `Guard`

其中主候选已经可以先切换为：

- `DualTrendGuardStrongRunnerStructureStrategy`
