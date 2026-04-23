# NFI X7 指标与数据流详解

## 1. Freqtrade 怎么调用这个策略

这个策略继承自 `IStrategy`。在 Java 里你可以把它理解成：

```java
public class NostalgiaForInfinityX7 implements Strategy {
    List<PairTimeframe> informativePairs();
    DataFrame populateIndicators(DataFrame df);
    DataFrame populateEntryTrend(DataFrame df);
    Object customExit(Trade trade, double currentRate);
    Object adjustTradePosition(Trade trade, double currentRate);
}
```

Freqtrade 不是每次只传一根 K 线，而是把某个交易对的一整段历史 K 线作为 `DataFrame` 传给策略。策略会给这个 DataFrame 增加很多列，例如 `RSI_14`、`EMA_200`、`WILLR_14_1h`。

## 2. DataFrame 是什么

如果你熟悉 Java，可以先把 DataFrame 想成：

```java
class CandleRow {
    LocalDateTime date;
    double open;
    double high;
    double low;
    double close;
    double volume;
    Map<String, Double> indicators;
}

List<CandleRow> dataframe;
```

但 Pandas 的核心优势是可以整列计算。例如 Python 里：

```python
df["RSI_14"] < 30
```

不是判断一行，而是对整列每一根 K 线都判断，得到一列 `True/False`。这类似 Java 里：

```java
for (CandleRow row : rows) {
    row.isOversold = row.rsi14 < 30;
}
```

## 3. informative_pairs 的作用

`informative_pairs` 告诉 Freqtrade：除了主周期 5m，还要额外加载哪些辅助周期数据。

这个策略主要加载：

- 当前交易白名单交易对的 `15m`、`1h`、`4h`、`1d`
- BTC/USDT、ETH/USDT 等基准币的 `5m`、`15m`、`1h`、`4h`、`1d`

原因是它不只看单个币自己的 5m 信号，还会用更高周期和 BTC 状态做过滤。

## 4. populate_indicators 的整体流程

`populate_indicators` 是指标生产线。它大致做这些事情：

1. 记录开始时间，用于日志统计耗时。
2. 判断当前 pair 是否属于 BTC stakes、BTC pair、top coins、grind coins。
3. 拉取 BTC 或 ETH 的辅助周期数据。
4. 调用各类 `informative_xxx_indicators` 生成高周期指标。
5. 用 `merge_informative_pair(..., ffill=True)` 合并到 5m 主 DataFrame。
6. 删除合并后不再需要的 OHLCV 辅助列，保留指标列。
7. 调用 `base_tf_5m_indicators` 计算当前 5m 周期指标。
8. 计算保护条件列，例如 `protections_long`、`protections_short`。
9. 返回带大量指标列的 DataFrame。

## 5. merge_informative_pair 是什么

主周期是 5m，辅助周期可能是 1h。1 小时 K 线对应 12 根 5m K 线。合并时会把 1h 指标填到对应的 5m 行上。

`ffill=True` 的意思是 forward fill，向前填充。比如 10:00 的 1h RSI 会被填到 10:00、10:05、10:10 等 5m 行，直到下一根 1h K 线出现。

Java 类比：

```java
for (Candle5m c : candles5m) {
    Candle1h latestClosed1h = findLatestClosed1h(c.time);
    c.rsi14_1h = latestClosed1h.rsi14;
}
```

## 6. 为什么有这么多周期

这个策略经常同时使用：

- 5m：具体入场点，适合找短线回调。
- 15m：过滤短线过热或确认小趋势。
- 1h：判断中短周期趋势。
- 4h：判断大周期是否极端。
- 1d：避免在日线极端风险位置开仓。
- BTC 多周期：判断市场整体环境。

这类策略不是单纯的 RSI 策略，而是“多周期共振 + 均值回归 + 风险过滤”。

## 7. protections_long / protections_short

`protections_long` 和 `protections_short` 是保护过滤器。它们通常用于避免在极端危险的行情下继续开仓。

可以理解成 Java 里的：

```java
boolean allowLong = !marketTooHot && !btcTooWeak && !volumeAbnormal;
boolean allowShort = !marketTooCold && !btcTooStrong;
```

不过在代码里它是通过 Pandas 条件列批量算出来的。

## 8. 你读指标代码时的技巧

看到这种代码：

```python
df["RSI_14_1h"] > 70
```

含义是：当前 5m 行对应的 1h RSI 是否大于 70。

看到这种代码：

```python
df["close"] < df["EMA_200"]
```

含义是：当前价格是否在 EMA200 下方。

看到这种代码：

```python
df["close"].rolling(48).max()
```

含义是：最近 48 根 K 线的最高收盘价。5m 周期下，48 根约等于 4 小时。

## 9. 最重要结论

这个策略的指标层非常重。真正的入场/出场只是使用这些已经计算好的列。如果你想读懂它，不要直接从入场 if 开始死磕，而是先知道每个字段来自哪个周期、表示什么市场状态。
