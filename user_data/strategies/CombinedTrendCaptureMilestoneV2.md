# CombinedTrendCapture 里程碑 V2

这是在 8 币 futures 主线基础上继续改进后冻结下来的当前正式基线，主要改进包括：

- 分支级仓位加权
- 基于已有日线趋势结构，对 `short_1h_center` 做质量过滤

策略文件：
- `CombinedTrendCaptureMilestoneV2Strategy`

来源基线：
- `CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy`

关键决策：
- 提高 `long_1d_center_compression` 的仓位权重
- 适度提高 `short_1d_center_compression` 的仓位权重
- 下调 `short_1h_center` 的仓位权重
- 只有当日线空头动能和日线下行斜率同时确认时，才保留 `short_1h_center`

回测结果：
- 全区间 `2021-04-17 -> 2026-04-04`
- 总收益 `122.52%`
- CAGR `17.47%`
- 最大回撤 `8.93%`
- 交易数 `327`

对比基线：
- V1 Top8 Weighted Aggressive：`120.10%`，CAGR `17.21%`，最大回撤 `8.97%`
- V2：`122.52%`，CAGR `17.47%`，最大回撤 `8.93%`

用途：
- 作为当前稳定、可复现的正式检查点，在继续做后续优化前优先保留。
