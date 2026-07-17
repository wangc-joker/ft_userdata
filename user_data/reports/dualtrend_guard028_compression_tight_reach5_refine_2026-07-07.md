# DualTrend CompressionTight reach5 放行细化验证

> **历史状态：** 本文是 2026-07-07 的阶段实验，文中的“当前 short 主候选”已经过时。最新状态见仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md)。

日期：2026-07-07

## 本轮目标

基于当前 short 主候选：

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

继续只研究一件事：

- 当 `short_pullback_restart` 已经达到 `+5%` 时，能不能把“强单放行”再做得更准一点。

不改：

1. 入场逻辑
2. pair pool
3. `max_open_trades`
4. 当前 `CompressionTightStop`
5. 全局止盈框架

## 候选设计

### 基线

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

当前逻辑本质上是：

- 只对 `short_pullback_restart`
- 只在到达 `+5%` 后判断
- 用一组结构条件决定是否继续放行到原有 `ROI 10% / partial_exit`

### 候选 1：Reach5 Loose

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5LooseStrategy`

思路：

- 保持结构型强单放行思路不变
- 只是把阈值轻微放宽：
  - `adverse limit`: `1.25% -> 1.50%`
  - `ret_6h`: `<= -2.0% -> <= -1.5%`
  - `4h ema50 slope3`: `<= -0.5% -> <= -0.4%`

目标：

- 看 current 版本是不是卡得稍微太窄

### 候选 2：Reach5 AdverseOnly

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5AdverseOnlyStrategy`

思路：

- 回到离线诊断里最稳定的单特征
- 只看：
  - 到 `+5%` 前最大不利波动是否足够小
  - 是否在 `18h` 内到达 `+5%`

目标：

- 验证 current 版本是不是加了太多结构条件，反而错杀了一部分真强单

## 三年回测

区间：

- `2023-06-18 -> 2026-06-18`

统一口径：

- timeframe: `1h`
- detail timeframe: `5m`
- Docker 回测

| Strategy | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy` | 319 | 162.46% | 2.44 | 5.05% | 53.3% |
| `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5LooseStrategy` | 319 | 162.46% | 2.44 | 5.05% | 53.3% |
| `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5AdverseOnlyStrategy` | 312 | 154.67% | 2.42 | 5.05% | 51.3% |

## 结果解释

### 1. Reach5 Loose 没有带来任何变化

这版三年结果与当前主候选完全一致：

- Trades 一样
- Profit 一样
- PF 一样
- MaxDD 一样

这说明至少在当前样本里：

- 把结构阈值从 current 版轻微放宽，并没有实际改变最终分流结果
- 也就是说，真正卡住分流的，不是这些边界值差 `0.1% ~ 0.5%` 的细枝末节

### 2. Reach5 AdverseOnly 方向退化

这版是更“纯”的小回撤放行：

- Profit: `162.46% -> 154.67%`
- PF: `2.44 -> 2.42`
- Winrate: `53.3% -> 51.3%`
- Trades: `319 -> 312`

虽然它保住了：

- MaxDD 基本不变：`5.05%`

但问题是：

1. 收益明显掉了
2. 交易数减少了
3. `short_pullback_restart` 总贡献也没能超过 current

这说明只靠：

- `adverse_before_5pct`
- `hours_to_5`

还不足以替代 current 这版的结构放行判断。

### 3. current 版仍然是更平衡的放行方式

从这轮结果看，current 版的优势在于：

1. 它没有单纯放得更宽
2. 它也没有单纯放得更窄
3. 它是用一个足够克制的结构条件，把该继续跑的 `short_pullback_restart` 留下来

而我们刚试的两个方向分别对应：

- 候选 1：微调边界
- 候选 2：去掉结构，只保留最核心单变量

这两条都没有打赢 current。

## 本轮结论

当前最优仍然是：

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

不建议升级为主线：

1. `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5LooseStrategy`
2. `DualTrendCompressionCloseQualityGuard028CompressionTightStopReach5AdverseOnlyStrategy`

## 当前判断

这轮给了我们两个很有用的否定结论：

1. **current 版不是因为阈值刚好卡得太严才表现最好**
   - 轻微放宽后没有改善

2. **current 版也不是可以被“更纯的小回撤规则”简单替代**
   - 去掉结构判断后，收益反而下降

换句话说：

- 现在这版 reach5 放行已经比较接近一个“够用的平衡点”

## 下一步建议

如果还要继续在这条主线上优化，更像样的方向不会是再去抠：

- `1.25%` 还是 `1.50%`
- `-2.0%` 还是 `-1.5%`

而应该是：

1. **做 same-trade 对照**
   - 专门比较 current 与 adverse-only 在相同开仓里的利润差
   - 看 current 到底多赚在哪些单

2. **只研究 current 错放 or 错杀的少数边界单**
   - 不再大范围调阈值

3. **把主精力回到前置坏信号过滤**
   - 因为 reach5 放行这块现在已经没有明显的低垂果实了
