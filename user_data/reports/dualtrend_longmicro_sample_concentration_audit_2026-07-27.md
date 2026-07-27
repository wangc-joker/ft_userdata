# DualTrend LongMicro 小样本与利润集中度审计

日期：2026-07-27

## 结论

- 当前研究候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 五年 Micro 只有 7 笔、3 胜 4 负，胜率 `42.86%`；Wilson 95% 区间为 `15.82% -> 74.95%`，范围过宽，无法据此确定真实胜率。
- 20 万次确定性逐笔 bootstrap 中，七笔收益和为正的概率为基准 `89.16%`、重成本压力 `85.79%`；但基准七笔收益率和的 95% 区间为 `-8.36% -> +40.68%`，仍包含亏损。
- 最佳单笔 `+63.02 USDT`，占净利润 `82.63%`；两笔 ROI 合计 `+107.53 USDT`，其余五笔合计 `-31.27 USDT`。去掉最佳单笔后仍有 `+13.24 USDT`，但同时去掉两笔 ROI 后整体为负。
- 7 笔只来自两个币：BNB 5 笔合计 `+79.29 USDT`，BTC 2 笔合计 `-3.03 USDT`。剔除 BNB 后，Micro 历史证据为负。
- Top20/max6 的 7 笔 Micro 与 Positive13/max3 是完全相同的 Pair 和入场时间，不是第二组独立验证，不能用于降低 BNB 集中度风险。
- 成本稳健性已通过，但统计可信度和横截面泛化仍不足。继续独立模拟观察，不晋级实盘，不新增 BNB 专属规则，不修改策略。

## 输入

本审计读取 2026-07-27 执行成本压力实验的逐笔 Micro 表：

- 基准手续费
- 手续费 1.5x
- 手续费 2x
- 2x 手续费 + 单边 0.03% / 0.05% / 0.10% 静态滑点

主统计使用每笔 `profit_ratio`，减少组合复利和不同时点 stake 金额对抽样结果的影响。绝对利润只用于说明历史组合中的贡献规模。

## 抽样不确定性

| 场景 | 七笔收益和为正的 bootstrap 概率 | 95% 收益率和区间 |
|---|---:|---:|
| 基准 | 89.16% | -8.36% -> +40.68% |
| 2x + 单边 0.10% 滑点 | 85.79% | 见结构化结果 |

bootstrap 固定 seed `20260727`，每个场景抽样 200,000 次，每次从当前 7 笔有放回抽取 7 笔。这个模型假设交易独立同分布，但历史中 5/7 来自 BNB，因此它是偏乐观诊断，不是置信度晋级依据。

胜率只有 3/7，Wilson 95% 区间从 `15.82%` 到 `74.95%`。现有样本既容许低胜率、依赖大赢家的真实分布，也容许更稳定的分布，无法区分。

## 单笔集中度

| 项目 | 基准结果 |
|---|---:|
| 净利润 | +76.26 USDT |
| 最佳单笔 | +63.02 USDT |
| 最佳单笔 / 净利润 | 82.63% |
| 两笔 ROI | +107.53 USDT |
| 其余五笔 | -31.27 USDT |
| 去掉最佳单笔 | +13.24 USDT |
| 将赢家封顶 +5% 后的收益率和 | +5.30% |
| 将赢家封顶 +3% 后的收益率和 | +1.30% |

封顶后仍略为正，说明利润并非只有最佳一笔；但 +3% 封顶后只剩 `+1.30%` 的七笔收益率和，边际很薄。两笔 ROI 同时缺失时，非 ROI 样本整体为负。

## 币种集中度

| 剔除币种 | 被剔除交易 | 被剔除利润 | 剩余利润 | 剩余收益率和 |
|---|---:|---:|---:|---:|
| BNB | 5 | +79.29 USDT | -3.03 USDT | -0.77% |
| BTC | 2 | -3.03 USDT | +79.29 USDT | +16.08% |

当前所有净利润都来自 BNB 组，而 BNB 组本身仍含两笔止损。不能据此把策略改成 BNB-only：那会从唯一盈利历史簇反推规则，是典型的样本内选择。正确做法是保留未改动候选，等待独立样本验证 BNB 以外的泛化，或验证 BNB 在样本外是否仍重复出现。

独立模拟盘首笔 BTC Micro 为 `-1.68% / -5.4923 USDT`。它与两笔历史 BTC 合计为负的方向一致，但单笔样本不足以单独淘汰候选，也不与历史回测机械合并。

## 年份剔除

| 剔除年份 | 被剔除交易 | 被剔除利润 | 剩余利润 |
|---:|---:|---:|---:|
| 2023 | 2 | -1.80 USDT | +78.06 USDT |
| 2024 | 1 | +44.51 USDT | +31.75 USDT |
| 2025 | 4 | +33.55 USDT | +42.71 USDT |

逐年剔除后绝对利润仍为正，但 2024 只有一笔 ROI 赢家，2025 的四笔中又包含另一笔 ROI 赢家。年度剔除不能抵消交易和币种层面的集中度。

## Top20 去重

Top20/max6 五年 Micro 仍为相同 7 个入场：

- BTC：2023-12-16、2025-01-06
- BNB：2023-12-21、2024-02-07、2025-01-17、2025-06-10、2025-08-07

Top20 Micro 合计 `+76.25 USDT`，与 Positive13 的小差异来自共享组合仓位金额，不是新增信号。Top20 结果只能说明扩大组合币池后候选整体仍保持优势，不能被描述为 Micro 的独立跨币验证。

## 决策

- LongMicro 继续作为小样本研究候选，SecondAdd20 继续作为稳定对照。
- 不切换其他 dry-run，不批准实盘，不新增 Pair 白名单或 BNB 特例。
- 保留现有“至少 30 笔已关闭交易、至少四个完整观察周”的观察门槛；当前只有 1 笔样本外交易。
- 晋级前除组合 PF/DD 外，还必须查看样本是否扩展到更多 Pair/市场阶段，以及是否仍由单个 Pair 或两笔大赢家主导。
- 在新样本出现前，不再对这 7 笔做阈值、币种或退出参数搜索。

## 证据

- `user_data/analysis/dualtrend_longmicro_sample_concentration.py`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_concentration_report.md`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_concentration_summary.csv`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_bootstrap.csv`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_group_leaveout.csv`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_trade_leaveout.csv`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_top20_micro_trades.csv`
