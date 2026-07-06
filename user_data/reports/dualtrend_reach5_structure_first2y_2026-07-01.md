# DualTrend Reach5 结构诊断

日期: 2026-07-01

目的:

- 只看 `short_pullback_restart`
- 只看已经先走到 `+5%` 的空头单
- 对比这些单在 `+5%` 节点时的结构差异，判断哪些更像应该继续放行到 `+10%+` 的真强单

样本口径:

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 周期: `1h + 5m detail`
- 区间: `2022-11-11 -> 2024-11-11`
- 策略: `DualTrendBaselineStrategy`, `DualTrendGuardStrategy`

## Baseline

- reach5 样本数: `41`
- 最终还能到 `+10%+`: `19` (46.3%)
- 到了 `+5%` 后没到 `+10%`: `22` (53.7%)

| 分组 | 到5%耗时 | 5%前不利波动 | 前6h收益 | 24h区间位置 | 4H EMA50斜率 | 距4H EMA50 | 1D center slope | BTC 4H downtrend | BTC距1D EMA50 | 最终利润 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reach10plus | 27.33h | 0.72% | -4.94% | 0.20 | -0.88% | -9.90% | -5.29% | 0.79 | -4.24% | 10.00% |
| giveback_before10 | 21.81h | 1.07% | -3.45% | 0.18 | -0.79% | -8.07% | -4.07% | 0.86 | -5.38% | 1.66% |

### 候选简单规则

| rule | coverage | reach10命中率 | 相对基线提升 | proxy_full_profit |
|---|---:|---:|---:|---:|
| pair_4h_ema50_slope_3 <= -0.005 AND pair_1h_ret_6h <= -0.02 | 68.3% | 53.6% | 7.2% | 5.88% |
| pair_1h_ret_6h <= -0.02 AND pair_1h_range_position_24h <= 0.4 | 68.3% | 53.6% | 7.2% | 5.87% |
| pair_4h_ema50_slope_3 <= -0.005 AND pair_1h_range_position_24h <= 0.3 | 70.7% | 48.3% | 1.9% | 5.76% |
| pair_1h_ret_6h <= -0.02 AND btc_1d_close_vs_ema50 <= -0.01 | 61.0% | 52.0% | 5.7% | 5.75% |
| pair_1h_ret_6h <= -0.02 AND btc_1d_close_vs_ema50 <= 0.0 | 65.9% | 51.9% | 5.5% | 5.75% |
| pair_4h_ema50_slope_3 <= -0.0075 AND pair_1h_range_position_24h <= 0.4 | 39.0% | 56.2% | 9.9% | 5.74% |

## Guard

- reach5 样本数: `40`
- 最终还能到 `+10%+`: `19` (47.5%)
- 到了 `+5%` 后没到 `+10%`: `21` (52.5%)

| 分组 | 到5%耗时 | 5%前不利波动 | 前6h收益 | 24h区间位置 | 4H EMA50斜率 | 距4H EMA50 | 1D center slope | BTC 4H downtrend | BTC距1D EMA50 | 最终利润 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reach10plus | 27.33h | 0.72% | -4.94% | 0.20 | -0.88% | -9.90% | -5.29% | 0.79 | -4.24% | 10.00% |
| giveback_before10 | 22.79h | 1.11% | -3.42% | 0.18 | -0.80% | -8.07% | -4.03% | 0.86 | -5.61% | 1.74% |

### 候选简单规则

| rule | coverage | reach10命中率 | 相对基线提升 | proxy_full_profit |
|---|---:|---:|---:|---:|
| pair_4h_ema50_slope_3 <= -0.005 AND pair_1h_ret_6h <= -0.02 | 67.5% | 55.6% | 8.1% | 6.02% |
| pair_1h_ret_6h <= -0.02 AND pair_1h_range_position_24h <= 0.4 | 67.5% | 55.6% | 8.1% | 6.02% |
| pair_4h_ema50_slope_3 <= -0.005 AND pair_1h_range_position_24h <= 0.3 | 70.0% | 50.0% | 2.5% | 5.91% |
| pair_1h_ret_6h <= -0.02 | 75.0% | 53.3% | 5.8% | 5.90% |
| pair_4h_ema50_slope_3 <= -0.0025 AND pair_1h_ret_6h <= -0.02 | 75.0% | 53.3% | 5.8% | 5.90% |
| pair_4h_close_vs_ema50 <= -0.03 AND pair_1h_ret_6h <= -0.02 | 75.0% | 53.3% | 5.8% | 5.90% |

## 总结

这轮结构诊断主要回答一个问题: 到了 `+5%` 之后，什么样的空头单更值得继续等 `+10%+`。

从样本上通常会重点关注这几类差异:

- 更快到 `+5%`
- 到 `+5%` 前回撤更小
- `+5%` 当下仍处于 4H 下行趋势中
- 价格相对 4H EMA50 仍明显偏弱
- BTC 大级别没有逆向抬头

如果这些条件在 `Baseline / Guard` 里都表现一致，下一步就值得围绕它们做更窄的一轮真实回测验证。
