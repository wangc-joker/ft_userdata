# DualTrend LongMicro 执行成本压力审计

日期：2026-07-27

## 结论

- 当前研究候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 修正后的 LongMicro 首次按权威五年 Positive13/max3 口径完成 `1.5x` 和 `2x` 手续费真实回测。候选优势从基准 `+15.64` 个百分点平滑降至 `+14.19` 和 `+11.74` 个百分点，没有出现成本断崖。
- `2x` 手续费下，对照为 `+213.92% / PF 2.118 / DD 6.27%`，候选为 `+225.66% / PF 2.139 / DD 6.26%`。
- Micro Tag 在基准、`1.5x`、`2x` 下均为 7 笔、3 胜 4 负，利润依次为 `+76.26 / +71.31 / +68.95 USDT`。高费用没有改变 7 个入场，但两笔 ROI 单的退出时间略有延后。
- 在 `2x` 手续费交易表上再静态施加单边 `0.10%` 入场和退出滑点，候选仍为 `+185.70% / PF 1.822 / 近似 DD 10.65%`，对照为 `+175.09% / PF 1.801`；候选仍领先 `+10.60` 个百分点。该行不传播 protections、资金和槽位状态，不是完整回测。
- 成本稳健性通过，但没有解决仅 7 笔、3 胜 4 负、利润依赖两笔 ROI 单的问题。继续保留研究候选和独立观察盘，不晋级实盘，不修改策略。

## 口径

- Positive13 静态白名单
- 1000 USDT、`stake_amount=unlimited`
- 共享 `max_open_trades=3`
- 1h + 5m detail
- protections 开启
- 有效区间：2021-07-29 16:00 UTC 至 2026-06-18 00:00 UTC
- 基准手续费：单边 `0.05%`
- `1.5x`：单边 `0.075%`
- `2x`：单边 `0.10%`
- Freqtrade 版本：2026.4，mainnet 市场元数据

基准直接读取 2026-07-20 参数隔离修复后的权威归档。`1.5x` 和 `2x` 使用 Freqtrade `--fee` 完整重跑，因此费用会参与当前利润、退出回调、加仓、protections、仓位和后续槽位路径。

## 组合结果

| 场景 | SecondAdd20 | LongMicro | 候选差值 | 对照 PF | 候选 PF | 候选 DD |
|---|---:|---:|---:|---:|---:|---:|
| 基准 | +261.73% | +277.37% | +15.64% | 2.405 | 2.429 | 4.78% |
| 手续费 1.5x | +232.96% | +247.15% | +14.19% | 2.255 | 2.282 | 6.08% |
| 手续费 2x | +213.92% | +225.66% | +11.74% | 2.118 | 2.139 | 6.26% |
| 2x + 单边 0.03% 滑点 | +202.27% | +213.67% | +11.40% | 2.014 | 2.035 | 9.08%* |
| 2x + 单边 0.05% 滑点 | +194.51% | +205.68% | +11.17% | 1.949 | 1.970 | 9.37%* |
| 2x + 单边 0.10% 滑点 | +175.09% | +185.70% | +10.60% | 1.801 | 1.822 | 10.65%* |

带 `*` 的回撤按交易关闭顺序和压力后利润静态重建。滑点通过不利调整平均开仓价和退出价估算，保留 fee2x 的实际交易清单，不重新触发退出、保护、仓位或后续信号。

候选优势随成本升高逐步收窄，但所有场景仍为正，并且候选 PF、收益和回撤均没有相对稳定对照出现结构性恶化。

## Micro Tag

| 场景 | Trades | 胜 / 负 | Profit | PF |
|---|---:|---:|---:|---:|
| 基准 | 7 | 3 / 4 | +76.26 USDT | 3.364 |
| 手续费 1.5x | 7 | 3 / 4 | +71.31 USDT | 3.256 |
| 手续费 2x | 7 | 3 / 4 | +68.95 USDT | 3.177 |
| 2x + 单边 0.03% 滑点 | 7 | 3 / 4 | +66.89 USDT | 3.031 |
| 2x + 单边 0.05% 滑点 | 7 | 3 / 4 | +65.52 USDT | 2.940 |
| 2x + 单边 0.10% 滑点 | 7 | 3 / 4 | +62.09 USDT | 2.731 |

按入场年份：

| 场景 | 2023，2 笔 | 2024，1 笔 | 2025，4 笔 |
|---|---:|---:|---:|
| 基准 | -1.80 USDT | +44.51 USDT | +33.55 USDT |
| 手续费 1.5x | -2.16 USDT | +43.00 USDT | +30.46 USDT |
| 手续费 2x | -2.49 USDT | +42.39 USDT | +29.05 USDT |
| 2x + 单边 0.10% 滑点 | -3.80 USDT | +41.51 USDT | +24.39 USDT |

高成本下年度方向没有翻转：2023 仍为小亏，2024 的单笔 ROI 赢家仍承担主要利润，2025 的 4 笔仍为正但持续衰减。执行成本不是当前最大风险，样本量和利润集中才是。

## 路径变化

| 场景 | 策略 | 与基准同入场 | 基准独有 | 压力独有 | 退出改变 | 订单数改变 |
|---|---|---:|---:|---:|---:|---:|
| 1.5x | SecondAdd20 | 473 | 4 | 0 | 23 | 7 |
| 1.5x | LongMicro | 477 | 4 | 0 | 25 | 7 |
| 2x | SecondAdd20 | 469 | 8 | 2 | 53 | 18 |
| 2x | LongMicro | 473 | 8 | 2 | 55 | 18 |

费用压力确实改变了退出、加仓和后续 protections/槽位路径，因此真实 `--fee` 结果优先于机械扣费估算。尽管总体路径变化，候选相对对照始终多 4 笔交易；Micro 的 7 个入场全部保留、订单数均仍为 1。

## 决策

- 不修改 LongMicro 入场、止损、ROI、仓位或过滤参数。
- 不因压力测试通过而替换现有其他 dry-run 或批准实盘。
- 继续观察独立 LongMicro 模拟盘，核心缺口仍是样本外交易数量、真实滑点和不同市场阶段分布。
- 后续不需要重复当前五年费用压力；只有基础手续费模型、策略实现或权威候选发生变化时才重跑。

## 证据

- `user_data/analysis/dualtrend_longmicro_execution_stress.py`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/fee1p5x-2026-07-27_04-49-43.zip`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/fee2x-2026-07-27_04-40-27.zip`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_report.md`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_summary.csv`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_micro_trades.csv`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_micro_yearly.csv`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_path_changes.csv`
