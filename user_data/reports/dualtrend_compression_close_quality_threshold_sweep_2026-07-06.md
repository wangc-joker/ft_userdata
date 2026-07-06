# DualTrend Compression Close Quality Threshold Sweep

日期：2026-07-06

## 目的

在不修改入场主逻辑的前提下，只调整 `short_compression_breakdown` 的坏信号过滤阈值：

- 拒绝条件：`close_position > threshold`
- 比较阈值：`0.28 / 0.30 / 0.32`

基准策略：

- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

候选策略：

- `DualTrendCompressionCloseQualityGuard028Strategy`
- `DualTrendCompressionCloseQualityGuardStrategy` (`0.30`)
- `DualTrendCompressionCloseQualityGuard032Strategy`

## 回测设置

- 币池：Positive13
- `max_open_trades = 3`
- 主周期：`1h`
- 细节周期：`5m`
- Docker Freqtrade 回测

样本区间：

1. 三年：`2023-06-18 -> 2026-06-18`
2. 压力期：`2026-03-01 -> 2026-05-31`

## 基线结果

### DualTrendRawBreakevenGuardStrongRunnerStructureStrategy

三年：

- Trades: `335`
- Profit: `155.07%`
- PF: `2.22`
- MaxDD: `5.77%`
- Winrate: `52.8%`

压力期：

- Trades: `20`
- Profit: `1.91%`
- PF: `1.38`
- MaxDD: `3.30%`
- Winrate: `35.0%`

## 阈值对照结果

### 1. threshold = 0.28

策略：`DualTrendCompressionCloseQualityGuard028Strategy`

三年：

- Trades: `319`
- Profit: `161.02%`
- PF: `2.42`
- MaxDD: `5.05%`
- Winrate: `53.3%`

按 tag：

- `short_pullback_restart`: `78.83%`
- `long_1d_center_compression`: `51.97%`
- `short_compression_breakdown`: `30.22%`

压力期：

- Trades: `16`
- Profit: `3.99%`
- PF: `2.37`
- MaxDD: `1.53%`
- Winrate: `37.5%`

按 tag：

- `short_pullback_restart`: `3.61%`
- `short_compression_breakdown`: `1.02%`
- `long_1d_center_compression`: `-0.64%`

### 2. threshold = 0.30

策略：`DualTrendCompressionCloseQualityGuardStrategy`

三年：

- Trades: `324`
- Profit: `153.51%`
- PF: `2.29`
- MaxDD: `4.84%`
- Winrate: `52.5%`

压力期：

- Trades: `18`
- Profit: `2.69%`
- PF: `1.64`
- MaxDD: `2.53%`
- Winrate: `33.3%`

### 3. threshold = 0.32

策略：`DualTrendCompressionCloseQualityGuard032Strategy`

三年：

- Trades: `326`
- Profit: `150.31%`
- PF: `2.24`
- MaxDD: `4.84%`
- Winrate: `52.1%`

按 tag：

- `short_pullback_restart`: `75.88%`
- `long_1d_center_compression`: `52.07%`
- `short_compression_breakdown`: `22.36%`

压力期：

- Trades: `19`
- Profit: `1.88%`
- PF: `1.38`
- MaxDD: `3.30%`
- Winrate: `31.6%`

按 tag：

- `short_pullback_restart`: `3.57%`
- `short_compression_breakdown`: `-1.05%`
- `long_1d_center_compression`: `-0.64%`

## 结论

本轮阈值扫描中，`0.28` 明显最好。

相对基线：

- 三年收益：`155.07% -> 161.02%`
- 三年 PF：`2.22 -> 2.42`
- 三年 MaxDD：`5.77% -> 5.05%`
- 压力期收益：`1.91% -> 3.99%`
- 压力期 PF：`1.38 -> 2.37`
- 压力期 MaxDD：`3.30% -> 1.53%`

解释：

1. `0.32` 太松，坏 breakdown 过滤不够，压力期优势基本丢失。
2. `0.30` 有改善，但幅度一般。
3. `0.28` 说明对“跌破后收盘不够低”的要求再严格一点，能更有效过滤假跌破与快速反抽。

## 当前建议

如果继续沿着 close-quality 这一支做优化，优先采用：

- `DualTrendCompressionCloseQualityGuard028Strategy`

暂不建议保留：

- `0.32` 版本

`0.30` 可以作为次优参考，但不应作为当前主候选。
