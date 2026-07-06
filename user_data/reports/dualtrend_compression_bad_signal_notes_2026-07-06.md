# DualTrend Compression Breakdown 坏信号特征笔记

日期：2026-07-06

## 本轮完成内容

这轮没有继续改策略，而是回到已有诊断数据，专门整理：

- `short_compression_breakdown`
- 三年样本
- 当前主线语境下，哪些“坏信号特征”更值得进入下一轮轻量回测

使用到的现有资料：

- `analysis/positive13_false_breakdown_features.csv`
- `analysis/positive13_guard_candidates.csv`
- `reports/positive13_false_breakdown_feature_diagnosis.md`

## 当前已知事实

从已有诊断报告里，`short_compression_breakdown` 最稳定的坏信号画像是：

1. 入场前 `3h / 6h` 已经跌太多
2. `1H ATR percentile` 偏高
3. `compression_width` 略大
4. 某些阶段存在 `pullback_depth` 偏深

这说明它本质上更像：

- 已经提前释放过一段跌幅
- 短线波动率过高
- 跌破时不够“干净”

也就是更容易出现假跌破 / 快速反抽。

## 重新整理后的观察

### 1. 旧 guard 候选虽然能抓坏单，但普遍太粗

当前 `short_compression_breakdown` 的前几个 guard 候选大致是：

- `atr_percentile_1h >= 0.25 AND compression_width >= 0.02`
- `prev_6h_return <= -0.008 AND pullback_depth >= 0.02`
- `prev_3h_return <= -0.004 AND atr_percentile_1h >= 0.3`
- `prev_6h_return <= -0.008`

这些规则的问题不是没效果，而是太重：

- `prev_6h_return <= -0.008`
  - blocked: `45.68%`
  - bad_capture: `52.31%`
  - loser_capture: `47.17%`
  - winner_kill: `42.86%`
- `prev_3h_return <= -0.004 AND atr_percentile_1h >= 0.25`
  - blocked: `39.51%`
  - bad_capture: `43.08%`
  - loser_capture: `43.40%`
  - winner_kill: `32.14%`
- `prev_6h_return <= -0.008 AND compression_width >= 0.02`
  - blocked: `41.98%`
  - bad_capture: `47.69%`
  - loser_capture: `43.40%`
  - winner_kill: `39.29%`
- `atr_percentile_1h >= 0.25 AND compression_width >= 0.02`
  - blocked: `53.09%`
  - bad_capture: `56.92%`
  - loser_capture: `56.60%`
  - winner_kill: `46.43%`

结论：

- 这些条件能抓到一部分坏单
- 但误杀盈利单仍然太高
- 如果直接并进主策略，大概率会重复 Phase 1A 那种问题

### 2. 一个更有意思的细特征：`close_not_low_enough`

在三年 `short_compression_breakdown` 样本里：

- 亏损单中 `close_not_low_enough=True` 占比：`26.42%`
- 盈利单中 `close_not_low_enough=True` 占比：`7.14%`

这个差异比很多动量类特征更干净。

它的含义也比较符合肉眼经验：

- 明明是在做“跌破”
- 但入场 K 收盘并没有足够贴近低点
- 说明卖压延续性不够，容易是假跌破或下破后被拉回

这类特征的优点：

1. 解释性强
2. 作用点更贴近形态本身
3. 理论上比“前 6h 已经跌太多”这类广谱过滤更不容易误杀

## 现在最值得回测的轻量候选

如果下一步继续验证，我更建议先试下面两条，而不是继续用大范围 momentum/ATR 组合：

### 候选 A：只过滤收盘不够弱的 breakdown

思路：

- 只针对 `short_compression_breakdown`
- 如果 `close_not_low_enough=True`
- 直接拒绝入场

优点：

- 最轻
- 不改市场状态
- 不改 broader trend 结构
- 更接近“跌破质量过滤”

### 候选 B：收盘不够弱 + 短线已超跌

思路：

- `close_not_low_enough=True`
- 并且 `prev_3h_return <= 某阈值` 或 `prev_6h_return <= 某阈值`

优点：

- 比单独用 `prev_6h_return` 更聚焦
- 比纯 reclaim 早退更前置
- 可能比前面的早退逻辑更不容易破坏正常单

## 本轮结论

1. `short_compression_breakdown` 的坏信号方向没有问题，问题在于当前候选条件太粗。
2. 仅靠 `prev_3h/6h return`、`ATR`、`compression_width` 这类广谱条件，误杀仍然偏高。
3. `close_not_low_enough` 是目前更值得进入下一轮轻量验证的特征。
4. 下一轮最适合做的是：
   - 不做 early-fail
   - 不做复杂组合 guard
   - 只在 `populate_entry_trend` 前置增加一个非常轻的 `short_compression_breakdown` 质量过滤验证

## 建议的下一步

下一轮可以只做两条极轻量分支：

1. `short_compression_breakdown` + `close_not_low_enough` 拒绝入场
2. `short_compression_breakdown` + `close_not_low_enough` + 轻微短线超跌阈值

这样能直接回答一个最关键的问题：

**真正有信息量的，是不是“跌破 K 收盘质量”本身，而不是后面的 reclaim 退出。**
