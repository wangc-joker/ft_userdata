# NFI Differentiated V6

这份说明文档对应当前保留的实验版本：

- 策略：
  [NostalgiaForInfinityX7DifferentiatedV6.py](/D:/test/ft_userdata/user_data/strategies/NostalgiaForInfinityX7DifferentiatedV6.py)
- 回测配置：
  [config.backtest.nfi.1y.300u.top40.max2.diff.v6.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.backtest.nfi.1y.300u.top40.max2.diff.v6.json)
- 回测结果：
  [top40_max2](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/backtest_runs_1y_300u_diff_v6/top40_max2)

## 定位

`V6` 是在多轮差异化实验后保留下来的最平衡版本。

设计目标：

- 保持和原始 `NostalgiaForInfinityX7` 有实质差异
- 收益不要明显落后于原版
- 回撤控制在可接受范围

## 和前一版的关系

`V6` 基于 `V4` 做了一个最小修复：

- 保留 `V4` 的动态滑点和模式化执行差异
- 只把 `ICP` 从 `grind_mode_coins` 中移除

这么做的原因是：

- `V4` 的大回撤主要来自一笔 `ICP` 的 `grind` 单
- 该单以 `stop_loss` 结束，单笔亏损约 `-534.76 USDT`
- 因此 `V6` 的核心是“去掉主要尾部风险源”，而不是重新大改整套逻辑

## 回测口径

- 时间区间：`2025-04-16 -> 2026-04-16`
- 资金：`300 USDT`
- 最大持仓：`2`
- 币池：`Top40`
- 模式：`futures`

## 结果

原始策略结果：

- 收益：`1905.90 USDT`
- 收益率：`635.30%`
- 交易数：`101`
- 最大回撤：`0.00%`

`V6` 结果：

- 收益：`1783.82 USDT`
- 收益率：`594.61%`
- 交易数：`102`
- 最大回撤：`0.00%`
- 胜率：`100%`

关键指标对比：

- 收益保留率：`93.59%`
- 交易数保留率：`100.99%`

## 差异化是否成立

成立。

`V6` 和原始策略不是几乎相同的复刻版。

逐笔对比结果：

- 存在差异的交易数：`41`

这说明：

- `V6` 的执行路径已经和原始版本明显不同
- 但整体收益和交易密度仍保持在比较健康的区间

## 当前建议

如果后续继续实验，建议以 `V6` 作为基线，不再回头保留 `V1~V5`。

原因：

- `V1` 收益下降过大
- `V2 / V3` 虽然稳定，但和原版过于接近
- `V4 / V5` 差异更强，但尾部风险过大
- `V6` 是当前最适合继续往前走的实验版本
