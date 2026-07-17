# CloseFloor07 加仓过滤实验总结

> **历史状态：** CloseFloor07 已成为当前 SecondAdd20 的父级，但它本身不再是当前主候选。最新状态见仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md)。

## 结论

- 当前有效增厚点只有一条：在原主候选的加仓逻辑上，增加 `close_position >= 0.07`，避免在极端收低的 flush K 上继续加仓。
- 这条过滤在近三年是正收益增强：`+193.31% / PF 2.66 / MaxDD(account) 4.83%`，优于原候选 `+191.75% / PF 2.60 / MaxDD(account) 5.03%`。
- 但拉到真实 5 年后，它不是全面更优：原候选 `+252.14%`，CloseFloor07 `+250.64%`。PF 更高一些，但总收益略低，说明它主要改善的是近三年，不是全周期无条件增强。
- 前面验证过的风险预算 / 结构化加仓退出分支都不如主线，已经从策略代码里清掉，只保留分析结果。

## 关键回测

### 3 年主对照

- 原候选 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
  - `20230618-20260618`
  - `313 trades`
  - `+191.75%`
  - `PF 2.60`
  - `Winrate 50.80%`
  - `MaxDD(account) 5.03%`
- 新候选 `DualTrendPyramidCloseFloor07V1Strategy`
  - `20230618-20260618`
  - `313 trades`
  - `+193.31%`
  - `PF 2.66`
  - `Winrate 51.12%`
  - `MaxDD(account) 4.83%`
- 无加仓对照 `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`
  - `20230618-20260618`
  - `317 trades`
  - `+171.09%`
  - `PF 2.51`
  - `Winrate 49.84%`
  - `MaxDD(account) 5.00%`

### 近 1 年与压力期

- CloseFloor07 `20250618-20260618`
  - `123 trades`
  - `+67.56%`
  - `PF 3.38`
  - `Winrate 56.10%`
  - `MaxDD(account) 4.75%`
- CloseFloor07 `20260301-20260531`
  - `15 trades`
  - `+4.82%`
  - `PF 2.96`
  - `Winrate 40.00%`
  - `MaxDD(account) 1.75%`

### 真实 5 年

- 原候选 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
  - `20210618-20260618`
  - `477 trades`
  - `+252.14%`
  - `PF 2.35`
  - `Winrate 51.15%`
  - `MaxDD(account) 5.02%`
- CloseFloor07 `DualTrendPyramidCloseFloor07V1Strategy`
  - `20210618-20260618`
  - `477 trades`
  - `+250.64%`
  - `PF 2.38`
  - `Winrate 51.36%`
  - `MaxDD(account) 4.82%`

## 5 年按年观察

- 2021 年尾段和 2022 年，CloseFloor07 比原候选更弱。
- 2023 年以后，CloseFloor07 整体更稳，主要收益增强发生在 2024-2026 这段。
- 这说明它更像“近年市场结构适配增强”，还不能直接下结论为全周期主替换。

## 3 年逐笔差异

- 完全匹配交易数：`313`
- 改善笔数：`90`
- 变差笔数：`121`
- 不变笔数：`102`
- 3 年总增量：`15.646 USDT`

按实验逻辑看，这条过滤不是大幅改造，而是少做了一些“已经收在极低位、继续向下挤压”的二次加仓。收益提升不大，但回撤也同步变浅，属于比较干净的小修正。

## 成本压力

- CloseFloor07 3 年，手续费 `1.5x`:
  - `+176.56%`
  - `PF 2.48`
  - `MaxDD(account) 6.09%`
- CloseFloor07 3 年，手续费 `2x`:
  - `+165.90%`
  - `PF 2.33`
  - `MaxDD(account) 6.26%`

成本升高后收益会下台阶，但没有塌，说明这条过滤不是纯靠摩擦很低才成立。

## 本轮判断

- 如果目标是“近三年主线更厚、更稳”，CloseFloor07 值得保留为当前加仓主候选。
- 如果目标是“全 5 年绝对收益最高”，它暂时还不能完全替掉原候选，因为 5 年总收益略低。
- 更准确的定位是：
  - 原候选：全周期收益上限略高。
  - CloseFloor07：近三年更稳、PF 更高、回撤更低。
- 下一步继续研究“盈利单再开第二笔”的话，建议基于 CloseFloor07 往前走，因为它的加仓位置质量已经比原版本更干净。

## 输出文件

- 汇总表：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_experiment_summary.csv`
- 5 年按年：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_5y_yearly.csv`
- 3 年按 pair 差异：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_3y_pair_delta.csv`
- 3 年逐笔差异：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_3y_trade_delta.csv`
