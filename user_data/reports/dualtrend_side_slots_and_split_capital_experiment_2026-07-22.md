# DualTrend 方向槽位与拆分资金实验（2026-07-22）

## 目的与口径

本轮不修改任何多空信号、止损、ROI、空头两次盈利加仓或盈利保护，只研究当前 LongMicro 组合中的资金与槽位机会成本：

1. 将全局槽位从 max3 提高到 max4，并限制最多 3 个空头、1 个多头。
2. 将多空引擎完全拆开，按 80% 空头资金、20% 多头资金重组独立资金池。

标准对照仍是修正后的 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，Positive13、1000 USDT、1h + 5m detail、protections、Freqtrade 2026.3。五年有效区间为 2021-07-29 16:00 UTC 至 2026-06-18 00:00 UTC。

## 方向槽位

实验类 `DualTrendPyramidSecondAdd20LongMicroSideSlots3S1LV1Strategy` 使用全局 max4，但在 `confirm_trade_entry()` 中硬限制最多 3 个未平空头和 1 个未平多头。unrestricted max4 使用原候选，不施加方向限制。

近一年冒烟：

| 方案 | Trades | Profit | PF | MaxDD |
|---|---:|---:|---:|---:|
| 当前 max3 | 123 | +72.49% | 3.499 | 4.74% |
| unrestricted max4 | 138 | +72.51% | 3.33 | 4.00% |
| max4，3 空 + 1 多 | 123 | +55.42% | 3.01 | 4.76% |

unrestricted max4 在近一年收益几乎持平且回撤较低，因此继续做了五年验证：

| 方案 | Trades | Long / Short | Profit | PF | MaxDD | Long / Short Profit |
|---|---:|---:|---:|---:|---:|---:|
| 当前 max3 | 481 | 59 / 422 | +277.37% | 2.429 | 4.78% | +707.24 / +2066.44 USDT |
| unrestricted max4 | 514 | 59 / 455 | +273.47% | 2.344 | 5.29% | +707.40 / +2027.32 USDT |
| max4，3 空 + 1 多 | 470 | 42 / 428 | +206.54% | 2.172 | 4.78% | +289.22 / +1776.20 USDT |

逐笔集合审计：

- unrestricted max4 相对 max3 新增 37 笔空头，归档利润合计 `-22.40 USDT`、PF `0.828`；其中 10 笔 `short_compression_breakdown` 为 `-59.33 USDT`。它也因成交路径变化少了 4 笔 max3 空头，但这 4 笔本身为 `-25.15 USDT`。新增周转仍未抵消仓位和复利稀释，五年总收益下降、PF 下降、回撤上升。
- 3S1L 相对 max3 少了 17 笔 `long_1d_center_compression`。这些被挡多头在 max3 中合计 `+379.08 USDT`、PF `8.159`，主要来自 BTC、BNB、ETH、XRP 和 DOGE。
- 3S1L 换来的 6 笔额外空头只有 `-13.04 USDT`、PF `0.612`。硬限制一个长期多头槽位错误地删除了高质量日线持仓。

结论：unrestricted max4 与 3S1L 均淘汰。近一年 max4 的低回撤没有在五年泛化；不继续测试 max5、2S2L、3S2L 或其他槽位排列。

## 独立资金池

为避免“一个多头槽位”阻塞后续日线信号，又建立两个只关闭相反方向入场的实验类：

- `DualTrendPyramidSecondAdd20LongMicroShortOnlyV1Strategy`
- `DualTrendPyramidSecondAdd20LongMicroLongOnlyV1Strategy`

两组均在 1000 USDT、max3 下独立完成五年回测：

| 引擎 | Trades | Profit | PF | MaxDD |
|---|---:|---:|---:|---:|
| 只做空 | 428 | +162.26% | 2.059 | 8.63% |
| 只做多 | 60 | +39.77% | 3.227 | 4.34% |

按固定 80% 空头、20% 多头缩放两组逐笔利润并按平仓时间合并：

| 方案 | Trades | Profit | PF | MaxDD | CAGR |
|---|---:|---:|---:|---:|---:|
| 当前共享 max3 | 481 | +277.37% | 2.429 | 4.78% | - |
| 80/20 独立资金池 | 488 | +137.76% | 2.092 | 6.78% | 19.39% |

多头历史最小名义仓位为 `283.82 USDT`，按 20% 缩放后仍约 `56.76 USDT`，高于交易所最小下单额；结果不是最小订单取整造成的。

固定资金拆分失败的核心原因是：多头仅 60 笔且分布稀疏，20% 资金池大部分时间闲置；空头资金池也失去使用全账户权益动态复利的能力。共享 max3 让风险预算随实际信号流动，历史上明显优于提前固定方向预算。

## 最终结论

- 保留当前 Positive13/max3 共享钱包与共享槽位，不改运行配置。
- 当前研究主候选仍是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`；稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 淘汰 unrestricted max4、3S1L 方向槽位和 80/20 拆分资金池。
- 不再围绕方向槽位数量、固定多空资金比例或拆 bot 做参数搜索。下一步以 LongMicro dry-run 样本外观察为主。

## 保留证据

- `user_data/analysis/side_slots_3s1l_2026-07-22/five_year/backtest-result-2026-07-22_03-15-49.zip`
- `user_data/analysis/side_slots_3s1l_2026-07-22/smoke/backtest-result-2026-07-22_02-58-10.zip`
- `user_data/analysis/side_slots_3s1l_2026-07-22/split_capital/backtest-result-2026-07-22_03-33-28.zip`
- `user_data/analysis/side_slots_3s1l_2026-07-22/analyze_side_slots.py`
- `user_data/analysis/side_slots_3s1l_2026-07-22/audit.md`
- `user_data/analysis/side_slots_3s1l_2026-07-22/trade_differences.csv`
- `user_data/analysis/side_slots_3s1l_2026-07-22/analyze_split_capital.py`
- `user_data/analysis/side_slots_3s1l_2026-07-22/split_capital_audit.md`
