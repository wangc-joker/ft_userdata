# CombinedTrendCapture 里程碑 V1

这是继续做后续实验前冻结下来的早期稳定基线。

策略文件：
- `CombinedTrendCaptureMilestoneV1Strategy`

来源基线：
- `CombinedTrendCaptureNoLongTriangleStrategy`

关键决策：
- 关闭 `long_1d_triangle`

回测结果：
- 全区间 `2023-01-11 -> 2026-04-04`
- 总收益 `80.86%`
- CAGR `20.13%`
- 最大回撤 `6.00%`
- 交易数 `100`

验证区间结果：
- 验证区间 `2025-07-01 -> 2026-04-04`
- 总收益 `41.57%`
- CAGR `58.10%`
- 最大回撤 `1.33%`
- 交易数 `34`

用途：
- 作为一个稳定、可复现的检查点，在继续探索更低过拟合风险的版本时使用。
