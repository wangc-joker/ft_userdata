# Positive13 Reach5 Strong Rule Search

基于 `positive13_reach5_diagnosis.csv` 对可解释的单变量/双变量规则进行枚举搜索。

说明：

- `hit_rate_reach10`：被识别为强单后，后续还能到 10%+ 的比例
- `coverage`：强单规则覆盖的 reach5 样本比例
- `proxy_full_profit_from_reach5`：弱单 5% 全平、强单继续 baseline 的粗略代理
- `proxy_half_profit_from_reach5`：弱单 5% 全平、强单 5% 平半后继续的粗略代理

## Top 12: Proxy Full Profit

| rule | terms | selected | coverage | hit_rate_reach10 | lift_vs_base | proxy_full_profit_from_reach5 | proxy_half_profit_from_reach5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| adverse_before_5pct <= 0.0125 | 1 | 84 | 69.4% | 75.0% | 6.4% | 6.65% | 5.82% |
| node_body_ratio >= 0.2 | 1 | 106 | 87.6% | 69.8% | 1.2% | 6.62% | 5.81% |
| adverse_before_5pct <= 0.0125 AND node_body_ratio >= 0.2 | 2 | 75 | 62.0% | 77.3% | 8.7% | 6.60% | 5.80% |
| node_body_ratio >= 0.3 | 1 | 100 | 82.6% | 71.0% | 2.4% | 6.54% | 5.77% |
| node_ret_1h <= -0.015 | 1 | 74 | 61.2% | 77.0% | 8.4% | 6.53% | 5.77% |
| node_ret_1h <= -0.015 AND node_close_vs_ema20 <= -0.005 | 2 | 74 | 61.2% | 77.0% | 8.4% | 6.53% | 5.77% |
| node_ret_1h <= -0.015 AND node_close_vs_ema20 <= -0.01 | 2 | 74 | 61.2% | 77.0% | 8.4% | 6.53% | 5.77% |
| node_ret_1h <= -0.015 AND node_close_vs_ema50 <= -0.005 | 2 | 74 | 61.2% | 77.0% | 8.4% | 6.53% | 5.77% |
| node_ret_1h <= -0.015 AND node_close_vs_ema50 <= -0.01 | 2 | 74 | 61.2% | 77.0% | 8.4% | 6.53% | 5.77% |
| node_close_vs_ema20 <= -0.01 | 1 | 84 | 69.4% | 73.8% | 5.2% | 6.53% | 5.76% |
| node_close_vs_ema20 <= -0.01 AND node_close_vs_ema50 <= -0.005 | 2 | 84 | 69.4% | 73.8% | 5.2% | 6.53% | 5.76% |
| node_close_vs_ema20 <= -0.01 AND node_close_vs_ema50 <= -0.01 | 2 | 84 | 69.4% | 73.8% | 5.2% | 6.53% | 5.76% |

## Top 12: Balanced Coverage

| rule | selected | coverage | hit_rate_reach10 | proxy_full_profit_from_reach5 |
|---|---:|---:|---:|---:|
| hours_to_5pct <= 12 AND node_ret_1h <= -0.01 | 31 | 25.6% | 90.3% | 5.98% |
| hours_to_5pct <= 12 AND node_close_vs_ema20 <= -0.005 | 31 | 25.6% | 90.3% | 5.98% |
| hours_to_5pct <= 12 AND node_close_vs_ema50 <= -0.005 | 31 | 25.6% | 90.3% | 5.98% |
| hours_to_5pct <= 12 AND node_close_vs_ema50 <= -0.01 | 31 | 25.6% | 90.3% | 5.98% |
| hours_to_5pct <= 12 AND node_body_ratio >= 0.2 | 34 | 28.1% | 88.2% | 5.97% |
| hours_to_5pct <= 12 AND node_body_ratio >= 0.3 | 33 | 27.3% | 87.9% | 5.93% |
| adverse_before_5pct <= 0.0075 AND node_ret_1h <= -0.015 | 31 | 25.6% | 87.1% | 5.91% |
| hours_to_5pct <= 12 | 37 | 30.6% | 86.5% | 6.02% |
| adverse_before_5pct <= 0.0125 AND node_ret_1h <= -0.015 | 49 | 40.5% | 85.7% | 6.38% |
| node_ret_1h <= -0.015 AND node_ret_3h <= -0.04 | 34 | 28.1% | 85.3% | 5.94% |
| adverse_before_5pct <= 0.0075 AND node_close_vs_ema20 <= -0.01 | 33 | 27.3% | 84.8% | 5.90% |
| node_ret_3h <= -0.04 AND node_body_ratio >= 0.2 | 33 | 27.3% | 84.8% | 5.90% |