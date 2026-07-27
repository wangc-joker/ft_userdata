# DualTrend 碰撞机会成本与候选排序审计

日期：2026-07-27

## 结论

- 当前研究候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 五年 80 笔已匹配的被挡反事实交易分布在 56 个碰撞时点。只有 26 个时点存在同一根 K 线刚开出的仓位，可由候选排序影响；另外 30 个时点全部由旧仓占满，Tag 排序对它们无效。
- 对 26 个全空头、可排序时点预设 `short_pullback_restart` 优先于 `short_compression_breakdown`。规则只改变 3 个时点，局部已知交易收益差合计 `-1.06%`，不采用。
- 30 个纯旧仓占位时点中有 29 个可评估。每个时点最多静态替换 1 笔：替换持有最久的仓位合计 `-16.87%`；替换当时浮动收益最差的仓位合计虽为 `+8.31%`，但只有 13/29 为正，中位数 `-0.28%`，去掉单个最佳事件后变为 `-3.05%`，且 2022、2024、2025 均为负。
- 不新增 Tag 排序，不抢占旧仓，不修改共享 `max_open_trades=3`。这些结果是局部静态筛查，不是传播后续仓位、资金和 protections 状态的组合回测。

## 数据范围

- 策略：`DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- Positive13、1000 USDT、`stake_amount=unlimited`
- `max_open_trades=3`
- 1h + 5m detail、protections 开启
- 有效区间：2021-07-29 16:00 UTC 至 2026-06-18 00:00 UTC
- 受限组合：481 笔、`+277.37%`、PF `2.429`、最大回撤 `4.78%`
- 输入：2026-07-24 原生信号碰撞回放中的 80 笔精确匹配反事实交易

## 同 K 线候选排序

56 个碰撞时点按占位来源拆分：

| 类型 | 时点 | 含义 |
|---|---:|---|
| 同 K 线有新开仓 | 26 | 候选处理顺序可能改变入选 Pair |
| 只有更早旧仓 | 30 | 只能通过提前退出或抢占改变 |

只对全空头候选池测试预先定义的局部规则：先按 Tag 排 `short_pullback_restart`、`short_compression_breakdown`，同 Tag 再按归档配置中的 whitelist 顺序。没有预先定义多空跨方向优先级，因此混合方向候选不参与规则筛查。

| 年份 | 可评估时点 | 实际换单时点 | 局部收益差 |
|---:|---:|---:|---:|
| 2021 | 2 | 1 | +0.12% |
| 2022 | 5 | 0 | +0.00% |
| 2023 | 4 | 0 | +0.00% |
| 2024 | 3 | 1 | -1.34% |
| 2025 | 8 | 1 | +0.16% |
| 2026 | 4 | 0 | +0.00% |
| 合计 | 26 | 3 | -1.06% |

事后 Oracle 在这些时点可得到 `+47.92%` 的局部上限，但它直接使用未来交易结果挑选 Pair，只说明碰撞候选之间确实存在质量差异，不构成可执行规则。

## 旧仓抢占筛查

对每笔占位仓位，使用碰撞时刻的 5m 开盘价估算立即平仓，并把继续持有时实际发生的后续加仓、退出现金流与其比较。计算包含归档交易费，不重建 funding。240 个占位仓位均完成估值。

先按未来已实现的剩余价值挑最差仓位时，被挡候选在 80 笔中有 54 笔更好；在具有旧仓的 72 笔中有 43 笔更好。这个选择偷看未来，只是机会空间上限，不能作为策略条件。

随后只使用碰撞时已经可见的信息选择被替换仓位，并限制每个纯旧仓时点最多换 1 笔：

| 年份 | 可评估 | 替换当时浮动收益最差 | 替换最老仓位 |
|---:|---:|---:|---:|
| 2022 | 5 | -0.42% | -6.27% |
| 2023 | 2 | +9.64% | -3.02% |
| 2024 | 5 | -6.14% | +4.30% |
| 2025 | 7 | -0.34% | -4.98% |
| 2026 | 10 | +5.56% | -6.90% |
| 合计 | 29 | +8.31% | -16.87% |

“替换浮动收益最差”由 2023-08-17 的单个 `+11.37%` 局部差值主导；删除该事件后合计为 `-3.05%`。年度不稳定、胜率不足一半、结果依赖单点，停止进入完整抢占回测，避免继续围绕历史事件拟合。

## 样本外运行状态

截至 2026-07-27 12:00（Asia/Shanghai）：

- LongMicro 独立观察 bot 正常运行，Positive13/max3、API 8086，当前 0 持仓。
- 共完成 1 笔模拟交易：BTC `long_pullback_restart_1h_body`，2026-07-24 13:10:04 止损，`-1.68% / -5.4923 USDT`。
- 信号碰撞影子采集器正常运行，累计 1 个候选，分类为 `admitted`；0 个满槽碰撞，最近一轮采集错误为 0。
- 2026-07-25 出现过 Binance 市场重载/OHLCV 瞬时错误；容器当前仍为 `running`，不把历史瞬时错误描述为当前停机。

第一笔样本外亏损与五年仅 7 笔的小样本不确定性一致，但单笔结果不足以淘汰 LongMicro。继续隔离观察，不替换现有其他 dry-run 入口。

## 证据

- `user_data/analysis/dualtrend_collision_opportunity_cost.py`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_opportunity_cost.md`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_admission_ranking.csv`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_preemption_screen.csv`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_occupant_opportunity_cost.csv`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_event_opportunity_cost.csv`
