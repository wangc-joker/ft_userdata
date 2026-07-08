# DualTrend 盈利单加仓 V1 诊断记录

日期: 2026-07-07

## 1. 研究目标

验证一个非常保守的盈利单加仓思路:

- 只针对 `short_pullback_restart`
- 只在已有仓位已经盈利时考虑加仓
- 只允许加仓 1 次
- 加仓规模 = 初始仓位的 50%
- 仅在当前 K 线再次出现相同 `enter_tag` 时触发

对应候选策略类:

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopPyramidV1Strategy`

对照基线:

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

## 2. 已实现内容

在 `D:\test\ft_userdata\user_data\strategies\DualTrendCompressionRestartShortV1Strategy.py` 中加入了:

- `pyramiding_enabled`
- `pyramid_allowed_tags`
- `pyramid_profit_threshold`
- `pyramid_profit_cap`
- `pyramid_stake_fraction`
- `pyramid_max_additions`
- `_current_entry_signal_matches_trade()`
- `_pyramid_stake_amount()`
- `adjust_trade_position()` 内的加仓分支

在 `D:\test\ft_userdata\user_data\strategies\DualTrendMainStrategies.py` 中加入了候选类:

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopPyramidV1Strategy`

## 3. 第一轮结果: 不开 stacking

三年样本:

- 区间: `2023-06-18 -> 2026-06-18`
- 周期: `1h`
- 细节周期: `5m`

结果:

- 基线: `319 trades / +162.46% / PF 2.44 / MaxDD 5.05%`
- PyramidV1: `319 trades / +162.46% / PF 2.44 / MaxDD 5.05%`

结论:

- 候选与基线完全一致
- 说明“盈利仓内追加仓位”没有实际触发

## 4. 第二轮结果: 开启 `--enable-position-stacking`

回测命令增加:

- `--enable-position-stacking`

结果:

- 基线: `530 trades / +198.10% / PF 1.78 / MaxDD 11.54%`
- PyramidV1: `530 trades / +198.10% / PF 1.78 / MaxDD 11.54%`

结论:

- 两者依然完全一致
- 交易数从 `319` 增长到 `530`
- 但这不是候选加仓逻辑带来的改善
- 这是 Freqtrade 回测层允许“同币重复开新仓”后，框架自身产生的结果

## 5. 关键验证

对最新两份回测结果进一步检查:

- `orders > 2` 的交易数: `0`
- `max_stake_amount > stake_amount` 的交易数: `0`

这说明:

1. 没有任何一笔交易在原仓位上真的发生“追加仓位”
2. 所有新增交易都只是 stacking 下的独立重复开仓
3. 当前写入 `adjust_trade_position()` 的盈利加仓逻辑没有真正执行

## 6. 当前判断

这轮研究的结论不是“盈利单加仓无效”，而是:

**当前 V1 触发方式没有打通。**

更准确地说:

- 我们设想的是“原盈利仓上再加一层”
- 但当前看到的只是“回测允许同币多开”
- 这和真实想研究的仓位管理不是一回事

## 7. 可能原因

当前最可疑的几个点:

1. `adjust_trade_position()` 内的“再次出现相同 enter_tag”判断，在 Freqtrade 回测时拿不到我们期望的状态
2. `enter_short == 1` / `enter_tag` 在持仓中的 analyzed dataframe 最后一根上，不一定会像入场那样保留
3. 需要改成更稳定的“结构再确认”触发，而不是依赖字面上的再次 entry signal
4. Freqtrade 对回测中的 position adjustment 触发时机，与普通 entry signal 生命周期不完全一致

## 8. 下一步建议

下一轮不要直接改参数，先做“可触发性诊断”，明确回答:

1. 持仓盈利期间，是否真的经常再次出现同向结构信号
2. 这些再次信号与原始 `enter_tag` 是否能在回测回调里稳定读到
3. 如果不能，是否改为以下两种更稳定的加仓定义之一:

- 方案 A: “盈利中再次出现原方向完整入场信号”
- 方案 B: “盈利中出现结构强化信号”，不要求字面上再次 `enter_tag`

## 9. 当前阶段结论

截至本次记录:

- 候选代码已落地
- 回测框架差异已查明
- 真实的“盈利仓内追加仓位”尚未生效

因此:

**现在还不能评价盈利单加仓策略本身优劣，只能确认当前 V1 实现没有真正跑起来。**
