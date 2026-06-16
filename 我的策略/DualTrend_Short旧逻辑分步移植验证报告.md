# DualTrend Short 旧逻辑分步移植验证报告

日期：2026-06-16

## 1. 本次做了什么

新增验证策略文件：

`D:\test\ft_userdata\user_data\strategies\DualTrendShortLegacyBorrowV1Strategy.py`

本次没有修改当前主策略 `DualTrendCompressionRestartShortV1Strategy` 的核心入场逻辑，而是做了两层验证：

1. 独立验证旧 short tag；
2. 作为附加入口挂到当前 Short V1 上，观察是否提升主策略。

新增主要验证类：

| 类 | 作用 |
|---|---|
| `DualTrendShortReversalBreakdownV1Strategy` | 独立验证 `short_reversal_breakdown` |
| `DualTrendShortReversalBreakdownOldPairsV1Strategy` | 只测旧表现较好的 ZEC/ADA/XRP |
| `DualTrendShortDailyCenterV1Strategy` | 独立验证 `short_1d_center_compression` |
| `DualTrendShortHourlyCenterV1Strategy` | 独立验证 `short_1h_center` |
| `DualTrendShortV1PlusDailyCenterV1Strategy` | 当前 Short V1 + borrow daily center |
| `DualTrendShortV1PlusReversalV1Strategy` | 当前 Short V1 + borrow reversal |
| `DualTrendShortV1PlusDailyCenterReversalV1Strategy` | 当前 Short V1 + 两者都加 |

## 2. 独立验证结果

### 2.1 13 币池

| 版本 | 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| `short_reversal_breakdown` | 全样本 | 27 | +95.61U / +9.56% | 1.64 | 6.07% | 29.6% |
| `short_reversal_breakdown` | 近期 | 20 | +63.64U / +6.36% | 1.54 | 6.07% | 30.4% |
| `short_1d_center_compression` | 全样本 | 28 | +369.69U / +36.97% | 2.85 | 4.59% | 39.3% |
| `short_1d_center_compression` | 近期 | 16 | +217.20U / +21.72% | 3.07 | 4.59% | 50.0% |
| `short_1h_center` | 全样本 | 218 | +100.10U / +10.01% | 1.08 | 28.98% | 32.1% |
| `short_1h_center` | 近期 | 136 | -28.04U / -2.80% | 0.96 | 25.44% | 30.1% |

### 2.2 旧 Top9 币池

| 版本 | 样本 | Trades | Profit | PF | MaxDD |
|---|---|---:|---:|---:|---:|
| `short_1d_center_compression` | 全样本 | 24 | +273.41U / +27.34% | 2.61 | 4.21% |
| `short_1h_center` | 全样本 | 139 | +350.36U / +35.04% | 1.43 | 18.95% |

### 2.3 旧 reversal 三币池

| 版本 | 样本 | Trades | Profit | PF | MaxDD |
|---|---|---:|---:|---:|---:|
| ZEC/ADA/XRP `short_reversal_breakdown` | 全样本 | 13 | +100.96U / +10.10% | 2.64 | 3.52% |

## 3. 独立验证判断

### `short_1d_center_compression`

独立表现最好。

特点：

1. 低频；
2. PF 高；
3. 回撤低；
4. 近期仍有效；
5. 更像大级别趋势段，不像噪音信号。

但它和当前 Short V1 的交易节奏不同，不能粗暴混进同一个资金槽位。

### `short_reversal_breakdown`

仍然为正，但复刻成独立策略后没有旧回测里那么亮。

原因：

1. 旧策略有父类 stake/exit/组合环境；
2. 旧结果里 `short_reversal_breakdown` 的收益被整体策略环境放大；
3. 新版独立复刻后，它更像一个小型补充信号。

优点是回撤不大，近期也为正。

### `short_1h_center`

不适合迁移。

13 币池下：

```text
全样本 PF 1.08
近期 PF 0.96
MaxDD 25%+
```

说明裸 `short_1h_center` 在当前币池里会带来大量噪音。它只适合借鉴 `market_center` 和 early-fail 思想，不适合作为新入口。

## 4. 挂到当前 Short V1 后的结果

样本：13 币池，max_open_trades=3。

### 全样本

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 当前 Short V1 基线 | 298 | +825.67U / +82.57% | 1.52 | 10.15% | 32.2% |
| + daily center | 406 | +587.73U / +58.77% | 1.29 | 13.53% | 27.3% |
| + reversal | 424 | +850.25U / +85.02% | 1.36 | 11.95% | 28.8% |
| + daily center + reversal | 424 | +764.91U / +76.49% | 1.34 | 13.79% | 28.5% |

### 近期

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 当前 Short V1 基线 | 171 | +391.54U / +39.15% | 1.48 | 9.32% | 33.9% |
| + daily center | 219 | +377.23U / +37.72% | 1.34 | 11.29% | 28.8% |
| + reversal | 230 | +478.89U / +47.89% | 1.40 | 11.71% | 30.4% |
| + daily center + reversal | 230 | +478.89U / +47.89% | 1.40 | 11.71% | 30.4% |

## 5. 为什么 daily center 独立好，合并反而差

原因不是信号本身坏，而是资金槽位和主策略冲突。

独立版 `short_1d_center_compression`：

```text
28 trades
+369.69U
PF 2.85
MaxDD 4.59%
```

但合并后：

```text
当前 Short V1 原有入口交易数量从 298 增到 406
总 PF 从 1.52 降到 1.29
MaxDD 从 10.15% 升到 13.53%
```

说明直接混入当前策略后，它可能改变了资金占用、保护触发、后续入场序列，导致主线收益被扰动。

结论：

`short_1d_center_compression` 不适合直接合并进当前 Short V1；更适合独立 bot / 独立资金槽位测试。

## 6. reversal 合并后的判断

`short_reversal_breakdown` 合并后：

全样本：

```text
收益：+825.67U -> +850.25U
PF：1.52 -> 1.36
MaxDD：10.15% -> 11.95%
```

近期：

```text
收益：+391.54U -> +478.89U
PF：1.48 -> 1.40
MaxDD：9.32% -> 11.71%
```

它能增加近期收益，但代价是 PF 和回撤变差。

结论：

不建议现在并入主策略。可以保留为候选，但需要再做过滤：

1. 只保留 ZEC/ADA/XRP/NEAR；
2. 去掉 LINK/TAO/SUI；
3. 加 BTC/日线市场状态过滤；
4. 或者独立 1 个小资金槽位。

## 7. 当前结论

### 不建议马上移植进主策略

1. `short_1h_center`
2. `short_1d_center_compression` 直接合并版
3. `short_reversal_breakdown` 直接合并版

### 值得继续保留验证

| 模块 | 推荐方式 |
|---|---|
| `short_1d_center_compression` | 独立 bot / 独立资金槽位，不挤占 Short V1 |
| `short_reversal_breakdown` | 小币池过滤后再合并或独立槽位 |
| `market_center` | 作为当前 Short V1 的质量过滤器，而不是新入口 |
| early-fail | 作为当前 Short V2 的退出过滤器 |

## 8. 下一步建议

下一步不要继续加入口，先做过滤验证：

1. `short_reversal_breakdown` 只保留正贡献 pair：
   - XRP
   - ZEC
   - ADA
   - NEAR
2. `short_1d_center_compression` 独立 bot 测：
   - 13 币池去掉 DOGE/TRX/ETH/ZEC
   - max_open_trades=1
   - max_open_trades=2
3. 对当前 Short V1 测 `market_center` 过滤：
   - 当前入口不变；
   - 只在 `market_center` 也向下时允许入场；
   - 或 `center_down` 与 `market_center_down` 至少二选一。

当前最稳的结论：

**不要把旧入口直接并入 Short V1。先保留当前 Short V1 主线，旧逻辑只作为独立候选和过滤器素材。**

## 9. 过滤后验证结果

本轮新增了 3 个候选策略类：

| 策略类 | 用途 |
|---|---|
| `DualTrendShortDailyCenterFilteredV1Strategy` | 只测过滤后的 `short_1d_center_compression` 独立入口 |
| `DualTrendShortReversalBreakdownPositivePairsV1Strategy` | 只测正贡献币种的 `short_reversal_breakdown` 独立入口 |
| `DualTrendShortV1PlusReversalPositivePairsV1Strategy` | 当前 Short V1 + 正贡献 reversal 入口 |

### 9.1 日线中枢压缩过滤版

过滤币池：

```text
BTC / BNB / SOL / XRP / ADA / LINK / NEAR / SUI / TAO
```

剔除：

```text
DOGE / TRX / ETH / ZEC
```

回测结果：

| 样本 | max_open_trades | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|---:|
| 全样本 2023-05-14 至 2026-05-07 | 1 | 13 | +710.33U / 71.03% | 5.46 | 4.07% | 53.8% |
| 近期 2025-01-01 至 2026-05-07 | 1 | 7 | +364.13U / 36.41% | 5.82 | 4.07% | 57.1% |
| 全样本 2023-05-14 至 2026-05-07 | 2 | 20 | +449.49U / 44.95% | 4.61 | 3.07% | 50.0% |
| 近期 2025-01-01 至 2026-05-07 | 2 | 11 | +256.67U / 25.67% | 5.23 | 3.07% | 54.5% |

pair 拆解要点：

| 版本 | 主要贡献 | 拖累 |
|---|---|---|
| max_open_trades=1 全样本 | XRP、TAO、SOL、BTC、BNB、ADA | NEAR |
| max_open_trades=1 近期 | TAO、BTC、SOL、BNB | NEAR、ADA |
| max_open_trades=2 全样本 | SOL、XRP、NEAR、TAO、BTC | BNB 贡献很弱 |
| max_open_trades=2 近期 | SOL、BTC、TAO、BNB、NEAR | ADA |

结论：

`short_1d_center_compression` 过滤后独立表现非常强，尤其 `max_open_trades=1`。但它交易频率很低，更像“高质量机会捕捉器”，不适合直接塞进 Short V1 主策略抢仓。建议后续作为独立 short bot / 独立资金槽位观察。

### 9.2 reversal 正贡献币种过滤版

过滤币池：

```text
XRP / ZEC / ADA / NEAR
```

独立回测结果：

| 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 全样本 2023-05-14 至 2026-05-07 | 17 | +132.92U | 2.63 | 3.52% | 35.3% |
| 近期 2025-01-01 至 2026-05-07 | 11 | +95.97U | 2.72 | 3.52% | 36.4% |

pair 拆解要点：

| 样本 | 主要贡献 |
|---|---|
| 全样本 | XRP、ADA、NEAR、ZEC 全部为正 |
| 近期 | ADA、NEAR、ZEC 为正，XRP 没有交易 |

结论：

过滤后 reversal 独立版本明显比原始 13 币池干净。它可以保留为独立候选，但交易数很少，不足以直接升级为主线。

### 9.3 reversal 过滤后合并进 Short V1

和当前 Short V1 基线对比：

| 版本 | 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| Short V1 基线 | 全样本 | 298 | +825.67U | 1.52 | 10.15% | 32.2% |
| + reversal 正贡献币种 | 全样本 | 416 | +762.94U | 1.34 | 11.27% | 28.4% |
| Short V1 基线 | 近期 | 171 | +391.54U | 1.48 | 9.32% | 33.9% |
| + reversal 正贡献币种 | 近期 | 224 | +459.32U | 1.39 | 11.32% | 29.9% |

合并版 entry_tag 拆解：

| 样本 | entry_tag | Trades | Profit | PF | Winrate |
|---|---|---:|---:|---:|---:|
| 全样本 | `short_pullback_restart` | 314 | +502.65U | 1.30 | 27.7% |
| 全样本 | `short_compression_breakdown` | 92 | +165.09U | 1.30 | 27.2% |
| 全样本 | `borrow_short_reversal` | 10 | +95.20U | 6.23 | 60.0% |
| 近期 | `short_pullback_restart` | 164 | +332.65U | 1.40 | 30.5% |
| 近期 | `short_compression_breakdown` | 55 | +66.42U | 1.20 | 23.6% |
| 近期 | `borrow_short_reversal` | 5 | +60.25U | 14.47 | 80.0% |

结论：

`borrow_short_reversal` 自身质量很高，但合并后会改变资金占用、保护触发和主线交易序列，导致全样本总收益下降、PF 下降、MaxDD 上升。近期收益提高，但代价仍然是 PF 与回撤变差。

因此不建议把 reversal 直接合并进当前 Short V1。

## 10. 当前移植建议

### 可以保留

1. `DualTrendShortDailyCenterFilteredV1Strategy`
   - 独立 short bot；
   - `max_open_trades=1` 优先；
   - 小资金槽位；
   - 不挤占 Short V1。

2. `DualTrendShortReversalBreakdownPositivePairsV1Strategy`
   - 独立观察；
   - 只保留 XRP/ZEC/ADA/NEAR；
   - 暂不并入主策略。

### 暂不移植

1. `short_1h_center`
2. `short_1d_center_compression` 直接合并版
3. `short_reversal_breakdown` 直接合并版
4. `short_reversal_breakdown` 过滤后合并版

### 下一步最合理

不要继续增加入口。下一步应该测试“过滤器借鉴”，尤其是旧策略里的：

1. `market_center` 方向过滤；
2. `1d_center` 环境过滤；
3. 入场后 early-fail 退出；
4. 独立日线中枢 bot 的 dry-run 配置。

当前主线判断不变：

**Short V1 主策略保持不动；旧策略中真正值得借鉴的是独立日线中枢机会和少数 reversal 信号，而不是把旧入口直接混进主策略。**

## 11. 过滤器验证：market_center / 1d_center / early-fail

本轮目标：

只验证旧策略中的过滤和退出思路，不新增旧入口，不改变 Short V1 的两个核心入场：

1. `short_pullback_restart`
2. `short_compression_breakdown`

新增验证策略文件：

```text
user_data/strategies/DualTrendShortV1FilterValidationStrategies.py
```

新增策略类：

| 策略类 | 验证内容 |
|---|---|
| `DualTrendShortV1MarketCenterFilterStrategy` | 1H legacy market_center 向下过滤 |
| `DualTrendShortV1DailyCenterFilterStrategy` | 1D legacy center 向下过滤 |
| `DualTrendShortV1MarketDailyCenterFilterStrategy` | 1H + 1D center 同时过滤 |
| `DualTrendShortV1EarlyFailExitStrategy` | 12h 内 center 反向的快速失败退出 |
| `DualTrendShortV1DailyCenterEarlyFailStrategy` | 1D center 过滤 + 激进 early-fail |
| `DualTrendShortV1EarlyFailLossOnly6hStrategy` | 6h 内且浮亏时 early-fail |
| `DualTrendShortV1DailyCenterEarlyFailLossOnly6hStrategy` | 1D center 过滤 + 保守 early-fail |

### 11.1 总结果对比

| 版本 | 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| Short V1 基线 | 全样本 | 298 | +825.67U / 82.57% | 1.52 | 9.35% | 32.2% |
| Short V1 基线 | 近期 | 171 | +391.54U / 39.15% | 1.48 | 9.32% | 33.9% |
| 1H market_center 过滤 | 全样本 | 296 | +799.91U / 79.99% | 1.51 | 9.07% | 32.4% |
| 1H market_center 过滤 | 近期 | 170 | +389.79U / 38.98% | 1.48 | 7.95% | 34.1% |
| 1D center 过滤 | 全样本 | 231 | +747.31U / 74.73% | 1.62 | 8.95% | 32.5% |
| 1D center 过滤 | 近期 | 132 | +328.85U / 32.88% | 1.53 | 8.99% | 34.1% |
| 1H + 1D center 过滤 | 全样本 | 228 | +724.81U / 72.48% | 1.61 | 8.61% | 32.9% |
| 1H + 1D center 过滤 | 近期 | 130 | +331.00U / 33.10% | 1.54 | 8.63% | 34.6% |
| 激进 early-fail | 全样本 | 362 | +570.02U / 57.00% | 1.43 | 9.72% | 26.2% |
| 激进 early-fail | 近期 | 211 | +272.36U / 27.24% | 1.38 | 9.71% | 28.4% |
| 保守 early-fail 6h 浮亏 | 全样本 | 313 | +920.04U / 92.00% | 1.59 | 12.45% | 30.4% |
| 保守 early-fail 6h 浮亏 | 近期 | 182 | +414.23U / 41.42% | 1.54 | 12.50% | 30.8% |
| 1D center + 激进 early-fail | 全样本 | 281 | +564.77U / 56.48% | 1.57 | 10.26% | 25.6% |
| 1D center + 激进 early-fail | 近期 | 162 | +287.70U / 28.77% | 1.55 | 10.23% | 28.4% |
| 1D center + 保守 early-fail | 全样本 | 245 | +797.13U / 79.71% | 1.68 | 10.69% | 30.6% |
| 1D center + 保守 early-fail | 近期 | 141 | +344.96U / 34.50% | 1.59 | 10.70% | 31.2% |

### 11.2 结论拆解

#### 1H market_center

影响很小：

```text
全样本：PF 1.52 -> 1.51，MaxDD 9.35% -> 9.07%
近期：PF 1.48 -> 1.48，MaxDD 9.32% -> 7.95%
```

它对近期回撤有帮助，但几乎不改变收益和 PF。说明 Short V1 当前已有的 1H `center_down` 已经覆盖了大部分同类信息，旧版 1H market_center 的新增价值有限。

结论：

不建议单独移植。

#### 1D center

这是本轮最稳的过滤器：

```text
全样本：PF 1.52 -> 1.62，MaxDD 9.35% -> 8.95%
近期：PF 1.48 -> 1.53，MaxDD 9.32% -> 8.99%
```

代价是交易数下降：

```text
全样本：298 -> 231
近期：171 -> 132
```

收益也下降：

```text
全样本：+825.67U -> +747.31U
近期：+391.54U -> +328.85U
```

这说明 1D center 是有效的质量过滤器，但不是收益增强器。它适合用在更保守的 dry-run / 实盘版本，目标是提高 PF 和降低假信号密度。

#### 1H + 1D center

组合后继续略降回撤：

```text
全样本 MaxDD：9.35% -> 8.61%
近期 MaxDD：9.32% -> 8.63%
```

但收益继续下降，PF 与 1D only 接近：

```text
全样本 PF：1.61
近期 PF：1.54
```

结论：

如果目标是降低回撤，1H + 1D center 可以作为候选；如果目标是保持收益，1D center only 更平衡。

#### early-fail

激进版明显失败：

```text
全样本：+825.67U -> +570.02U，PF 1.52 -> 1.43
近期：+391.54U -> +272.36U，PF 1.48 -> 1.38
```

保守 6h 浮亏版收益和 PF 提升：

```text
全样本：+920.04U，PF 1.59
近期：+414.23U，PF 1.54
```

但 MaxDD 明显变差：

```text
全样本 MaxDD：9.35% -> 12.45%
近期 MaxDD：9.32% -> 12.50%
```

原因是 early-fail 释放仓位后增加后续交易次数，收益提高，但资金曲线波动变大。它不是“稳健性优化”，更像是提高周转率的进攻型改动。

结论：

暂不建议并入主策略。

### 11.3 pair 变化

基线拖累：

```text
TRX：-65.23U
LINK：-60.21U
NEAR：-3.24U
```

1D center 后拖累：

```text
NEAR：-61.76U
TRX：-59.85U
ADA：+15.79U
```

1H + 1D center 后拖累：

```text
TRX：-53.89U
NEAR：-37.04U
ADA：-10.45U
```

观察：

1D center 明显改善了 LINK，但没有解决 TRX；NEAR 在 1D center 下反而变差。后续如果要继续稳健化，比继续加过滤器更直接的方式是做 pair 级别剔除，尤其关注 TRX / LINK / NEAR。

### 11.4 当前建议

不建议马上动主策略生产版本。

可以保留两个候选：

1. `DualTrendShortV1DailyCenterFilterStrategy`
   - 更平衡；
   - PF 提升；
   - 回撤略降；
   - 收益下降可接受。

2. `DualTrendShortV1MarketDailyCenterFilterStrategy`
   - 更保守；
   - 回撤最低；
   - 收益牺牲更多。

暂不建议保留：

1. 1H market_center 单独过滤；
2. 激进 early-fail；
3. 保守 early-fail 直接并入主策略。

下一步如果继续优化，建议不要再加形态，而是验证：

1. Short V1 + 1D center filter + 去掉 TRX；
2. Short V1 + 1D center filter + 去掉 TRX/LINK/NEAR；
3. Short V1 基线 + 去掉 TRX/LINK/NEAR；
4. 再比较是否 1D center 仍有必要。

## 12. Long Daily Center 与 Short V1 合并验证

用户问题：

`DualTrendLongDailyCenterV1Strategy.py` 里从旧策略拿过来的 `long_1d_center_compression`，能否和当前新 Short V1 合并成一个策略。

### 12.1 实现结论

可以合并，但不能直接多继承或简单复制入口。

关键原因：

当前 Short V1 的仓位 sizing 依赖：

```text
enter_initial_stop
enter_risk_pct
```

原 `DualTrendLongDailyCenterV1Strategy` 没有在入场 K 线上写入这两个字段。如果直接合并，Short V1 的 `custom_stake_amount()` 会认为风险字段缺失，从而拒绝开仓，或者造成止损/仓位逻辑错位。

已新增合并验证策略：

```text
user_data/strategies/DualTrendCombinedLongDailyCenterShortV1Strategy.py
```

包含 3 个类：

| 策略类 | 说明 |
|---|---|
| `DualTrendCombinedLongDailyCenterShortV1Strategy` | Short V1 + long daily center，全配置币池 |
| `DualTrendCombinedLongDailyCenterTop9ShortV1Strategy` | Short V1 + long daily center Top9 long 币池 |
| `DualTrendCombinedLongDailyCenterCore3ShortV1Strategy` | Short V1 + long daily center Core3 long 币池 |

合并方式：

1. Short 侧完整继承当前 `DualTrendCompressionRestartShortV1Strategy`；
2. Long 侧只加入 `long_1d_center_compression`；
3. Long 入场时单独计算：
   - `enter_initial_stop`
   - `enter_risk_pct`
4. `custom_stoploss()` 按 `trade.is_short` 分支：
   - short 使用原 Short V1 止损；
   - long 使用 long entry candle 的初始 stop；
5. `custom_exit()` 按 `trade.is_short` 分支：
   - short 使用原 Short V1 stale / trend flip；
   - long 使用旧 long daily center 的 1D 趋势/结构退出。

### 12.2 回测结果

使用配置：

```text
user_data/config.backtest.dualtrend.short_v1.1000u.max3.3y.json
max_open_trades = 3
```

对比基线：

| 版本 | 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| Short V1 基线 | 全样本 | 298 | +825.67U / 82.57% | 1.52 | 9.35% | 32.2% |
| Combined 全币池 | 全样本 | 353 | +1561.01U / 156.10% | 1.65 | 8.64% | 32.9% |
| Short V1 基线 | 近期 | 171 | +391.54U / 39.15% | 1.48 | 9.32% | 33.9% |
| Combined 全币池 | 近期 | 192 | +592.33U / 59.23% | 1.61 | 8.55% | 34.4% |

### 12.3 entry_tag 拆解

全样本：

| entry_tag | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| `long_1d_center_compression` | 57 | +572.37U | 2.52 | 36.8% |
| `short_pullback_restart` | 230 | +496.78U | 1.31 | 30.9% |
| `short_compression_breakdown` | 66 | +491.85U | 2.21 | 36.4% |
| TOTAL | 353 | +1561.01U | 1.65 | 32.9% |

近期：

| entry_tag | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| `long_1d_center_compression` | 21 | +179.18U | 2.73 | 38.1% |
| `short_pullback_restart` | 136 | +162.69U | 1.23 | 32.4% |
| `short_compression_breakdown` | 35 | +250.45U | 2.53 | 40.0% |
| TOTAL | 192 | +592.33U | 1.61 | 34.4% |

### 12.4 是否挤占 Short

全样本 short 交易数对比：

```text
Short V1 基线：
short_pullback_restart         231
short_compression_breakdown     67

Combined：
short_pullback_restart         230
short_compression_breakdown     66
```

近期 combined short：

```text
short_pullback_restart         136
short_compression_breakdown     35
```

观察：

合并后的 long 信号没有明显挤占 short 主线。全样本 short 交易数只少 2 笔，说明 `long_1d_center_compression` 和 Short V1 的高质量 short 信号大多不在同一时间抢槽位。

### 12.5 pair 拆解

全样本主要贡献：

```text
ETH +289.23U
ZEC +243.24U
BNB +221.57U
SOL +160.94U
ADA +155.55U
BTC +150.56U
```

全样本拖累：

```text
LINK -65.46U
NEAR -13.82U
```

近期主要贡献：

```text
ETH +152.62U
XRP +97.59U
SOL +76.35U
DOGE +65.24U
BTC +50.63U
ZEC +49.49U
```

近期拖累：

```text
LINK -41.11U
TRX -1.60U
```

### 12.6 当前判断

合并可行，而且这版是目前比单独 Short V1 更强的候选：

```text
全样本收益明显提升；
近期收益明显提升；
PF 提升；
MaxDD 下降；
short 主线没有明显被挤占。
```

当前建议：

1. 可以保留 `DualTrendCombinedLongDailyCenterShortV1Strategy` 作为 Combined V1 候选；
2. 暂时不要直接替换 dry-run 主策略；
3. 下一步先做：
   - Combined 去掉 LINK；
   - Combined 去掉 LINK/NEAR；
   - Combined max_open_trades = 3 / 4 / 5；
   - Combined 成本压力测试；
   - 检查同一 pair 是否会出现 long/short 接近时间反向冲突。

如果这些验证仍稳，Combined V1 才适合进入 dry-run。
