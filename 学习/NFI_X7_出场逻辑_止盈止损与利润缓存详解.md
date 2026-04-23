# NFI X7 出场逻辑详解

## 1. 出场不是简单的 sell 条件

这个策略的出场逻辑主要由 `custom_exit` 控制。Freqtrade 会在交易打开后不断调用这个方法，让策略决定当前是否应该退出。

在 Java 里可以理解成：

```java
Optional<String> customExit(String pair, Trade trade, double currentRate, double currentProfit) {
    MarketSnapshot snapshot = dataProvider.getLatest(pair);
    ProfitInfo profit = calcTotalProfit(trade, currentRate);
    List<String> tags = trade.getEnterTags();

    if (tags contains topCoinsTag) {
        return longExitTopCoins(...);
    }
    return Optional.empty();
}
```

## 2. custom_exit 做了什么

`custom_exit` 的核心步骤：

1. 从 `dp.get_analyzed_dataframe(pair, timeframe)` 获取已经计算好指标的 DataFrame。
2. 取最后 6 根 K 线：当前 K 线和前 5 根 K 线。
3. 从交易对象里读取 `enter_tag`。
4. 查询这笔交易已经成交的入场单和出场单。
5. 调用 `calc_total_profit` 重新计算真实收益。
6. 根据 tag 分发到不同出场函数。

它不是只看 `current_profit`，而是用订单记录重新计算利润，这对补仓/减仓后的交易更准确。

## 3. calc_total_profit 为什么重要

普通策略可能只有一笔买入、一笔卖出，利润计算很简单。但 NFI X7 会补仓、减仓，因此一笔 Trade 里可能包含多次 entry 和 exit。

`calc_total_profit` 会遍历：

- filled_entries：所有已成交入场单
- filled_exits：所有已成交出场单
- 当前还持有的数量
- 手续费
- 合约模式下的 funding fees

最后返回：

- `profit_stake`：以 USDT 计的绝对收益
- `profit_ratio`：相对总投入的收益率
- `profit_current_stake_ratio`：相对当前剩余仓位的收益率
- `profit_init_ratio`：相对第一笔入场金额的收益率

这个设计说明：策略非常关心“补仓和减仓后的真实整体收益”。

## 4. top coins 的出场链路

对于 top coins 模式，入口是 `long_exit_top_coins`。

它依次调用：

1. `long_exit_signals`
   - 原始出场信号。
   - 通常是一些短线过热、反弹到位、指标转弱的组合。

2. `long_exit_main`
   - 主出场逻辑。
   - 更像常规盈利了结条件。

3. `long_exit_williams_r`
   - 基于 Williams %R 的出场。
   - Williams %R 常用于判断超买超卖。

4. `long_exit_dec`
   - downtrend / descending 相关出场。
   - 用于识别反弹失败、趋势转弱。

5. `long_exit_stoploss`
   - 策略自定义止损。
   - 注意原始 `stoploss = -0.99` 几乎等于不让 Freqtrade 普通止损主动接管，真正止损主要在这里。

6. `target_profit_cache`
   - 如果已经触发过卖出理由，但策略认为可以尝试多拿一点利润，会先缓存目标，而不是立刻卖。

## 5. target_profit_cache 的意义

这是理解高胜率的关键之一。

当某个出场信号出现时，策略不一定马上卖。它可能会：

1. 记录当前价格、利润、卖出原因、时间。
2. 后续继续观察是否能拿到更高利润。
3. 如果利润回落或满足目标退出，再真正卖出。

这类似 Java 里维护一个 Map：

```java
Map<String, ProfitTarget> targetProfitCache = new HashMap<>();

class ProfitTarget {
    String pair;
    double rate;
    double profit;
    String sellReason;
    LocalDateTime timeProfitReached;
}
```

这种机制会让回测里的退出更“挑剔”：不是一出现信号就卖，而是等更合适的点。

## 6. long_exit_stoploss 的特点

这个策略文件顶部设置：

```python
stoploss = -0.99
```

表面看是最大亏损 99%，非常吓人。但实际策略还写了自定义止损：`long_exit_stoploss`。

它会根据不同 system version 使用不同阈值：

- system v3
- system v3_1
- system v3_2
- 默认系统

并根据现货/合约模式使用不同 stop threshold。

但是你要特别注意：这仍然不是传统意义上的硬止损。它带有很多条件，比如是否启用 doom stop、是否还有有效入场条件、价格和 EMA200 的关系、CMF、RSI 状态等。

## 7. confirm_trade_exit 又拦了一层

即使 `custom_exit` 返回卖出信号，Freqtrade 还会调用 `confirm_trade_exit`。

这里可能再次拒绝退出：

- 如果是 force_exit，允许。
- 如果 `_should_hold_trade` 判断需要持有，拒绝。
- 如果是普通 stop_loss 或 trailing_stop_loss，大多数情况下拒绝。
- 如果 `exit_profit_only` 开启，利润低于偏移值时拒绝。
- 最后才清除 profit target cache 并允许退出。

所以实际链路是：

```text
custom_exit 说可以卖
        |
        v
confirm_trade_exit 再确认是否真的允许卖
```

## 8. 为什么回测胜率可能达到 100%

胜率 100% 不代表没有风险。常见原因包括：

- 策略尽量不亏损卖出，而是等待反弹。
- 会使用补仓摊低成本。
- 出场逻辑偏向盈利退出。
- 自定义止损不是每次亏损都立即触发。
- 回测区间如果没有遇到长期单边暴跌，亏损单可能没有被关闭。
- 未关闭亏损仓位不计入胜率，但会体现在浮亏、回撤、资金占用里。

所以你看这类策略，不能只看胜率，还要看：

- 最大回撤
- 未平仓交易
- 最长持仓时间
- 最低资金占用
- 是否有被套单
- 实盘是否能承受补仓资金

## 9. 出场逻辑的一句话总结

NFI X7 的出场逻辑是“多信号触发 + 利润目标缓存 + 条件止损 + 退出确认拦截”。这也是为什么它回测看起来胜率很高，但实盘风险更集中在资金占用、极端行情和未平仓浮亏上。
