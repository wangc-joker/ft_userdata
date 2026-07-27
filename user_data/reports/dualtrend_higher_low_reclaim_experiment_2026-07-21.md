# DualTrend Higher-Low Reclaim 多头实验

> 日期：2026-07-21。结论：淘汰，不替换当前候选，不进入 max3 组合验证。

## 假设

测试经典的 higher-low 加颈线收回结构，作为现有 `long_pullback_restart_1h_body` 之外的独立多头形态：

- pivot low 只在右侧两根 K 完成后确认；
- 第二低点比第一低点高 `0.05` 至 `2.0 ATR`；
- 两低点相隔 4 至 24 根 1h K；
- 中间反弹至少 `1.0 ATR`，形成颈线；
- 第二低点后 8 根 K 内，收盘首次突破颈线 `0.1%`；
- 同时要求 4h 趋势向上、价格在上升 EMA20 上方、波动率和 K 线收盘质量通过、BTC filter 通过；
- 结构止损位于第二低点下方 `0.2 ATR`，继续受现有最小/最大止损距离约束。

实现类：

- `DualTrendHigherLowOnlyV1Strategy`：只用于观察形态原始边际；
- `DualTrendPyramidSecondAdd20HigherLowV1Strategy`：SecondAdd20 加新形态；
- `DualTrendPyramidSecondAdd20LongMicroHigherLowV1Strategy`：保留供后续诊断，未进入本轮重型回测。

当前 `DualTrendPyramidSecondAdd20LongMicroV1Strategy` 没有修改，模拟盘没有切换或重启。

## 无前视验证

使用真实 BTC futures 1h 数据最后 20,000 根 K，对完整计算结果和长度为 2,000、5,000、10,000、15,000、19,999 的截断前缀逐列比较：

```text
PrefixConsistency=PASS
FullSignals=271
```

所有 higher-low 结构列完全一致，历史信号不会因未来 K 线加入而改变。

## 五年 max100 筛选

统一口径：Positive13、Freqtrade 2026.3 固定镜像、1h 加 5m detail、protections、1000 USDT、unlimited stake、`2021-07-29 -> 2026-06-18`。命令行设置 `max_open_trades=100`，实际最多只能同时持有 13 个白名单币种，因此报告显示 max 13。

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| SecondAdd20 对照 | 519 | +249.31% | 2.2638 | 5.2853% | 53.0% |
| HigherLowOnly 诊断总计 | 458 | -24.26% | 0.8073 | 31.5656% | 21.4% |
| SecondAdd20 + HigherLow | 938 | +121.82% | 1.3752 | 14.9679% | 38.5% |

max100 是形态筛选口径，不是当前权威 max3 收益复现。对照的 `+249.31%` 不替换 `CURRENT_DUALTREND.md` 中的标准五年结果。

### 新 tag 原始结果

纯诊断类中的 `long_higher_low_reclaim_1h`：

| Trades | Wins | Losses | Profit | PF |
|---:|---:|---:|---:|---:|
| 452 | 96 | 356 | -269.154896 USDT | 0.807306 |

按开仓年份拆分：

| 年份 | Trades | Wins | Profit |
|---|---:|---:|---:|
| 2021，7 月 29 日起 | 59 | 13 | -69.966394 USDT |
| 2022 | 36 | 5 | -32.238196 USDT |
| 2023 | 113 | 26 | +20.470642 USDT |
| 2024 | 128 | 27 | -58.224684 USDT |
| 2025 | 86 | 16 | -73.310099 USDT |
| 2026，截至 6 月 18 日 | 30 | 9 | -55.886165 USDT |

六个年度段只有 2023 为正，不具备年度稳定性。

### 加入组合后的结果

组合内新 tag 为 447 笔、94 胜 353 负、`-471.725935 USDT`。同时：

- 总收益从 `+249.31%` 降至 `+121.82%`；
- PF 从 `2.2638` 降至 `1.3752`；
- MaxDD 从 `5.2853%` 升至 `14.9679%`；
- 原日线多头从 55 笔减少到 31 笔；
- 空头从 464 笔减少到 460 笔，空头利润也因资金路径变化而下降。

这不是单纯的 max3 槽位挤压：在近似无槽位约束的 max100 诊断下，新 tag 本身已经是负期望。

## 诊断修正说明

归档中的 `DualTrendHigherLowOnlyV1Strategy` 总计混入 6 笔 PAXG `long_1d_center_compression`，原因是父级入场清空原先位于 pair allowlist 提前返回之后。代码已把清空顺序提前。

该问题只影响纯诊断类的总计行；452 笔 higher-low tag 行、年度拆分和实际 add-on 策略均不受影响。混入的 6 笔原日线多头盈利 `+26.584512 USDT`，反而让诊断总计看起来略好，不能逆转淘汰结论。

## 结论

- 淘汰通用 `long_higher_low_reclaim_1h`。
- 不继续做窗口、ATR、K 线质量或单币种筛选；原始 PF 已低于 1，继续调参容易过拟合。
- 不运行 max3、Top20 或 LongMicro 叠加重型验证。
- 当前候选继续保持 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`。

原始证据：`user_data/analysis/higher_low_reclaim_2026-07-21/max100_five_year/backtest-result-2026-07-21_11-28-05.zip`。
