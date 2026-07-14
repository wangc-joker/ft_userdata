# DualTrend ret_6h 修复验证记录

日期：2026-07-09

## 1. 问题背景

用户反馈：

- 在另一台机器同步代码后，看到 `ret_6...` 相关异常
- 同时回测收益掉到只有 `140%+`

怀疑点：

- 当前主线中的 `StrongRunnerStructure` 在 +5% 分流时，会读取 `ret_6h`
- 但代码中存在“读取了 `ret_6h`，却没有在指标链里生成它”的风险

## 2. 确认结果

在 `D:\test\ft_userdata\user_data\strategies\DualTrendMainStrategies.py` 中确认：

### 已存在

- `_current_ret_6h()` 会读取 `ret_6h`
- `_DualTrendStructureStrongRunnerReach5Mixin` 会用 `ret_6h <= -0.02` 参与强单判定

### 修复前缺失

`populate_indicators()` 里有：

- `ret_1h`
- `prev_3h_return`
- `prev_6h_return`

但没有：

- `ret_6h`

这意味着如果 dataframe 中不存在该列，`_current_ret_6h()` 会退回到 `0.0`。

于是条件：

`ret_6h <= -0.02`

几乎恒为 False。

直接后果：

- 本来该继续持有的强单
- 会被误判为弱单
- 提前 partial / 提前退出
- 总收益明显下降

## 3. 修复内容

文件：

- `D:\test\ft_userdata\user_data\strategies\DualTrendMainStrategies.py`

补回：

```python
dataframe["ret_6h"] = dataframe["close"] / dataframe["close"].shift(6) - 1.0
```

这是一次很小但很关键的修复。

## 4. 修复后回测验证

统一条件：

- 配置：`config.backtest.dualtrend.combined.top50.positive13.max3.json`
- 币池：Positive13
- `max_open_trades = 3`
- `timeframe = 1h`
- `timeframe_detail = 5m`
- 实际有效区间：`2022-11-11 16:00:00 -> 2026-06-18 00:00:00`

本轮重新核对输出文件：

- 汇总表：`D:\test\ft_userdata\user_data\analysis\ret6h_recheck_2026-07-09\summary.csv`
- 原始日志目录：`D:\test\ft_userdata\user_data\analysis\ret6h_recheck_2026-07-09\`

## 4.1 StrongRunnerStructure 主线

策略：

- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

修复后结果：

- `388 trades`
- `+192.58%`
- `PF 2.25`
- `MaxDD 5.78%`
- `Winrate 52.1%`

结论：

- 结果明显高于“140%+”那类退化结果
- 说明 `ret_6h` 缺失确实会严重影响这条主线

## 4.2 当前加仓主线

策略：

- `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

修复后结果：

- `364 trades`
- `+231.67%`
- `PF 2.56`
- `MaxDD 4.97%`
- `Winrate 51.4%`

按方向：

- Long：`+60.89%`
- Short：`+170.77%`

结论：

- 当前这条加仓主线同样依赖 `ret_6h` 链路完整
- 修复后整体结果处于明显正常区间

## 4.3 三条主线重新核对

本轮按用户要求，统一重跑：

1. `DualTrendRawStrategy`
2. `DualTrendBaselineStrategy`
3. `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

统一窗口：

1. `3y`: `2023-06-18 -> 2026-06-18`
2. `1y`: `2025-06-18 -> 2026-06-18`
3. `pressure`: `2026-03-01 -> 2026-05-31`

### 汇总表

| 策略 | 窗口 | Trades | Profit | PF | MaxDD | Winrate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `DualTrendRawStrategy` | 3y | 295 | 199.63% | 2.00 | 7.06% | 34.2% |
| `DualTrendRawStrategy` | 1y | 112 | 51.07% | 1.98 | 7.05% | 38.4% |
| `DualTrendRawStrategy` | pressure | 17 | -4.36% | 0.40 | 6.07% | 17.6% |
| `DualTrendBaselineStrategy` | 3y | 330 | 144.61% | 2.15 | 5.77% | 50.0% |
| `DualTrendBaselineStrategy` | 1y | 131 | 42.40% | 2.34 | 4.84% | 55.0% |
| `DualTrendBaselineStrategy` | pressure | 18 | 1.98% | 1.46 | 2.65% | 38.9% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 3y | 313 | 191.75% | 2.60 | 5.03% | 50.8% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 1y | 123 | 66.01% | 3.21 | 4.96% | 55.3% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | pressure | 15 | 4.82% | 2.96 | 1.75% | 40.0% |

### 简要解读

- `Raw`：
  - 3 年总收益仍然最高之一，达到 `199.63%`
  - 但压力期明显偏弱，`-4.36%`，PF 只有 `0.40`
  - 这说明 Raw 的进攻性仍然最强，但回撤防守不够厚

- `Baseline`：
  - 3 年结果为 `144.61%`
  - 1 年 `42.40%`
  - 压力期转正，`1.98%`
  - 说明主基线在防守上明显强于 Raw，但收益天花板更低

- `Current Candidate`：
  - 3 年 `191.75%`
  - 1 年 `66.01%`
  - 压力期 `4.82%`
  - PF 分别达到 `2.60 / 3.21 / 2.96`
  - 这是三条线里目前综合性最强的一条：收益接近 Raw，但稳健性明显更好

## 5. 对用户问题的解释

“为什么在家里同步代码后，只跑出 140% 多？”

最可能原因不是市场变化，而是：

1. 家里的同步版本中，`ret_6h` 没有正确生成
2. `StrongRunnerStructure` 在 +5% 位置无法正确识别强单
3. 强趋势单被过早处理
4. 收益退化到 `140%~150%` 区间

## 6. 最终结论

本次已经基本确认：

- `ret_6h` 缺失是一个真实问题
- 它足以显著拉低当前主线与加仓主线的收益
- 修复后，主线结果恢复到合理区间
- 重新核对后，当前最值得继续作为实战候选保留的，仍然是：
  - `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

一句话总结：

这次 `140%+` 的异常，大概率不是策略思想失效，而是 `ret_6h` 指标链断了。
