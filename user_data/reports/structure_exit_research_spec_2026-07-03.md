# Structure Exit Research Spec

生成日期: 2026-07-03

## 目标

放弃上一轮 `profit lock` 思路，改为研究“盈利单结构失效止盈”。

核心想法：

- 保留原来的结构止损和 `+2%` 保本；
- 不用固定的利润锁仓；
- 只在盈利已经成立之后，检查当前级别局部结构是否开始反向；
- 如果盈利单所在方向出现“盘整 -> 尝试续趋势 -> 失败回区间 -> 交易重心反向移动”，则止盈。

## 当前落地版本

本次先实现为 **1h 结构 research 版**，不改主策略：

- `DualTrendRawBreakevenStructureExitResearchStrategy`
- `DualTrendRawBreakevenGuardStructureExitResearchStrategy`

文件：

- [DualTrendMainStrategies.py](D:/test/ft_userdata/user_data/strategies/DualTrendMainStrategies.py)

## 规则翻译

### 生效前提

- 仅当 `current_profit >= 2%` 时才启用结构止盈；
- 也就是说，这个退出层是加在保本逻辑之上的，不会替代原始止损。

### 盘整区间识别

使用最近的 1h K 线识别：

- 盘整区间长度：最近 6 根 1h；
- 区间宽度需要足够窄：
  - 区间总宽度 <= `2.6 * atr_ref`
  - 且区间宽度占当前价格比例 <= `3%`

### 多头盈利单退出

若满足以下任一条件，则退出：

1. `structure_exit_long_failed_breakout`
   - 最近几根 K 曾经向上突破盘整区间上沿；
   - 但当前收盘又掉回区间内；
   - 同时 1h 市场重心开始下移；
   - 且当前价格跌回 `EMA20_1h` 下方。

2. `structure_exit_long_countertrend`
   - 当前盈利已经不低于 `3%`；
   - 1h 市场重心开始下移；
   - 价格位于 `EMA20_1h` 下方；
   - 当前 1h 收益已经明显转弱。

### 空头盈利单退出

镜像处理：

1. `structure_exit_short_failed_breakdown`
   - 最近几根 K 曾经向下跌破盘整区间下沿；
   - 但当前收盘又回到区间内；
   - 同时 1h 市场重心开始上移；
   - 且当前价格重新站回 `EMA20_1h` 上方。

2. `structure_exit_short_countertrend`
   - 当前盈利已经不低于 `3%`；
   - 1h 市场重心开始上移；
   - 价格位于 `EMA20_1h` 上方；
   - 当前 1h 收益已经明显转强。

## 本次没有做的事

- 没有改 `populate_entry_trend`
- 没有改主策略类
- 没有改 pair pool
- 没有加新的 15m informative 指标
- 没有直接并入 dry-run 策略

## 下一步建议

下一轮直接做对照回测：

1. `DualTrendRawBreakevenStrategy`
2. `DualTrendRawBreakevenStructureExitResearchStrategy`
3. `DualTrendRawBreakevenGuardStrategy`
4. `DualTrendRawBreakevenGuardStructureExitResearchStrategy`

建议先跑：

- 3年：`2023-06-18 -> 2026-06-18`
- 近1年：`2025-06-18 -> 2026-06-18`
- 压力期：`2026-03-01 -> 2026-05-31`
- 修复期：`2026-06-01 -> 2026-06-18`

重点回答：

- 结构止盈是否能减少“大盈利单回吐”；
- 是否比上一轮 `profit lock` 更少切掉大盈利单；
- 是否会让 `short_pullback_restart` 主利润结构受损；
- `structure_exit_*` 退出原因分别贡献多少收益。
