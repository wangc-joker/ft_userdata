# DualTrend Guard028 结构止损验证

日期：2026-07-06

## 本轮目标

在不修改入场逻辑的前提下，研究 `DualTrendCompressionCloseQualityGuard028Strategy`
是否可以通过 **tag-specific structured stoploss** 进一步优化。

原则：

1. 不改入场
2. 不改 pair pool
3. 不改 `max_open_trades`
4. 不改已有的主止盈框架
5. 只改 short 两类 tag 的 stop 宽窄

## 基线

- `DualTrendCompressionCloseQualityGuard028Strategy`

三年基线：

- Profit: `161.02%`
- PF: `2.42`
- MaxDD: `5.05%`
- Winrate: `53.3%`
- Trades: `319`

## 研究思路

当前 short 两类单本质区别：

1. `short_pullback_restart`
   - 更像趋势中的二次转弱
   - 理论上可以容忍略大一点波动

2. `short_compression_breakdown`
   - 更像压缩后跌破
   - 假跌破概率更高
   - 理论上可以用更紧 stop

因此测试 3 个方向：

### A. Compression Tight

- `short_compression_breakdown` 止损更紧
- `short_pullback_restart` 保持原样

策略：

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

### B. Pullback Wide + Compression Tight

- `short_pullback_restart` 略放宽
- `short_compression_breakdown` 更紧

策略：

- `DualTrendCompressionCloseQualityGuard028PullbackWideCompressionTightStopStrategy`

### C. Pullback Wide Only

- 只放宽 `short_pullback_restart`
- `short_compression_breakdown` 保持原样

策略：

- `DualTrendCompressionCloseQualityGuard028PullbackWideStopStrategy`

## 三年回测

区间：

- `2023-06-18 -> 2026-06-18`

### 基线

- `DualTrendCompressionCloseQualityGuard028Strategy`
- Profit: `161.02%`
- PF: `2.42`
- MaxDD: `5.05%`
- Winrate: `53.3%`
- Trades: `319`

### A. Compression Tight

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`
- Profit: `162.46%`
- PF: `2.44`
- MaxDD: `5.05%`
- Winrate: `53.3%`
- Trades: `319`

观察：

- 收益小幅提升
- PF 小幅提升
- 回撤基本持平
- 主要改善来自 `short_compression_breakdown`
  - tag 收益：`30.22% -> 31.20%`

### B. Pullback Wide + Compression Tight

- `DualTrendCompressionCloseQualityGuard028PullbackWideCompressionTightStopStrategy`
- Profit: `161.45%`
- PF: `2.43`
- MaxDD: `8.46%`
- Winrate: `53.4%`
- Trades: `320`

观察：

- 收益基本持平
- PF 变化不大
- 回撤显著恶化

### C. Pullback Wide Only

- `DualTrendCompressionCloseQualityGuard028PullbackWideStopStrategy`
- Profit: `159.12%`
- PF: `2.40`
- MaxDD: `8.48%`
- Winrate: `53.4%`
- Trades: `320`

观察：

- 收益略降
- PF 略降
- 回撤显著恶化

## 结论

本轮最值得保留的是：

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

原因：

1. 它是唯一一个在三年样本里同时做到：
   - 收益略增
   - PF 略增
   - MaxDD 不恶化
2. 它的改善符合逻辑：
   - `short_compression_breakdown` 更怕假跌破
   - 因此紧一点的结构 stop 是合理的

不建议保留：

- `DualTrendCompressionCloseQualityGuard028PullbackWideCompressionTightStopStrategy`
- `DualTrendCompressionCloseQualityGuard028PullbackWideStopStrategy`

原因：

- 两者都把回撤从约 `5%` 拉高到 `8.4%+`
- 不符合当前主线“稳健优先”的要求

## 补充验证

在三年结果可接受后，又补跑了两个更敏感的样本，确认它不是只在长样本里“看起来更好”。

### 近一年

区间：

- `2025-06-18 -> 2026-06-18`

| Strategy | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `DualTrendCompressionCloseQualityGuard028Strategy` | 129 | 56.28% | 2.96 | 4.09% | 57.36% |
| `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy` | 129 | 56.69% | 2.99 | 4.05% | 57.36% |

观察：

1. 候选版依旧小幅领先
2. 收益 `+0.41pct`
3. PF `+0.03`
4. MaxDD `-0.04pct`
5. 交易数和胜率完全一致，说明改善主要来自出场质量而不是少做单

### 压力期

区间：

- `2026-03-01 -> 2026-05-31`

| Strategy | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `DualTrendCompressionCloseQualityGuard028Strategy` | 16 | 3.99% | 2.37 | 1.53% | 37.50% |
| `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy` | 16 | 4.01% | 2.39 | 1.51% | 37.50% |

观察：

1. 压力期没有恶化
2. 收益 `+0.02pct`
3. PF `+0.02`
4. MaxDD `-0.02pct`

## 当前建议

主线可以考虑从：

- `DualTrendCompressionCloseQualityGuard028Strategy`

升级为候选：

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

原因：

1. 三年样本略优
2. 近一年样本略优
3. 压力期不恶化
4. 回撤没有被放大
5. 改动范围非常克制，只动了 `short_compression_breakdown` 的结构止损

因此，这个版本已经可以视为 `Guard028` 主线的下一版 short 主候选。
