# DualTrend LongV1ConfirmStrong 整理验证报告

生成时间：2026-06-16  
回测区间：全样本 2022-10-01 至 2026-05-07（实际因 startup 为 2022-11-11 起）；近期 2025-01-01 至 2026-05-07。  
实现版本：`LongV1ConfirmStrongRoi5Strategy` / `LongV1ConfirmStrongRoi6Strategy`。核心设定：只启用 `long_pullback_restart`，关闭 `long_compression_breakout`；下一根确认入场；确认 K 必须满足基本 K 线质量、成交量和 risk_pct_ok；增加 pair 4H EMA50 强斜率过滤；BTC 过滤保持 BTC 4H uptrend；不启用 3h/6h 跌回快速退出；不启用分批止盈。

## 1. 本次完成记录

- 修正 `DualTrendCompressionRestartLongPullbackConfirmNextV1Strategy`：确认 K 现在必须满足 `candle_quality_long`、`long_pullback_risk_pct_ok` 和 `volume > 0`。
- 新增正式 long-only 类：`LongV1ConfirmStrongRoi5Strategy`、`LongV1ConfirmStrongRoi6Strategy`。
- 新增合并验证类：`ShortPullbackLongV1ConfirmStrongRoi5Strategy`、`ShortPullbackLongV1ConfirmStrongRoi6Strategy`。合并类中 short 侧保持 pullback-only 和 10% ROI custom exit，long 侧分别测试 5%/6% ROI。
- 完成语法检查、策略加载检查、long-only 全样本/近期、手续费压力、滑点模拟、short-only 合并全样本/近期验证。

## 2. Long-only 总览

| 样本 | 策略 | Trades | 收益U | 收益% | PF | MaxDD% | Winrate% | Rejected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 全样本 | LongV1ConfirmStrongRoi5Strategy | 10 | 35.33 | 3.53 | 2.28 | 0.80 | 60.00 | 0 |
| 全样本 | LongV1ConfirmStrongRoi6Strategy | 10 | 24.47 | 2.45 | 1.69 | 1.59 | 50.00 | 0 |
| 近期 | LongV1ConfirmStrongRoi5Strategy | 2 | 2.39 | 0.24 | 1.31 | 0.77 | 50.00 | 0 |
| 近期 | LongV1ConfirmStrongRoi6Strategy | 2 | 4.41 | 0.44 | 1.57 | 0.77 | 50.00 | 0 |

结论：ROI5 全样本更稳，PF 2.28、MaxDD 0.80%；ROI6 全样本 PF 降到 1.69、MaxDD 增到 1.59%。近期只有 2 笔，统计意义偏弱，不能单独作为上线依据。

## 3. 成本压力测试

| 压力 | 策略 | Trades | 收益U | PF | MaxDD% | Winrate% |
| --- | --- | --- | --- | --- | --- | --- |
| 基准 | LongV1ConfirmStrongRoi5Strategy | 10 | 35.33 | 2.28 | 0.80 | 60.00 |
| 基准 | LongV1ConfirmStrongRoi6Strategy | 10 | 24.47 | 1.69 | 1.59 | 50.00 |
| 手续费1.5倍 | LongV1ConfirmStrongRoi5Strategy | 10 | 35.01 | 2.25 | 0.81 | 60.00 |
| 手续费1.5倍 | LongV1ConfirmStrongRoi6Strategy | 10 | 23.95 | 1.66 | 1.61 | 50.00 |
| 手续费2倍 | LongV1ConfirmStrongRoi5Strategy | 10 | 34.62 | 2.22 | 0.82 | 60.00 |
| 手续费2倍 | LongV1ConfirmStrongRoi6Strategy | 10 | 23.53 | 1.64 | 1.63 | 50.00 |
| 滑点0.05% | LongV1ConfirmStrongRoi5Strategy | 10 | 33.34 | 2.17 | 逐笔模拟 | 60.00 |
| 滑点0.05% | LongV1ConfirmStrongRoi6Strategy | 10 | 22.49 | 1.61 | 逐笔模拟 | 50.00 |
| 滑点0.10% | LongV1ConfirmStrongRoi5Strategy | 10 | 31.36 | 2.08 | 逐笔模拟 | 60.00 |
| 滑点0.10% | LongV1ConfirmStrongRoi6Strategy | 10 | 20.52 | 1.55 | 逐笔模拟 | 50.00 |

说明：手续费压力为真实 Freqtrade 回测；滑点为基于逐笔 `stake_amount` 的双边扣减模拟。低频确认版本对手续费不敏感，但 0.10% 双边滑点会明显压缩 ROI6 的 PF。

## 4. Long-only 拆解

### 全样本

#### LongV1ConfirmStrongRoi5Strategy

| Year | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/12/2023 | 4 | 27.85 | 8.88 | 75.00 |
| 31/12/2024 | 4 | 4.99 | 1.31 | 50.00 |
| 31/12/2025 | 2 | 2.48 | 1.31 | 50.00 |

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| DOGE/USDT:USDT | 2 | 19.57 | 1.96 | 0.00 | 100.00 |
| BNB/USDT:USDT | 3 | 17.60 | 1.76 | 5.98 | 66.67 |
| XRP/USDT:USDT | 2 | 2.48 | 0.25 | 1.31 | 50.00 |
| ZEC/USDT:USDT | 3 | -4.33 | -0.43 | 0.73 | 33.33 |

| Month | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 28/02/2023 | 1 | -3.54 | 0.00 | 0.00 |
| 30/11/2023 | 1 | 11.82 | 0.00 | 100.00 |
| 31/12/2023 | 2 | 19.57 | 0.00 | 100.00 |
| 29/02/2024 | 2 | 4.31 | 1.52 | 50.00 |
| 31/03/2024 | 1 | 8.56 | 0.00 | 100.00 |
| 31/10/2024 | 1 | -7.88 | 0.00 | 0.00 |
| 31/07/2025 | 1 | 10.49 | 0.00 | 100.00 |
| 30/09/2025 | 1 | -8.02 | 0.00 | 0.00 |

#### LongV1ConfirmStrongRoi6Strategy

| Year | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/12/2023 | 4 | 34.25 | 10.69 | 75.00 |
| 31/12/2024 | 4 | -14.28 | 0.41 | 25.00 |
| 31/12/2025 | 2 | 4.50 | 1.57 | 50.00 |

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| DOGE/USDT:USDT | 2 | 23.55 | 2.36 | 0.00 | 100.00 |
| XRP/USDT:USDT | 2 | 4.50 | 0.45 | 1.57 | 50.00 |
| BNB/USDT:USDT | 3 | -1.72 | -0.17 | 0.85 | 33.33 |
| ZEC/USDT:USDT | 3 | -1.87 | -0.19 | 0.88 | 33.33 |

| Month | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 28/02/2023 | 1 | -3.54 | 0.00 | 0.00 |
| 30/11/2023 | 1 | 14.23 | 0.00 | 100.00 |
| 31/12/2023 | 2 | 23.55 | 0.00 | 100.00 |
| 29/02/2024 | 2 | -16.45 | 0.00 | 0.00 |
| 31/03/2024 | 1 | 9.95 | 0.00 | 100.00 |
| 31/10/2024 | 1 | -7.78 | 0.00 | 0.00 |
| 31/07/2025 | 1 | 12.43 | 0.00 | 100.00 |
| 30/09/2025 | 1 | -7.93 | 0.00 | 0.00 |

### 近期样本

#### LongV1ConfirmStrongRoi5Strategy

| Year | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/12/2025 | 2 | 2.39 | 1.31 | 50.00 |

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| XRP/USDT:USDT | 2 | 2.39 | 0.24 | 1.31 | 50.00 |

| Month | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/07/2025 | 1 | 10.16 | 0.00 | 100.00 |
| 30/09/2025 | 1 | -7.77 | 0.00 | 0.00 |

#### LongV1ConfirmStrongRoi6Strategy

| Year | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/12/2025 | 2 | 4.41 | 1.57 | 50.00 |

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| XRP/USDT:USDT | 2 | 4.41 | 0.44 | 1.57 | 50.00 |

| Month | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- |
| 31/07/2025 | 1 | 12.19 | 0.00 | 100.00 |
| 30/09/2025 | 1 | -7.78 | 0.00 | 0.00 |

## 5. 与 Short-only Pullback 合并回测

| 样本 | 策略 | Trades | 收益U | 收益% | PF | MaxDD% | Winrate% | Rejected | Long | Short | Long收益U | Short收益U |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 全样本 | DualTrendCompressionRestartShortPullbackOnlyV1Strategy | 337 | 1007.05 | 100.71 | 1.52 | 10.17 | 31.45 | 160 | 0 | 337 | 0.00 | 1007.05 |
| 全样本 | ShortPullbackLongV1ConfirmStrongRoi5Strategy | 333 | 1202.49 | 120.25 | 1.60 | 9.66 | 31.83 | 172 | 10 | 323 | 8.88 | 1193.61 |
| 全样本 | ShortPullbackLongV1ConfirmStrongRoi6Strategy | 333 | 1211.02 | 121.10 | 1.60 | 9.70 | 31.83 | 172 | 10 | 323 | 16.19 | 1194.83 |
| 近期 | DualTrendCompressionRestartShortPullbackOnlyV1Strategy | 169 | 377.67 | 37.77 | 1.47 | 9.31 | 33.73 | 100 | 0 | 169 | 0.00 | 377.67 |
| 近期 | ShortPullbackLongV1ConfirmStrongRoi5Strategy | 166 | 481.42 | 48.14 | 1.59 | 9.69 | 34.34 | 105 | 2 | 164 | 8.05 | 473.37 |
| 近期 | ShortPullbackLongV1ConfirmStrongRoi6Strategy | 166 | 481.42 | 48.14 | 1.59 | 9.69 | 34.34 | 105 | 2 | 164 | 8.05 | 473.37 |

### Entry Tag 拆解：全样本

| 策略 | EntryTag | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| DualTrendCompressionRestartShortPullbackOnlyV1Strategy | short_pullback_restart | 337 | 1007.05 | 1.52 | 31.45 |
| ShortPullbackLongV1ConfirmStrongRoi5Strategy | short_pullback_restart | 323 | 1193.61 | 1.62 | 31.58 |
| ShortPullbackLongV1ConfirmStrongRoi5Strategy | long_pullback_confirm_next | 10 | 8.88 | 1.15 | 40.00 |
| ShortPullbackLongV1ConfirmStrongRoi6Strategy | short_pullback_restart | 323 | 1194.83 | 1.61 | 31.58 |
| ShortPullbackLongV1ConfirmStrongRoi6Strategy | long_pullback_confirm_next | 10 | 16.19 | 1.28 | 40.00 |

### Entry Tag 拆解：近期

| 策略 | EntryTag | Trades | 收益U | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| DualTrendCompressionRestartShortPullbackOnlyV1Strategy | short_pullback_restart | 169 | 377.67 | 1.47 | 33.73 |
| ShortPullbackLongV1ConfirmStrongRoi5Strategy | short_pullback_restart | 164 | 473.37 | 1.59 | 34.15 |
| ShortPullbackLongV1ConfirmStrongRoi5Strategy | long_pullback_confirm_next | 2 | 8.05 | 1.82 | 50.00 |
| ShortPullbackLongV1ConfirmStrongRoi6Strategy | short_pullback_restart | 164 | 473.37 | 1.59 | 34.15 |
| ShortPullbackLongV1ConfirmStrongRoi6Strategy | long_pullback_confirm_next | 2 | 8.05 | 1.82 | 50.00 |

### 资金竞争与信号冲突观察

| 样本 | 合并策略 | 交易数差(合并-单跑和) | 收益差U | Rejected增加 | 合并Long/单跑Long | 合并Short/单跑Short |
| --- | --- | --- | --- | --- | --- | --- |
| 全样本 | ShortPullbackLongV1ConfirmStrongRoi5Strategy | -14 | 160.11 | 12 | 10/10 | 323/337 |
| 全样本 | ShortPullbackLongV1ConfirmStrongRoi6Strategy | -14 | 179.50 | 12 | 10/10 | 323/337 |
| 近期 | ShortPullbackLongV1ConfirmStrongRoi5Strategy | -5 | 101.36 | 5 | 2/2 | 164/169 |
| 近期 | ShortPullbackLongV1ConfirmStrongRoi6Strategy | -5 | 99.34 | 5 | 2/2 | 164/169 |

观察：合并策略中 long 信号全部成交（全样本 10/10，近期 2/2），但 short 成交被挤出（全样本 323/337，近期 164/169），同时 rejected signals 增加。合并后全样本收益提升、回撤略降；近期收益提升但回撤略增。收益改善不完全来自 long 本身，更多是 long 插入后改变了 short 的成交顺序和资金槽位分配，所以这里存在明确的资金竞争/信号排队效应。

## 6. 结论

- 最佳 long-only 版本：ROI5 优先。全样本 PF 2.28、回撤 0.80%，费用 2 倍后 PF 仍 2.22。
- ROI6 不如 ROI5 稳：全样本 PF 1.69，手续费 2 倍后 1.64，回撤约为 ROI5 的两倍。
- 主要贡献 pair：DOGE、BNB；主要拖累 pair：ZEC。近期只剩 XRP 两笔，不足以证明近期稳定性。
- 合并 short-only 主策略：收益有提升，但不能简单归因于 long alpha；它同时挤出了部分 short 交易，并增加 rejected signals。
- 建议保留 `LongV1ConfirmStrongRoi5Strategy` 作为观察版/备选模块。若要并入主策略，应先做“long 独立资金槽位”或“仅在 short 无仓/弱信号阶段启用 long”的小范围验证，而不是继续调参。
