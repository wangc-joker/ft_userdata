# 结构止盈研究报告

生成时间: 2026-07-03 10:49:59

## 研究对象

- `DualTrendRawBreakevenStrategy`
- `DualTrendRawBreakevenStructureExitResearchStrategy`
- `DualTrendRawBreakevenGuardStrategy`
- `DualTrendRawBreakevenGuardStructureExitResearchStrategy`

结构止盈逻辑：盈利后识别 1h 局部盘整、突破失败、交易重心反向移动，再提前止盈；不改入场。

## 核心结论

- `Raw + Breakeven`：3年收益 **138.07% -> 100.41%**，PF **2.14 -> 1.84**。
- `Guard + Breakeven`：3年收益 **144.67% -> 106.06%**，PF **2.21 -> 1.89**。
- 近1年也没有提升：Raw **41.15% -> 34.28%**；Guard **41.72% -> 34.92%**。
- 压力期有修补作用：Raw **-1.55% -> 0.38%**；Guard **-1.55% -> 0.38%**。
- 结论：**这版结构止盈不值得并入当前主策略**。它更像压力期局部补丁，但长期会提前切掉大量原本能走到 ROI 的单子。

## 总表

| Strategy | Window | Trades | Profit % | PF | MaxDD % | Winrate % |
|---|---:|---:|---:|---:|---:|---:|
| raw_breakeven | 3y | 326 | 138.07 | 2.14 | 7.13 | 49.69 |
| raw_breakeven_structure | 3y | 342 | 100.41 | 1.84 | 7.79 | 50.00 |
| guard_breakeven | 3y | 321 | 144.67 | 2.21 | 7.13 | 50.16 |
| guard_breakeven_structure | 3y | 337 | 106.06 | 1.89 | 7.79 | 50.45 |
| raw_breakeven | 1y | 129 | 41.15 | 2.32 | 4.75 | 53.49 |
| raw_breakeven_structure | 1y | 137 | 34.28 | 2.04 | 4.92 | 52.55 |
| guard_breakeven | 1y | 127 | 41.72 | 2.36 | 4.85 | 53.54 |
| guard_breakeven_structure | 1y | 135 | 34.92 | 2.08 | 4.92 | 52.59 |
| raw_breakeven | pressure | 18 | -1.55 | 0.64 | 3.30 | 33.33 |
| raw_breakeven_structure | pressure | 21 | 0.38 | 1.08 | 3.30 | 33.33 |
| guard_breakeven | pressure | 18 | -1.55 | 0.64 | 3.30 | 33.33 |
| guard_breakeven_structure | pressure | 21 | 0.38 | 1.08 | 3.30 | 33.33 |
| raw_breakeven | repair | 11 | 1.40 | 1.62 | 2.19 | 63.64 |
| raw_breakeven_structure | repair | 11 | 1.40 | 1.62 | 2.19 | 63.64 |
| guard_breakeven | repair | 10 | 1.20 | 1.53 | 2.19 | 60.00 |
| guard_breakeven_structure | repair | 10 | 1.20 | 1.53 | 2.19 | 60.00 |

## 对照解读

### Raw 主线
- 3年: 138.07% -> 100.41%
- 1年: 41.15% -> 34.28%
- 压力期: -1.55% -> 0.38%
- 修复期: 1.40% -> 1.40%
- 判断：压力期略有帮助，但长期和近1年都明显变差。

### Guard 主线
- 3年: 144.67% -> 106.06%
- 1年: 41.72% -> 34.92%
- 压力期: -1.55% -> 0.38%
- 修复期: 1.20% -> 1.20%
- 判断：Guard 本来已经更稳，这版结构止盈加上去以后，收益同样被削掉。

## 新退出原因贡献

- `guard_breakeven_structure` / `structure_exit_long_countertrend`: 10 笔, 216.23 USDT
- `guard_breakeven_structure` / `structure_exit_long_failed_breakout`: 7 笔, 100.44 USDT
- `guard_breakeven_structure` / `structure_exit_short_countertrend`: 18 笔, 255.14 USDT
- `guard_breakeven_structure` / `structure_exit_short_failed_breakdown`: 14 笔, 171.82 USDT
- `raw_breakeven_structure` / `structure_exit_long_countertrend`: 10 笔, 213.77 USDT
- `raw_breakeven_structure` / `structure_exit_long_failed_breakout`: 7 笔, 99.50 USDT
- `raw_breakeven_structure` / `structure_exit_short_countertrend`: 18 笔, 248.89 USDT
- `raw_breakeven_structure` / `structure_exit_short_failed_breakdown`: 14 笔, 166.74 USDT

这些退出本身多数是赚钱离场，但问题不在“赚没赚钱”，而在“是否比原来留到 ROI 更好”。从总收益看，答案是否定的。

## Tag 影响

### Raw
- 3y:
  - `long_1d_center_compression`: 51.36% / 47 -> 33.11% / 50
  - `short_compression_breakdown`: 17.39% / 87 -> 11.84% / 89
  - `short_pullback_restart`: 69.32% / 192 -> 55.45% / 203
- 1y:
  - `long_1d_center_compression`: 18.41% / 14 -> 11.85% / 16
  - `short_compression_breakdown`: -1.07% / 33 -> -1.73% / 34
  - `short_pullback_restart`: 23.81% / 82 -> 24.15% / 87

### Guard
- 3y:
  - `long_1d_center_compression`: 52.42% / 47 -> 33.79% / 50
  - `short_compression_breakdown`: 22.09% / 81 -> 16.16% / 83
  - `short_pullback_restart`: 70.16% / 193 -> 56.11% / 204
- 1y:
  - `long_1d_center_compression`: 18.32% / 14 -> 11.85% / 16
  - `short_compression_breakdown`: -0.52% / 31 -> -1.18% / 32
  - `short_pullback_restart`: 23.92% / 82 -> 24.25% / 87

最明显的现象是：主利润 short 标签 `short_pullback_restart`、`short_compression_breakdown` 并没有因为结构止盈变得更强，反而多数窗口被削弱。

## Pair 影响

### Raw 3y
- 受损最多的 5 个 pair:
  - `ADA/USDT:USDT`: 22.19% -> 15.44% (-6.75)
  - `BTC/USDT:USDT`: 11.66% -> 5.27% (-6.39)
  - `ETH/USDT:USDT`: 26.44% -> 20.24% (-6.20)
  - `DOGE/USDT:USDT`: 13.74% -> 8.77% (-4.97)
  - `PAXG/USDT:USDT`: 8.85% -> 4.28% (-4.57)
- 改善最多的 5 个 pair:
  - `NEAR/USDT:USDT`: -0.96% -> 0.22% (1.18)
  - `ZEC/USDT:USDT`: 14.49% -> 14.81% (0.32)
  - `SUI/USDT:USDT`: -2.78% -> -3.52% (-0.73)
  - `BNB/USDT:USDT`: 17.14% -> 16.28% (-0.86)
  - `SOL/USDT:USDT`: 5.23% -> 4.16% (-1.07)

### Guard 3y
- 受损最多的 5 个 pair:
  - `ADA/USDT:USDT`: 21.42% -> 14.63% (-6.79)
  - `ETH/USDT:USDT`: 29.40% -> 22.78% (-6.62)
  - `BTC/USDT:USDT`: 13.16% -> 6.80% (-6.36)
  - `DOGE/USDT:USDT`: 14.08% -> 8.98% (-5.09)
  - `PAXG/USDT:USDT`: 9.09% -> 4.43% (-4.67)
- 改善最多的 5 个 pair:
  - `NEAR/USDT:USDT`: -0.95% -> 0.30% (1.25)
  - `ZEC/USDT:USDT`: 14.74% -> 15.07% (0.33)
  - `SUI/USDT:USDT`: -2.83% -> -3.59% (-0.76)
  - `BNB/USDT:USDT`: 17.61% -> 16.64% (-0.96)
  - `SOL/USDT:USDT`: 6.28% -> 5.07% (-1.21)

总体看，并没有出现“弱 pair 被修复、强 pair 保持”的理想状态，更多是强 pair 利润被提前收掉。

## 最终结论

1. 这版结构止盈不优于当前 `breakeven` 基线。
2. 它只在压力期局部改善，无法覆盖 3 年和近 1 年的总收益损失。
3. 暂不建议并入主策略，也不建议直接进入 V2 实盘开发。
4. 如果未来还继续研究，应该改成更窄的条件化触发，而不是当前这种通用 1h 结构止盈。

## 产物

- [structure_exit_research_summary.csv](D:/test/ft_userdata/user_data/analysis/structure_exit_research_summary.csv)
- [structure_exit_research_exit_reasons.csv](D:/test/ft_userdata/user_data/analysis/structure_exit_research_exit_reasons.csv)
- [structure_exit_research_pairs.csv](D:/test/ft_userdata/user_data/analysis/structure_exit_research_pairs.csv)
- [structure_exit_research_tags.csv](D:/test/ft_userdata/user_data/analysis/structure_exit_research_tags.csv)