# NostalgiaForInfinityX7 完整学习索引

这套文档是为 Python 初学者、Java 开发者视角准备的。原策略文件非常大，核心难点不是 Python 语法本身，而是 Freqtrade 生命周期、Pandas 向量化条件、不同模式 tag、以及 custom_exit / adjust_trade_position 这些运行期回调之间的配合。

## 建议阅读顺序

1. `NFI_X7_CODE_GUIDE_FOR_JAVA_BEGINNER.md`
   - 先建立整体认知：这个 Python 文件相当于一个 Java 策略类，Freqtrade 框架会在不同阶段调用它的方法。

2. `NFI_X7_FUNCTION_MAP.md`
   - 当作目录。你想找某个函数时，先从这里定位。

3. `NFI_X7_INDICATORS_AND_DATAFLOW_EXPLAINED.md`
   - 重点理解数据是怎么来的、指标列是怎么加到 DataFrame 上的、多周期数据是怎么合并的。

4. `NFI_X7_TOP_COINS_141_145_EXPLAINED.md`
   - 重点理解你之前测试收益最高的 top coins 入场逻辑。

5. `NFI_X7_EXIT_LOGIC_EXPLAINED.md`
   - 理解它为什么胜率很高：出场不是简单卖出，而是有利润目标缓存、延迟卖出、止损拦截等机制。

6. `NFI_X7_POSITION_ADJUSTMENT_GRIND_REBUY_DERISK_EXPLAINED.md`
   - 理解补仓、减仓、grind、rebuy、derisk。这个部分直接影响小资金能不能跑起来。

7. `NFI_X7_CONFIG_AND_RISK_NOTES.md`
   - 从实盘风险角度看这个策略，包括资金量、max_open_trades、stoploss=-99%、回测胜率 100% 的含义。

8. `NFI_X7_JAVA_STYLE_PSEUDOCODE.md`
   - 用 Java 思维重写核心结构，帮助你把 Python/Freqtrade 逻辑映射成熟悉的类、方法、对象。

## 一句话理解这个策略

NostalgiaForInfinityX7 是一个多模式、多周期、强状态化的 Freqtrade 策略。它会先在 5m 主周期上生成大量指标，同时合并 15m、1h、4h、1d 以及 BTC 相关指标，然后根据不同 tag 触发入场；交易打开后，策略通过 custom_exit 控制何时卖出，通过 adjust_trade_position 控制是否补仓或减仓。

## 最重要的几个概念

- DataFrame：类似 Java 里的 `List<Candle>` 加很多指标字段，但 Pandas 是按整列批量计算。
- tag：每次入场会记录策略编号，例如 `141`、`142`，之后出场和补仓会根据这个 tag 选择不同逻辑。
- informative timeframe：辅助周期，例如 1h、4h、1d，用来判断大趋势。
- custom_exit：运行中决定是否卖出。
- adjust_trade_position：运行中决定是否追加仓位或部分减仓。
- target_profit_cache：策略自己维护的利润目标缓存，用来尝试吃更多利润。

## 学习重点

不要一开始就试图逐行读完整个 7 万多行文件。更好的方式是先掌握框架调用顺序：

```text
informative_pairs -> populate_indicators -> populate_entry_trend -> confirm_trade_entry
                                               |
                                               v
                                  交易打开后 custom_exit / adjust_trade_position
                                               |
                                               v
                                      confirm_trade_exit
```

掌握这个流程后，再去看某个具体 tag 的入场/出场条件，会容易很多。
