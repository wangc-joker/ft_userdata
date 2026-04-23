# NFI X7 配置与风险说明

## 1. 关键默认配置

从策略文件中可以看到几个非常关键的设置：

- 主周期：`5m`
- 辅助周期：`15m`、`1h`、`4h`、`1d`
- 原始 stoploss：`-0.99`
- 启用仓位调整：`position_adjustment_enable = True`
- 启用 grind：`grinding_enable = True`
- 启用 derisk：`derisk_enable = True`
- 启用 doom stops：`doom_stops_enable = True`
- grind 最大槽位：`grind_mode_max_slots = 1`
- 滑点限制：`max_slippage = 0.01`

## 2. stoploss = -0.99 怎么理解

这不是说策略愿意亏 99% 才止损，而是说它不希望 Freqtrade 内置止损过早接管。真正的止损逻辑在 `long_exit_stoploss` / `short_exit_stoploss` 里。

但这依然代表一个重要风险：它不是硬止损型策略，而是更依赖自定义条件、补仓、等待反弹。

## 3. max_open_trades 的影响

`max_open_trades` 通常在 config 文件里设置，不一定在策略文件里硬编码。策略内部也有一些模式级别限制，例如 grind 模式最多槽位。

影响逻辑：

- max_open_trades 越大，同时开仓机会越多。
- 但资金也会被更多交易分散。
- 如果开启补仓，开仓太多可能导致后续补仓资金不足。
- 小资金情况下，较小的 max_open_trades 往往更稳。

## 4. 为什么同样 top9 300U 回测会有差异

你之前发现同一个配置跑出来收益差异很大，常见原因包括：

- 回测时间段不同。
- 数据文件更新或缺失。
- pairlist 不同。
- `max_open_trades` 不同。
- `stake_amount` 是否 unlimited 不同。
- 是否启用 position adjustment。
- 手续费、滑点、交易所最小额不同。
- 是否包含未平仓交易统计。
- 启动目录不同导致加载的 config 或 strategy path 不同。

对于这种策略，任何一个差异都可能显著影响结果。

## 5. 胜率 100% 的正确理解

胜率 100% 只说明“已经关闭的交易里没有亏损退出”。它不保证：

- 没有浮亏。
- 没有被套单。
- 没有资金长时间占用。
- 实盘也能补到同样仓位。
- 极端行情不会出现大亏。

更应该一起看：

- 最大回撤。
- 未平仓交易数量。
- 最长持仓时间。
- 最低余额。
- 最大单笔浮亏。
- 入场后是否靠补仓才盈利。

## 6. 100U / 300U / 500U 的实盘思路

如果资金只有 100U，不建议无脑放大交易对数量和 max_open_trades。因为策略需要为补仓预留资金。

相对合理的思路：

- 100U：更适合极少币种、很低 max_open_trades，并且确认最小下单额满足要求。
- 300U：可以跑 top9 或更保守组合，但仍要限制开仓数。
- 500U：更容易覆盖补仓路径，也更接近回测配置。

这不是投资建议，只是从策略机制看资金约束。

## 7. 实盘前建议检查项

上线 dry-run 或实盘前，至少检查：

- config 里实际 pair_whitelist 是不是你想跑的币种。
- max_open_trades 是否和回测一致。
- stake_amount 是否和回测一致。
- dry-run 是否启用 position adjustment。
- 交易所最小下单金额是否满足。
- 是否存在 Telegram / API 状态查看方式。
- 是否已经下载足够新的数据。

## 8. 最重要的风险结论

NFI X7 的收益来自“入场筛选 + 多周期过滤 + 状态化出场 + 补仓/减仓管理”。所以它不是纯信号策略，而是仓位管理策略。资金不足、配置不一致、交易所限制、极端行情都会让实盘结果和回测出现很大差异。
