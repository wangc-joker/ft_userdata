# DualTrend Combined top40_302u 全局过滤验证

## 1. 目标

这轮验证的目标不是针对单个币种做适配，而是测试能否通过更统一的全局过滤，减少不适配币种的误判，降低亏损，提高整体胜率和稳定性。

验证基线：

```text
DualTrendCombinedLongDailyCenterShortV1Strategy
```

币池：

```text
D:/test/real_trade/user_data/generated/pairs.dynamic.top40.302u.balanced.json
```

说明：

这个文件名叫 top40，但实际内容为 30 个 pair。

## 2. 本轮新增验证版本

新增文件：

```text
D:/test/ft_userdata/user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
```

包含 3 个实验版本：

1. `DualTrendCombinedShortDailyCenterFilterStrategy`
2. `DualTrendCombinedLongStrongConfirmStrategy`
3. `DualTrendCombinedBalancedGlobalFilterStrategy`

### 2.1 Short Daily Center Filter

思路：

1. short 入场增加旧策略里的 `market_center / 1d_center` 方向过滤；
2. 要求 short 信号出现时，`close < legacy_market_center_1d` 且 `legacy_center_down_1d = True`。

目的：

减少逆大级别中轴方向的 short 误判。

### 2.2 Long Strong Confirm

思路：

1. 保留现有 long 逻辑；
2. long 增加更强的全局确认：
   - `daily_momentum_long_1d = True`
   - `trend_up_4h = True`
   - `center_up_1d = True`
   - 非 BTC 币种额外要求 `btc_trend_up_4h = True`

目的：

减少长周期不够顺、但局部形态勉强触发的 long 误判。

### 2.3 Balanced Global Filter

思路：

同时启用：

1. short 的 `1d center` 过滤；
2. long 的强确认过滤。

目的：

测试双边一起收紧后，是否能得到更稳的组合。

## 3. 回测过程记录

### 3.1 执行前问题

第一次运行时报错：

```text
KeyError: 'rsi_1d'
```

原因：

子类里覆写了 `populate_indicators_1d()`，但没有加 `@informative("1d")`，导致 1D 指标没有按 Freqtrade 的 informative 流程正确挂到主 dataframe。

修正：

在新文件中补上：

```python
from freqtrade.strategy import informative
```

并给 `populate_indicators_1d()` 加上：

```python
@informative("1d")
```

修正后重新完成 6 组回测。

### 3.2 回测样本

1. 1 年：`2025-05-07` 至 `2026-05-07`
2. 3 年：`2023-05-14` 至 `2026-05-07`

## 4. 基线结果

来自之前已确认的 combined 基线：

### 4.1 1 年基线

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% |

### 4.2 3 年基线

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% |

## 5. 全局过滤结果

### 5.1 1 年样本

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% |
| Short Daily Center Filter | 110 | +175.10U / +17.51% | 1.37 | 7.01% | 30.0% |
| Long Strong Confirm | 136 | +254.15U / +25.41% | 1.42 | 8.51% | 32.35% |
| Balanced Global Filter | 106 | +142.55U / +14.25% | 1.31 | 7.04% | 29.25% |

### 5.2 3 年样本

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% |
| Short Daily Center Filter | 291 | +1225.29U / +122.53% | 1.67 | 7.06% | 30.93% |
| Long Strong Confirm | 347 | +1073.14U / +107.31% | 1.52 | 8.61% | 30.84% |
| Balanced Global Filter | 278 | +955.85U / +95.58% | 1.58 | 7.00% | 30.22% |

## 6. 各版本解读

### 6.1 Short Daily Center Filter

特点：

1. 1 年样本明显变差；
2. 3 年样本 PF 从 `1.60` 提升到 `1.67`；
3. 3 年样本 MaxDD 从 `8.62%` 降到 `7.06%`；
4. 交易数显著减少，说明它确实在过滤信号，而不是只改了统计表现。

解读：

这个过滤的方向是对的，它能减少一部分 short 误判，长期质量有改善。

但问题也很明确：

它在近期样本上过于保守，把利润也砍掉了，属于“质量更干净，但收益损失偏大”。

### 6.2 Long Strong Confirm

特点：

1. 1 年、3 年都弱于基线；
2. 1 年回撤没有改善，3 年 PF 还下降；
3. 说明这组 long 强确认并没有有效筛掉主要亏损，反而更多是在减少有效信号。

解读：

这条线当前不值得继续深挖。至少以现在这组确认条件来看，它不是一个好的“整体优化器”。

### 6.3 Balanced Global Filter

特点：

1. 双边一起加过滤后，1 年和 3 年收益都下降明显；
2. 回撤下降，但收益下降幅度更大；
3. PF 没有得到与收益损失相匹配的提升。

解读：

这说明当前“双边一起收紧”的版本太克制了，不适合作为主版本。

## 7. tag 层面的变化

从结果上看：

### 7.1 Short Daily Center Filter

1 年：

1. `long_1d_center_compression`: `23 trades / +119.1U`
2. `short_pullback_restart`: `73 trades / +65.5U`
3. `short_compression_breakdown`: `14 trades / -9.5U`

3 年：

1. `short_pullback_restart`: `181 trades / +490.3U`
2. `long_1d_center_compression`: `68 trades / +463.4U`
3. `short_compression_breakdown`: `42 trades / +271.5U`

解读：

这个过滤没有伤到主要盈利结构本身，但它明显减少了 short 的触发频率。长期看，留下来的 short 质量更高；短期看，减少过头。

### 7.2 Long Strong Confirm

1 年：

1. `short_compression_breakdown`: `24 trades / +111.3U`
2. `long_1d_center_compression`: `19 trades / +92.0U`
3. `short_pullback_restart`: `93 trades / +50.8U`

3 年：

1. `short_pullback_restart`: `225 trades / +408.2U`
2. `short_compression_breakdown`: `68 trades / +397.5U`
3. `long_1d_center_compression`: `54 trades / +267.5U`

解读：

它没有把 long 变得更强，反而让整体分布更偏向 short。也就是说，这不是一个真正有效的 long 质量提升器。

## 8. 结论

结合这轮结果，可以得到几个明确判断：

1. 你的方向是对的，优先做整体过滤，比按单个币种做特判更值得。
2. 这轮 3 个全局过滤里，唯一值得保留并继续微调的，是 `short_1d_center / market_center` 这条线。
3. 这条线的优点是：
   - 长周期 PF 更高；
   - 回撤更低；
   - 更符合“减少误判”的目标。
4. 它当前的问题是：
   - 近期样本过于保守；
   - 砍掉了太多 short 机会，导致 1 年收益明显下降。
5. long 的强确认过滤当前不成立，不建议继续加码。
6. 双边同时收紧也不成立，不建议直接并入主策略。

## 9. 下一步建议

下一步建议只沿着一条线继续，而不是再开很多分支：

### 主线

只优化 short 的全局过滤强度，不做 pair 特判。

### 具体做法

1. 保留 `market_center / 1d_center` 思路；
2. 但不要直接当成硬门槛全开；
3. 可以测试更温和的版本，例如：
   - 只过滤 `short_compression_breakdown`
   - 只在 `1d center` 明显向上时拒绝 short
   - 或者只把它作为“弱信号剔除器”，不拦截所有 short
4. 判断标准优先看：
   - 1 年样本利润不能明显塌；
   - 3 年 PF 不能回落；
   - MaxDD 最好继续低于基线。

### 暂不建议

1. 暂不建议对 `LTC/BCH/LINK/DOT/NEAR` 做专门规则；
2. 暂不建议继续扩大 long 过滤模块；
3. 暂不建议把 balanced 版本当主线。

## 10. 当前阶段结论

如果坚持“尽量不单独处理某个币种，最坏直接去掉”，那当前最合理的方向是：

1. 主策略先保持基线；
2. 单独把 short 的 `1d center / market_center` 过滤做成一个更轻量的全局版本继续验证；
3. 只有当它能在 1 年样本不明显伤收益、同时 3 年 PF 仍优于基线时，才考虑正式并入。

目前还不到直接替换主策略的时候，但已经找到一个有希望的整体优化方向。

## 11. 第二轮：short 轻量全局过滤

在第一轮验证后，没有继续扩展 long 过滤，也没有对单个币种做适配。

只围绕 short 侧继续做一轮更轻的全局过滤验证。

### 11.1 设计原则

目标：

1. 不改 short 核心入场结构；
2. 不对单币种单独处理；
3. 只减少明显逆大级别中轴方向的 short；
4. 尽量保住 1 年收益，不再像第一轮 strict 版本那样砍掉过多机会。

### 11.2 新增 3 个轻量版本

更新文件：

```text
D:/test/ft_userdata/user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
```

新增模式：

1. `DualTrendCombinedShortBreakdownDailyCenterFilterStrategy`
2. `DualTrendCombinedShortRejectClearUptrendStrategy`
3. `DualTrendCombinedShortBreakdownRejectClearUptrendStrategy`

### 11.3 逻辑说明

#### A. ShortBreakdownDailyCenterFilter

只对：

```text
short_compression_breakdown
```

启用第一轮那种严格门槛：

1. `legacy_center_down_1d = True`
2. `close < legacy_market_center_1d`

也就是：

只收紧更容易误判的 breakdown，不碰 `short_pullback_restart`。

#### B. ShortRejectClearUptrend

不再要求 short 必须处于 `1d center down`，而是只拒绝最明显逆势的情况：

1. `legacy_center_up_1d = True`
2. `close > legacy_market_center_1d`

满足以上两点时，拒绝 short。

这比“必须 center_down 才能 short”轻很多，更接近一个全局逆势拦截器。

#### C. ShortBreakdownRejectClearUptrend

把 B 的逻辑进一步收窄：

1. 只对 `short_compression_breakdown` 生效；
2. 只有在 `1d center up` 且 `close > market_center_1d` 时才拒绝。

## 12. 第二轮结果

### 12.1 1 年样本：2025-05-07 至 2026-05-07

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 140 | +295.88U / +29.59% | 1.48 | 8.46% | 32.9% |
| 第一轮 strict all | 110 | +175.10U / +17.51% | 1.37 | 7.01% | 30.0% |
| Breakdown strict only | 133 | +151.37U / +15.14% | 1.26 | 10.24% | 30.8% |
| Reject clear uptrend all | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% |
| Reject clear uptrend breakdown only | 139 | +298.72U / +29.87% | 1.48 | 8.45% | 33.09% |

### 12.2 3 年样本：2023-05-14 至 2026-05-07

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 359 | +1377.96U / +137.80% | 1.60 | 8.62% | 31.5% |
| 第一轮 strict all | 291 | +1225.29U / +122.53% | 1.67 | 7.06% | 30.93% |
| Breakdown strict only | 339 | +1152.21U / +115.22% | 1.53 | 10.20% | 30.97% |
| Reject clear uptrend all | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% |
| Reject clear uptrend breakdown only | 357 | +1401.56U / +140.16% | 1.61 | 8.60% | 31.65% |

## 13. 第二轮解读

### 13.1 Breakdown strict only 失败

这个结果很直接：

1. 1 年收益掉到 `+15.14%`
2. 3 年 PF 反而降到 `1.53`
3. MaxDD 还升到 `10.20%`

说明：

只对 `short_compression_breakdown` 套第一轮那种 strict 逻辑，并没有达到“更轻更优”的效果，反而是把该留的机会砍掉了，但没有有效改善整体质量。

这条线可以直接淘汰。

### 13.2 Reject clear uptrend all 是目前最优

它的表现是：

1. 1 年：`+30.47% / PF 1.50 / MaxDD 8.54% / Winrate 33.33%`
2. 3 年：`+142.17% / PF 1.62 / MaxDD 8.63% / Winrate 31.74%`

相对基线：

1. 1 年收益更高：`29.59% -> 30.47%`
2. 1 年 PF 更高：`1.48 -> 1.50`
3. 1 年胜率更高：`32.9% -> 33.33%`
4. 3 年收益更高：`137.80% -> 142.17%`
5. 3 年 PF 更高：`1.60 -> 1.62`
6. 3 年胜率更高：`31.5% -> 31.74%`
7. MaxDD 基本持平：`8.62% -> 8.63%`

这说明它没有像 strict 版本那样“靠减少交易换指标”，而是在几乎不伤主结构的前提下，拦掉了一部分明显逆大级别中轴的 short。

这正符合“整体优化，不做单币适配”的目标。

### 13.3 Reject clear uptrend breakdown only 也有效，但略弱

这个版本也不错：

1. 1 年：`+29.87% / PF 1.48 / MaxDD 8.45%`
2. 3 年：`+140.16% / PF 1.61 / MaxDD 8.60%`

它比基线稍好，也比 strict 版本自然。

但和 `Reject clear uptrend all` 比：

1. 收益略低；
2. PF 略低；
3. 提升幅度更小。

所以它更像保守备选，不是当前最优。

## 14. 当前最佳方向

到目前为止，最值得保留并继续推进的全局优化版本是：

```text
DualTrendCombinedShortRejectClearUptrendStrategy
```

它的核心思想非常简单：

1. 不要求做空必须满足 `1d center down`；
2. 只在最明显逆势时拒绝做空：
   - `legacy_center_up_1d = True`
   - `close > legacy_market_center_1d`

这种过滤比第一轮 strict 逻辑更符合策略实际：

1. 保留大部分原有 short 主线；
2. 避免在大级别明显偏上的环境里去硬做 short；
3. 不需要为 `LTC/BCH/LINK/DOT/NEAR` 单独写例外规则。

## 15. 当前阶段结论更新

现在可以把结论更新为：

1. “按整体过滤优化，而不是按币种特判” 这条路成立。
2. 第一轮 strict `1d center` 过滤太硬，不适合作为主版本。
3. 第二轮 `reject clear uptrend` 过滤强度合适，已经表现出真实提升。
4. 当前最优候选是：

```text
DualTrendCombinedShortRejectClearUptrendStrategy
```

5. 如果继续推进，下一步应该优先：
   - 把这个逻辑并入 combined 主策略候选；
   - 再做一轮成本压力与 `max_open_trades 3/4/5` 验证；
   - 确认改进不是偶然样本收益漂移。

## 16. 主候选稳健性复核

在第二轮确认 `DualTrendCombinedShortRejectClearUptrendStrategy` 是当前最优候选后，继续做一轮稳健性复核：

1. `max_open_trades = 3 / 4 / 5`
2. 成本压力
3. same-pair long / short 近距离反向冲突
4. 重新检查 `LTC/BCH/LINK/DOT/NEAR` 是否自然改善

说明：

这轮没有再改策略逻辑，只是验证当前主候选是否足够稳。

## 17. max_open_trades 验证

### 17.1 1 年样本：2025-05-07 至 2026-05-07

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 3 | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% |
| 4 | 159 | +285.32U / +28.53% | 1.42 | 10.00% | 31.45% |
| 5 | 167 | +312.14U / +31.21% | 1.44 | 9.99% | 31.74% |

### 17.2 3 年样本：2023-05-14 至 2026-05-07

| max_open_trades | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 3 | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% |
| 4 | 397 | +1549.75U / +154.97% | 1.60 | 10.01% | 30.98% |
| 5 | 413 | +1588.24U / +158.82% | 1.60 | 10.01% | 30.99% |

### 17.3 解读

和之前基线版本的规律一致：

1. `4/5` 会提高总收益；
2. 但 PF 会下降；
3. MaxDD 会明显升到约 `10%`；
4. 胜率也没有跟着变好。

结论仍然是：

```text
max_open_trades = 3
```

依然是最平衡的稳健值。

## 18. 成本压力验证

口径延续之前的定义：

1. 手续费 1.5x => `fee = 0.00075`
2. 手续费 2x => `fee = 0.0010`
3. 滑点 0.10% => 用每侧额外成本折算为 `fee = 0.0015`
4. 滑点 0.20% => 用每侧额外成本折算为 `fee = 0.0025`

### 18.1 1 年样本

| 场景 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% |
| 手续费 1.5x | 138 | +288.56U / +28.86% | 1.46 | 8.77% | 32.61% |
| 手续费 2x | 138 | +271.27U / +27.13% | 1.43 | 9.09% | 32.61% |
| 滑点 0.10% | 141 | +214.13U / +21.41% | 1.32 | 9.73% | 30.50% |
| 滑点 0.20% | 140 | +121.09U / +12.11% | 1.17 | 10.57% | 30.00% |

### 18.2 3 年样本

| 场景 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% |
| 手续费 1.5x | 357 | +1328.98U / +132.90% | 1.58 | 8.97% | 31.37% |
| 手续费 2x | 357 | +1264.87U / +126.49% | 1.55 | 9.26% | 31.37% |
| 滑点 0.10% | 360 | +1070.05U / +107.00% | 1.46 | 9.86% | 30.00% |
| 滑点 0.20% | 358 | +615.14U / +61.51% | 1.28 | 10.65% | 29.33% |

### 18.3 解读

这个主候选的成本表现和之前基线类似，但略好一点：

1. 手续费放大到 `1.5x / 2x` 后，1 年和 3 年都仍然稳健为正；
2. `0.10%` 滑点压力下，策略仍保持有效；
3. `0.20%` 滑点下优势被明显侵蚀，但 3 年样本仍为正。

也就是说，这版不是“完全不怕成本”，但没有表现出脆弱化。

## 19. same-pair long / short 反向冲突

检查口径：

1. 同一 pair；
2. 前一笔和平后一笔方向相反；
3. 统计平仓到下一笔开仓是否在 `24h / 72h` 内。

3 年主候选结果：

```text
24h 内反向冲突：0
72h 内反向冲突：0
```

结论：

新的 short 全局过滤并没有制造 long / short 的近距离互打问题。

## 20. 拖累币复查

对比对象：

1. 旧 combined 基线 3 年版本
2. 新主候选 `DualTrendCombinedShortRejectClearUptrendStrategy` 3 年版本

### 20.1 对比结果

| Pair | 基线 Trades | 基线 Profit | 新版 Trades | 新版 Profit | 改善额 |
|---|---:|---:|---:|---:|---:|
| LTC | 3 | -30.48U | 3 | -30.59U | -0.11U |
| BCH | 2 | -28.38U | 2 | -28.60U | -0.22U |
| LINK | 24 | -28.08U | 24 | -28.40U | -0.32U |
| DOT | 2 | -20.10U | 2 | -20.10U | 0.00U |
| NEAR | 32 | -16.76U | 32 | -16.23U | +0.53U |

### 20.2 原因拆解

新版 3 年主候选里：

1. `LTC`：`long_1d_center_compression` 3 笔，合计 `-30.6U`
2. `BCH`：`long_1d_center_compression` 2 笔，合计 `-28.6U`
3. `DOT`：`long_1d_center_compression` 2 笔，合计 `-20.1U`
4. `LINK`：以 short 为主拖累
   - `short_compression_breakdown` 6 笔，`-24.5U`
   - `short_pullback_restart` 18 笔，`-3.9U`
5. `NEAR`：混合型
   - `long_1d_center_compression` 2 笔，`-17.5U`
   - `short_compression_breakdown` 8 笔，`+4.5U`
   - `short_pullback_restart` 22 笔，`-3.2U`

### 20.3 结论

这一步很关键：

新的 short 全局过滤确实提升了整体质量，但它不会自动修复所有拖累 pair。

原因是：

1. `LTC/BCH/DOT` 的主要亏损仍然来自 long；
2. `LINK` 的问题仍然是 short 本身结构不佳；
3. `NEAR` 只有很轻微改善。

也就是说：

这轮验证证明了“整体 short 过滤优化”是有效的，但它解决的是 short 的整体误判率，不是所有拖累币的全部来源。

## 21. 当前最终结论

到目前为止，可以把这个方向的判断收敛为：

1. `DualTrendCombinedShortRejectClearUptrendStrategy` 是当前 combined 版本的最佳全局优化候选。
2. 它相对旧基线同时做到了：
   - 1 年收益更高
   - 1 年 PF 更高
   - 3 年收益更高
   - 3 年 PF 更高
   - 胜率更高
   - MaxDD 基本持平
3. `max_open_trades = 3` 仍然最稳。
4. 成本压力下策略仍有效。
5. long / short 没有 same-pair 近距离反向冲突。
6. 但它不会自动消除 `LTC/BCH/DOT` 这类主要由 long 带来的拖累。

## 22. 下一步建议

如果继续保持“尽量不做单币特判”的原则，下一步最合理的是：

1. 把这版 short 全局过滤保留为 combined 主候选；
2. short 侧先不再继续加复杂模块；
3. 如果要继续优化拖累 pair，下一阶段应转到：
   - long `1d_center_compression` 的整体过滤质量；
   - 或者干脆评估是否把极少数长期不适配币种从 long 侧移除。

换句话说：

short 这条线目前已经找到一个成立的整体优化版本，后面再继续提升，主战场大概率不在 short，而在 long。

## 23. 口径修正：GlobalV2 正式候选

复查代码后发现一个重要细节：

```text
DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
```

里的全局验证基类已经把：

```text
long_daily_rsi = 58
```

所以前面验证出来的 `DualTrendCombinedShortRejectClearUptrendStrategy`，实际并不是“只改 short 过滤”的版本。

它真实包含两部分：

1. long 侧：`long_daily_rsi` 从原始 combined 的 `55` 提高到 `58`
2. short 侧：拒绝 `1d legacy center` 明显向上、且价格在 `legacy_market_center_1d` 上方时继续做空

这不是问题，因为回测结果已经验证这个组合有效。

但后续命名和报告口径需要更准确，所以新增正式候选类：

```text
DualTrendCombinedGlobalV2Strategy
```

其定义为：

```text
long_daily_rsi = 58
short_filter_mode = reject_clear_uptrend_all
```

之后把它作为 combined 主候选，而不是继续称为“纯 short 过滤版”。

## 24. Long 整体过滤验证

在 `DualTrendCombinedGlobalV2Strategy` 基础上，继续验证 long 侧能否通过统一过滤减少误判。

本轮仍然不做单币特判。

新增 long 验证分支：

1. `DualTrendCombinedGlobalV2LongRejectClearDowntrendStrategy`
2. `DualTrendCombinedGlobalV2LongRequire4hTrendStrategy`
3. `DualTrendCombinedGlobalV2LongRequireLegacyCenterUpStrategy`
4. `DualTrendCombinedGlobalV2LongRsi60Strategy`

### 24.1 验证逻辑

#### A. LongRejectClearDowntrend

拒绝明显逆 1D legacy center 的 long：

```text
legacy_center_down_1d = True
close < legacy_market_center_1d
```

#### B. LongRequire4hTrend

要求 long 入场时：

```text
trend_up_4h = True
```

#### C. LongRequireLegacyCenterUp

要求 long 入场时：

```text
legacy_center_up_1d = True
close > legacy_market_center_1d
```

#### D. LongRsi60

把 long 侧 RSI 门槛继续从 `58` 提高到 `60`。

## 25. Long 过滤结果

### 25.1 1 年样本：2025-05-07 至 2026-05-07

| 版本 | Trades | Profit | PF | MaxDD | Winrate | Long Trades | Long Profit |
|---|---:|---:|---:|---:|---:|---:|---:|
| GlobalV2 | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% | 23 | +124.70U |
| LongRejectClearDowntrend | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% | 23 | +124.70U |
| LongRequire4hTrend | 115 | +164.65U / +16.46% | 1.35 | 7.96% | 33.04% | 0 | 0.00U |
| LongRequireLegacyCenterUp | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% | 23 | +124.70U |
| LongRsi60 | 138 | +304.65U / +30.47% | 1.50 | 8.54% | 33.33% | 23 | +124.70U |

### 25.2 3 年样本：2023-05-14 至 2026-05-07

| 版本 | Trades | Profit | PF | MaxDD | Winrate | Long Trades | Long Profit |
|---|---:|---:|---:|---:|---:|---:|---:|
| GlobalV2 | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% | 67 | +472.45U |
| LongRejectClearDowntrend | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% | 67 | +472.45U |
| LongRequire4hTrend | 291 | +740.17U / +74.02% | 1.50 | 8.05% | 31.27% | 0 | 0.00U |
| LongRequireLegacyCenterUp | 356 | +1421.72U / +142.17% | 1.62 | 8.63% | 31.74% | 67 | +472.45U |
| LongRsi60 | 353 | +1381.73U / +138.17% | 1.62 | 8.62% | 31.73% | 64 | +451.30U |

## 26. Long 过滤结论

### 26.1 无效但不伤的过滤

以下两个过滤没有改变结果：

1. `LongRejectClearDowntrend`
2. `LongRequireLegacyCenterUp`

这说明当前 `long_1d_center_compression` 入场本身已经天然满足这些 1D legacy center 条件。

所以它们没有必要并入主策略，因为加了也不产生实际过滤效果。

### 26.2 Require4hTrend 过度过滤

`LongRequire4hTrend` 会把 long 交易全部过滤掉：

```text
1 年 long trades: 23 -> 0
3 年 long trades: 67 -> 0
```

结果：

1 年收益从 `+30.47%` 掉到 `+16.46%`；
3 年收益从 `+142.17%` 掉到 `+74.02%`。

结论：

这说明 `long_1d_center_compression` 的盈利并不依赖当下 4H 已经完全转强。它更像是日线结构启动早期信号，如果强行要求 4H trend_up，反而会错过核心利润。

这条线不建议继续。

### 26.3 RSI 60 略微变差

`LongRsi60` 在 1 年样本无变化，在 3 年样本少了 3 笔 long：

```text
67 trades / +472.45U -> 64 trades / +451.30U
```

总收益从：

```text
+142.17% -> +138.17%
```

PF 基本不变，回撤也基本不变。

结论：

RSI 58 已经比较合适，继续提高到 60 没有带来质量改善。

## 27. 当前主候选更新

当前建议保留的正式 combined 主候选是：

```text
DualTrendCombinedGlobalV2Strategy
```

保留内容：

1. `long_daily_rsi = 58`
2. short 侧 `reject_clear_uptrend_all`

暂不并入：

1. `LongRejectClearDowntrend`
2. `LongRequire4hTrend`
3. `LongRequireLegacyCenterUp`
4. `LongRsi60`

原因：

这些 long 过滤要么没有实际过滤效果，要么明显砍掉有效利润。

## 28. 下一步建议

如果继续优化 long，不建议继续加这种趋势确认型硬过滤。

更值得做的是：

1. 按交易结果诊断 `long_1d_center_compression` 的亏损单；
2. 重点看亏损是否集中在：
   - 入场后很快跌回 1D center 下方
   - 结构止损太近或太远
   - 突破后未能在 N 天内推进
   - 高位追涨后回落
3. 然后再决定是做：
   - 早失败退出
   - 更精细的风险距离过滤
   - 或者只限制 long 的可交易币池

目前从这轮验证看，long 侧不能靠简单趋势过滤继续提升。下一步应该先做亏损画像，再动规则。
