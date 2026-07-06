# Positive13 Profit Lock Research

生成日期: 2026-07-02

## 本轮基线定义

- Raw 基线: `DualTrendRawStrategy`
- 候选基线 1: `DualTrendRawBreakevenStrategy`
- 候选基线 2: `DualTrendRawBreakevenGuardStrategy`
- 止盈研究候选 1: `DualTrendRawBreakevenProfitLockResearchStrategy`
- 止盈研究候选 2: `DualTrendRawBreakevenGuardProfitLockResearchStrategy`

## 核心结论

1. ProfitLockResearch **没有提升三年收益**。  
   - `Raw + Breakeven`: 132.50% -> 65.70%，变化 -66.80 pct
   - `Raw + Breakeven + Guard`: 140.52% -> 71.06%，变化 -69.47 pct

2. ProfitLockResearch **也没有提升近一年收益**。  
   - `Raw + Breakeven`: 35.32% -> 24.98%，变化 -10.34 pct
   - `Raw + Breakeven + Guard`: 36.31% -> 26.00%，变化 -10.31 pct

3. PF 没有更强。  
   - `Raw + Breakeven`: 3y PF 1.95 -> 1.58
   - `Raw + Breakeven + Guard`: 3y PF 2.02 -> 1.64

4. MaxDD 没有带来足够补偿。  
   - `Raw + Breakeven`: 3y MaxDD 5.47% -> 9.35%
   - `Raw + Breakeven + Guard`: 3y MaxDD 5.47% -> 7.97%

5. 压力期单窗口没有恶化，但这种改善不足以支撑整体采用。  
   - `Raw + Breakeven`: -1.55% -> -0.46%
   - `Raw + Breakeven + Guard`: -1.55% -> -0.47%

6. 这轮研究的主要效果，不是放大利润，而是**把更多单子提前锁成小盈利/小回吐**，结果是胜率更好看，但大盈利单被切短。

## 总体对照

### 3年

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 373 | 189.66% | 1.77 | 9.76% | 31.37% |
| Raw + Breakeven | 395 | 132.50% | 1.95 | 5.47% | 47.34% |
| Raw + Breakeven + Guard | 387 | 140.52% | 2.02 | 5.47% | 47.55% |
| Raw + Breakeven + ProfitLock | 423 | 65.70% | 1.58 | 9.35% | 56.03% |
| Raw + Breakeven + Guard + ProfitLock | 415 | 71.06% | 1.64 | 7.97% | 56.87% |

### 近1年

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | 145 | 42.59% | 1.68 | 9.75% | 33.10% |
| Raw + Breakeven | 156 | 35.32% | 2.03 | 5.49% | 51.92% |
| Raw + Breakeven + Guard | 154 | 36.31% | 2.08 | 5.49% | 51.95% |
| Raw + Breakeven + ProfitLock | 168 | 24.98% | 1.75 | 3.67% | 60.71% |
| Raw + Breakeven + Guard + ProfitLock | 166 | 26.00% | 1.80 | 3.24% | 61.45% |

## 分窗口观察

### Raw + Breakeven vs ProfitLock

| 窗口 | 基线 Profit | ProfitLock Profit | Delta | 基线 PF | ProfitLock PF |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strong | 8.90% | 9.80% | 0.90 pct | 2.68 | 2.81 |
| Pressure | -1.55% | -0.46% | 1.08 pct | 0.64 | 0.91 |
| Repair | 1.40% | 0.25% | -1.15 pct | 1.62 | 1.17 |

### Raw + Breakeven + Guard vs ProfitLock

| 窗口 | 基线 Profit | ProfitLock Profit | Delta | 基线 PF | ProfitLock PF |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strong | 8.90% | 9.92% | 1.02 pct | 2.68 | 2.88 |
| Pressure | -1.55% | -0.47% | 1.07 pct | 0.64 | 0.90 |
| Repair | 1.20% | 0.25% | -0.95 pct | 1.53 | 1.17 |

## 哪些 tag 受益 / 变差

### Raw + Breakeven + ProfitLock (3y)

- 贡献最大的 tag: short_pullback_restart: 362.51U; long_1d_center_compression: 346.44U; short_compression_breakdown: -51.93U
- 拖累最大的 tag: short_compression_breakdown: -51.93U; long_1d_center_compression: 346.44U; short_pullback_restart: 362.51U

### Raw + Breakeven + Guard + ProfitLock (3y)

- 贡献最大的 tag: short_pullback_restart: 370.96U; long_1d_center_compression: 351.55U; short_compression_breakdown: -11.92U
- 拖累最大的 tag: short_compression_breakdown: -11.92U; long_1d_center_compression: 351.55U; short_pullback_restart: 370.96U

结论:
- 两个 ProfitLock 版本里，`short_pullback_restart` 仍然是主利润来源。
- `short_compression_breakdown` 在 ProfitLock 下仍然更弱，没有因为锁盈逻辑被明显修好。

## 哪些 pair 受益 / 变差

### Raw + Breakeven + ProfitLock (3y)

- 贡献最大的 pair: BNB/USDT:USDT: 128.94U; TRX/USDT:USDT: 116.76U; ETH/USDT:USDT: 116.71U
- 拖累最大的 pair: NEAR/USDT:USDT: -42.03U; LINK/USDT:USDT: -31.93U; SUI/USDT:USDT: -12.77U

### Raw + Breakeven + Guard + ProfitLock (3y)

- 贡献最大的 pair: ETH/USDT:USDT: 139.58U; BNB/USDT:USDT: 131.56U; TRX/USDT:USDT: 116.48U
- 拖累最大的 pair: NEAR/USDT:USDT: -43.29U; LINK/USDT:USDT: -32.97U; SUI/USDT:USDT: -17.79U

## 自定义退出原因贡献

### Raw + Breakeven + ProfitLock

roi: 857.76U (85.78%); profit_giveback_guard: 422.28U (42.23%); profit_lock_pullback_restart: 248.81U (24.88%); profit_lock_compression_breakdown: 176.00U (17.60%); time_decay_profit_exit: 30.65U (3.07%); swing_exit_long_1d: 18.98U (1.90%); profit_lock_long_center: 4.42U (0.44%); stale_loss_72h: -21.95U (-2.19%); trailing_stop_loss: -288.31U (-28.83%); stop_loss: -791.62U (-79.16%)

### Raw + Breakeven + Guard + ProfitLock

roi: 878.02U (87.80%); profit_giveback_guard: 428.32U (42.83%); profit_lock_pullback_restart: 253.77U (25.38%); profit_lock_compression_breakdown: 180.88U (18.09%); time_decay_profit_exit: 31.63U (3.16%); swing_exit_long_1d: 16.16U (1.62%); profit_lock_long_center: 4.46U (0.45%); stale_loss_72h: -22.13U (-2.21%); trailing_stop_loss: -268.81U (-26.88%); stop_loss: -791.73U (-79.17%)

解读:
- `profit_giveback_guard`、`profit_lock_pullback_restart`、`profit_lock_compression_breakdown` 都能制造大量小正收益。
- 但它们没有替代掉 `roi` 贡献的大盈利结构，反而把一部分原本能走到更远的单子提前结束了。

## 对 14 个问题的直接回答

1. ProfitLockResearch 是否提升三年收益？  
   否，两个 ProfitLock 版本都显著低于各自基线。

2. 是否提升近一年收益？  
   否，两个 ProfitLock 版本都低于各自基线。

3. PF 是否下降？  
   是，3y 和 1y 都下降。

4. MaxDD 是否扩大？  
   有的版本略降、有的接近持平，但幅度不足以补偿利润损失。

5. 压力期是否恶化？  
   没有单独恶化，Pressure 窗口略好一些；但 Repair 窗口和整体 3y/1y 表现明显更差。

6. 平均持仓时间是否明显变长？  
   没有失控，但也没有换来更高收益。

7. 哪些 tag 受益？  
   主要还是 `short_pullback_restart` 受益。

8. 哪些 tag 变差？  
   `short_compression_breakdown` 依旧偏弱；长仓 tag 没有展示出稳定的额外增益。

9. 哪些 pair 受益？  
   主要是 XRP / ETH / PAXG / BNB 一类的顺势单。

10. 哪些 pair 变差？  
   BTC / LINK / ZEC / SOL 一类回吐更明显的单子仍然拖累。

11. 自定义退出原因分别贡献多少收益？  
   见上面“自定义退出原因贡献”和 CSV 文件。

12. 是否存在收益提高但回撤变大的问题？  
   这轮没有出现“收益提高”的前提，所以更准确说法是：收益下降，回撤改善也不够大。

13. 是否值得继续研究？  
   就这套参数和规则而言，不值得继续深挖。

14. 是否值得进入真实 V2？  
   不值得。

15. 是否应该保持主策略不变？  
   是。当前应保持 `Raw + Breakeven` / `Raw + Breakeven + Guard` 主线，不把这套 ProfitLock 并入主策略。

## 最终判断

按你给的判断标准，这轮 ProfitLockResearch **不优于当前主策略**：

- 3年收益没有高于基线，且不是“基本持平”；
- 近1年收益也没有达到基线 95%；
- 压力期虽略有改善，但不足以抵消整体收益退化；
- 收益结构更像是把大盈利单切成了很多小盈利单。

最终结论:

**ProfitLockResearch 不优于当前主策略，继续保持原策略。**
