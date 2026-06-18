# DualTrend 当前Top50合约池 3年稳定性验证

日期: 2026-06-18

## 1. 目标

把币池从之前的 30 个 / 40 个候选，扩大到 **Binance 当前 USD-M 合约 24h 成交额前 50**，验证当前主候选策略在更大币池上的：

- 收益率
- 稳定性
- 回撤控制
- 是否仍然主要依赖少数核心币

本次默认验证的策略为当前主候选：

- `DualTrendCombinedShortPullbackShapeV1Strategy`

## 2. 本次使用的口径

实时币池来源采用 Binance 官方 USD-M 合约接口：

- `GET /fapi/v1/exchangeInfo`
- `GET /fapi/v1/ticker/24hr`

筛选条件：

1. `contractType = PERPETUAL`
2. `status = TRADING`
3. `quoteAsset = USDT`
4. 按 `quoteVolume` 从高到低排序
5. 取前 50 个

生成文件：

- 币池 JSON  
  [pairs.dynamic.top50.futures.quotevolume.json](D:/test/real_trade/user_data/generated/pairs.dynamic.top50.futures.quotevolume.json)
- 币池明细报告  
  [pairs.dynamic.top50.futures.quotevolume.report.json](D:/test/real_trade/user_data/generated/pairs.dynamic.top50.futures.quotevolume.report.json)
- 导出 CSV  
  [binance_usdt_futures_top50_quotevolume_20260618.csv](D:/test/ft_userdata/binance_usdt_futures_top50_quotevolume_20260618.csv)

## 3. 回测配置

新增配置：

- [config.backtest.dualtrend.combined.top50.futures.max3.json](D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.futures.max3.json)

核心参数：

- `strategy = DualTrendCombinedShortPullbackShapeV1Strategy`
- `max_open_trades = 3`
- `dry_run_wallet = 1000`
- `trading_mode = futures`
- `margin_mode = isolated`

## 4. 数据同步

### 4.1 执行内容

使用 Docker 执行：

1. 先下载最近缺失数据
2. 再使用 `--prepend` 向前补历史

时间范围：

- `2023-06-18 -> 2026-06-18`

时间周期：

- `1h`
- `4h`
- `1d`

### 4.2 数据说明

这次 top50 里包含不少近一年才上线的新合约。

因此本次样本天然分两类：

1. **老币**：历史能覆盖完整 3 年或接近 3 年
2. **新币**：只能从 Binance 上线时间开始回测

所以这次结果更准确地说，是：

- **当前 top50 合约池，在最近 3 年窗口内可获得历史下的组合表现**

不是每个币都拥有完整 3 年自然样本。

## 5. Docker 回测结果

回测结果文件：

- [backtest-result-2026-06-18_06-40-16.zip](D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-40-16.zip)

回测区间：

- `2023-06-18 -> 2026-06-18`

### 5.1 总结果

| 指标 | 结果 |
|---|---:|
| Trades | 308 |
| Profit | +1563.88U / +156.39% |
| Profit Factor | 1.79 |
| Max Drawdown | 8.27% |
| Winrate | 32.47% |
| Long / Short | 61 / 247 |
| Final Balance | 2563.88U |
| Trades / Day | 0.28 |

结论：

- 在扩大到 **当前 top50 合约池** 后，策略仍然保持明显正收益。
- PF 提升到 `1.79`，回撤仍控制在 `8.27%`，这说明扩池后并没有把策略质量拖散。
- 整体仍然是 **以做空为主、做多为辅** 的结构。

## 6. Entry Tag 拆解

| entry_tag | Trades | Profit Abs | Profit Factor | Winrate |
|---|---:|---:|---:|---:|
| `short_pullback_restart` | 167 | +873.48U | 1.83 | 34.13% |
| `short_compression_breakdown` | 80 | +397.20U | 1.84 | 33.75% |
| `long_1d_center_compression` | 61 | +293.20U | 1.64 | 26.23% |

观察：

1. 主收益仍然来自 `short_pullback_restart`。
2. `short_compression_breakdown` 依旧稳定，是很重要的副引擎。
3. long 仍然为正，但收益贡献和胜率都明显弱于 short。

## 7. 年度表现

| 年份 | Trades | Profit Abs | Profit Factor |
|---|---:|---:|---:|
| 2023 下半年 | 40 | -43.95U | 0.78 |
| 2024 | 93 | +377.24U | 1.83 |
| 2025 | 120 | +829.30U | 1.96 |
| 2026 至 06-18 | 55 | +401.29U | 1.87 |

观察：

1. 2023 下半年仍然偏弱，和我们前面其他版本的表现一致。
2. 真正稳定赚钱还是从 2024 开始。
3. 2025、2026 这两段表现都比较强，说明这版策略对近两年的合约市场结构适应度不错。

## 8. 最近 12 个月月度表现

| 月份 | Trades | Profit Abs | Profit Factor |
|---|---:|---:|---:|
| 2025-07 | 5 | +84.31U | 3.59 |
| 2025-08 | 7 | -10.40U | 0.86 |
| 2025-09 | 10 | +0.93U | 1.01 |
| 2025-10 | 8 | +37.24U | 1.47 |
| 2025-11 | 13 | +148.89U | 2.65 |
| 2025-12 | 13 | +117.21U | 2.11 |
| 2026-01 | 13 | +296.55U | 5.09 |
| 2026-02 | 12 | +39.54U | 1.42 |
| 2026-03 | 7 | -51.73U | 0.47 |
| 2026-04 | 6 | -28.11U | 0.48 |
| 2026-05 | 5 | -48.26U | 0.00 |
| 2026-06 至 06-18 | 12 | +193.31U | 2.97 |

观察：

1. 月度并不是线性平滑增长，存在正常波动。
2. 2026-03 到 2026-05 有连续压力期。
3. 2026-06 又快速修复回来，说明策略并没有失效，更像是阶段性不顺。

## 9. Pair 贡献

### 9.1 贡献最大的 10 个 pair

| Pair | Trades | Profit Abs | PF |
|---|---:|---:|---:|
| ETH | 29 | +320.82U | 3.09 |
| ZEC | 13 | +208.23U | 6.24 |
| BTC | 37 | +182.17U | 1.85 |
| ADA | 29 | +163.25U | 1.98 |
| BNB | 19 | +157.98U | 2.33 |
| SOL | 25 | +150.98U | 1.82 |
| DOGE | 20 | +142.77U | 2.21 |
| XRP | 37 | +128.68U | 1.55 |
| TAO | 11 | +93.53U | 2.48 |
| SUI | 19 | +77.97U | 1.62 |

### 9.2 拖累最大的 10 个 pair

| Pair | Trades | Profit Abs | PF |
|---|---:|---:|---:|
| BCH | 3 | -38.47U | 0.00 |
| LTC | 3 | -28.51U | 0.00 |
| INJ | 2 | -19.42U | 0.00 |
| DOT | 2 | -18.77U | 0.00 |
| SYN | 1 | -17.02U | 0.00 |
| HOME | 1 | -15.76U | 0.00 |
| FIL | 1 | -9.40U | 0.00 |
| 1000PEPE | 1 | -8.24U | 0.00 |
| ID | 1 | -8.03U | 0.00 |
| AVAX | 1 | -7.26U | 0.00 |

观察：

1. 收益主力还是我们熟悉的老核心币：
   - `ETH`
   - `ZEC`
   - `BTC`
   - `ADA`
   - `BNB`
   - `SOL`
   - `DOGE`
   - `XRP`
2. 新增的 top50 新币并没有成为主要利润来源。
3. 拖累项大多是交易次数很少、只触发 1-3 次的小样本亏损。

## 10. 币池利用率

本次 top50 的实际使用情况：

| 项目 | 数量 |
|---|---:|
| 总 pair 数 | 50 |
| 有交易 pair | 23 |
| 0 交易 pair | 27 |

解释：

这说明当前策略虽然允许 top50 全部进入观察池，但它真正“认可”的交易环境，仍然集中在一部分更符合双顺结构的币上。

换句话说：

- **扩池没有明显伤害策略**
- 但 **扩池也没有让策略自然吃到更多新币红利**

## 11. 稳定性判断

从这次 top50 扩池结果看，当前主候选策略的稳定性结论是：

1. **整体稳定性仍然合格**
   - PF `1.79`
   - MaxDD `8.27%`
   - 收益 `+156.39%`

2. **策略没有因为币池放大而明显失真**
   - 没有出现“交易数暴涨但质量塌掉”
   - 也没有出现“回撤突然显著放大”

3. **收益仍主要依赖老核心币**
   - 新进 top50 的很多新币对结果影响很小
   - 说明这套策略更像“结构型筛选器”，不是简单的广谱扫射策略

4. **样本扩张后的真实结论不是‘策略适合全部 50 个币’**
   - 更准确的说法是：
   - `top50` 作为大观察池是可以的
   - 但有效交易仍然集中在 20 来个更匹配的币

## 12. 本次执行记录

本轮已完成：

1. 按 Binance 当前 USD-M 合约 24h 成交额生成 top50 币池
2. 新建 top50 回测配置
3. 使用 Docker 下载和补齐 1h / 4h / 1d 数据
4. 使用 Docker 完成 3 年正式回测
5. 输出收益、PF、DD、entry_tag、年度、月度、pair 拆解

## 13. 当前建议

基于这轮结果，我的建议是：

1. **可以把 top50 作为上层观察池保留**
2. **不要因为扩池后收益仍然不错，就直接认为 50 个币都适合交易**
3. 如果下一步继续收敛，优先做这两件事：
   - 对 top50 结果做 `有交易 pair / 无交易 pair / 小样本亏损 pair` 的分层
   - 再跑一版 `只保留有交易且非明显拖累 pair` 的对照回测

当前这版结果说明：

- 策略本身是稳的
- 币池扩大后没有崩
- 但 alpha 仍然集中在少数熟悉结构币上

