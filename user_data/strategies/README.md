# 策略目录说明

## 当前正式基线

- `CombinedTrendCaptureMilestoneV2Strategy.py`
  - 当前表现最好的冻结版本。
  - 后续回测、dry-run、继续验证时，优先使用这个版本。

## 当前主线依赖链

- `CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy.py`
  - Milestone V2 的直接父版本逻辑。
- `CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy.py`
  - 加权版本，尚未加入 short 质量过滤。
- `CombinedTrendCaptureMilestoneV1Top8Strategy.py`
  - 8 币扩展层。
- `CombinedTrendCaptureMilestoneV1Strategy.py`
  - 更早期冻结的里程碑版本。
- `CombinedTrendCaptureNoLongTriangleStrategy.py`
  - 去掉弱势 `long_1d_triangle` 分支后的版本。
- `CombinedTrendCaptureOptStrategy.py`
  - 带参数化能力的策略层。
- `DoubleShunStrategy.py`
  - 核心指标、止损和退出逻辑基础。

## 里程碑说明

- `CombinedTrendCaptureMilestoneV1.md`
  - 早期里程碑说明。
- `CombinedTrendCaptureMilestoneV2.md`
  - 当前最优里程碑说明。

## 参考策略

- `BestLongTrendFollowingStrategy.py`
  - 主要的多头趋势参考策略。
- `CombinedTrendCaptureStrategy.py`
  - 更早期的组合趋势捕捉基线。

## 旧参考 / 可选保留

- `DoubleShunStrategy5m1h.py`
- `DoubleShunStrategyWithETH.py`
- `QuantEdgeStrategy.py`
- `ShortTrendCaptureStrategy.py`
- `SpotMTFMomentumStrategy.py`

这些文件目前只作为旧版本参考保留，不属于当前主线。
