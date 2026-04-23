# NostalgiaForInfinityX7 Top Coins 多头开仓条件 141-145 详解

源码文件：`D:\test\NostalgiaForInfinity\NostalgiaForInfinityX7.py`

相关函数：`populate_entry_trend`

相关行号：

| 条件编号 | 源码位置 | 模式 |
| ---: | ---: | --- |
| 141 | 20670 | Top Coins Long |
| 142 | 21100 | Top Coins Long |
| 143 | 21501 | Top Coins Long |
| 144 | 21706 | Top Coins Long |
| 145 | 21952 | Top Coins Long |

## 1. 先理解 Top Coins 是什么

`Top Coins mode` 是策略里专门给主流币/强流动性币种准备的一组多头开仓逻辑。

它对应的 tag 是：

```python
long_top_coins_mode_tags = ["141", "142", "143", "144", "145"]
long_top_coins_mode_name = "long_tc"
```

也就是说，开仓时如果命中 141-145 中的任意一个条件，这笔交易会被标记为 `long_tc` 系列。

后续平仓时，它会走：

```python
long_exit_top_coins(...)
```

这和 Java 里给订单设置一个 `strategyMode` 很像：

```java
trade.setEntryTag("141");
trade.setMode(Mode.LONG_TOP_COINS);
```

## 2. 141-145 的共同结构

每个条件大致都是三段：

```python
if long_entry_condition_index == 141:
    # Protections
    long_entry_logic.append(is_pair_long_top_coins_mode)
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    long_entry_logic.append(df["protections_long_global"] == True)

    # 多周期保护过滤
    long_entry_logic.append(...大量 OR/AND 条件...)

    # 真正的核心触发逻辑
    long_entry_logic.append(...)
```

也就是说：

1. 先确认这个币是不是 Top Coins 列表里的币
2. 再确认数据质量正常
3. 再确认全局保护允许开多
4. 再通过大量多周期过滤，排除太危险的行情
5. 最后用一个相对明确的局部超跌/趋势条件触发开仓

Java 风格伪代码：

```java
boolean condition141(Candle c) {
    if (!isTopCoin(c.pair)) return false;
    if (c.numEmpty288 > allowedEmptyCandles288) return false;
    if (!c.protectionsLongGlobal) return false;
    if (!multiTimeframeSafetyFilter141(c)) return false;
    return triggerLogic141(c);
}
```

## 3. 为什么有很多 `|` 和 `&`

Python 这里的 `|` 和 `&` 不是普通布尔值的 `||` / `&&`，而是 Pandas Series 的按列运算。

例如：

```python
(df["RSI_3"] > 3.0) | (df["RSI_3_15m"] > 15.0)
```

意思是对 DataFrame 里的每一根 K 线分别判断。

Java 类比：

```java
for (Candle c : candles) {
    boolean ok = c.rsi3 > 3.0 || c.rsi3_15m > 15.0;
}
```

`&` 是“并且”，`|` 是“或者”。

## 4. 共同保护条件

每个 141-145 都有这三句：

```python
long_entry_logic.append(is_pair_long_top_coins_mode)
long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
long_entry_logic.append(df["protections_long_global"] == True)
```

### 4.1 `is_pair_long_top_coins_mode`

意思是当前币必须在 `top_coins_mode_coins` 里。

也就是说，不是所有币都可以触发 141-145。

Java 类比：

```java
if (!topCoins.contains(pairBaseSymbol)) return false;
```

### 4.2 `num_empty_288 <= allowed_empty_candles_288`

这是数据质量过滤。

`288` 根 5m K 线刚好是一天：

```text
288 * 5 minutes = 1440 minutes = 1 day
```

它检查最近一天里空 K 线是否太多。空 K 线太多说明数据质量差，不适合开仓。

### 4.3 `protections_long_global == True`

这是全局多头保护。

可以理解为：

- 市场环境不能太危险
- 大盘过滤不能否定开多
- 该策略内部保护条件必须允许

## 5. 多周期过滤的阅读方法

你会看到大量类似：

```python
((df["RSI_3_15m"] > 3.0) | (df["RSI_3_1h"] > 10.0) | (df["ROC_9_1d"] < 60.0))
```

这些不是主要触发器，而是“排除极端坏场景”的过滤器。

这种写法可以翻译成：

```text
如果 15m 和 1h 都跌得很深，那么至少 1d 不要太过热/太危险。
```

或者：

```text
多个周期同时极端超跌/极端过热时，不要贸然开仓。
```

这类过滤器很多，是为了避免某些组合行情下误入场。

## 6. 条件 141 详解

源码位置：`20670`

核心触发逻辑在 `21092-21098`：

```python
long_entry_logic.append(
    (df["RSI_20"] < df["RSI_20"].shift(1))
    & (df["RSI_3"] < 30.0)
    & (df["AROONU_14"] < 25.0)
    & (df["close"] < df["SMA_16"] * 0.960)
)
```

逐句解释：

| 条件 | 含义 |
| --- | --- |
| `RSI_20 < RSI_20.shift(1)` | 当前 RSI20 比上一根更低，说明中短期动能继续走弱 |
| `RSI_3 < 30` | 5m 级别短 RSI 已经偏超卖 |
| `AROONU_14 < 25` | Aroon Up 很低，说明近期没有强上攻 |
| `close < SMA_16 * 0.960` | 当前价格低于 16 均线 4%，属于明显回落 |

策略意图：

`141` 是一个“价格明显跌破短均线 + 短线超卖 + 动能继续走弱”的抄底型条件。

Java 风格伪代码：

```java
boolean trigger141(Candle c, Candle prev) {
    return c.rsi20 < prev.rsi20
        && c.rsi3 < 30.0
        && c.aroonUp14 < 25.0
        && c.close < c.sma16 * 0.960;
}
```

更直白地说：

```text
Top Coin 价格跌得比较深，短线很弱，且继续下压，策略尝试在这种回落中找反弹机会。
```

## 7. 条件 142 详解

源码位置：`21100`

核心触发逻辑在 `21492-21499`：

```python
long_entry_logic.append(
    (df["RSI_3"] > 5.0)
    & (df["RSI_4"] < 46.0)
    & (df["RSI_20"] < df["RSI_20"].shift(1))
    & (df["close"] < df["SMA_16"] * 0.960)
)
```

逐句解释：

| 条件 | 含义 |
| --- | --- |
| `RSI_3 > 5` | 不是极端死亡式下跌，避免太极端的插针或崩盘继续下杀 |
| `RSI_4 < 46` | 短周期仍偏弱，没有明显走强 |
| `RSI_20 < RSI_20.shift(1)` | 中短期 RSI 仍在下降 |
| `close < SMA_16 * 0.960` | 当前价格低于 16 均线 4% |

策略意图：

`142` 和 `141` 很像，也是在价格明显低于短均线时寻找机会。不同点是：

- `141` 要求 `RSI_3 < 30` 和 `AROONU_14 < 25`
- `142` 要求 `RSI_3 > 5`，避免过度极端，并要求 `RSI_4 < 46`

Java 风格伪代码：

```java
boolean trigger142(Candle c, Candle prev) {
    return c.rsi3 > 5.0
        && c.rsi4 < 46.0
        && c.rsi20 < prev.rsi20
        && c.close < c.sma16 * 0.960;
}
```

更直白地说：

```text
Top Coin 有明显回落，但不是完全崩盘式极端下跌；短线仍弱，策略尝试接反弹。
```

## 8. 条件 143 详解

源码位置：`21501`

核心触发逻辑在 `21697-21704`：

```python
long_entry_logic.append(
    (df["RSI_3"] < 40.0)
    & (df["STOCHRSIk_14_14_3_3"] < 20.0)
    & (df["EMA_26"] > df["EMA_12"])
    & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.020))
    & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
)
```

逐句解释：

| 条件 | 含义 |
| --- | --- |
| `RSI_3 < 40` | 短 RSI 偏弱 |
| `STOCHRSIk < 20` | 随机 RSI 进入超卖区 |
| `EMA_26 > EMA_12` | 短 EMA 在长 EMA 下方，短线趋势偏空 |
| `EMA_26 - EMA_12 > open * 0.020` | 两条 EMA 距离超过价格 2%，说明下跌趋势已经拉开距离 |
| `上一根 EMA 差值 > open / 100` | 上一根也有明显 EMA 差距，确认不是瞬间噪音 |

策略意图：

`143` 是一个“短线趋势已经明显向下 + 指标超卖”的反弹条件。

Java 风格伪代码：

```java
boolean trigger143(Candle c, Candle prev) {
    return c.rsi3 < 40.0
        && c.stochRsiK < 20.0
        && c.ema26 > c.ema12
        && (c.ema26 - c.ema12) > c.open * 0.020
        && (prev.ema26 - prev.ema12) > c.open / 100.0;
}
```

更直白地说：

```text
短线已经明显走弱，EMA 空头排列拉开，随机 RSI 超卖，策略赌一次均值回归反弹。
```

## 9. 条件 144 详解

源码位置：`21706`

核心触发逻辑在 `21942-21950`：

```python
long_entry_logic.append(
    (df["WILLR_14"] < -50.0)
    & (df["STOCHRSIk_14_14_3_3"] < 30.0)
    & (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    & (df["BBB_20_2.0_1h"] > 12.0)
    & (df["close_max_48"] >= (df["close"] * 1.10))
)
```

逐句解释：

| 条件 | 含义 |
| --- | --- |
| `WILLR_14 < -50` | Williams %R 偏弱，价格靠近区间下半部 |
| `STOCHRSIk < 30` | 5m 随机 RSI 偏低 |
| `STOCHRSIk_1h < 40` | 1h 随机 RSI 也偏低 |
| `BBB_20_2.0_1h > 12` | 1h 布林带宽度较大，说明波动率足够 |
| `close_max_48 >= close * 1.10` | 最近 48 根内的最高价至少比当前价高 10%，说明刚经历较大回落 |

策略意图：

`144` 是一个“近期跌幅较大 + 波动率足够 + 多周期超卖”的条件。

Java 风格伪代码：

```java
boolean trigger144(Candle c) {
    return c.willr14 < -50.0
        && c.stochRsiK < 30.0
        && c.stochRsiK1h < 40.0
        && c.bollingerBandWidth1h > 12.0
        && c.closeMax48 >= c.close * 1.10;
}
```

更直白地说：

```text
这个币最近从高点跌了至少约 10%，而且 5m/1h 都偏超卖，策略认为可能有反弹空间。
```

## 10. 条件 145 详解

源码位置：`21952`

核心触发逻辑在 `22164-22172`：

```python
long_entry_logic.append(
    (df["RSI_14"] < 36.0)
    & (df["BBD_40_2.0"].gt(df["close"] * 0.020))
    & (df["close_delta"].gt(df["close"] * 0.02))
    & (df["BBT_40_2.0"].lt(df["BBD_40_2.0"] * 0.3))
    & (df["close"].lt(df["BBL_40_2.0"].shift()))
    & (df["close"].le(df["close"].shift()))
)
```

逐句解释：

| 条件 | 含义 |
| --- | --- |
| `RSI_14 < 36` | 标准 RSI 偏低，接近超卖 |
| `BBD_40_2.0 > close * 0.020` | 40周期布林带宽度足够大，波动不小 |
| `close_delta > close * 0.02` | 价格变化幅度较大，说明有明显下跌/波动 |
| `BBT_40_2.0 < BBD_40_2.0 * 0.3` | 布林带相关位置偏低，价格靠近下轨区域 |
| `close < BBL_40_2.0.shift()` | 当前收盘价低于上一根布林下轨 |
| `close <= close.shift()` | 当前收盘价不高于上一根，仍在下行或未反弹 |

策略意图：

`145` 是更典型的“布林带下轨跌破 + RSI 偏低”的均值回归条件。

Java 风格伪代码：

```java
boolean trigger145(Candle c, Candle prev) {
    return c.rsi14 < 36.0
        && c.bbd40 > c.close * 0.020
        && c.closeDelta > c.close * 0.020
        && c.bbt40 < c.bbd40 * 0.3
        && c.close < prev.bollingerLower40
        && c.close <= prev.close;
}
```

更直白地说：

```text
价格跌到布林带下轨附近甚至下方，同时 RSI 偏低，策略尝试捕捉超跌反弹。
```

## 11. 141-145 的对比总结

| 条件 | 核心类型 | 主要触发点 | 风格 |
| ---: | --- | --- | --- |
| 141 | RSI + SMA 回落 | `RSI_3 < 30` 且价格低于 `SMA16 * 0.96` | 偏深跌抄底 |
| 142 | RSI + SMA 回落 | `RSI_3 > 5`、`RSI_4 < 46`、价格低于短均线 | 避免极端崩盘的回落买入 |
| 143 | EMA 空头拉开 + 超卖 | `EMA26 > EMA12` 且差距较大，StochRSI 超卖 | 趋势下跌后的反弹 |
| 144 | 大跌幅 + 波动率 + 超卖 | 近 48 根高点比当前价高 10%，1h 波动足够 | 大幅回撤后的反弹 |
| 145 | 布林带下轨 + RSI | 跌破/接近布林下轨，RSI14 偏低 | 布林均值回归 |

## 12. 这些条件的本质

141-145 都不是追涨条件，而是偏“回落买入 / 超跌反弹”的条件。

它们共同想解决的问题是：

```text
在主流币里，找那些已经跌了一段、但还没有坏到完全不能买的位置。
```

这就是为什么它们有很多多周期保护：

- 5m 看短线是否超跌
- 15m 看短周期是否还危险
- 1h 看中短周期是否过热或过弱
- 4h 看大一些的趋势是否太差
- 1d 看日线级别是否过热、下行太猛或风险太大

## 13. 为什么这些条件会让胜率看起来很高

这些条件本身只是“找入场点”。

真正让胜率变高的是后面的：

- 宽止损
- 补仓
- grind 分段交易
- derisk 减仓
- top coins 专用退出逻辑

如果只看 141-145，你会误以为策略只是抄底。实际上它是：

```text
用多周期过滤找较优入场，再用复杂仓位管理把亏损单处理成盈利或小亏。
```

## 14. 初学者如何继续读源码

建议你接下来按这个顺序看：

1. 先看 `141-145` 的核心 `Logic` 部分，不要先看上百行保护过滤
2. 再看共同保护条件
3. 再回头看多周期过滤
4. 然后看 `long_exit_top_coins`
5. 最后看 `adjust_trade_position`

如果你只看入场条件，会少看一半逻辑。这个策略真正复杂的是入场后的处理。

## 15. Java 风格整体伪代码

```java
boolean topCoinsLongEntry(Candle c, Candle prev, int tag) {
    if (!isTopCoin(c.pair)) return false;
    if (c.numEmpty288 > allowedEmptyCandles288) return false;
    if (!c.protectionsLongGlobal) return false;

    switch (tag) {
        case 141:
            return safetyFilter141(c) && trigger141(c, prev);
        case 142:
            return safetyFilter142(c) && trigger142(c, prev);
        case 143:
            return safetyFilter143(c) && trigger143(c, prev);
        case 144:
            return safetyFilter144(c) && trigger144(c);
        case 145:
            return safetyFilter145(c) && trigger145(c, prev);
        default:
            return false;
    }
}
```

## 16. 一句话记忆

- `141`：RSI 下滑 + 价格深低于 SMA
- `142`：类似 141，但避免极端 RSI 崩盘
- `143`：EMA 空头拉开后的超卖反弹
- `144`：近期高点回落 10% 后的波动反弹
- `145`：跌破布林下轨后的均值回归

这五个条件都是 Top Coins 的多头“低吸/反弹”入口，不是趋势追涨入口。
