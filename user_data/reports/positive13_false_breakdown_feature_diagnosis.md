# Positive13 False Breakdown Feature Diagnosis

日期: 2026-06-23

## 1. 范围与说明

当前 baseline 保持不变：`Positive13 + Combined + max_open_trades=3`。

本轮只做 short 诊断，不修改策略。分析对象仅包含：

- `short_pullback_restart`
- `short_compression_breakdown`

分析时间窗：

- 三年：`2023-06-18 -> 2026-06-18`
- 近一年：`2025-06-18 -> 2026-06-18`
- 压力期：`2026-03-01 -> 2026-05-31`

标签口径说明：

- `false_breakdown = True`：入场后 24h 内，在尚未先达到 `+0.5R` 有利位之前，1h 收盘重新站回 `compression_low` 上方。
- `quick_reverse_1h_5h = True`：入场后 1-5h 内，在尚未先达到 `+0.5R` 有利位之前，1h 收盘重新站回入场价上方。

这两个标签是本地诊断口径，不是策略现有字段。

## 2. 总体分布

- short 样本总数：`248`
- short 亏损单数：`162`
- `false_breakdown=True` 占比：`67.3%`
- `quick_reverse_1h_5h=True` 占比：`73.0%`
- 亏损单中 `false_breakdown=True` 占比：`77.8%`
- 亏损单中 `quick_reverse_1h_5h=True` 占比：`82.1%`

## 3. false_breakdown=True vs False

### 3y

- `short_compression_breakdown`
  - `prev_6h_return`: bad=-0.0090, good=-0.0017, effect=-1.362
  - `prev_12h_return`: bad=-0.0129, good=-0.0083, effect=-0.577
  - `atr_percentile_1h`: bad=0.4287, good=0.3031, effect=0.554
- `short_pullback_restart`
  - `breakdown_depth`: bad=0.0041, good=0.0097, effect=-0.815
  - `entry_candle_body_ratio`: bad=0.6447, good=0.7079, effect=-0.356
  - `atr_percentile_1h`: bad=0.3444, good=0.4391, effect=-0.338

### 1y

- `short_compression_breakdown`
  - `prev_3h_return`: bad=-0.0041, good=0.0016, effect=-1.588
  - `prev_6h_return`: bad=-0.0084, good=-0.0023, effect=-1.246
  - `atr_percentile_1h`: bad=0.2906, good=0.1323, effect=0.887
- `short_pullback_restart`
  - `breakdown_depth`: bad=0.0027, good=0.0100, effect=-1.081
  - `entry_candle_body_ratio`: bad=0.5670, good=0.6975, effect=-0.740
  - `prev_3h_return`: bad=-0.0062, good=-0.0010, effect=-0.631

### stress_2026_03_05

- `short_pullback_restart`
  - `breakdown_depth`: bad=0.0024, good=0.0176, effect=-3.393
  - `distance_to_ema50_1d`: bad=-0.0333, good=-0.0772, effect=2.611
  - `distance_to_ema50_4h`: bad=-0.0174, good=-0.0341, effect=2.023

## 4. quick_reverse_1h_5h=True vs False

### 3y

- `short_compression_breakdown`
  - `prev_6h_return`: bad=-0.0088, good=-0.0034, effect=-0.849
  - `entry_candle_body_ratio`: bad=0.6927, good=0.6238, effect=0.578
  - `atr_percentile_1h`: bad=0.4297, good=0.3122, effect=0.541
- `short_pullback_restart`
  - `prev_6h_return`: bad=-0.0062, good=-0.0084, effect=0.334
  - `distance_to_ema50_1d`: bad=-0.1112, good=-0.0926, effect=-0.314
  - `pullback_depth`: bad=0.0298, good=0.0349, effect=-0.302

### 1y

- `short_compression_breakdown`
  - `pullback_depth`: bad=0.0246, good=0.0196, effect=1.997
  - `compression_width`: bad=0.0241, good=0.0190, effect=1.875
  - `prev_3h_return`: bad=-0.0037, good=0.0013, effect=-1.361
- `short_pullback_restart`
  - `compression_duration`: bad=15.8667, good=14.6364, effect=0.345
  - `distance_to_ema50_1d`: bad=-0.1269, good=-0.1069, effect=-0.311
  - `breakdown_depth`: bad=0.0044, good=0.0060, effect=-0.246

### stress_2026_03_05


## 5. 候选简单过滤条件

这里先只看单条件过滤，不叠复杂模块。评分口径是：多抓坏信号、少误杀盈利单。

### false_breakdown

- `pair_ema50_slope_4h >= -0.0070`: 坏信号捕获 `84.1%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `breakdown_depth <= 0.0063`: 坏信号捕获 `69.0%`，盈利单误杀 `52.3%`，总拦截 `60.1%`
- `entry_candle_body_ratio <= 0.8155`: 坏信号捕获 `83.3%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `entry_candle_close_position >= 0.0924`: 坏信号捕获 `83.3%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `distance_to_ema50_4h >= -0.0669`: 坏信号捕获 `84.1%`，盈利单误杀 `73.3%`，总拦截 `79.8%`

### quick_reverse_1h_5h

- `pair_ema50_slope_4h >= -0.0070`: 坏信号捕获 `85.0%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `entry_candle_body_ratio <= 0.8155`: 坏信号捕获 `83.5%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `entry_candle_close_position >= 0.0924`: 坏信号捕获 `83.5%`，盈利单误杀 `72.1%`，总拦截 `79.8%`
- `distance_to_ema50_4h >= -0.0669`: 坏信号捕获 `84.2%`，盈利单误杀 `73.3%`，总拦截 `79.8%`
- `atr_percentile_1h >= 0.0928`: 坏信号捕获 `83.5%`，盈利单误杀 `74.4%`，总拦截 `79.8%`

## 6. 结论回答

1. false_breakdown=True 和 False 在入场前是否有明显差异？
   - 有，但强度中等，不是单一特征一眼分离。当前最稳定的差异更集中在：`breakdown_depth` 偏浅、`prev_3h/6h/12h return` 更负，部分阶段还会表现为更贴近 `1D EMA50`、`4H slope` 没那么向下。
2. quick_reverse=True 和 False 在入场前是否有明显差异？
   - 有，但稳定性弱于 false_breakdown，主要集中在 `short_compression_breakdown` 上。更常见的是：前 3h/6h 跌幅更大、`1H ATR percentile` 更高、压缩宽度略更大。
3. 哪些特征最能区分坏信号？
   - 这轮最有区分度的通常是：`breakdown_depth`、`prev_3h_return`、`prev_6h_return`、`atr_percentile_1h`，以及压力期里很明显的 `distance_to_ema50_1d / distance_to_ema50_4h`。
4. 是否存在简单过滤条件？
   - 没有看到足够干净的简单过滤条件。虽然有候选，但它们都更像“研究线索”，还不适合直接并入主策略。
5. 这个过滤条件会误杀多少盈利单？
   - 当前候选条件的盈利单误杀都偏高。相对最温和的 `breakdown_depth <= 0.0063` 仍会误杀大约 `52.3%` 的盈利单；其它候选多数会误杀 `70%+` 的盈利单。
6. 是否值得进入 V2 FalseBreakdownGuardStrategy 开发？
   - 暂时**不值得直接进入完整 V2 开发**。如果要继续，也更适合做一轮非常轻量的 guard 验证，而不是马上扩成新的主策略分支。
7. 如果不值得，是否继续保持当前主策略？
   - 是。当前 baseline 仍应保持：`Positive13 + Combined + max_open_trades=3`。
