# DualTrend Compression Close Quality Validation

日期：2026-07-06

## 本轮目标

不改核心入场逻辑，只对 `short_compression_breakdown` 增加两条极轻量的前置过滤验证：

1. `DualTrendCompressionCloseQualityGuardStrategy`
   - 仅过滤 `close_not_low_enough=True`
2. `DualTrendCompressionCloseQualityOversoldGuardStrategy`
   - 过滤 `close_not_low_enough=True`
   - 且短线已有超跌：
     - `prev_3h_return <= -0.004` 或
     - `prev_6h_return <= -0.008`

对照基线：

- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

基线参考值：

- 3年：`155.07% / PF 2.22 / MaxDD 5.77% / Trades 335 / Winrate 52.8%`
- 压力期：`1.91% / PF 1.38 / MaxDD 3.30% / Trades 20 / Winrate 35.0%`

## 本轮完成内容

1. 在 `DualTrendMainStrategies.py` 中新增两组仅针对 `short_compression_breakdown` 的轻量过滤开关。
2. 新增两个研究策略：
   - `DualTrendCompressionCloseQualityGuardStrategy`
   - `DualTrendCompressionCloseQualityOversoldGuardStrategy`
3. 使用 docker 回测：
   - 3年：`2023-06-18 -> 2026-06-18`
   - 压力期：`2026-03-01 -> 2026-05-31`

## 回测结果

### 3年样本

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 335 | 155.07% | 2.22 | 5.77% | 52.8% |
| Close Quality | 324 | 153.51% | 2.29 | 4.84% | 52.5% |
| Close Quality + Oversold | 328 | 155.62% | 2.26 | 4.83% | 52.4% |

### 压力期

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 20 | 1.91% | 1.38 | 3.30% | 35.0% |
| Close Quality | 18 | 2.69% | 1.64 | 2.53% | 33.3% |
| Close Quality + Oversold | 20 | 1.91% | 1.38 | 3.30% | 35.0% |

## 结果解读

### 1. Close Quality 单独过滤是有效的

`DualTrendCompressionCloseQualityGuardStrategy` 的表现：

- 3年收益只比基线少 `1.56` 个百分点
- PF 从 `2.22` 提升到 `2.29`
- MaxDD 从 `5.77%` 降到 `4.84%`
- 压力期从 `1.91%` 提升到 `2.69%`
- 压力期 MaxDD 从 `3.30%` 降到 `2.53%`

这说明：

- `close_not_low_enough` 这条特征确实有信息量
- 它不像之前的大范围 momentum/ATR guard 那样误杀过重
- 是目前这条线上第一次看到“风报比改善比较干净”的轻过滤

### 2. 再叠超跌条件，反而把优势吃掉了

`DualTrendCompressionCloseQualityOversoldGuardStrategy`：

- 3年收益回到 `155.62%`
- PF 也还不错 `2.26`
- 但压力期完全退回基线：
  - `1.91% / PF 1.38 / MaxDD 3.30%`

这说明：

- “close 不够低”本身已经能抓到一部分坏 breakdown
- 再叠 `prev_3h/6h` 超跌条件后，过滤变得过于保守
- 导致真正想砍掉的压力期坏单又被放回来了

## 按 tag 看

### Close Quality

- `short_compression_breakdown`
  - 从基线 `26.76%` 变为 `26.17%`
- `short_pullback_restart`
  - 从基线 `75.49%` 变为 `75.30%`
- `long_1d_center_compression`
  - 从基线 `52.82%` 变为 `52.04%`

这说明：

- 影响主要集中在 `short_compression_breakdown`
- 其它 tag 基本没被明显破坏
- 很符合“局部提纯”的设计目标

### Close Quality + Oversold

- `short_compression_breakdown`
  - `26.86%`

这版虽然 3年利润略高于基线，但压力期没有改善，因此不如单独 Close Quality 有实战意义。

## 本轮结论

### 当前最值得保留的候选

- `DualTrendCompressionCloseQualityGuardStrategy`

### 为什么

因为它满足了一个比较难得的组合：

1. 3年收益基本持平
2. PF 提升
3. MaxDD 明显下降
4. 压力期收益提升
5. 压力期回撤下降

### 不建议保留的候选

- `DualTrendCompressionCloseQualityOversoldGuardStrategy`

原因：

- 虽然 3年表面利润更高一点
- 但它没有保住压力期优势
- 对这轮研究目标来说，不如单独 Close Quality 有价值

## 下一步建议

当前可以进入下一轮 very-light 主线验证的，是：

- 保留 `DualTrendCompressionCloseQualityGuardStrategy`

下一步如果继续优化，建议只做两种小动作之一：

1. 对 `close_not_low_enough` 阈值做极小范围微调
   - 例如 `close_position > 0.28 / 0.30 / 0.32`
2. 保持这条过滤不动，转去研究 stop / add-on / reduce 的其它层面

当前不建议再把：

- `prev_3h/6h`
- `ATR`
- `compression_width`

这类条件重新大范围叠回去。
