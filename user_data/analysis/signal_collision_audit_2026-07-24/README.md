# Signal Collision Audit

本目录只保留 2026-07-24 五年正式回放及 2026-07-27 机会成本审计所需证据。短区间 smoke 和 Freqtrade `.last_result.json` 指针已于 2026-07-27 清理。

## 权威产物

- `five_year/max3_signals-2026-07-24_09-43-56.zip`：Positive13/max3 原生信号与满槽拒绝记录。
- `five_year/max100_counterfactual-2026-07-24_09-56-18.zip`：固定小仓、无 protections 的反事实交易路径；不能把组合收益当作策略收益。
- `five_year/report/collision_replay.md`：五年碰撞回放总结。
- `five_year/report/collision_opportunity_cost.md`：同 K 线排序与旧仓抢占机会成本总结。
- `five_year/report/*.csv`：碰撞信号、排序、抢占和逐事件结构化明细。

## 结论

- LongMicro 五年被满槽挡住 0 笔，只在 1 个碰撞蜡烛占位，没有历史证据表明它挤掉空头利润。
- pullback 优先只改变 3 个同 K 线时点，局部收益差为 `-1.06%`。
- 替换最老仓位为负；替换当时浮亏最差仓位不稳定且由单一事件主导。
- 不增加槽位，不写死 Tag 优先级，不新增提前平仓腾槽规则。

## 复现入口

- `user_data/analysis/dualtrend_signal_collision_replay.py`
- `user_data/analysis/dualtrend_collision_opportunity_cost.py`
- `user_data/strategies/DualTrendCollisionReplayStrategies.py`

实时影子采集器是独立运行证据，脚本为 `user_data/analysis/dualtrend_signal_collision_shadow.py`，数据库为被 Git 忽略的 `user_data/analysis/signal_collision_shadow.sqlite*`。运行状态必须现场检查，不能由本目录快照推断。
