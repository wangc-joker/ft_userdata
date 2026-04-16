# NostalgiaForInfinityX7 最佳回测组合汇总

本文档整理当前已经完成的核心回测，目的是把 300U / 500U、Top9 / Top20 的较优组合固定下来，便于后续直接复用。

## 说明

- 策略: `NostalgiaForInfinityX7`
- 交易模式: Binance Futures
- 下单方式: `stake_amount = "unlimited"`
- 杠杆: 采用策略原始逻辑
- 这里的“最佳”是指当前已经实测过的组合里表现最优，不代表未来一定继续最优。
- Top9 结果主要基于 1 年区间测试。
- Top20 结果主要基于最近半年区间测试。

## 最佳组合总表

| 组合 | 时间区间 | max_open_trades | 起始资金 | 最终资金 | 收益额 | 收益率 | 胜率 | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Top9 + 500U | 2024-04-15 -> 2025-04-15 | 3 | 500 | 1188.921 | 688.921 | 137.78% | 100% | 9币 1年测试中最佳 |
| Top9 + 300U | 2024-04-15 -> 2025-04-15 | 3 | 300 | 700.779 | 400.779 | 133.59% | 100% | 300U 下仍接近 500U 表现 |
| Top20 + 500U | 2025-10-15 -> 2026-04-15 | 2 | 500 | 984.841 | 484.841 | 96.97% | 100% | 20币近半年测试中最佳 |
| Top20 + 300U | 2025-10-15 -> 2026-04-15 | 2 | 300 | 609.571 | 309.571 | 103.19% | 100% | 当前已测 300U 方案里表现很好 |

## 逐项说明

### 1. Top9 + 500U

- 推荐配置: `config.backtest.nfi.best.top9.500u.json`
- 币种:
  - BTC, SOL, TRX, ADA, BNB, ZEC, ETH, XRP, DOGE
- 核心参数:
  - `max_open_trades = 3`
  - `dry_run_wallet = 500`
  - `stake_amount = "unlimited"`
- 适用理解:
  - 这是目前 9 币组合里最平衡的一组。
  - 相比 `max_open_trades = 2` 和 `5`，`3` 的年化区间表现最好。
  - 如果你想保持此前我们讨论过的“原策略推荐风格”，这组最适合做主参考。

### 2. Top9 + 300U

- 推荐配置: `config.backtest.nfi.best.top9.300u.json`
- 币种:
  - BTC, SOL, TRX, ADA, BNB, ZEC, ETH, XRP, DOGE
- 核心参数:
  - `max_open_trades = 3`
  - `dry_run_wallet = 300`
  - `stake_amount = "unlimited"`
- 适用理解:
  - 如果预算压到 300U，这组依旧能维持较高收益率。
  - 从我们已经实测的数据看，300U 没有出现明显的“资金不够导致策略完全失真”的情况。
  - 它是比较适合小资金参考的 9 币版本。

### 3. Top20 + 500U

- 推荐配置: `config.backtest.nfi.best.top20.500u.json`
- 币种:
  - BTC, ETH, BNB, SOL, ADA, XRP, DOGE, TRX, ZEC, AVAX, LINK, LTC, DOT, BCH, ATOM, NEAR, AAVE, UNI, ETC, FIL
- 核心参数:
  - `max_open_trades = 2`
  - `dry_run_wallet = 500`
  - `stake_amount = "unlimited"`
- 适用理解:
  - 在 20 币扩展组合里，`max_open_trades = 2` 明显优于 `1 / 3 / 5`。
  - 这说明币种扩多以后，并不是同时开得越多越好，反而适当收紧并发更能保留利润。
  - 这是目前 Top20 里最值得优先复用的配置。

### 4. Top20 + 300U

- 推荐配置: `config.backtest.nfi.best.top20.300u.json`
- 币种:
  - BTC, ETH, BNB, SOL, ADA, XRP, DOGE, TRX, ZEC, AVAX, LINK, LTC, DOT, BCH, ATOM, NEAR, AAVE, UNI, ETC, FIL
- 核心参数:
  - `max_open_trades = 2`
  - `dry_run_wallet = 300`
  - `stake_amount = "unlimited"`
- 适用理解:
  - 这是最近半年的 20 币扩展方案里，当前我们已经验证过的 300U 版本。
  - 百分比收益甚至略高于 500U 版本，说明在这个区间里，小一些的资金规模也能跑起来。
  - 后续如果你要做 300U 的扩展组合模拟盘，可以优先从这组开始。

## 建议怎么用

- 想看更接近“原策略推荐节奏”的稳定参考，用 `Top9 + 500U`。
- 想压低本金又尽量保留利润，用 `Top9 + 300U`。
- 想扩大币种覆盖，同时控制并发，用 `Top20 + 500U`。
- 想用较低本金测试扩展组合，用 `Top20 + 300U`。

## 当前保留的最佳配置文件

- `D:\test\ft_userdata\user_data\config.backtest.nfi.best.top9.500u.json`
- `D:\test\ft_userdata\user_data\config.backtest.nfi.best.top9.300u.json`
- `D:\test\ft_userdata\user_data\config.backtest.nfi.best.top20.500u.json`
- `D:\test\ft_userdata\user_data\config.backtest.nfi.best.top20.300u.json`
