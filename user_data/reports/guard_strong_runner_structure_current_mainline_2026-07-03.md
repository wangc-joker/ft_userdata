# Guard 主线 5% 强单放行结构版验证

生成时间: 2026-07-03

## 本轮做了什么

本轮没有改入场，只在当前主线 `DualTrendRawBreakevenGuardStrategy` 上，加了一个更窄的候选：

- 新增策略类：`DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`
- 作用范围：只影响 `short_pullback_restart`
- 触发前提：该单先走到 `+5%`
- 处理思路：沿用旧版 strong-runner / structure 放行逻辑，让已经证明自己是强单的仓位，别太早被普通保本逻辑切掉

实现位置：

- [DualTrendMainStrategies.py](D:/test/ft_userdata/user_data/strategies/DualTrendMainStrategies.py)

## 研究目标

验证一件事：

在**不改当前入场逻辑**的前提下，能不能只对已经达到 `+5%` 的 `short_pullback_restart` 强单放行，从而打赢当前 Guard 主线。

对照基线使用上一轮已经确认的：

- `DualTrendRawBreakevenGuardStrategy`

## 回测窗口

1. 三年：`2023-06-18 -> 2026-06-18`
2. 近一年：`2025-06-18 -> 2026-06-18`
3. 压力期：`2026-03-01 -> 2026-05-31`
4. 修复期：`2026-06-01 -> 2026-06-18`

统一口径：

- timeframe: `1h`
- detail timeframe: `5m`
- Docker 回测

## 总表

| Window | Strategy | Trades | Profit % | PF | MaxDD % | Winrate % | Avg Duration |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 3y | Guard baseline | 321 | 144.67 | 2.21 | 7.13 | 50.16 | - |
| 3y | Guard + StrongRunnerStructure | 335 | 155.07 | 2.22 | 5.77 | 52.84 | 1 day, 4:08:00 |
| 1y | Guard baseline | 127 | 41.72 | 2.36 | 4.85 | 53.54 | - |
| 1y | Guard + StrongRunnerStructure | 135 | 47.75 | 2.41 | 4.84 | 54.81 | 1 day, 7:09:00 |
| pressure | Guard baseline | 18 | -1.55 | 0.64 | 3.30 | 33.33 | - |
| pressure | Guard + StrongRunnerStructure | 20 | 1.91 | 1.38 | 3.30 | 35.00 | 1 day, 6:47:00 |
| repair | Guard baseline | 10 | 1.20 | 1.53 | 2.19 | 60.00 | - |
| repair | Guard + StrongRunnerStructure | 11 | -0.45 | 0.80 | 2.21 | 63.64 | 11:19:00 |

## 核心结果

### 1. 三年结果是明显提升

- 收益：`144.67% -> 155.07%`
- PF：`2.21 -> 2.22`
- MaxDD：`7.13% -> 5.77%`
- 胜率：`50.16% -> 52.84%`

这不是只换来更高收益的“冒险版本”，而是同时把回撤压下来了。

### 2. 近一年也提升

- 收益：`41.72% -> 47.75%`
- PF：`2.36 -> 2.41`
- MaxDD：`4.85% -> 4.84%`

说明它不是只靠老样本吃饭，近期同样成立。

### 3. 压力期改善很明显

- `-1.55% -> +1.91%`
- PF：`0.64 -> 1.38`

这点比较关键。它不是“平时更猛，压力期更脆”，反而在差行情里也更能扛。

### 4. 修复期反而变差

- `+1.20% -> -0.45%`
- PF：`1.53 -> 0.80`

这说明它不是无条件更优，而是对某些短促修复段不友好。这个风险需要记着。

## Tag 贡献

三年窗口：

- `short_pullback_restart`: `75.49%`
- `long_1d_center_compression`: `52.82%`
- `short_compression_breakdown`: `26.76%`

近一年窗口：

- `short_pullback_restart`: `27.65%`
- `long_1d_center_compression`: `18.27%`
- `short_compression_breakdown`: `1.83%`

结论很直白：

- 这版增强，主要还是在放大 `short_pullback_restart` 的强单利润贡献。
- 它没有破坏整体结构，`long_1d_center_compression` 仍然贡献稳定。

## Pair 观察

三年窗口：

- 最强：`ETH/USDT:USDT`，`27.83%`
- 最弱：`LINK/USDT:USDT`，`-7.70%`

近一年窗口：

- 最强：`ETH/USDT:USDT`，`10.12%`
- 最弱：`LINK/USDT:USDT`，`-1.50%`

目前最稳定受益的还是 `ETH`，拖累最明显的还是 `LINK`。

## 退出结构观察

三年窗口里，新增候选最主要的盈利来源还是：

- `partial_exit`: `143.72%`
- `roi`: `133.90%`

也就是说，这版并不是把原来的盈利结构完全推翻了，它本质上还是：

- 先让强单活得更久
- 然后继续通过原本的分批 / ROI 结构兑现利润

这点是健康的，因为它没有变成“只靠一个很脆的新退出规则赚钱”。

## 怎么理解这版为什么有效

和上一轮“全局结构止盈”不同，这一版的范围收得很窄：

1. 不碰所有单
2. 不碰所有 tag
3. 只在 `short_pullback_restart` 已经跑到 `+5%` 后才介入

这就避免了上一轮最大的问题：

- 还没证明自己是强单，就提前结构化处理，结果把很多本来能走到 ROI 的单子切掉

这次等于先让市场证明“这单确实强”，再给它更多跑赢空间。

## 本轮判断

如果只看当前 Guard 主线，这个候选是值得继续的，因为它同时满足：

- 三年收益更高
- 三年 PF 没掉
- 三年 MaxDD 更低
- 近一年也更好
- 压力期改善明显

唯一需要保留的风险提示是：

- 修复期变差，说明它不是所有市场状态都占优

## 结论

这版 `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`：

- **比当前 Guard 主线更强**
- **值得保留为下一轮主候选**
- **比上一轮“全局结构止盈”靠谱得多**

下一步更合理的方向，不是再做大范围止盈实验，而是围绕这条主线继续做更窄的验证：

1. 只研究 `short_pullback_restart`
2. 只研究“达到 `+5%` 后，哪些单值得继续放行”
3. 避免碰全局所有 tag 的止盈逻辑

