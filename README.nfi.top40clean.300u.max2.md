# NFI Clean Top40 300U Max2

保留配置文件：

- `user_data/config.backtest.nfi.top40clean.300u.max2.json`

用途：

- 用 `NostalgiaForInfinityX7` 跑 Binance futures 回测
- 资金规模固定为 `300 USDT`
- 最大持仓数固定为 `2`
- 币池为当前清洗后的 `Top40` 名单和本地已有 `5m futures` 数据的交集

当前配置中的币池：

- `BTC/USDT:USDT`
- `ETH/USDT:USDT`
- `SOL/USDT:USDT`
- `XRP/USDT:USDT`
- `DOGE/USDT:USDT`
- `ZEC/USDT:USDT`
- `BNB/USDT:USDT`
- `ADA/USDT:USDT`
- `AAVE/USDT:USDT`
- `AVAX/USDT:USDT`

这版为什么保留：

- 在最近半年测试里，`300U + max_open_trades=2` 明显优于 `300U + max_open_trades=3`
- 同时也符合这套币池“少数强势币主导收益”的特征，仓位不过度分散

最近一次对应结果：

- 回测区间：`2025-10-16` 到 `2026-04-15 02:30`
- 起始资金：`300 USDT`
- 最终资金：`522.890 USDT`
- 绝对收益：`+222.890 USDT`
- 总收益率：`+74.30%`
- 交易数：`26`
- 胜率：`100%`

快速回测命令：

```powershell
docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.nfi.top40clean.300u.max2.json --strategy NostalgiaForInfinityX7 --timerange 20251016-20260416 --export none
```

说明：

- 这里的 `Top40 clean` 是指按 Binance 成交额筛选时，排除了明显不适合混入币池的杠杆币或异常标的
- 实际参与回测的仍然受本地已有数据覆盖范围限制
- 如果后面补齐更多本地数据，这份配置可以继续扩充币池再复测
