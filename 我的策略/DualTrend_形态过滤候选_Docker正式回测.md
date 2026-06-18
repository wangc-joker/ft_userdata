# DualTrend 形态过滤候选 Docker 正式回测

## 1. 执行记录

1. 基于主策略 `DualTrendCombinedGlobalV2Strategy` 新增 3 个轻量验证分支。
2. 使用 Docker 容器内 `freqtrade 2026.4` 正式回测，不使用本机近似筛选。
3. 回测区间分为：
   - 全样本：`2023-05-07` 至 `2026-05-07`
   - 近期：`2025-05-07` 至 `2026-05-07`

新增验证分支：

- `DualTrendCombinedShortPullbackShapeV1Strategy`
  - 只强化 `short_pullback_restart`
  - 要求 `legacy_center_down_1d = True`
  - 要求 `close < legacy_market_center_1d`
  - 要求 `compression_width_pct <= 0.035`
- `DualTrendCombinedLongCenterStreakV1Strategy`
  - 只强化 `long_1d_center_compression`
  - 要求 `range_contracting_1d = True`
  - 要求 `legacy_center_up_1d` 连续至少 3 根
- `DualTrendCombinedShapeFocusedV1Strategy`
  - 同时启用上面两个过滤器

## 2. 全样本 3 年结果

| 版本 | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|
| `GlobalV2` | 360 | `+138.86%` / `+1388.56U` | 1.61 | 11.10% | 31.67% | 67 / 293 |
| `ShortPullbackShapeV1` | 320 | `+145.16%` / `+1451.58U` | 1.72 | 9.86% | 31.25% | 67 / 253 |
| `LongCenterStreakV1` | 339 | `+118.28%` / `+1182.75U` | 1.61 | 13.44% | 31.56% | 45 / 294 |
| `ShapeFocusedV1` | 299 | `+124.83%` / `+1248.30U` | 1.73 | 12.12% | 31.10% | 45 / 254 |

## 3. 近期 1 年结果

| 版本 | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|
| `GlobalV2` | 138 | `+30.47%` / `+304.65U` | 1.50 | 8.54% | 33.33% | 23 / 115 |
| `ShortPullbackShapeV1` | 118 | `+29.87%` / `+298.72U` | 1.57 | 6.03% | 32.20% | 23 / 95 |
| `LongCenterStreakV1` | 130 | `+32.31%` / `+323.05U` | 1.56 | 8.63% | 34.62% | 15 / 115 |
| `ShapeFocusedV1` | 110 | `+31.93%` / `+319.32U` | 1.66 | 6.02% | 33.64% | 15 / 95 |

## 4. Tag 级变化

### 4.1 ShortPullbackShapeV1

3 年：

- `short_pullback_restart`
  - 226 笔 -> 178 笔
  - `+46.44%` -> `+56.27%`
  - PF `1.32` -> `1.50`
- `short_compression_breakdown`
  - 67 笔 -> 75 笔
  - `+45.55%` -> `+42.25%`

1 年：

- `short_pullback_restart`
  - 92 笔 -> 69 笔
  - `+6.07%` -> `+8.05%`
  - PF `1.15` -> `1.27`
- `short_compression_breakdown`
  - 23 笔 -> 26 笔
  - `+11.92%` -> `+9.40%`

结论：

这个过滤器的核心作用是砍掉一批质量差的 `short_pullback_restart`，让 pullback short 更干净。全样本提升最明显，近期则主要体现为回撤下降、PF 上升。

### 4.2 LongCenterStreakV1

3 年：

- `long_1d_center_compression`
  - 67 笔 -> 45 笔
  - `+46.87%` -> `+35.28%`
  - PF `2.05` -> `2.37`
  - Winrate `32.84%` -> `33.33%`
- 组合总收益明显下降。

1 年：

- `long_1d_center_compression`
  - 23 笔 -> 15 笔
  - `+12.47%` -> `+14.05%`
  - PF `2.18` -> `3.43`
  - Winrate `34.78%` -> `46.67%`

结论：

这个过滤器对 long 本身的“纯度”提升很明显，尤其近一年改善最好；但全样本因为砍单过多，组合总收益被拉低。

### 4.3 ShapeFocusedV1

3 年：

- 比 `GlobalV2` 更稳：PF `1.73`，MaxDD `12.12%`
- 但收益低于 `ShortPullbackShapeV1`

1 年：

- PF 最高：`1.66`
- MaxDD 最低之一：`6.02%`
- 收益高于基线：`31.93% > 30.47%`

结论：

这是“更稳”的组合版，但不是“最赚钱”的组合版。它更像后续 dry-run 候选，不像当前收益最优候选。

## 5. 最终判断

### 5.1 最值得继续的

优先保留并继续验证：

- `DualTrendCombinedShortPullbackShapeV1Strategy`

原因：

- 3 年正式回测里，它是唯一同时做到：
  - 收益高于基线
  - PF 高于基线
  - MaxDD 低于基线
- 说明 `short_pullback_restart` 的“日线重心同向 + 更窄压缩”确实是有效过滤，不只是图感。

### 5.2 可以保留为次候选的

- `DualTrendCombinedShapeFocusedV1Strategy`

原因：

- 近期 1 年表现很均衡，PF 和 DD 最漂亮。
- 如果后面目标偏向 dry-run 稳定性，它有继续验证价值。

### 5.3 暂时不建议直接并入主策略的

- `DualTrendCombinedLongCenterStreakV1Strategy`

原因：

- long 质量提升是真的，但全样本砍单太多，导致组合总收益下降。
- 更适合继续微调 long 过滤强度，而不是直接全量替换。

## 6. 下一步建议

建议下一步按这个顺序做：

1. 先以 `ShortPullbackShapeV1` 为主线，再跑：
   - 成本压力
   - max_open_trades 3 / 4 / 5
   - pair 拆解
2. 再单独微调 long 过滤强度：
   - 把 `legacy_center_up` 连续 3 根，改成 `>=2` 或“3 根里至少 2 根”
   - 看能否保留 long 质量提升，同时减少砍掉的好单
3. 如果目标转向更稳的实盘候选，再把 `ShapeFocusedV1` 作为第二候选做 dry-run 准备
