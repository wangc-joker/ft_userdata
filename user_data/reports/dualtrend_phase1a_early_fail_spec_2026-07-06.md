# DualTrend Phase 1A Early-Fail 研究说明

## 研究对象

- 主基线：`DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`
- 研究版：`DualTrendEarlyFailPhase1AStrategy`
- 文件：`D:/test/ft_userdata/user_data/strategies/DualTrendMainStrategies.py`

## 本轮只改什么

只新增两类 short 方向早失败退出：

1. `short_pullback_restart`
2. `short_compression_breakdown`

退出发生在开仓后前几小时内，用于处理：

- 假跌破
- 跌破后快速收回区间
- 入场后很快出现 1H 重心上移
- 很快失去 4H / BTC 支持

## 本轮明确不改什么

- 不改 `populate_entry_trend`
- 不改 pair pool
- 不改 `max_open_trades`
- 不改 leverage
- 不改初始结构止损
- 不改保本规则
- 不改 `reach5` 强单放行逻辑
- 不改减仓逻辑
- 不改加仓逻辑

## 研究版新增退出

### `short_pullback_restart`

- `early_fail_short_pullback_reclaim`
  条件：
  开仓后 `6h` 内，利润未明显扩展，价格重新收回 `compression_low` 上方，同时 1H 重心上移，且价格重新站回 `EMA20` 附近/上方。

- `early_fail_short_pullback_trend_flip`
  条件：
  开仓后 `3h` 内，pair 4H 已经不再支持做空。

- `early_fail_short_pullback_btc_flip`
  条件：
  开仓后 `6h` 内，非 BTC 币种的 BTC 4H 已转为支持做多，且当前利润很薄。

### `short_compression_breakdown`

- `early_fail_short_breakdown_reclaim`
  条件：
  开仓后 `6h` 内，价格重新收回 `compression_low` 上方，同时 1H 重心上移。

- `early_fail_short_breakdown_ema_reclaim`
  条件：
  开仓后 `6h` 内，价格重新收回 `compression_low` 上方，并重新站回 `EMA20` 附近/上方。

- `early_fail_short_breakdown_trend_flip`
  条件：
  开仓后 `3h` 内，pair 4H 已不再支持做空。

- `early_fail_short_breakdown_btc_flip`
  条件：
  开仓后 `6h` 内，BTC 4H 不再支持做空，且当前利润很薄。

## 当前参数

- `early_fail_short_window_hours = 6`
- `early_fail_trend_flip_window_hours = 3`
- `early_fail_profit_cap = 0.01`
- `early_fail_close_vs_ema20_min = 0.0`

## 本轮回测重点

需要重点回答：

1. 三年收益是否提升
2. 压力期是否改善
3. `short_compression_breakdown` 是否减少假跌破亏损
4. `short_pullback_restart` 是否减少快速反抽亏损
5. 是否误杀了太多原本能走成趋势单的交易
6. 新 exit_reason 分别触发多少次、贡献多少净收益
