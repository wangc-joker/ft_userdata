# SecondAdd15 坏加仓过滤诊断

## 结论

本轮只研究 `DualTrendPyramidSecondAdd15V1Strategy` 的第二腿坏加仓识别，不修改原始入场逻辑。

结论是：暂时不建议给第二腿增加简单过滤。当前 `SecondAdd15` 仍然保留为主候选。

原因：

- 3 年里第二腿加仓只有 `11` 笔，5 年只有 `20` 笔，样本很小。
- 第二腿整体是正贡献：3 年第二腿相关净增约 `+23.62 USDT`，5 年净增约 `+18.05 USDT`。
- 坏第二腿确实存在，但用简单阈值过滤会误杀不少贡献单。
- 两个实盘可实现候选都没有打赢原 `SecondAdd15`。

## 诊断结果

订单层面诊断：

- 3 年：`11` 笔第二腿，`9` 笔改善，`2` 笔变差。
- 5 年：`20` 笔第二腿，`14` 笔改善，`6` 笔变差。

第二腿坏单主要集中在：

- 加仓后最终 `trailing_stop_loss` 或 `stale_loss_72h`。
- 部分早期样本，比如 2021-2022 的 DOGE / XRP。
- 个别第二腿触发时短线延续不足，但这个特征不够稳定。

## 验证过的过滤

### Ret3Guard

规则：第二腿要求当前 `prev_3h_return <= -1.2%`。

3 年结果：

- CloseFloor07: `+195.02% / PF 2.658 / MaxDD 4.82%`
- SecondAdd15: `+198.33% / PF 2.677 / MaxDD 4.82%`
- Ret3Guard: `+196.01% / PF 2.662 / MaxDD 4.82%`

结论：过滤过度，只保留 `3` 笔第二腿，误杀贡献单。

### Profit19

规则：第二腿触发浮盈从 `1.8%` 提高到 `1.9%`。

3 年结果：

- Profit19: `+197.34% / PF 2.673 / MaxDD 4.82%`

结论：略弱于 `SecondAdd15`，没有必要替换。

## 当前保留

保留：

- `DualTrendPyramidCloseFloor07V1Strategy`
- `DualTrendPyramidSecondAdd15V1Strategy`

删除：

- `DualTrendPyramidSecondAdd15Ret3GuardV1Strategy`
- `DualTrendPyramidSecondAdd15Profit19V1Strategy`

## 下一步建议

不要继续用单一阈值硬过滤第二腿。

更值得做的是：

- 第二腿触发后 3-6 小时行为诊断。
- 判断第二腿加仓后是否快速失败。
- 如果加仓后没有继续创新低，考虑只退出第二腿，而不是禁止第二腿。

也就是说，第二腿更像需要“加仓后管理”，而不是“加仓前一刀切过滤”。

## 输出文件

- `user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_bad_add_diagnosis.csv`
- `user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_bad_add_summary.csv`
- `user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_candle_features.csv`
- `user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_guard_threshold_scan.csv`
