# DualTrend Failed-Breakdown Reclaim 多头实验

> 日期：2026-07-21。结论：样本过稀、单笔依赖，不采用，不进入组合验证。

## 形态定义

测试经典的流动性扫低后收回：

- 前一根 1h K 跌破过去 24 小时最低点；
- 跌破深度在 `0.05` 至 `0.8 ATR`；
- 前一根 K 收盘重新站上旧低点，阳线实体和收盘位置通过质量要求；
- 当前 K 不再创前一根低点，并收盘突破扫低 K 高点 `0.1%`；
- 入场时继续要求 4h 趋势向上、价格站在上升 EMA20 上方、波动率通过和 BTC filter 通过；
- 止损放在扫低点下方 `0.2 ATR`，同时受现有风险距离约束。

确认只引用前一根及更早 K 线，不使用未来 pivot。实现类：

- `DualTrendFailedBreakdownOnlyV1Strategy`：纯形态诊断；
- `DualTrendPyramidSecondAdd20FailedBreakdownV1Strategy`：预留组合诊断类，本轮未运行。

当前 LongMicro 候选和模拟盘均未修改。

## 五年筛选

口径：Positive13、Freqtrade 2026.3 固定镜像、1h 加 5m detail、protections、1000 USDT、unlimited stake、`2021-07-29 -> 2026-06-18`、`max_open_trades=100`。

| Trades | Wins | Losses | Profit | PF | MaxDD |
|---:|---:|---:|---:|---:|---:|
| 5 | 2 | 3 | +24.062314 USDT / +2.4062% | 136.7882 | 0.0092% |

PF 数字没有解释价值：亏损总额极小，而一笔 NEAR ROI 单贡献了几乎全部利润。

| Pair | Open date UTC | Profit | Exit |
|---|---|---:|---|
| BTC | 2023-02-01 21:00 | -0.037889 USDT | trailing stop |
| ETH | 2023-02-01 21:00 | -0.044772 USDT | trailing stop |
| NEAR | 2023-11-30 04:00 | +24.228998 USDT | 10% ROI |
| NEAR | 2024-04-09 10:00 | +0.010521 USDT | trailing stop |
| BTC | 2024-10-15 17:00 | -0.094543 USDT | trailing stop |

四笔非 ROI 交易合计约 `-0.166684 USDT`。2021、2022、2025 和 2026 没有任何成交，信号不能提供持续的多头覆盖。

## 结论

- 不把 `long_failed_breakdown_reclaim_1h` 加入当前候选。
- 不运行 max3、Top20 或 LongMicro 组合回测；5 笔不足以判断槽位和年度稳定性。
- 不在看到单笔赢家后扩大扫低深度、确认时限或删除趋势过滤，这会形成结果导向调参。
- 保留形态代码和原始归档，避免以后重复把这 5 笔误判为高 PF 优势。

原始证据：`user_data/analysis/failed_breakdown_reclaim_2026-07-21/max100_five_year/backtest-result-2026-07-21_11-38-09.zip`。
