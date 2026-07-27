# LongMicro Execution Stress

本目录是 2026-07-27 修正后 LongMicro 五年执行成本压力实验的正式归档。候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。

## 权威产物

- `fee1p5x-2026-07-27_04-49-43.zip`：单边手续费 `0.075%` 的完整回测。
- `fee2x-2026-07-27_04-40-27.zip`：单边手续费 `0.10%` 的完整回测。
- `report/execution_stress_report.md`：总结果与口径。
- `report/execution_stress_summary.csv`：组合压力场景汇总。
- `report/execution_stress_micro_trades.csv`、`execution_stress_micro_yearly.csv`：Micro 逐笔与年度结果。
- `report/execution_stress_path_changes.csv`：相对基准的交易路径变化。

## 结论

- 1.5x 手续费下，对照/候选为 `+232.96% / +247.15%`。
- 2x 手续费下，对照/候选为 `+213.92% / +225.66%`。
- 2x 手续费加单边 `0.10%` 静态滑点时，候选仍为 `+185.70%`，对照为 `+175.09%`。
- Micro 7 笔在基准、1.5x、2x 和重滑点下分别为 `+76.26 / +71.31 / +68.95 / +62.09 USDT`。
- 成本稳健性通过，但不解决样本小和利润集中的问题，不据此晋级实盘。

复现与汇总脚本：`user_data/analysis/dualtrend_longmicro_execution_stress.py`。只有基础手续费模型、策略实现或当前权威候选变化时才需要重跑。
