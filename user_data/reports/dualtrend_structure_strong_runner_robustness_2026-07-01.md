# DualTrend 结构型强单放行稳健性验证

日期: 2026-07-01

## 目的

验证前两年表现较好的 `Structure Strong Runner` 分支，是否在更长周期下仍然成立。

验证对象:

- `DualTrendBaselineStrategy`
- `DualTrendBaselineStrongRunnerStructureStrategy`
- `DualTrendGuardStrategy`
- `DualTrendGuardStrongRunnerStructureStrategy`

## 结构分支规则

仅作用于 `short_pullback_restart`，且只在订单先达到 `+5%` 浮盈后判断。

继续放行的条件:

- `adverse_before_5 <= 1.25%`
- `pair_1h_ret_6h <= -2%`
- `pair_4h_ema50_slope_3 <= -0.5%`

## 回测口径

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 周期: `1h + 5m detail`
- 模式: Binance Futures, isolated

样本:

1. 前两年: `2022-11-11 16:00:00 -> 2024-11-11 00:00:00`
2. 三年: `2023-06-18 00:00:00 -> 2026-06-18 00:00:00`
3. 全可用样本: `2022-11-11 16:00:00 -> 2026-06-30 00:00:00`

## 结果总表

| 样本 | 策略 | 收益率 | PF | MaxDD | Trades | Winrate |
|---|---|---:|---:|---:|---:|---:|
| 前两年 | Baseline | 51.39% | 1.7580 | 7.91% | 218 | 46.33% |
| 前两年 | Baseline Structure | 53.48% | 1.7602 | 7.18% | 225 | 48.44% |
| 前两年 | Guard | 55.27% | 1.8495 | 7.91% | 213 | 46.48% |
| 前两年 | Guard Structure | 57.39% | 1.8487 | 7.05% | 220 | 48.64% |
| 三年 | Baseline | 149.59% | 2.0223 | 4.92% | 399 | 47.62% |
| 三年 | Baseline Structure | 143.15% | 1.9528 | 4.94% | 409 | 50.12% |
| 三年 | Guard | 157.61% | 2.0846 | 4.91% | 391 | 47.83% |
| 三年 | Guard Structure | 152.10% | 2.0152 | 4.92% | 402 | 50.25% |
| 全样本 | Baseline | 178.35% | 1.9999 | 4.87% | 462 | 48.05% |
| 全样本 | Baseline Structure | 170.22% | 1.9308 | 4.88% | 474 | 50.00% |
| 全样本 | Guard | 187.28% | 2.0583 | 4.94% | 454 | 48.24% |
| 全样本 | Guard Structure | 179.19% | 1.9842 | 4.87% | 466 | 50.43% |

## 核心结论

### 1. 前两年有效，但不稳健

前两年里，结构分支确实优于父策略：

- `Baseline Structure` 比 `Baseline` 高 `+2.09%`
- `Guard Structure` 比 `Guard` 高 `+2.12%`

但一拉长周期，这个优势消失了。

### 2. 三年样本开始转弱

#### Baseline

- `149.59% -> 143.15%`
- 少了 `6.44%`
- PF 也从 `2.0223` 降到 `1.9528`

#### Guard

- `157.61% -> 152.10%`
- 少了 `5.51%`
- PF 从 `2.0846` 降到 `2.0152`

虽然结构分支的胜率更高，但收益和 PF 都掉了。

### 3. 全样本也没打赢父策略

#### Baseline

- `178.35% -> 170.22%`
- 少了 `8.13%`

#### Guard

- `187.28% -> 179.19%`
- 少了 `8.09%`

也就是说，这不是三年偶然失效，而是在更长样本里同样没有保住优势。

## 为什么会这样

从 tag 拆解上看，问题很集中。

### 三年样本

#### Baseline

- `short_pullback_restart`: `806.81 -> 761.02`
- `short_compression_breakdown`: `167.63 -> 154.85`
- `long_1d_center_compression`: `521.44 -> 515.68`

#### Guard

- `short_pullback_restart`: `827.61 -> 786.49`
- `short_compression_breakdown`: `220.97 -> 208.84`
- `long_1d_center_compression`: `527.49 -> 525.63`

### 全样本

#### Baseline

- `short_pullback_restart`: `1034.52 -> 987.59`
- `short_compression_breakdown`: `160.17 -> 134.40`
- `long_1d_center_compression`: `588.85 -> 580.18`

#### Guard

- `short_pullback_restart`: `1055.29 -> 1008.71`
- `short_compression_breakdown`: `218.17 -> 191.90`
- `long_1d_center_compression`: `599.32 -> 591.28`

结论很直接：

- 结构分支虽然提高了 `short_pullback_restart` 的命中率
- 但它削掉了更多真正的大利润空单
- 同时也顺带拖弱了 `short_compression_breakdown`
- long 侧基本不是主要矛盾

也就是说，它在“看起来更像真强单”的地方，还是卡得偏窄了。

## 这次验证说明了什么

### 正面

- `+5%` 节点结构确实有信息量
- 这条思路不是完全错
- 它稳定提高了 winrate

### 负面

- 当前阈值版不具备跨周期稳健性
- 它更像“局部阶段适配”
- 还不够资格替换主策略

## 是否升级主线

当前结论：**不建议升级。**

主线仍保持:

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

其中综合主候选仍然是:

- `DualTrendGuardStrategy`

## 后续建议

下一步如果还要继续做“强单放行”，不要直接保留这版阈值。

更稳妥的方向是：

1. 回到 `Guard` 主线，不切换策略。
2. 如果继续研究，只做很小范围微调：
   - 放宽 `ret_6h`
   - 放宽 `4h ema50 slope`
   - 只测 `Guard`，不要同时扩两条线
3. 如果不想继续消耗回测预算，这条分支可以先停。

## 最终结论

`Structure Strong Runner` 的前两年结果是有效信号，但不是稳健信号。

它在更长周期上：

- 提高了 winrate
- 没有降低长期回撤多少
- 反而削弱了总收益和 PF

所以当前最合理的决定是：

- 保留研究记录
- 不并入主策略
- 主线继续用 `DualTrendGuardStrategy`
