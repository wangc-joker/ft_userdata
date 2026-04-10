# 策略目录说明

## 当前正式候选

- `CombinedTrendCaptureMilestoneV2Strategy.py`
  - 原始 8 币 V2 冻结基线。
  - 适合继续作为总主线参考和最初的 dry-run 基线。
- `CombinedTrendCaptureMilestoneV2Top8ZecStrategy.py`
  - 稳健候选版。
  - 在原 8 币里用 `ZEC` 替换 `LINK`。
  - 特点是回撤控制更好，适合更看重稳健性的场景。
- `CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy.py`
  - 高收益平衡候选版。
  - 在 `Top9` 币池基础上，把 `long_1d_center_compression` 权重调到 `1.20`。
  - 特点是收益高于稳健版，但回撤也更高。
- `CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy.py`
  - `Top9` 平衡增强候选版。
  - 保留 `Top9 1.20` 的主逻辑，但单独降低 `DOGE` 仓位。
  - 特点是收益略低于 `Top9 1.20`，但回撤更低、Sharpe 更高。
- `CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy.py`
  - `Top9` 状态层稳健版。
  - 按 `1d` 区分牛市、熊市、震荡，并根据状态调整多空权重。
  - 不启用震荡高抛低吸分支。
  - 特点是比 `Top9 DogeLite` 收益更高，同时回撤明显更低。
- `CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy.py`
  - `Top9` 状态层进攻版。
  - 在状态层稳健版基础上，进一步提高牛市多头权重，并更强压缩牛市中的小时级空头。
  - 特点是当前 `Top9` 主线里总收益最高，同时仍显著低于旧版 `Top9` 回撤。
- `Top9RegimeMainStrategy.py`
  - 当前 `Top9` 主版本短名称。
  - 对应现阶段正在运行的模拟盘主策略。
  - 逻辑等同于当前最优主线，只是改成更短、便于回测和 dry-run 使用的名字。

## 标准回测口径

- 带保护机制（推荐，和当前里程碑统计口径一致）
  - `docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.futures.top8.json --strategy CombinedTrendCaptureMilestoneV2Strategy --timerange 20210417-20260404 --enable-protections --export none`
- 不带保护机制
  - `docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.futures.top8.json --strategy CombinedTrendCaptureMilestoneV2Strategy --timerange 20210417-20260404 --export none`

说明：

- 这套策略在代码里定义了 `protections`，只有命令里显式带上 `--enable-protections` 才会生效。
- 当前主线实际使用的保护机制来自 `CombinedTrendCaptureOptStrategy.py`，包括：
  - `CooldownPeriod`：开仓后冷却若干根 K 线，避免刚出场就连续追单。
  - `StoplossGuard`：最近窗口内如果止损过多，暂时停止开新仓，避免连续亏损时继续硬做。
  - `MaxDrawdown`：最近窗口内如果累计回撤过大，暂时停止开新仓，降低回撤扩大的风险。
- 是否开启会直接影响交易数、收益和回撤，所以比较结果时一定要统一口径。

## 当前推荐口径

- 原始 8 币 V2
  - 配置：`/freqtrade/user_data/config.backtest.futures.top8.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Strategy`
- 稳健候选 `Top8 ZEC`
  - 配置：`/freqtrade/user_data/config.backtest.futures.top8zec.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Top8ZecStrategy`
- 高收益平衡候选 `Top9 1.20`
  - 配置：`/freqtrade/user_data/config.backtest.futures.top9.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy`
- 风险收益更均衡的 `Top9 DogeLite`
  - 配置：`/freqtrade/user_data/config.backtest.futures.top9.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy`
- `Top9` 状态层稳健版
  - 配置：`/freqtrade/user_data/config.backtest.futures.top9.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy`
- `Top9` 状态层进攻版
  - 配置：`/freqtrade/user_data/config.backtest.futures.top9.json`
  - 策略：`CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy`
- 当前 `Top9` 主版本短名称
  - 配置：`/freqtrade/user_data/config.backtest.futures.top9.json`
  - 策略：`Top9RegimeMainStrategy`

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
- `CombinedTrendCaptureMilestoneV2Top8Zec.md`
  - `Top8 ZEC` 稳健候选说明。
- `CombinedTrendCaptureMilestoneV2Top9LongCenter120.md`
  - `Top9 1.20` 高收益平衡候选说明。
- `策略总览.md`
  - 当前主要策略、币池和回测结果的总览说明。
- `策略架构说明.md`
  - 当前主线策略的层次结构、缺口和优化方向说明。

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
