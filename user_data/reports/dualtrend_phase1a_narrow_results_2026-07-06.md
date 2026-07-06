# DualTrend Phase 1A Narrow 验证结果

日期：2026-07-06

## 本轮完成内容

在 `DualTrendEarlyFailPhase1AStrategy` 基础上继续收缩，新增：

- `DualTrendEarlyFailCompressionOnlyNarrowStrategy`

设计约束：

1. 只作用于 `short_compression_breakdown`
2. 只在开仓后 `<= 3h`
3. 只在 `current_profit <= 0`
4. 只保留：
   - 跌破失败后重新站回 `compression_low`
   - 同时 `legacy_market_center` 上移
5. 不再使用：
   - `short_pullback_restart` 早退
   - BTC flip
   - EMA reclaim
   - trend flip

目标：

- 尽量保留 Phase 1A 在压力期“减少假 breakdown”的优点
- 同时避免 Phase 1A 全量版对 3 年总收益的明显伤害

## 对比对象

基线：

- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

参考上一轮：

- `DualTrendEarlyFailPhase1AStrategy`

## 回测结果

### 3 年样本 `2023-06-18 -> 2026-06-18`

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 335 | 155.07% | 2.22 | 5.77% | 52.8% |
| Phase 1A 全量 | 349 | 138.46% | 2.18 | 7.79% | 46.4% |
| Narrow | 335 | 148.34% | 2.19 | 5.78% | 52.5% |

解读：

- Narrow 明显比 Phase 1A 全量版更克制。
- 3 年收益从 `138.46%` 修复到 `148.34%`。
- 但仍低于基线 `155.07%`。
- PF 也略低于基线。
- 回撤几乎与基线一致，没有带来额外风控收益。

### 压力期 `2026-03-01 -> 2026-05-31`

| 策略 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 基线 | 20 | 1.91% | 1.38 | 3.30% | 35.0% |
| Phase 1A 全量 | 20 | 3.51% | 2.03 | 2.04% | 35.0% |
| Narrow | 20 | 1.91% | 1.38 | 3.30% | 35.0% |

解读：

- Narrow 在压力期没有保留住 Phase 1A 全量版的改进。
- 结果基本回到了基线。
- 说明当前“只留最弱 reclaim 条件”的版本过于保守，已经没有实际策略增益。

## 按 tag 看

### 3 年样本

- 基线：
  - `short_pullback_restart`: `75.49%`
  - `short_compression_breakdown`: `26.76%`
  - `long_1d_center_compression`: `52.82%`
- Narrow：
  - `short_pullback_restart`: `74.13%`
  - `short_compression_breakdown`: `22.18%`
  - `long_1d_center_compression`: `52.04%`

结论：

- 这版没有破坏 long。
- 也没有明显破坏 `short_pullback_restart`。
- 但 `short_compression_breakdown` 依然从 `26.76%` 降到 `22.18%`。
- 说明即便是更窄的 reclaim 早退，仍然存在误杀问题。

## Narrow 退出触发情况

3 年中新增退出：

- `early_fail_short_breakdown_reclaim_narrow`
  - 触发：`5` 次
  - 总收益：`-38.474 USDT`
  - 平均：`-1.89%`

这说明：

- 这版其实已经非常少触发
- 但少量触发也没有换来压力期改进
- 因而性价比不高

## 本轮结论

### 结论一句话

`DualTrendEarlyFailCompressionOnlyNarrowStrategy` 比 Phase 1A 全量版稳，但没有优于基线，也没有保住压力期优势。

### 是否进入主线

- 不进入主线

### 当前主线保持

- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`

## 对后续优化的启示

这轮结果说明：

1. 方向没错：
   - 压力期确实存在“假 breakdown 提前认错”空间
2. 但直接用静态 reclaim 条件不够：
   - 激进版会误杀太多
   - 保守版又几乎不起作用
3. 如果继续做这个方向，下一步应该从“条件质量”而不是“条件数量”入手：
   - reclaim 后收盘位置质量
   - reclaim 当根实体强弱
   - reclaim 前后 1h / 4h 波动环境
   - 是否同时出现 BTC 反向确认

也就是说，后面更适合做“高质量坏信号识别”，而不是继续机械收紧窗口。
