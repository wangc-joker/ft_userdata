# DualTrend 信号碰撞影子审计与五年回放

日期：2026-07-24

> 2026-07-27 后续已完成同 K 线排序与旧仓机会成本审计，结论仍是不新增排序或抢占规则。最新结论见 `dualtrend_collision_opportunity_cost_2026-07-27.md`。

## 结论

- 当前研究候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 保留 Positive13、共享 `max_open_trades=3`，不增加槽位，也不新增 Tag 优先级规则。
- 五年 max3 原生信号导出记录到 101 个满槽碰撞蜡烛；归并重复信号后，对应 80 笔可解析的反事实交易。
- 80 笔反事实交易为 50 胜 30 负，收益率合计 `+84.87%`，PF `2.201`。这说明满槽挡掉的并不全是坏信号，但不等于增加槽位或替换持仓会得到这些利润。
- 结果年度不稳定：2021、2024 为负，2025 基本持平；总利润主要来自 2023 和 2026。因此当前证据不足以在策略里写死排序规则。
- 五年只挡到 1 笔多头，为 `long_1d_center_compression`，反事实为 `-0.01%`；LongMicro 被挡 0 笔。
- LongMicro 只在 1 个碰撞蜡烛中占用槽位，当时被挡的是上述接近持平的小亏日线多头；没有出现 LongMicro 挤掉空头的历史记录。

## 方法

受限回放使用当前权威口径：

- 策略：`DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- Positive13
- 1000 USDT、`stake_amount=unlimited`
- `max_open_trades=3`
- 1h + 5m detail
- protections 开启
- 有效区间：2021-07-29 16:00 UTC 至 2026-06-18 00:00 UTC

Freqtrade 2026.4 的 `--export signals` 会在以下条件全部满足后写入 `rejected.pkl`：策略确有入场信号、同币没有持仓、Pair 未锁定，但全局槽位已满。因此本实验不从 max3/max4 交易差异猜测碰撞，而是读取回测引擎的原生满槽拒绝记录。

反事实回放使用诊断别名 `DualTrendPyramidSecondAdd20LongMicroCollisionReplayV1Strategy`：

- 入场、退出、止损、ROI 和加仓逻辑继承当前候选。
- 单笔初始 stake 固定为 1000 USDT，钱包为 1,000,000 USDT，移除共享资金不足的影响。
- `max_open_trades=100`，保护列表为空，避免新增反事实交易反过来触发全局保护。
- 不使用该回放的组合收益，只把同 Pair、同 Tag、同时间的交易路径连接到 max3 被挡信号。
- 同一 Pair 在反事实交易仍持仓期间再次发出的信号算重复信号，不重复计为独立机会。

## 五年结果

max3 回放精确复现权威结果：481 笔、`+277.37%`、PF `2.429`、最大回撤 `4.78%`。

| 项目 | 结果 |
|---|---:|
| 满槽碰撞蜡烛 | 101 |
| 独立反事实交易 | 80 |
| 重复持仓期信号 | 18 |
| 未解析 | 3 |
| 胜 / 负 | 50 / 30 |
| 收益率合计 | +84.87% |
| 平均单笔 | +1.06% |
| PF | 2.201 |

按被挡 Tag：

| Tag | 独立交易 | 胜 / 负 | 收益率合计 | PF |
|---|---:|---:|---:|---:|
| `short_pullback_restart` | 61 | 39 / 22 | +73.21% | 2.401 |
| `short_compression_breakdown` | 18 | 11 / 7 | +11.67% | 1.633 |
| `long_1d_center_compression` | 1 | 0 / 1 | -0.01% | 0.000 |

按年度：

| 年份 | 独立交易 | 收益率合计 | PF |
|---|---:|---:|---:|
| 2021 | 2 | -3.94% | 0.003 |
| 2022 | 14 | +9.47% | 1.706 |
| 2023 | 13 | +57.63% | 8.575 |
| 2024 | 10 | -3.82% | 0.581 |
| 2025 | 19 | +0.27% | 1.011 |
| 2026 | 22 | +25.26% | 3.367 |

`short_pullback_restart` 的反事实质量高于 compression，但这只是“被挡机会”的独立路径质量。它没有计算为了腾出槽位而提前退出某笔已有持仓的损失，也没有复现共享账户的仓位复利。此前 unrestricted max4 五年仍只有 `+273.47% / PF 2.344 / DD 5.29%`，低于 max3，说明不能把本表直接转换成加槽或抢占规则。

## 实时影子审计

新增只读采集器 `user_data/analysis/dualtrend_signal_collision_shadow.py`，通过观察 bot 的 8086 API 读取：

- 每个 Pair 已分析 K 线中的入场信号、Tag、初始止损和风险字段。
- 当前及已平仓模拟交易。
- 信号预计执行时刻的已有持仓数。

记录写入独立的 `user_data/analysis/signal_collision_shadow.sqlite`，不修改策略、交易数据库或下单流程。分类包括：

- `admitted`
- `shadow_rejected_slot_full`
- `shadow_not_admitted_other`

2026-07-24 首次验证记录到当前 BTC LongMicro 信号，正确分类为 `admitted`，采集错误为 0。采集器已作为隐藏 Windows 进程启动；状态、启动和停止入口分别为：

- `show_positive13_collision_shadow_status.cmd`
- `start_positive13_collision_shadow.cmd`
- `stop_positive13_collision_shadow.cmd`

## 决策

本轮不修改交易优先级。历史结果支持继续观察“满槽时 pullback 是否普遍优于 compression”，但年度稳定性不足，而且还没有计算替换已有持仓的真实机会成本。

下一次评估至少同时查看：

- dry-run 中新增的独立满槽碰撞样本。
- 被挡信号最终结果与当时三笔占位持仓的剩余收益。
- Tag、方向和年度/市场阶段分布。
- 是否出现 LongMicro 或日线多头真实挤压高质量空头。

在样本外证据出现前，不根据本轮总 PF 增加 max4、固定多空槽位、拆分资金池或写死 Tag 排序。

## 证据

- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/max3_signals-2026-07-24_09-43-56.zip`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/max100_counterfactual-2026-07-24_09-56-18.zip`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_replay.md`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_signals.csv`
