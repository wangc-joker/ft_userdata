# DualTrend LongDailyCenterV1 旧 `long_1d_center_compression` 参考验证报告

日期：2026-06-16

## 1. 本次做了什么

本次目标是验证旧策略里的 `long_1d_center_compression` 是否值得作为新版 DualTrend 多头策略参考。

新增验证策略文件：

`D:\test\ft_userdata\user_data\strategies\DualTrendLongDailyCenterV1Strategy.py`

新增策略类：

| 策略类 | 用途 |
|---|---|
| `DualTrendLongDailyCenterV1Strategy` | 只启用日线中心压缩突破，多头结构退出，默认 ROI 10% |
| `DualTrendLongDailyCenterRoi5V1Strategy` | 同一入场，固定 ROI 5%，关闭结构 `custom_exit` |
| `DualTrendLongDailyCenterRoi6V1Strategy` | 同一入场，固定 ROI 6%，关闭结构 `custom_exit` |
| `DualTrendLongDailyCenterTop9V1Strategy` | Top9 旧币池限制版 |
| `DualTrendLongDailyCenterCore3V1Strategy` | BNB/DOGE/XRP 限制版，备用 |

## 2. 复刻的入场思想

旧 tag 的核心不是普通 1H 突破，而是日线级别结构启动：

```text
restart_ready_long_1d
+ center_breakout_long_1d
+ rsi_1d > 55
+ daily_long_signal 首次触发
= long_1d_center_compression
```

`center_breakout_long_1d` 由旧结构指标生成，包含：

```text
日线上升趋势
+ 曾经回踩
+ 结构未破
+ 区间收缩
+ 靠近前高压缩
+ 市场中心线抬高
+ 突破近期高点
+ 放量
```

这和当前 `LongV1ConfirmStrong` 不同：

| 模块 | 当前 LongV1ConfirmStrong | LongDailyCenterV1 |
|---|---|---|
| 主周期 | 1H 入场，4H/BTC 过滤 | 1D 结构触发，1H 执行 |
| 入场 | 下一根确认突破 | 日线中心压缩突破首次触发 |
| 出场 | ROI 5%/6% | 结构退出 + ROI 10% |
| 交易频率 | 很低 | 中低 |
| 目标 | 减少假突破 | 捕捉大级别趋势段 |

## 3. 全样本结果

样本：2023-05-14 至 2026-05-07，初始资金 1000U。

### max_open_trades = 2

| 币池/版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Top9 结构退出 | 52 | +554.62U / +55.46% | 2.47 | 6.95% | 36.5% |
| Top9 ROI 5% | 58 | +232.99U / +23.30% | 1.66 | 6.99% | 41.4% |
| Top9 ROI 6% | 55 | +239.20U / +23.92% | 1.71 | 7.04% | 38.2% |
| 13 币池结构退出 | 54 | +525.40U / +52.54% | 2.33 | 6.98% | 35.2% |
| 13 币池 ROI 5% | 61 | +237.77U / +23.78% | 1.64 | 7.84% | 41.0% |
| 13 币池 ROI 6% | 58 | +252.68U / +25.27% | 1.70 | 7.81% | 37.9% |
| BNB/DOGE/XRP 结构退出 | 12 | +187.52U / +18.75% | 3.43 | 4.63% | 41.7% |
| BNB/DOGE/XRP ROI 5% | 12 | +133.20U / +13.32% | 3.56 | 3.62% | 58.3% |
| BNB/DOGE/XRP ROI 6% | 12 | +124.19U / +12.42% | 2.95 | 4.64% | 50.0% |

结论：

`long_1d_center_compression` 的优势不只是入场，结构退出也很关键。固定 ROI 5% / 6% 会明显砍掉大趋势段收益。

## 4. 近期样本结果

样本：2025-01-01 至 2026-05-07。

| 币池/版本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Top9 结构退出，max2 | 18 | +160.87U / +16.09% | 2.53 | 6.91% | 38.9% |
| 13 币池结构退出，max2 | 18 | +160.87U / +16.09% | 2.53 | 6.91% | 38.9% |
| BNB/DOGE/XRP 结构退出，max2 | 4 | +22.06U / +2.21% | 1.85 | 2.60% | 25.0% |

近期阶段，Top9 和 13 币池结果一致，因为额外币种基本没有贡献有效交易。

## 5. 单槽位 Long bot 结果

为了模拟独立 Long bot 只给 1 个资金槽位，补测 `max_open_trades = 1`。

| 币池/版本 | 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---|---:|---:|---:|---:|---:|
| Top9 结构退出，max1 | 全样本 | 38 | +600.15U / +60.01% | 2.07 | 15.95% | 34.2% |
| 13 币池结构退出，max1 | 全样本 | 40 | +537.27U / +53.73% | 1.91 | 15.70% | 32.5% |
| Top9 结构退出，max1 | 近期 | 11 | +227.91U / +22.79% | 3.19 | 9.92% | 45.5% |
| 13 币池结构退出，max1 | 近期 | 11 | +227.91U / +22.79% | 3.19 | 9.92% | 45.5% |

单槽位收益更集中，但回撤明显变大。原因是单槽位会让资金集中押在少数大级别信号上，吃到趋势时很好，连续假启动时也更疼。

## 6. pair 拆解

### Top9 结构退出，全样本 max2

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| BNB | 5 | +159.19U | 6.96 | 60.0% |
| TRX | 19 | +156.30U | 2.27 | 36.8% |
| BTC | 13 | +121.43U | 2.37 | 38.5% |
| ADA | 2 | +49.41U | 5.43 | 50.0% |
| XRP | 3 | +33.22U | 2.26 | 33.3% |
| SOL | 4 | +29.93U | 1.74 | 25.0% |
| ETH | 5 | +16.24U | 1.32 | 20.0% |
| ZEC | 0 | 0.00U | 0.00 | 0.0% |
| DOGE | 1 | -11.10U | 0.00 | 0.0% |

### 13 币池结构退出，全样本 max2

| Pair | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| BNB | 5 | +155.68U | 6.95 | 60.0% |
| TRX | 19 | +155.00U | 2.28 | 36.8% |
| BTC | 13 | +125.18U | 2.47 | 38.5% |
| ADA | 2 | +48.21U | 5.32 | 50.0% |
| XRP | 3 | +32.49U | 2.26 | 33.3% |
| SOL | 4 | +29.41U | 1.74 | 25.0% |
| ETH | 5 | +15.81U | 1.31 | 20.0% |
| LINK | 0 | 0.00U | 0.00 | 0.0% |
| SUI | 0 | 0.00U | 0.00 | 0.0% |
| ZEC | 0 | 0.00U | 0.00 | 0.0% |
| TAO | 0 | 0.00U | 0.00 | 0.0% |
| DOGE | 1 | -11.10U | 0.00 | 0.0% |
| NEAR | 2 | -25.27U | 0.00 | 0.0% |

## 7. 判断

### 是否值得参考

值得。

旧策略中 `long_1d_center_compression` 是真正有参考价值的多头模块，比 `long_reversal_breakout` 更值得继承。

### 不能直接照搬什么

不要把它直接塞进当前 `LongV1ConfirmStrongRoi5`。

原因：

1. 当前 Long V1 是 1H 突破确认逻辑；
2. `long_1d_center_compression` 是日线结构启动逻辑；
3. 两者持仓周期、止损逻辑、盈利来源不同；
4. 如果混在一个 tag 里，会让后续归因变脏。

### 更推荐的路线

保留两个独立 Long 分支：

| 分支 | 作用 |
|---|---|
| `LongV1ConfirmStrongRoi5` | 小币池、轻仓、低频 dry-run |
| `LongDailyCenterV1` | 日线结构趋势段验证，可作为 Long V2 主线候选 |

## 8. 下一步建议

下一步不要大范围调参，建议只做三件事：

1. 对 `LongDailyCenterV1` 做成本压力测试；
2. 测试去掉 DOGE / NEAR 后的 13 币池；
3. 测试和 Short-only Pullback 主策略双 bot 合并后的资金曲线。

当前临时结论：

`long_1d_center_compression` 可以作为新版多头 V2 的核心参考，但更适合用结构退出，不适合简单改成 ROI 5% / 6%。
