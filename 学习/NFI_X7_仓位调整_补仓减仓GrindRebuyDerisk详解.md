# NFI X7 补仓、减仓、Grind、Rebuy、Derisk 详解

## 1. adjust_trade_position 是什么

`adjust_trade_position` 是 Freqtrade 提供的仓位调整回调。交易已经打开后，框架会不断调用它，策略可以返回：

- 正数：追加仓位，也就是补仓。
- 负数：减少仓位，也就是部分卖出。
- `None`：不调整。
- `(金额, tag)`：调整仓位并记录这次调整原因。

Java 类比：

```java
PositionAdjustment adjustTradePosition(Trade trade, MarketSnapshot market) {
    if (shouldAddPosition(trade, market)) {
        return new PositionAdjustment(+20.0, "grind_1");
    }
    if (shouldReducePosition(trade, market)) {
        return new PositionAdjustment(-15.0, "derisk_1");
    }
    return null;
}
```

## 2. 为什么这个策略需要仓位调整

NFI X7 不是“一次买入，一次卖出”的简单策略。它有一些模式会在价格继续下跌时补仓，试图降低平均成本；当反弹到一定程度时，可能先减掉一部分风险。

这套机制带来两个结果：

- 好处：震荡行情中更容易盈利退出，胜率可能很高。
- 风险：单边下跌时会不断占用资金，甚至出现深套。

## 3. Rebuy 是什么

Rebuy 可以理解为“再次买入/补仓模式”。当一笔交易开仓后，如果价格继续向不利方向移动，但策略认为仍有反弹机会，就追加买入。

它通常会检查：

- 当前亏损幅度。
- 距离上一笔入场价的跌幅。
- 是否已有足够多次补仓。
- 当前指标是否仍然支持入场。
- 最小下单额是否满足交易所要求。
- 当前是否已有未成交订单。

## 4. Grind 是什么

Grind 可以理解为“网格化/磨仓式补仓”。它比普通 rebuy 更复杂，会把一笔交易拆成多个子层级，例如 grind_1、grind_2、grind_3 等。

每一层可能有：

- 自己的补仓金额倍率。
- 自己的触发跌幅阈值。
- 自己的减风险规则。
- 自己的买回规则。

所以 grind 不是简单的 martingale 加仓，而是一套带层级状态的仓位管理系统。

## 5. Derisk 是什么

Derisk 是“降低风险”。当策略已经补过仓，后续价格有所反弹时，它可能不等整笔交易完全盈利，而是先卖出一部分，释放资金、降低风险敞口。

你可以把它理解成：

```java
if (positionWasAveragedDown && reboundEnough) {
    sellPartialPosition();
}
```

这对小资金特别重要，因为它能释放一部分被占用的 USDT。

## 6. v2 / v3 / v3_1 / v3_2 是什么

策略里出现很多 system version：

- v2
- v3
- v3_1
- v3_2

它们不是 Python 版本，而是作者给策略内部仓位系统起的版本名。不同版本可能有不同的：

- 补仓阈值
- 止损阈值
- derisk 规则
- stake 倍率
- 适用日期

代码里会通过 `trade.get_custom_data(key="system_version")` 判断这笔交易属于哪个系统版本。

## 7. 小资金为什么容易遇到问题

你之前关心 60U、100U、300U、500U 是否够。核心原因就在这里。

如果策略允许补仓，那么一笔交易不只占用初始下单金额，还可能占用后续多层补仓金额。资金太少时会遇到：

- 初始订单低于交易所最小下单额。
- 第一笔能开，但后续补仓资金不够。
- 多个币同时触发，max_open_trades 太大导致资金分散。
- 回测中理论能补仓，实盘因为余额不足补不上，结果收益曲线完全不同。

所以小资金跑这个策略，`max_open_trades` 和 `stake_amount` 比入场条件更关键。

## 8. correct_min_stake 的作用

`correct_min_stake` 会根据交易所和合约模式修正最小下单额。例如 Bybit 合约里，如果最小名义价值低于要求，会按杠杆调整。

这说明策略内部知道交易所有最小单限制，不是无限小金额都能下单。

## 9. 仓位调整的典型流程

简化后可以这样理解：

```text
交易已打开
  |
  v
是否有未成交订单？有 -> 不动
  |
  v
读取最新指标和订单历史
  |
  v
计算真实整体利润
  |
  v
判断当前 tag 属于 rebuy / grind / scalp / top coins
  |
  v
如果价格继续下跌且满足规则 -> 补仓
  |
  v
如果价格反弹且满足 derisk -> 部分减仓
  |
  v
否则不调整
```

## 10. 对实盘的核心启发

这类策略的收益不是只来自入场信号，也来自仓位管理。也就是说，同一个入场条件，在不同资金量、不同 max_open_trades、不同 stake_amount 下，最终结果可能完全不同。

如果你想尽量接近回测，需要保证：

- 资金量足够覆盖补仓路径。
- `max_open_trades` 不要高到让资金被过度分散。
- 每单金额不要低于交易所最小额。
- dry-run 配置和 backtest 配置尽量一致。
- 关注未平仓浮亏，而不是只看已平仓胜率。
