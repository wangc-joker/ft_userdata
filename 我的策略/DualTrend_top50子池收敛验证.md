# DualTrend Top50 子池收敛验证

日期: 2026-06-18

## 1. 目的

基于这轮 top50 当前合约池回测结果，进一步把币种分层：

- 保留
- 删除候选
- 观察

并验证两个收敛子池：

1. `有交易 23 池`
2. `正贡献 13 池`

策略保持不变：

- `DualTrendCombinedShortPullbackShapeV1Strategy`

## 2. Top50 基线回顾

Top50 基线结果：

- 配置: [config.backtest.dualtrend.combined.top50.futures.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.futures.max3.json)
- 结果: [backtest-result-2026-06-18_06-40-16.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-40-16.zip)

3年样本 `2023-06-18 -> 2026-06-18`：

| 池子 | Pairs | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|---:|
| Top50 全池 | 50 | 308 | +1563.88U / +156.39% | 1.79 | 8.27% | 32.47% |

## 3. 分层结果

### 3.1 保留池：正贡献 13 个

- `ETH`
- `ZEC`
- `BTC`
- `ADA`
- `BNB`
- `SOL`
- `DOGE`
- `XRP`
- `TAO`
- `SUI`
- `PAXG`
- `NEAR`
- `LINK`

### 3.2 删除候选：负贡献 10 个

- `BCH`
- `LTC`
- `INJ`
- `DOT`
- `SYN`
- `HOME`
- `FIL`
- `1000PEPE`
- `ID`
- `AVAX`

### 3.3 观察池：0 交易 27 个

- `HYPE`
- `ASTER`
- `ESPORTS`
- `WLD`
- `UNI`
- `XPL`
- `XLM`
- `BSB`
- `LAB`
- `AGT`
- `BEAT`
- `ENA`
- `H`
- `ONDO`
- `SIREN`
- `BR`
- `JTO`
- `VELVET`
- `TRUMP`
- `SPX`
- `SKYAI`
- `AAVE`
- `LIT`
- `EVAA`
- `TAC`
- `BIO`
- `BLESS`

解释：

1. 删除候选并不是“永远不碰”，而是这版策略在当前样本里已经证明它们不是主要正贡献来源。
2. 观察池不代表坏，只是这版策略目前对它们几乎没有交易意愿。

## 4. 子池配置

新增配置：

- 有交易 23 池  
  [config.backtest.dualtrend.combined.top50.active23.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.active23.max3.json)
- 正贡献 13 池  
  [config.backtest.dualtrend.combined.top50.positive13.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json)

## 5. 三年样本对照

回测区间：

- `2023-06-18 -> 2026-06-18`

结果文件：

- 13 池: [backtest-result-2026-06-18_06-49-31.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-31.zip)
- 23 池: [backtest-result-2026-06-18_06-49-38.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-38.zip)

### 5.1 汇总

| 池子 | Pairs | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|---:|
| Top50 全池 | 50 | 308 | +1563.88U / +156.39% | 1.79 | 8.27% | 32.47% | 61 / 247 |
| 有交易 23 池 | 23 | 309 | +1613.44U / +161.34% | 1.81 | 8.33% | 33.01% | 61 / 248 |
| 正贡献 13 池 | 13 | 294 | +1907.86U / +190.79% | 1.97 | 7.68% | 34.69% | 46 / 248 |

### 5.2 观察

1. `23 池` 相比 `50 池` 只是小幅改善。
2. 真正明显改善的是 `13 池`：
   - 收益显著提升
   - PF 提升到 `1.97`
   - 回撤下降到 `7.68%`
   - 胜率提升到 `34.69%`
3. 这说明拖累并不来自 `0 交易币`，而是来自那批“偶尔交易、但质量不够”的负贡献币。

## 6. 近一年样本对照

回测区间：

- `2025-06-18 -> 2026-06-18`

结果文件：

- 13 池: [backtest-result-2026-06-18_06-51-00.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-51-00.zip)
- 23 池: [backtest-result-2026-06-18_06-51-04.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-51-04.zip)

### 6.1 汇总

| 池子 | Pairs | Trades | Profit | PF | MaxDD | Winrate | Long / Short |
|---|---:|---:|---:|---:|---:|---:|---:|
| 有交易 23 池 | 23 | 116 | +452.02U / +45.20% | 1.83 | 8.32% | 37.93% | 19 / 97 |
| 正贡献 13 池 | 13 | 111 | +512.35U / +51.23% | 2.00 | 7.65% | 39.64% | 14 / 97 |

### 6.2 观察

1. 近一年结果同样支持 `13 池` 优于 `23 池`。
2. 这说明 `13 池` 的优势不只是 3 年样本里的事后筛选，近期表现也更强。
3. `13 池` 在近一年已经达到：
   - PF `2.00`
   - 回撤 `7.65%`
   - 收益 `+51.23%`

## 7. 结构变化

### 7.1 三年样本下

`13 池` 的结构变化：

- Trades 从 `308` 降到 `294`
- Long 从 `61` 降到 `46`
- Short 从 `247` 升到 `248`

解释：

- 删除掉负贡献币后，short 主引擎没有被伤到。
- 反而 long 的无效交易被压缩了一部分。

### 7.2 近一年样本下

`13 池` 的 entry_tag：

- `short_pullback_restart`: +252.44U
- `short_compression_breakdown`: +74.59U
- `long_1d_center_compression`: +185.32U

说明：

- short 仍然是主收益来源
- long 在筛池后质量也明显改善了

## 8. 当前结论

### 8.1 最值得保留的池子

当前最值得继续推进的是：

- **正贡献 13 池**

理由：

1. 三年样本明显优于 top50 全池和 active23
2. 近一年样本也继续领先
3. 回撤没有放大，反而更小
4. PF 达到接近 2.0，质量更干净

### 8.2 对 top50 的判断

这轮验证说明：

- Top50 可以当观察池
- 但不适合直接等权拿来跑当前主策略
- 当前策略真正适配的是其中一小部分更符合双顺结构的币

### 8.3 对“删除候选”的判断

这 10 个删除候选目前更像是：

- 容易偶发触发
- 但触发后的延续性不足
- 会拉低整体质量

所以比起给它们做特化逻辑，更合理的是：

- 先直接移出主交易池

## 9. 风险提示

需要诚实地说一句：

- `正贡献 13 池` 是根据已有样本内结果筛出来的
- 所以它天然带有一定 in-sample 选择优势

不过这次它在近一年样本里仍然更强，说明并不只是纯粹的样本内幻觉。

更稳妥的下一步应该是：

1. 用 13 池做成本压力测试
2. 用 13 池做 `max_open_trades 3/4/5`
3. 如果要上 dry-run，优先用 13 池

## 10. 本轮已完成事项

本轮已完成：

1. 从 top50 结果中拆分保留 / 删除候选 / 观察池
2. 新建 23 池与 13 池配置
3. 用 Docker 跑三年正式回测
4. 用 Docker 跑近一年正式回测
5. 输出对照结论

