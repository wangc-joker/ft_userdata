# DualTrend 当前权威状态

> **唯一权威入口，更新于 2026-07-27。** 其他带日期的 DualTrend 文档都是当时的实验快照。发生冲突时，以本文和当前代码为准。

## 一眼结论

- 当前研究主候选：`DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- 稳定对照：`DualTrendPyramidSecondAdd20V1Strategy`
- 策略文件：`user_data/strategies/DualTrendMainStrategies.py`
- 主口径：Positive13、`max_open_trades=3`、1000 USDT、`stake_amount=unlimited`、1h + 5m detail、启用 protections
- 参数隔离修复后，Positive13 三年为 `+209.59%`，对照 `+199.22%`；五年为 `+277.37%`，对照 `+261.73%`
- Top20/max6 三年为 `+190.23%`，对照 `+180.62%`；五年为 `+243.23%`，对照 `+231.17%`
- 五年新增 tag 仍只有 7 笔，3 胜 4 负，收益依赖两笔 `+10%` ROI 单；保留为小样本研究候选，不替换现有 dry-run
- 独立 LongMicro 观察 bot 已于 2026-07-20 15:01（Asia/Shanghai）启动：Positive13/max3、1000 USDT dry-run、API 8086；初始 0 持仓/0 成交
- 2026-07-21 观察 bot 因 Docker Desktop 关闭而中断；Docker 恢复后已自动重启。2026-07-25 当前周期出现过 Binance 市场重载/OHLCV 瞬时错误，随后恢复；截至 2026-07-27 bot 仍为 `running`
- 本地策略的 pandas boolean `fillna(False)` FutureWarning 已用显式 nullable-boolean 归一化修复；近一年 123 笔交易与修复前逐笔、逐利润完全一致。Freqtrade 2026.3 的 `strategy_helper.py:109` 上游同类警告已在独立观察容器中按模块精确屏蔽，不改变 pandas 行为或策略逻辑
- 2026-07-21 已淘汰通用 `long_higher_low_reclaim_1h`：五年 max100 纯 tag 452 笔、PF `0.8073`、`-269.15 USDT`，加入 SecondAdd20 后收益与回撤均明显恶化
- `long_failed_breakdown_reclaim_1h` 五年 max100 只有 5 笔，利润几乎全部来自一笔 NEAR `+10%` ROI；样本过稀且仅出现在 2023-2024，不采用也不扩窗
- 2026-07-22 三项多头市场状态预筛均未通过：PAIR/BTC 相对强度拒绝组仍赚 `+79.16 USDT`；4H 市场广度拒绝组反而赚 `+426.29 USDT`、PF `6.503`；BTC 日线熊市保护只挡到一笔 `+41.42 USDT` 的赢家。未新增策略类，也未修改候选
- 2026-07-22 资金隔离实验也未通过：unrestricted max4 五年 `+273.47% / DD 5.29%`，低于 max3 的 `+277.37% / DD 4.78%`；3 空 + 1 多仅 `+206.54%`；80% 空头 + 20% 多头独立资金池仅 `+137.76% / DD 6.78%`。继续保留共享 max3
- 2026-07-24 五年信号碰撞回放完成：max3 原生导出 101 个满槽碰撞蜡烛，归并为 80 笔反事实交易，50 胜 30 负、收益率合计 `+84.87%`、PF `2.201`；但 2021/2024 为负、2025 基本持平，收益主要集中在 2023/2026，不据此新增 Tag 排序或槽位
- 五年只挡到 1 笔多头，反事实 `-0.01%`；LongMicro 被挡 0 笔，只在 1 个碰撞蜡烛占位，且没有挤掉空头。现有证据不支持“新增多头挤压空头利润”的判断
- LongMicro 信号碰撞影子采集器已于 2026-07-24 启动，通过 8086 API 只读记录候选和槽位状态；首条 BTC LongMicro 信号正确分类为 `admitted`，不改变策略或下单行为
- 2026-07-27 机会成本审计把 56 个碰撞时点拆成 26 个同 K 线可排序时点和 30 个纯旧仓占位时点；pullback 优先只改变 3 个时点且局部收益差 `-1.06%`，不采用 Tag 排序
- 旧仓静态抢占也不采用：替换最老仓位合计 `-16.87%`；替换当时浮动收益最差仓位虽合计 `+8.31%`，但仅 13/29 为正、中位数 `-0.28%`，删除单个最佳事件后为 `-3.05%`，且三个年度为负
- 截至 2026-07-27 14:45，LongMicro 观察 bot 正常运行、0 持仓；首笔 BTC Micro 模拟交易止损 `-1.68% / -5.4923 USDT`。影子采集仍只有 1 个 `admitted` 候选、0 个满槽碰撞、最近采集错误 0
- 2026-07-27 修正后五年成本压力通过：手续费 1.5x 时对照/候选为 `+232.96% / +247.15%`，2x 时为 `+213.92% / +225.66%`；候选优势由基准 `+15.64` 平滑收窄至 `+14.19 / +11.74` 个百分点，没有成本断崖
- `2x + 单边 0.10% 入场/退出滑点` 的静态压力下，候选仍为 `+185.70% / PF 1.822 / 近似 DD 10.65%`，对照 `+175.09% / PF 1.801`；该滑点行不传播后续状态，不作完整回测解释
- Micro 7 笔在基准/1.5x/2x/2x+重滑点下分别为 `+76.26 / +71.31 / +68.95 / +62.09 USDT`；成本不是当前主要风险，3 胜 4 负、两笔 ROI 单利润集中和样本外不足仍是主要限制
- 2026-07-27 小样本集中度审计：7 笔胜率 `42.86%`，Wilson 95% 区间 `15.82%-74.95%`；20 万次逐笔 bootstrap 的正收益概率为 `89.16%`，但七笔收益率和 95% 区间仍为 `-8.36% -> +40.68%`，不能据此晋级
- 最佳 Micro 单笔占净利润 `82.63%`；两笔 ROI 合计 `+107.53 USDT`，其余五笔 `-31.27 USDT`。BNB 5 笔 `+79.29 USDT`，BTC 2 笔 `-3.03 USDT`；剔除 BNB 后证据为负，禁止从该结果反推 BNB-only 规则
- Top20/max6 的 7 笔 Micro 与 Positive13/max3 的 Pair 和入场时间完全相同，不是独立跨币验证；Top20 正增益不能用于降低 Micro 的样本集中度风险
- 2026-07-27 已完成实验归档清理：只删除 `.last_result.json`、Python 缓存和被正式结果替代的 smoke 产物；正式五年 zip/meta、CSV、脚本、失败实验记录和运行时观察数据均保留，候选与运行入口未变
- 历史 `+191.75%` Window05To15 不是当前候选

**重要作废项：** 2026-07-17 报告中的 LongMicro `+216.62%`、`+281.17%`、`+200.99%`、`+253.85%` 均不可再引用。扩展 mixin 曾用同名 `long_breakout_buffer=0.001`，意外覆盖父级日线多头的 `0.009`，旧收益不是纯 Micro 增益。当前代码已改用独立的 `long_expansion_breakout_buffer`。

## 当前主候选

继承关系：

```text
DualTrendPyramidSecondAdd20LongMicroV1Strategy
  -> DualTrendLongExpansionPullbackBodyMicroV1Strategy
  -> DualTrendLongExpansionPullbackBodyOnlyV1Strategy
  -> _DualTrendLongExpansionMixin
  -> DualTrendPyramidSecondAdd20V1Strategy
  -> DualTrendPyramidSecondAdd15V1Strategy
  -> DualTrendPyramidCloseFloor07V1Strategy
  -> DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy
  -> 更早的 Guard / Baseline / Raw 公共逻辑
```

SecondAdd20 的两次盈利加仓比例仍为第一笔 `25%`、第二笔 `20%`。新增多头只接受非深回踩强实体 `long_pullback_restart_1h_body`；`_deep_body`、无强实体 pullback 和 compression breakout 均过滤。

新增多头沿用通用 ROI、结构止损、移动止损和盈利保护，但不符合空头 tag 专属的两次盈利加仓资格。五年 7 笔 Micro 每笔均只有一次入场和一次出场。

## 修正后结果

Positive13/max3：

| 样本 | 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| 三年，2023-06-18 -> 2026-06-18 | SecondAdd20 | 314 | +199.22% | 2.682 | 4.82% | 51.27% |
| 三年 | LongMicro | 318 | +209.59% | 2.685 | 4.80% | 51.26% |
| 近一年，2025-06-18 -> 2026-06-18 | SecondAdd20 | 123 | +68.02% | 3.395 | 4.75% | 56.10% |
| 近一年 | LongMicro | 123 | +72.49% | 3.499 | 4.74% | 56.91% |
| 压力期，2026-03-01 -> 2026-05-31 | 两者相同 | 15 | +5.11% | 3.077 | 1.75% | 40.00% |
| 五年，有效起点 2021-07-29 | SecondAdd20 | 477 | +261.73% | 2.405 | 4.80% | 51.57% |
| 五年 | LongMicro | 481 | +277.37% | 2.429 | 4.78% | 51.56% |

五年方向拆分：

| 方向 | LongMicro | SecondAdd20 | 差值 |
|---|---:|---:|---:|
| Long | +707.24 USDT | +613.96 USDT | +93.28 USDT |
| Short | +2066.44 USDT | +2003.32 USDT | +63.12 USDT |
| Total | +2773.68 USDT | +2617.27 USDT | +156.41 USDT |

逐笔审计显示：422 笔空头全部同开仓、同平仓、同退出原因、同订单数，空头差值只是前序利润改变仓位金额后的复利结果。多头有 52 笔路径一致；候选新增 7 笔 Micro，并因共享槽位少了 3 笔日线多头。7 笔 Micro 合计 `+76.26 USDT`，不能把组合总差值 `+156.41 USDT` 全归因给该 tag。

独立年度中，有 Micro 成交的三个窗口为：

| 窗口 | SecondAdd20 | LongMicro | Micro 成交/利润 |
|---|---:|---:|---:|
| 2023-06-18 -> 2024-06-18 | +16.36% | +19.76% | 3 / +35.23 USDT |
| 2024-06-18 -> 2025-06-18 | +52.48% | +50.23% | 3 / -20.19 USDT |
| 2025-06-18 -> 2026-06-18 | +68.02% | +72.49% | 1 / +29.15 USDT |

候选并非逐年占优。2024-25 的负贡献和 7 笔小样本是当前最大不确定性。

Top20/max6：

| 样本 | 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| 三年 | SecondAdd20 | 339 | +180.62% | 2.445 | 5.287% | 53.10% |
| 三年 | LongMicro | 342 | +190.23% | 2.454 | 5.284% | 53.22% |
| 五年，有效起点 2021-07-29 | SecondAdd20 | 511 | +231.17% | 2.208 | 5.286% | 53.03% |
| 五年 | LongMicro | 515 | +243.23% | 2.229 | 5.289% | 52.62% |

Top20 五年 LongMicro 的 long/short 利润为 `+539.54 / +1892.73 USDT`，对照为 `+465.54 / +1846.19 USDT`。三年少 1 笔对照空头，该单仅 `-0.22 USDT`；五年各有 455 笔空头，但候选用一笔 `-0.01 USDT` 的空头替换了一笔 `+0.01 USDT` 的空头，其余 454 笔路径一致。存在轻微槽位扰动，没有实质挤压空头利润。修正后仍有泛化增益，但幅度低于旧的碰撞实现。

## 参数碰撞审计

- 父级 `DualTrendCombinedLongDailyCenterShortV1Strategy` 的 `long_breakout_buffer=0.009` 用于原日线多头。
- 扩展 mixin 旧代码也声明 `long_breakout_buffer=0.001`，MRO 导致 LongMicro 同时放松原日线多头。
- 修复后扩展分支使用 `long_expansion_breakout_buffer=0.001`，父级日线参数保持 `0.009`。
- 在 2021 独立窗口、`max_open_trades=100` 下，SecondAdd20、禁用扩展入场的诊断类和修正后 LongMicro 均为 81 笔，三者交易逐笔完全一致，证明隔离有效。
- Binance testnet 合约元数据使 Top20 三年基线从 339 笔变成 338 笔，不可用于 mainnet 结果复现；标准结果继续使用 mainnet 元数据。

## 策略角色

| 类名 | 当前角色 |
|---|---|
| `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 当前研究主候选；小样本观察升级 |
| `DualTrendPyramidSecondAdd20V1Strategy` | 稳定对照；不含新增 1h 多头 |
| `DualTrendPyramidSecondAdd20LongMicroCollisionReplayV1Strategy` | 固定小仓、无 protections 的 max100 反事实诊断别名；不用于运行或比较组合收益 |
| `DualTrendLongExpansionPullbackBodyMicroV1Strategy` | 候选实现父级；历史实验类名 |
| `DualTrendPyramidSecondAdd20LongMicroSideSlots3S1LV1Strategy` | 3 空 + 1 多槽位实验；已淘汰，不用于运行 |
| `DualTrendPyramidSecondAdd20LongMicroShortOnlyV1Strategy` / `LongOnlyV1Strategy` | 80/20 拆分资金诊断类；已淘汰，不用于运行 |
| `DualTrendPyramidSecondAdd15V1Strategy` | 仓位比例对照 |
| `DualTrendPyramidCloseFloor07V1Strategy` | 历史父级/诊断对照 |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 约 `+191.75%` 的历史候选 |
| `DualTrendRawStrategy` / `DualTrendBaselineStrategy` / `DualTrendGuardStrategy` | 原始、保本和 Guard 对照 |
| `DualTrendCombinedShortPullbackShapeV1Strategy` | Raw 向后兼容别名，不是当前候选 |

## 保留与淘汰

继续保留：

- 非深回踩强实体 `long_pullback_restart_1h_body`
- SecondAdd20 的原有空头、两次盈利加仓和盈利保护逻辑
- LongMicro 作为研究候选，SecondAdd20 作为稳定控制，不切换运行入口
- 修正后 LongMicro 的五年成本稳健性证据；只支持继续观察，不构成实盘晋级
- LongMicro 的小样本与集中度审计结论；明确要求样本外扩展，不围绕 BNB 或两笔 ROI 做拟合

继续淘汰或停止重复：

- `_deep_body`：深回踩后强拉在三年样本不干净，容易成为反弹诱多
- 全量 `long_pullback_restart_1h`、无强实体 pullback、compression breakout
- 空头 `+5%/+6%` 峰值回撤锁盈、`+7%/+8%` 后等待反转退出
- 原日线多头达到 `+5%/+7%` 后等待反转退出
- 直接移植 NFI 的超长 custom-exit 规则树
- 7 月 17 日基于碰撞实现的 Micro 25%/50%/75% 仓位缩放排名；这些数字需要视为失效证据，不据此继续调参
- Binance testnet 元数据覆盖作为可比较回测来源
- 通用 higher-low 加颈线突破：纯 tag 五年 452 笔、96 胜 356 负，六个年度段仅 2023 为正；不再调窗口、ATR 或按币筛选
- failed-breakdown reclaim：五年 5 笔、2 胜 3 负，单笔 ROI 依赖且四个年度无信号；保留记录，不进入组合验证
- PAIR/BTC 的 24/72 小时均线与 6 小时斜率硬过滤：被拒绝的非 BTC 多头仍有 10 笔、`+79.16 USDT`，日线拒绝组 PF 高于通过组；不再调均线周期
- Positive13 4H 多头广度至少 7/13：被拒绝组 22 笔、`+426.29 USDT`、PF `6.503`，显著优于通过组；日线压缩突破具有早期领先特征，不等待广度全面确认
- BTC 日线 `close < EMA50 < EMA200` 熊市保护：完整特征只覆盖 53/59 笔，仅挡到一笔 `+41.42 USDT` 的 PAXG 赢家；不扩展均线或窗口
- unrestricted max4：五年新增 37 笔空头归档利润 `-22.40 USDT`、PF `0.828`；总收益降至 `+273.47%`、PF `2.344`、MaxDD 升至 `5.29%`
- max4 的 3 空 + 1 多硬槽位：相对 max3 错过 17 笔日线多头，这些单合计 `+379.08 USDT`、PF `8.159`；组合仅 `+206.54%`
- 80% 空头 + 20% 多头独立资金池：五年 `+137.76%`、PF `2.092`、MaxDD `6.78%`，资金闲置且失去共享复利；不再调方向槽位、固定资金比例或拆 bot
- `short_pullback_restart` 优先于 `short_compression_breakdown` 的同 K 线排序：五年只改变 3 个时点，局部收益差 `-1.06%`；不写死 Tag 优先级
- 旧仓抢占：替换最老仓位明显为负；替换当时浮动收益最差仓位年度不稳且由单个事件主导；不新增提前平仓腾槽规则

下一步优先通过独立 LongMicro dry-run 和信号碰撞影子采集器继续收集样本外交易。五年成本压力已经完成并通过，小样本集中度也已量化；当前缺口是更多独立 Pair 和市场阶段，而不是新的历史阈值。保留至少 30 笔已关闭交易、至少四个完整观察周的晋级门槛。历史碰撞的同 K 线排序与旧仓机会成本已经补齐，预设规则均未通过；在出现新的样本外满槽碰撞前，不再做 Tag 排序或抢占参数搜索。不要重复调整市场状态、方向槽位、固定资金或手续费方向，不围绕仅 7 笔历史交易做细参数、Pair 白名单或退出拟合，也不继续扩宽多头 tag。

## 配置与运行入口

| 入口 | 文件内/实际策略 | 状态 |
|---|---|---|
| Positive13/max3 回测配置 | `DualTrendRawStrategy` | 旧默认；回测需命令行覆盖候选 |
| Top20/max6 回测配置 | `DualTrendPyramidSecondAdd20V1Strategy` | 稳定对照，不是候选 |
| Positive13/max3 dry-run 配置 | `DualTrendGuardStrategy` | 不是研究候选 |
| `start_positive13_max3_dryrun.ps1` | `DualTrendCombinedShortPullbackShapeV1Strategy` | 实际运行 Raw 兼容别名 |
| `config.dryrun.dualtrend.longmicro.positive13.max3.json` | `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 独立观察配置；8086、独立 SQLite，当前运行中 |
| `start_positive13_longmicro_observation.ps1` | `DualTrendPyramidSecondAdd20LongMicroV1Strategy` | 已于 2026-07-20 启动观察容器；保证主容器状态和身份不变 |
| `start_positive13_collision_shadow.ps1` | 只读 8086 API，独立 SQLite | 已于 2026-07-24 启动隐藏采集进程；不改变观察 bot 行为 |
| `docker-compose.yml` | 默认 `SampleStrategy` | 与 DualTrend 无自动关联 |

LongMicro 当前只作为隔离观察模拟盘运行，不代表已替换历史 Raw-compatible dry-run 配置或获准实盘。它使用独立容器、API、数据库、日志和报告目录；观察结果达到门槛前，不替换其他运行入口。

运行故障记录：2026-07-20 曾出现 Binance futures 主网 `exchangeInfo/klines` 451，随后自行恢复；2026-07-21 用户看到的停止状态由 Docker Desktop 关闭导致。启动脚本现在会在 Docker daemon 不可用时自动隐藏启动 Docker Desktop，状态脚本只报告当前容器启动周期内的告警，避免历史 451 和 Docker 关闭时的日志流错误被误报为当前故障。不要改用 testnet 元数据规避此问题。

## 标准复现命令

```powershell
docker --context desktop-linux compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json --strategy-path /freqtrade/user_data/strategies --strategy-list DualTrendPyramidSecondAdd20V1Strategy DualTrendPyramidSecondAdd20LongMicroV1Strategy --timeframe 1h --timeframe-detail 5m --timerange 20230618-20260618 --enable-protections --cache none --export trades
```

复现后至少核对策略类名、pair whitelist、`max_open_trades`、有效起止时间、初始钱包、protections 和 mainnet 市场元数据。

## 关键证据

- `user_data/reports/dualtrend_long_micro_parameter_collision_audit_2026-07-20.md`
- `user_data/reports/dualtrend_pandas_boolean_futurewarning_fix_2026-07-21.md`
- `user_data/reports/dualtrend_higher_low_reclaim_experiment_2026-07-21.md`
- `user_data/reports/dualtrend_failed_breakdown_reclaim_experiment_2026-07-21.md`
- `user_data/reports/dualtrend_long_market_state_filters_experiment_2026-07-22.md`
- `user_data/reports/dualtrend_side_slots_and_split_capital_experiment_2026-07-22.md`
- `user_data/reports/dualtrend_signal_collision_shadow_and_replay_2026-07-24.md`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_replay.md`
- `user_data/reports/dualtrend_collision_opportunity_cost_2026-07-27.md`
- `user_data/analysis/signal_collision_audit_2026-07-24/five_year/report/collision_opportunity_cost.md`
- `user_data/reports/dualtrend_longmicro_execution_cost_stress_2026-07-27.md`
- `user_data/analysis/longmicro_execution_stress_2026-07-27/report/execution_stress_report.md`
- `user_data/reports/dualtrend_longmicro_sample_concentration_audit_2026-07-27.md`
- `user_data/analysis/longmicro_sample_concentration_2026-07-27/sample_concentration_report.md`
- `user_data/reports/dualtrend_experiment_cleanup_2026-07-27.md`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13/backtest-result-2026-07-20_05-25-10.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13_five_year-2026-07-20_05-54-29.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_top20_three_year-2026-07-20_06-05-49.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_top20_five_year-2026-07-20_06-18-23.zip`
- `user_data/analysis/long_micro_validation_2026-07-20/corrected_control_2021_max100/backtest-result-2026-07-20_05-12-08.zip`
- `user_data/analysis/futurewarning_fix_2026-07-21-2026-07-21_01-43-22.zip`
- `user_data/analysis/higher_low_reclaim_2026-07-21/max100_five_year/backtest-result-2026-07-21_11-28-05.zip`
- `user_data/analysis/failed_breakdown_reclaim_2026-07-21/max100_five_year/backtest-result-2026-07-21_11-38-09.zip`
- `user_data/analysis/relative_strength_2026-07-22/`
- `user_data/analysis/side_slots_3s1l_2026-07-22/`
- `user_data/reports/longmicro_observation/README.md`
- `user_data/reports/dualtrend_nfi_peak_and_long_micro_upgrade_2026-07-17.md`（历史碰撞实现，仅保留实验脉络）

读取顺序：先读本文和当前代码，再读 2026-07-20 审计报告；其他日期型报告只作历史证据。新实验若替换候选，必须在同一变更中更新本文、`AGENTS.md`、结果、运行状态和淘汰方向。
