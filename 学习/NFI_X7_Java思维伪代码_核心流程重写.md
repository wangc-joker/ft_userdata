# NFI X7 Java 思维伪代码

这份文档不是把 Python 逐行翻译成 Java，而是帮你建立“如果用 Java 写这个策略，大概会怎么组织”的理解。

## 1. 总体类结构

```java
public class NostalgiaForInfinityX7Strategy implements Strategy {

    private StrategyConfig config;
    private DataProvider dataProvider;
    private ProfitTargetCache targetProfitCache;

    @Override
    public List<PairTimeframe> informativePairs() {
        return buildInformativePairs();
    }

    @Override
    public DataFrame populateIndicators(String pair, DataFrame df) {
        df = mergeInformativeIndicators(pair, df);
        df = addBaseTimeframeIndicators(df);
        df = addProtections(df);
        return df;
    }

    @Override
    public DataFrame populateEntryTrend(String pair, DataFrame df) {
        df = calculateLongEntries(df);
        df = calculateShortEntries(df);
        return df;
    }

    @Override
    public Optional<String> customExit(Trade trade, MarketContext ctx) {
        return exitRouter.route(trade, ctx);
    }

    @Override
    public PositionAdjustment adjustTradePosition(Trade trade, MarketContext ctx) {
        return positionManager.adjust(trade, ctx);
    }
}
```

## 2. Candle 数据结构

```java
public class Candle {
    public LocalDateTime date;
    public double open;
    public double high;
    public double low;
    public double close;
    public double volume;

    public Map<String, Double> indicators = new HashMap<>();
    public boolean enterLong;
    public boolean enterShort;
    public String enterTag;
}
```

Python 的 DataFrame 列，例如 `df["RSI_14"]`，在 Java 里可以理解成：

```java
row.indicators.get("RSI_14")
```

## 3. 指标合并伪代码

```java
public DataFrame populateIndicators(String pair, DataFrame df5m) {
    DataFrame df15m = dataProvider.get(pair, "15m");
    DataFrame df1h = dataProvider.get(pair, "1h");
    DataFrame df4h = dataProvider.get(pair, "4h");
    DataFrame df1d = dataProvider.get(pair, "1d");

    addIndicators15m(df15m);
    addIndicators1h(df1h);
    addIndicators4h(df4h);
    addIndicators1d(df1d);

    mergeForwardFill(df5m, df15m, "_15m");
    mergeForwardFill(df5m, df1h, "_1h");
    mergeForwardFill(df5m, df4h, "_4h");
    mergeForwardFill(df5m, df1d, "_1d");

    addBase5mIndicators(df5m);
    addProtectionColumns(df5m);

    return df5m;
}
```

## 4. top coins 入场伪代码

以 tag 141-145 为例，真实代码条件更长，但整体思想类似：

```java
if (isTopCoin(pair) && protectionsLong && condition141(candle)) {
    candle.enterLong = true;
    candle.enterTag += " 141";
}

if (isTopCoin(pair) && protectionsLong && condition142(candle)) {
    candle.enterLong = true;
    candle.enterTag += " 142";
}
```

多个 tag 可以同时出现，所以 `enter_tag` 是字符串列表，而不是一个单独枚举。

## 5. 入场确认伪代码

```java
public boolean confirmTradeEntry(String pair, String entryTag, String side, double rate) {
    if (entryTag.equals("force_entry")) {
        return true;
    }

    if (isGrindTag(entryTag)) {
        if (!grindCoins.contains(baseCoin(pair))) return false;
        if (openGrindTrades() >= grindMaxSlots) return false;
    }

    if (isTopCoinsTag(entryTag)) {
        if (!topCoins.contains(baseCoin(pair))) return false;
    }

    if (isFuturesMode()) {
        if (side.equals("long") && openLongTrades() >= maxLongTrades) return false;
        if (side.equals("short") && openShortTrades() >= maxShortTrades) return false;
    }

    if (slippageTooHigh(pair, side, rate)) {
        return false;
    }

    return true;
}
```

## 6. 出场路由伪代码

```java
public Optional<String> customExit(Trade trade, double currentRate) {
    List<String> tags = trade.getEnterTags();
    ProfitInfo profit = profitCalculator.calculate(trade, currentRate);
    Candle last = market.latest(trade.pair);

    if (containsAny(tags, LONG_TOP_COINS_TAGS)) {
        return longExitTopCoins(trade, profit, last);
    }

    if (containsAny(tags, LONG_REBUY_TAGS)) {
        return longExitRebuy(trade, profit, last);
    }

    if (containsAny(tags, LONG_GRIND_TAGS)) {
        return longExitGrind(trade, profit, last);
    }

    return Optional.empty();
}
```

## 7. top coins 出场伪代码

```java
public Optional<String> longExitTopCoins(Trade trade, ProfitInfo profit, Candle last) {
    ExitSignal signal = null;

    signal = longExitSignals(profit, last);
    if (signal == null) signal = longExitMain(profit, last);
    if (signal == null) signal = longExitWilliamsR(profit, last);
    if (signal == null) signal = longExitDescending(profit, last);
    if (signal == null) signal = longExitStoploss(trade, profit, last);

    if (targetProfitCache.contains(trade.pair)) {
        Optional<String> result = checkProfitTarget(trade, profit, signal);
        if (result.isPresent()) return result;
    }

    if (signal != null && shouldMarkProfitTarget(signal, profit)) {
        targetProfitCache.put(trade.pair, new ProfitTarget(signal, profit));
        return Optional.empty();
    }

    if (signal != null) {
        return Optional.of(signal.name);
    }

    return Optional.empty();
}
```

## 8. 仓位调整伪代码

```java
public PositionAdjustment adjustTradePosition(Trade trade, double currentRate) {
    if (!positionAdjustmentEnabled) return null;
    if (trade.hasOpenOrders()) return null;

    List<String> tags = trade.getEnterTags();
    ProfitInfo profit = profitCalculator.calculate(trade, currentRate);

    if (isRebuyTrade(tags)) {
        return longRebuyAdjustTradePosition(trade, profit);
    }

    if (isGrindTrade(tags)) {
        return longGrindAdjustTradePosition(trade, profit);
    }

    return null;
}
```

## 9. Rebuy 补仓伪代码

```java
public PositionAdjustment longRebuyAdjustTradePosition(Trade trade, ProfitInfo profit) {
    if (profit.currentRatio > rebuyThreshold) {
        return null;
    }

    if (!stillHasEntrySignal(trade.pair)) {
        return null;
    }

    double nextStake = calculateNextRebuyStake(trade);
    if (nextStake < minStake) {
        nextStake = minStake;
    }

    if (nextStake > availableBalance) {
        return null;
    }

    return new PositionAdjustment(+nextStake, "rebuy");
}
```

## 10. Derisk 减仓伪代码

```java
public PositionAdjustment tryDerisk(Trade trade, ProfitInfo profit) {
    if (!trade.hasAveragedDown()) {
        return null;
    }

    if (profit.reboundedEnough()) {
        double reduceAmount = calculateDeriskAmount(trade);
        return new PositionAdjustment(-reduceAmount, "derisk");
    }

    return null;
}
```

## 11. 最终心智模型

如果用 Java 架构来理解，NFI X7 可以拆成几个模块：

```text
NostalgiaForInfinityX7Strategy
  -> IndicatorBuilder
  -> EntrySignalBuilder
  -> EntryConfirmer
  -> ExitRouter
  -> ProfitTargetCache
  -> PositionAdjustmentManager
  -> RiskProtectionBuilder
```

原 Python 文件把这些模块都写在一个大类里，所以看起来非常长。你学习时可以按模块拆开理解，不需要从第 1 行读到最后一行。
