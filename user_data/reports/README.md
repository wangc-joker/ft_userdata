# DualTrend Reports Index

本目录保存按日期积累的回测、诊断和淘汰实验记录。它们是研究证据，不共同定义“当前主候选”。

分析 DualTrend 前先读仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md)。如果某份历史报告中的“当前”“主线”“候选”与权威页冲突，以权威页为准。

当前研究主候选为 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，`DualTrendPyramidSecondAdd20V1Strategy` 是稳定对照。LongMicro 必须使用 2026-07-20 参数隔离修复后的结果；7 月 17 日报告中的旧高收益数字已经失效。最近的直接依据是：

- `dualtrend_long_micro_parameter_collision_audit_2026-07-20.md`
- `dualtrend_pandas_boolean_futurewarning_fix_2026-07-21.md`
- `dualtrend_higher_low_reclaim_experiment_2026-07-21.md`
- `dualtrend_failed_breakdown_reclaim_experiment_2026-07-21.md`
- `dualtrend_long_market_state_filters_experiment_2026-07-22.md`
- `dualtrend_side_slots_and_split_capital_experiment_2026-07-22.md`
- `dualtrend_signal_collision_shadow_and_replay_2026-07-24.md`
- `dualtrend_collision_opportunity_cost_2026-07-27.md`
- `dualtrend_longmicro_execution_cost_stress_2026-07-27.md`
- `dualtrend_longmicro_sample_concentration_audit_2026-07-27.md`
- `dualtrend_experiment_cleanup_2026-07-27.md`
- `dualtrend_nfi_peak_and_long_micro_upgrade_2026-07-17.md`
- `dualtrend_second_add20_仓位比例实验_2026-07-14.md`
- `dualtrend_long_entry_expansion_2026-07-15.md`
- `dualtrend_top20_max6_backtest_2026-07-15.md`

LongMicro 的独立 dry-run 观察入口、数据库和报告路径见 `longmicro_observation/README.md`。信号碰撞影子采集器的运行状态也必须单独检查，不能仅凭文档快照推断。

报告中的实验策略、旧类名和已淘汰方向继续保留，用于避免重复走老路。

2026-07-27 已清理分析目录中的 `.last_result.json`、Python 缓存和被正式结果替代的 smoke 产物。三项最新实验的正式归档入口分别是：

- `../analysis/signal_collision_audit_2026-07-24/README.md`
- `../analysis/longmicro_execution_stress_2026-07-27/README.md`
- `../analysis/longmicro_sample_concentration_2026-07-27/README.md`
