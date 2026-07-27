# DualTrend 实验归档清理

日期：2026-07-27

## 范围

本次只整理研究产物，没有修改策略代码、回测配置、候选角色、模拟盘或影子采集器运行状态。

已删除：

- `user_data/analysis/` 下 35 个 Freqtrade `.last_result.json` 临时指针。
- 1 个 `__pycache__` 目录及其中 8 个 Python 缓存文件。
- higher-low、3S1L 和碰撞回放的 3 个 smoke 目录。
- 碰撞回放根目录中 6 个 `smoke_*` zip/meta 文件。

共清理 55 个文件，约 0.70 MiB。`.gitignore` 已改为统一忽略分析目录中的 `.last_result.json`，避免后续同步再次产生无意义差异。

## 保留原则

- 保留所有正式五年回测 zip/meta，确保原始交易可复核。
- 保留最终 CSV、Markdown 报告和复现脚本。
- 保留失败实验的正式结果与报告，防止重复走 higher-low、市场状态硬过滤、方向槽位、Tag 排序和旧仓抢占等老路。
- 保留参数碰撞修复前的历史归档作为失效证据，但只能按 `CURRENT_DUALTREND.md` 的作废说明阅读。
- 保留并继续忽略本地运行时数据库、WAL/SHM、PID 和日志；这些不是可提交的研究归档。

## 新增目录索引

- `user_data/analysis/signal_collision_audit_2026-07-24/README.md`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/README.md`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/README.md`

当前研究候选仍为 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍为 `DualTrendPyramidSecondAdd20V1Strategy`。本次整理不构成策略晋级。
