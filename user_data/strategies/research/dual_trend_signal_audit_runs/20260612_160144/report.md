# 双周期顺势压缩再启动策略信号审计报告

- 生成时间：2026-06-12T08:01:44.260013+00:00
- 数据目录：`user_data/data/binance/futures`
- BTC 过滤：开启
- timerange：`2025-01-01:2026-05-07`
- 交易对：`BTC, ETH, SOL`

## 参数快照

```text
trend_ema_fast_4h = 50
trend_ema_slow_4h = 200
trend_slope_lookback_4h = 3
atr_period_1h = 14
volume_ma_window_1h = 20
compression_window = 12
compression_half_window = 6
pretrend_window = 24
compression_atr_multiplier = 3.0
volume_breakout_multiplier = 1.2
breakout_buffer = 0.001
stop_atr_buffer = 0.2
min_stop_distance = 0.005
max_stop_distance = 0.05
pullback_min_depth = 0.008
pullback_max_depth = 0.08
high_zone_buffer = 0.965
low_zone_buffer = 1.035
candle_body_min = 0.35
long_close_position_min = 0.6
short_close_position_max = 0.4
```

## Pair 概览

| symbol | rows_1h | start                     | end                       | trend_up_4h_hours | trend_down_4h_hours | compression_ok_hours | vol_ok_hours | signal_count |
| ------ | ------- | ------------------------- | ------------------------- | ----------------- | ------------------- | -------------------- | ------------ | ------------ |
| SOL    | 11785   | 2025-01-01 00:00:00+00:00 | 2026-05-07 00:00:00+00:00 | 2753              | 4736                | 4236                 | 3165         | 72           |
| ETH    | 11785   | 2025-01-01 00:00:00+00:00 | 2026-05-07 00:00:00+00:00 | 3005              | 4324                | 4285                 | 3220         | 63           |
| BTC    | 11785   | 2025-01-01 00:00:00+00:00 | 2026-05-07 00:00:00+00:00 | 3489              | 3924                | 4399                 | 3220         | 59           |

## Entry Tag 概览

| symbol | entry_tag                   | side  | signals | first_signal              | last_signal               | avg_risk_pct | median_risk_pct | avg_forward_ret_6h | avg_forward_ret_24h | median_forward_ret_24h | avg_forward_ret_72h | avg_mfe_24h | avg_mae_24h |
| ------ | --------------------------- | ----- | ------- | ------------------------- | ------------------------- | ------------ | --------------- | ------------------ | ------------------- | ---------------------- | ------------------- | ----------- | ----------- |
| BTC    | short_pullback_restart      | short | 29      | 2025-01-12 09:00:00+00:00 | 2026-03-27 08:00:00+00:00 | 2.31%        | 2.11%           | 0.40%              | 0.45%               | 0.34%                  | 0.17%               | 2.64%       | -1.73%      |
| ETH    | short_pullback_restart      | short | 29      | 2025-01-09 13:00:00+00:00 | 2026-03-29 13:00:00+00:00 | 3.33%        | 3.44%           | 1.08%              | 2.26%               | 1.62%                  | 2.27%               | 7.73%       | -2.36%      |
| SOL    | short_pullback_restart      | short | 29      | 2025-02-05 15:00:00+00:00 | 2026-03-07 19:00:00+00:00 | 3.62%        | 3.94%           | 0.01%              | 1.16%               | 0.04%                  | 2.66%               | 4.73%       | -3.12%      |
| ETH    | long_pullback_restart       | long  | 24      | 2025-05-01 10:00:00+00:00 | 2026-05-06 09:00:00+00:00 | 2.92%        | 2.89%           | 0.40%              | 0.12%               | -0.24%                 | 0.45%               | 3.17%       | -3.05%      |
| SOL    | long_pullback_restart       | long  | 24      | 2025-01-25 16:00:00+00:00 | 2026-04-27 01:00:00+00:00 | 3.06%        | 3.30%           | -0.48%             | -1.14%              | -1.04%                 | 0.43%               | 2.24%       | -3.23%      |
| BTC    | long_pullback_restart       | long  | 22      | 2025-01-04 20:00:00+00:00 | 2026-05-06 08:00:00+00:00 | 1.77%        | 1.78%           | -0.38%             | -0.43%              | -0.34%                 | -1.12%              | 1.06%       | -1.54%      |
| SOL    | long_compression_breakout   | long  | 11      | 2025-04-25 07:00:00+00:00 | 2026-01-13 22:00:00+00:00 | 3.45%        | 3.43%           | -1.10%             | -1.79%              | -2.27%                 | -1.67%              | 1.93%       | -4.03%      |
| SOL    | short_compression_breakdown | short | 8       | 2025-02-05 15:00:00+00:00 | 2026-03-07 19:00:00+00:00 | 3.94%        | 3.98%           | 0.60%              | 3.33%               | 3.69%                  | 4.04%               | 5.99%       | -2.46%      |
| ETH    | short_compression_breakdown | short | 6       | 2025-02-01 19:00:00+00:00 | 2025-10-30 12:00:00+00:00 | 3.56%        | 3.56%           | 1.83%              | 6.97%               | 6.38%                  | 5.08%               | 18.76%      | -1.95%      |
| BTC    | long_compression_breakout   | long  | 4       | 2025-05-08 15:00:00+00:00 | 2026-04-14 13:00:00+00:00 | 2.22%        | 2.22%           | -0.02%             | -0.38%              | -0.84%                 | 1.07%               | 1.32%       | -1.43%      |
| BTC    | short_compression_breakdown | short | 4       | 2025-04-03 14:00:00+00:00 | 2026-03-27 08:00:00+00:00 | 2.73%        | 2.77%           | 1.19%              | 1.19%               | 0.65%                  | 2.25%               | 2.90%       | -1.23%      |
| ETH    | long_compression_breakout   | long  | 4       | 2025-07-03 13:00:00+00:00 | 2026-04-10 14:00:00+00:00 | 3.08%        | 3.13%           | 0.92%              | -0.11%              | -1.58%                 | 1.67%               | 2.54%       | -2.64%      |

## 最近信号样本

| date                      | symbol | entry_tag                   | side  | close   | risk_pct | forward_ret_24h | mfe_24h | mae_24h |
| ------------------------- | ------ | --------------------------- | ----- | ------- | -------- | --------------- | ------- | ------- |
| 2026-05-06 09:00:00+00:00 | ETH    | long_pullback_restart       | long  | 2411.55 | 2.58%    |                 | 0.45%   | -3.50%  |
| 2026-05-06 08:00:00+00:00 | BTC    | long_pullback_restart       | long  | 81903.6 | 1.63%    |                 | 1.13%   | -1.19%  |
| 2026-04-27 01:00:00+00:00 | SOL    | long_pullback_restart       | long  | 87.79   | 2.25%    | -3.91%          | 0.33%   | -4.82%  |
| 2026-04-26 04:00:00+00:00 | BTC    | long_pullback_restart       | long  | 77727.0 | 0.86%    | 1.49%           | 2.22%   | -0.07%  |
| 2026-04-15 19:00:00+00:00 | ETH    | long_pullback_restart       | long  | 2373.7  | 2.98%    | -0.64%          | 0.26%   | -3.83%  |
| 2026-04-15 19:00:00+00:00 | BTC    | long_pullback_restart       | long  | 74957.8 | 2.14%    | 0.47%           | 0.62%   | -2.27%  |
| 2026-04-14 13:00:00+00:00 | BTC    | long_pullback_restart       | long  | 75471.2 | 2.13%    | -1.93%          | 0.71%   | -2.68%  |
| 2026-04-14 13:00:00+00:00 | BTC    | long_compression_breakout   | long  | 75471.2 | 2.13%    | -1.93%          | 0.71%   | -2.68%  |
| 2026-04-10 14:00:00+00:00 | ETH    | long_compression_breakout   | long  | 2241.17 | 3.10%    | -0.01%          | 0.73%   | -0.98%  |
| 2026-04-10 14:00:00+00:00 | BTC    | long_compression_breakout   | long  | 72870.6 | 2.17%    | -0.29%          | 0.80%   | -0.77%  |
| 2026-04-10 14:00:00+00:00 | BTC    | long_pullback_restart       | long  | 72870.6 | 2.17%    | -0.29%          | 0.80%   | -0.77%  |
| 2026-04-10 14:00:00+00:00 | ETH    | long_pullback_restart       | long  | 2241.17 | 3.10%    | -0.01%          | 0.73%   | -0.98%  |
| 2026-03-29 13:00:00+00:00 | ETH    | short_pullback_restart      | short | 1986.12 | 1.77%    | -3.58%          | 2.56%   | -4.83%  |
| 2026-03-27 10:00:00+00:00 | ETH    | short_pullback_restart      | short | 1989.7  | 4.54%    | -0.30%          | 1.20%   | -0.98%  |
| 2026-03-27 08:00:00+00:00 | BTC    | short_pullback_restart      | short | 67876.6 | 2.48%    | 2.26%           | 3.63%   | -0.05%  |
| 2026-03-27 08:00:00+00:00 | BTC    | short_compression_breakdown | short | 67876.6 | 2.48%    | 2.26%           | 3.63%   | -0.05%  |
| 2026-03-07 19:00:00+00:00 | SOL    | short_pullback_restart      | short | 82.47   | 3.07%    | 0.04%           | 1.68%   | -1.90%  |
| 2026-03-07 19:00:00+00:00 | SOL    | short_compression_breakdown | short | 82.47   | 3.07%    | 0.04%           | 1.68%   | -1.90%  |
| 2026-03-07 19:00:00+00:00 | ETH    | short_pullback_restart      | short | 1954.01 | 2.18%    | -0.47%          | 1.62%   | -1.26%  |
| 2026-03-07 19:00:00+00:00 | BTC    | short_pullback_restart      | short | 67042.6 | 1.86%    | -0.38%          | 0.80%   | -1.66%  |
| 2026-02-17 14:00:00+00:00 | ETH    | short_pullback_restart      | short | 1947.55 | 3.34%    | -1.32%          | 0.39%   | -4.45%  |
| 2026-02-11 04:00:00+00:00 | BTC    | short_pullback_restart      | short | 67548.8 | 3.77%    | 0.83%           | 2.79%   | -1.85%  |
| 2026-02-10 18:00:00+00:00 | SOL    | short_pullback_restart      | short | 82.89   | 4.00%    | 3.92%           | 6.38%   | -1.72%  |
| 2026-02-10 18:00:00+00:00 | SOL    | short_compression_breakdown | short | 82.89   | 4.00%    | 3.92%           | 6.38%   | -1.72%  |
| 2026-02-09 07:00:00+00:00 | SOL    | short_pullback_restart      | short | 85.43   | 4.59%    | 0.99%           | 3.15%   | -3.64%  |
| 2026-02-03 16:00:00+00:00 | BTC    | short_pullback_restart      | short | 76458.2 | 3.59%    | 3.87%           | 4.90%   | -0.64%  |
| 2026-02-03 14:00:00+00:00 | SOL    | short_pullback_restart      | short | 100.79  | 4.50%    | 8.35%           | 8.60%   | -1.89%  |
| 2026-02-03 14:00:00+00:00 | ETH    | short_pullback_restart      | short | 2255.66 | 4.69%    | 3.92%           | 7.24%   | -4.18%  |
| 2026-01-29 14:00:00+00:00 | SOL    | short_pullback_restart      | short | 120.3   | 3.81%    | 3.46%           | 7.65%   | -0.07%  |
| 2026-01-29 14:00:00+00:00 | SOL    | short_compression_breakdown | short | 120.3   | 3.81%    | 3.46%           | 7.65%   | -0.07%  |

## 解读提醒

- 这是信号审计，不是完整交易回测。
- forward_ret / MFE / MAE 用未来价格做事后观察，只用于判断信号形态是否值得继续实现。
- 后续正式策略仍必须单独实现仓位、止损、分批止盈、protections 和完整回测。
