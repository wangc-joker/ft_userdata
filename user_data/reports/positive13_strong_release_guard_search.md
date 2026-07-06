# Positive13 Strong Release / Guard Offline Search

生成时间：2026-07-01

这轮是离线代理验证，不是新的 Freqtrade 回测结果。

原因：Docker 容器当前访问 Binance futures `exchangeInfo` 返回 `451 restricted location`，导致新增策略分支无法继续在线回测。

本报告只做两件事：

1. 在已导出的 `reach5` 诊断样本里，继续找更强的“5% 后放行强单”候选。
2. 在已导出的 false breakdown / quick reverse 特征表里，找更轻的坏信号 guard 候选。

## 1. Reach5 强单放行候选

- reach5 样本数：`121`
- 基线 reach10+ 比例：`68.6%`
- 基线 reach5 样本最终平均利润：`6.73%`

### Top candidates by proxy full profit

| rule | coverage | hit_rate_reach10 | proxy_full | proxy_half |
|---|---:|---:|---:|---:|
| adverse_before_5pct <= 0.0125 | 69.4% | 75.0% | 6.65% | 5.82% |
| node_body_ratio >= 0.2 | 87.6% | 69.8% | 6.62% | 5.81% |
| adverse_before_5pct <= 0.0125 AND node_body_ratio >= 0.2 | 62.0% | 77.3% | 6.60% | 5.80% |
| node_body_ratio >= 0.3 | 82.6% | 71.0% | 6.54% | 5.77% |
| node_close_vs_ema20 <= -0.01 | 69.4% | 73.8% | 6.53% | 5.76% |
| adverse_before_5pct <= 0.0125 AND node_body_ratio >= 0.3 | 60.3% | 78.1% | 6.52% | 5.76% |
| adverse_before_5pct <= 0.0175 | 81.8% | 69.7% | 6.52% | 5.76% |
| adverse_before_5pct <= 0.015 | 77.7% | 70.2% | 6.50% | 5.75% |

观察：

- 当前离线最强候选仍围绕 `adverse_before_5pct` 展开；最佳候选为 `adverse_before_5pct <= 0.0125`。
- 这和前面的回测结论是一致的：真正有信息量的，不是单纯冲得快，而是到 5% 前走得顺。
- 之前新加的 `node_ret_1h <= -1.5%` 在线回测已经失败，所以本轮即使个别离线组合看起来漂亮，也不把它直接升级成主候选。

## 2. 坏信号 guard 候选

### short_pullback_restart

| rule | blocked_share | bad_capture | loser_capture | winner_kill | quality |
|---|---:|---:|---:|---:|---:|
| breakdown_depth <= 0.005 | 53.3% | 56.4% | 61.5% | 37.9% | 0.260 |
| breakdown_depth <= 0.005 AND distance_to_ema50_4h >= -0.05 | 38.3% | 42.1% | 46.8% | 22.4% | 0.242 |
| breakdown_depth <= 0.004 | 42.5% | 44.4% | 48.6% | 31.0% | 0.195 |
| breakdown_depth <= 0.006 AND distance_to_ema50_4h >= -0.05 | 41.3% | 42.9% | 47.7% | 29.3% | 0.194 |
| breakdown_depth <= 0.005 AND distance_to_ema50_4h >= -0.04 | 30.5% | 33.8% | 36.7% | 19.0% | 0.187 |
| breakdown_depth <= 0.004 AND distance_to_ema50_4h >= -0.05 | 31.7% | 34.6% | 37.6% | 20.7% | 0.180 |

### short_compression_breakdown

| rule | blocked_share | bad_capture | loser_capture | winner_kill | quality |
|---|---:|---:|---:|---:|---:|
| atr_percentile_1h >= 0.25 AND compression_width >= 0.02 | 53.1% | 56.9% | 56.6% | 46.4% | 0.198 |
| prev_6h_return <= -0.008 AND pullback_depth >= 0.02 | 44.4% | 50.8% | 47.2% | 39.3% | 0.193 |
| prev_3h_return <= -0.004 AND atr_percentile_1h >= 0.3 | 37.0% | 41.5% | 41.5% | 28.6% | 0.187 |
| prev_6h_return <= -0.008 AND atr_percentile_1h >= 0.3 | 28.4% | 35.4% | 32.1% | 21.4% | 0.182 |
| prev_6h_return <= -0.008 | 45.7% | 52.3% | 47.2% | 42.9% | 0.180 |
| prev_3h_return <= -0.01 | 22.2% | 23.1% | 30.2% | 7.1% | 0.174 |

观察：

- `short_pullback_restart` 里，最有希望的仍是浅 breakdown depth 方向，但必须比 `<= 0.0063` 更保守。
- `short_compression_breakdown` 里，前 3h/6h 已经跌太多 + ATR 偏高，仍然是最像坏信号的组合。
- 只要 winner_kill 还在 30% 左右，这类 guard 就还不够资格直接并入主策略。

## 3. 当前结论

1. 离线结果继续支持当前主线：`Breakeven Only + 5% 小回撤强单放行`。
2. 更强的强单放行，目前仍应围绕 `adverse_before_5pct` 微调，而不是再叠追跌类瞬时动量条件。
3. 坏信号过滤并不是完全没线索，但暂时还没有看到“抓坏单很多、误杀好单很少”的干净规则。
4. 下一步最值得回测的，只应保留 1-2 条最轻量候选，等 Docker/网络恢复后再做正式验证。