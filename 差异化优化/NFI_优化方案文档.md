# NFI 优化方案文档

> 适用对象：当前已经在 Freqtrade 中运行 NostalgiaForInfinity / NFI / NFI-X 系列策略，并且正在用小资金实盘测试的用户。  
> 目标：在不引入 AI 的情况下，先解决 NFI 常见的两个核心问题：**亏损死扛、持仓时间过长、卖出过于苛刻、交易频率偏低**。  
> 风险提示：本文是技术实施方案，不构成投资建议。所有参数必须先回测、再 dry-run、最后小资金实盘验证。

---

## 1. 背景与问题定义

NFI 类策略通常属于“趋势回调 + 低吸反弹”型策略。它的优势在于牛市或震荡上行市场中，能抓住回调后的反弹；它的问题也很明显：当市场从回调变成单边下跌时，策略容易把“下跌趋势”误判为“低吸机会”。

你当前观察到的问题可以拆成四类：

1. **卖出条件偏苛刻**
   - 盈利单可能迟迟不出。
   - 到手利润可能回吐。
   - 等待更高 ROI 导致交易完成周期过长。

2. **亏损单死扛**
   - 亏损后继续等待反弹。
   - 持仓时间过长。
   - 浮亏扩大，资金利用率下降。

3. **交易笔数偏少**
   - NFI 本身入场条件较严格。
   - 出场慢也会占用仓位，进一步降低新交易数量。

4. **行情状态适应性不足**
   - 牛市、震荡市、熊市使用近似同一套逻辑。
   - 在 BTC 或大盘走弱时，山寨币低吸信号容易失效。

---

## 2. 优化总原则

本方案不建议一开始大改 NFI 买入逻辑，而是按优先级逐层优化：

```text
第一优先级：控制亏损深度
第二优先级：缩短坏单持仓时间
第三优先级：保护盈利单利润
第四优先级：过滤弱行情
第五优先级：在风险下降后，再适度增加交易笔数
```

核心思路：

```text
不要先追求更多交易。
先让策略少亏、快认错、少死扛。
等风险指标改善后，再考虑放宽入场条件。
```

---

## 3. 优化目标

### 3.1 核心目标

| 目标 | 说明 |
|---|---|
| 降低最大浮亏 | 避免单笔交易深套 |
| 降低最大回撤 | 防止连续亏损拖垮账户 |
| 降低平均持仓时间 | 提高资金周转 |
| 降低亏损单平均亏损 | 小亏及时退出 |
| 保持或提升 Profit Factor | 不能为了频率牺牲质量 |
| 在风险稳定后增加交易数 | 交易数提升必须建立在回撤可控基础上 |

### 3.2 不建议追求的目标

| 不建议目标 | 原因 |
|---|---|
| 单纯提高胜率 | 高胜率可能来自死扛，风险更大 |
| 单纯提高交易数 | 可能引入大量垃圾交易 |
| 单纯追求最高回测收益 | 容易过拟合 |
| 无限优化参数 | 实盘失效概率高 |

---

## 4. 总体实施路线

```text
阶段 0：建立基准回测
阶段 1：增加硬止损和时间止损
阶段 2：优化盈利保护和退出逻辑
阶段 3：增加市场状态过滤
阶段 4：增加 Pair 级别保护机制
阶段 5：小幅放宽入场条件
阶段 6：Walk-forward 验证
阶段 7：Dry-run 验证
阶段 8：小资金实盘灰度
```

---

# 阶段 0：建立 NFI 原始基准

## 0.1 目的

任何优化前，必须先知道原始策略的基准表现。否则后面不知道改动是否真的有效。

## 0.2 建议回测周期

至少分三类行情：

| 行情类型 | 建议区间 |
|---|---|
| 上涨行情 | BTC 明显上涨阶段 |
| 震荡行情 | BTC 横盘阶段 |
| 下跌行情 | BTC 单边下跌阶段 |

如果你使用 5m 或 15m 周期，建议至少回测 6-12 个月数据。时间越短，结果越容易偶然。

## 0.3 基准指标

记录以下指标：

```text
Total profit
Profit factor
Win rate
Max drawdown
Average trade duration
Median trade duration
Worst trade
Average profit
Rejected signals
Total trades
Open-ended trades
Exit reason 分布
Pair 维度盈亏
```

## 0.4 建议保存文件

```text
backtest_baseline_original_nfi.json
backtest_baseline_original_nfi.csv
baseline_summary.md
```

---

# 阶段 1：增加硬止损

## 1.1 问题

NFI 最容易出现的问题是亏损单越拿越久。如果没有足够强的止损纪律，策略会在熊市或急跌行情中承受很大的浮亏。

## 1.2 优化点

增加硬止损：

```python
stoploss = -0.08
```

含义：单笔最大亏损约 8%。

对于小资金实盘，建议先测试：

```text
保守：-0.05
中性：-0.08
宽松：-0.10
```

## 1.3 实施任务

- [ ] 复制原 NFI 策略文件，命名为 `NFI_Optimized_V1.py`
- [ ] 设置明确的 `stoploss`
- [ ] 禁止无止损或超大止损
- [ ] 回测不同止损参数
- [ ] 对比最大回撤、亏损单平均亏损、总收益

## 1.4 验收标准

通过标准：

```text
最大回撤下降
单笔最大亏损下降
亏损单平均亏损下降
Profit Factor 不明显恶化
总收益不大幅下降
```

不通过标准：

```text
止损太紧导致频繁扫损
交易数增加但总收益下降
Profit Factor 明显下降
```

---

# 阶段 2：增加时间止损

## 2.1 问题

NFI 的很多亏损不是瞬间爆亏，而是“亏损单长时间不动，占用仓位”。时间止损用于解决这类问题。

## 2.2 设计原则

如果一笔交易持仓很久仍然亏损，说明买点质量可能不高，或者行情环境已经变化。

建议逻辑：

```text
持仓超过 24 小时且亏损 > 1%：退出
持仓超过 48 小时且仍未盈利：退出
持仓超过 72 小时且盈利低于 0.5%：退出或收紧止损
```

## 2.3 示例代码

```python
def custom_exit(self, pair, trade, current_time, current_rate,
                current_profit, **kwargs):

    trade_duration_min = (current_time - trade.open_date_utc).total_seconds() / 60

    # 持仓超过 24 小时且亏损超过 1.5%，退出
    if trade_duration_min > 24 * 60 and current_profit < -0.015:
        return "time_stop_24h_loss"

    # 持仓超过 48 小时仍然亏损，退出
    if trade_duration_min > 48 * 60 and current_profit < 0:
        return "time_stop_48h_negative"

    # 持仓超过 72 小时，利润很低，退出释放资金
    if trade_duration_min > 72 * 60 and current_profit < 0.005:
        return "time_stop_72h_low_profit"

    return None
```

## 2.4 回测验证重点

| 指标 | 期望变化 |
|---|---|
| 平均持仓时间 | 明显下降 |
| 最大持仓时间 | 明显下降 |
| 亏损单平均亏损 | 下降 |
| 总交易数 | 可能上升 |
| 总收益 | 不能明显恶化 |
| Profit Factor | 尽量保持或提升 |

## 2.5 风险

时间止损可能会卖飞一些后续反弹单。所以不能只看单笔案例，要看整体统计。

---

# 阶段 3：增加动态止损

## 3.1 目的

硬止损解决“最大亏损”，但不够灵活。动态止损可以根据当前收益、持仓时间、趋势状态调整退出阈值。

## 3.2 推荐逻辑

```text
盈利 > 2%：止损提高到 -1.5% 到 -2%
盈利 > 4%：止损提高到 -1%
亏损超过 -3% 且行情弱：最大亏损收紧
持仓越久，允许亏损越小
```

## 3.3 示例代码

```python
use_custom_stoploss = True
stoploss = -0.08

def custom_stoploss(self, pair, trade, current_time, current_rate,
                    current_profit, **kwargs):

    trade_duration_min = (current_time - trade.open_date_utc).total_seconds() / 60

    # 盈利保护
    if current_profit > 0.04:
        return -0.01

    if current_profit > 0.02:
        return -0.02

    # 持仓越久，越不允许继续深亏
    if trade_duration_min > 48 * 60 and current_profit < -0.02:
        return -0.035

    if trade_duration_min > 24 * 60 and current_profit < -0.03:
        return -0.045

    # 默认最大亏损
    return -0.08
```

## 3.4 注意事项

如果使用 `custom_stoploss()`，需要谨慎处理 `trailing_stop`，避免两个机制互相冲突。建议先只启用一种利润保护逻辑，稳定后再组合测试。

---

# 阶段 4：优化盈利退出

## 4.1 问题

NFI 有时为了吃更大波段，导致已有利润回吐。优化盈利退出不是为了“卖在最高点”，而是为了提高资金周转和降低回撤。

## 4.2 推荐退出规则

```text
盈利达到 2% 后，如果动量衰减，退出
盈利达到 3% 后，如果跌破短 EMA，退出
盈利达到 5% 后，启用更紧的保护
持仓超过 24 小时且利润不足 1%，退出
```

## 4.3 示例逻辑

```python
def custom_exit(self, pair, trade, current_time, current_rate,
                current_profit, **kwargs):

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last = dataframe.iloc[-1]

    trade_duration_min = (current_time - trade.open_date_utc).total_seconds() / 60

    # 盈利后动量减弱，落袋
    if current_profit > 0.025:
        if last["rsi"] < 50 and last["close"] < last["ema_20"]:
            return "profit_momentum_exit"

    # 高利润保护
    if current_profit > 0.05:
        if last["close"] < last["ema_12"]:
            return "high_profit_protection_exit"

    # 低效率持仓退出
    if trade_duration_min > 24 * 60 and 0 < current_profit < 0.01:
        return "low_efficiency_profit_exit"

    return None
```

## 4.4 验收标准

```text
盈利单平均持仓时间下降
利润回吐减少
总交易数增加
总收益不明显下降
最大回撤下降
```

---

# 阶段 5：增加市场状态过滤

## 5.1 为什么需要市场过滤

NFI 低吸逻辑在上涨趋势回调中有效，但在单边下跌中危险。因此要增加市场状态判断。

## 5.2 推荐过滤条件

### BTC 大盘过滤

如果交易山寨币，建议所有交易参考 BTC 状态：

```text
BTC 4h close > BTC 4h EMA200：允许正常交易
BTC 4h close < BTC 4h EMA200：减少交易或禁止弱信号
BTC 4h RSI < 35 且跌破 EMA：暂停低吸
```

### 本币趋势过滤

```text
当前交易对 close > EMA200：允许正常交易
当前交易对 close < EMA200：只允许强反弹信号
```

### 波动率过滤

```text
ATR 急剧放大时，降低仓位或禁止入场
连续大阴线后，不立即低吸
```

## 5.3 示例任务

- [ ] 添加 BTC 信息周期指标，例如 1h / 4h
- [ ] 添加 `market_ok` 字段
- [ ] 在 `populate_entry_trend()` 或 `confirm_trade_entry()` 中过滤弱行情
- [ ] 回测牛市、震荡市、熊市表现

## 5.4 示例伪代码

```python
market_ok = (
    btc_close_4h > btc_ema200_4h and
    btc_rsi_4h > 40
)

if not market_ok:
    # 禁止弱低吸信号
    dataframe.loc[dataframe["entry_tag"].str.contains("weak", na=False), "enter_long"] = 0
```

---

# 阶段 6：增加 Protections

## 6.1 目的

Protections 用来防止策略在坏行情里连续交易，尤其适合 NFI 这种容易连续低吸的策略。

## 6.2 推荐保护

| Protection | 作用 |
|---|---|
| CooldownPeriod | 卖出后冷却，避免马上重新进入 |
| StoplossGuard | 连续止损后暂停交易 |
| MaxDrawdown | 总体回撤过大时暂停 |
| LowProfitPairs | 某交易对近期表现差时暂停 |

## 6.3 示例配置

```json
"protections": [
  {
    "method": "CooldownPeriod",
    "stop_duration_candles": 12
  },
  {
    "method": "StoplossGuard",
    "lookback_period_candles": 72,
    "trade_limit": 3,
    "stop_duration_candles": 48,
    "only_per_pair": false
  },
  {
    "method": "MaxDrawdown",
    "lookback_period_candles": 288,
    "trade_limit": 20,
    "stop_duration_candles": 72,
    "max_allowed_drawdown": 0.08
  },
  {
    "method": "LowProfitPairs",
    "lookback_period_candles": 288,
    "trade_limit": 3,
    "stop_duration_candles": 72,
    "required_profit": 0.01
  }
]
```

## 6.4 验收标准

```text
连续亏损次数下降
同一交易对反复亏损减少
最大回撤下降
总收益不明显下降
```

---

# 阶段 7：适度增加交易笔数

## 7.1 前提条件

只有在以下条件满足后，才建议增加交易笔数：

```text
最大回撤下降
亏损单平均亏损下降
平均持仓时间下降
Profit Factor 没有明显下降
Dry-run 表现稳定
```

## 7.2 可放宽的方向

不要全面放宽。只放宽部分候选信号。

| 可放宽项 | 建议 |
|---|---|
| RSI 阈值 | 小幅放宽，例如 30 改 33 |
| BB 偏离 | 小幅放宽 |
| EMA 偏离 | 小幅放宽 |
| 成交量条件 | 不建议过度放宽 |
| BTC 弱行情过滤 | 不建议放宽 |

## 7.3 建议新增 entry_tag

所有新增交易必须带 tag，方便后续统计：

```text
nfi_original_buy
nfi_weak_dip_buy
nfi_trend_pullback_buy
nfi_reversal_candidate
```

## 7.4 验证方式

分别统计每种 `entry_tag` 的表现：

```text
交易次数
胜率
平均收益
亏损单平均亏损
Profit Factor
最大连续亏损
平均持仓时间
```

如果某个新增 tag 表现差，直接删除，不要继续调参硬救。

---

# 阶段 8：回测验证方案

## 8.1 回测分组

至少建立以下版本：

| 版本 | 说明 |
|---|---|
| Baseline | 原始 NFI |
| V1 | 硬止损 |
| V2 | 硬止损 + 时间止损 |
| V3 | V2 + 动态止损 |
| V4 | V3 + 盈利保护 |
| V5 | V4 + 市场过滤 |
| V6 | V5 + Protections |
| V7 | V6 + 小幅增加交易信号 |

## 8.2 回测命令示例

```bash
freqtrade backtesting \
  --strategy NFI_Optimized_V1 \
  --timerange 20240101-20240601 \
  --timeframe 5m \
  --export trades
```

## 8.3 多行情回测

```bash
# 上涨行情
freqtrade backtesting --strategy NFI_Optimized_V1 --timerange 20240101-20240315 --export trades

# 震荡行情
freqtrade backtesting --strategy NFI_Optimized_V1 --timerange 20240316-20240515 --export trades

# 下跌行情
freqtrade backtesting --strategy NFI_Optimized_V1 --timerange 20240516-20240730 --export trades
```

## 8.4 禁止只看总收益

必须重点看：

```text
Max drawdown
Worst trade
Average losing trade
Average duration
Exit reason
Pair performance
Tag performance
Profit factor
Expectancy
```

---

# 阶段 9：Walk-forward 验证

## 9.1 为什么需要 Walk-forward

如果你只在一个时间段调参，很容易过拟合。Walk-forward 的目标是验证策略在未参与优化的数据上是否仍然有效。

## 9.2 建议流程

```text
训练/优化区间：前 3 个月
验证区间：后 1 个月
向前滚动
重复 6-12 次
```

示例：

| 轮次 | 优化区间 | 验证区间 |
|---|---|---|
| 1 | 1-3 月 | 4 月 |
| 2 | 2-4 月 | 5 月 |
| 3 | 3-5 月 | 6 月 |
| 4 | 4-6 月 | 7 月 |

## 9.3 通过标准

```text
大多数验证区间 Profit Factor > 1
最大回撤可控
没有某一个月份爆亏
不同市场状态都没有明显崩溃
```

---

# 阶段 10：Dry-run 与小资金实盘

## 10.1 Dry-run 周期

建议至少：

```text
7 天：基本运行稳定性
14 天：观察交易行为
30 天：观察不同市场环境
```

## 10.2 Dry-run 记录

每天记录：

```text
产生了多少信号
实际开了多少单
拒绝了多少单
平均持仓时间
当前浮亏
最大浮亏
退出原因
是否有异常重复开单
```

## 10.3 小资金实盘规则

```text
第一周：极小仓位
第二周：如果表现稳定，略微增加
连续 3 笔异常亏损：暂停
总回撤超过 5%-8%：暂停
某交易对连续亏损：加入黑名单或冷却
```

---

# 11. 推荐最终策略结构

```text
NFI_Optimized
├── 原始 NFI 入场逻辑
├── entry_tag 标记
├── 硬止损
├── 时间止损
├── 动态止损
├── 盈利保护退出
├── BTC 大盘过滤
├── 本币趋势过滤
├── Protections
└── 回测统计脚本
```

---

# 12. 优先级任务清单

## P0：必须做

- [ ] 建立原始 NFI 基准回测
- [ ] 增加硬止损
- [ ] 增加时间止损
- [ ] 增加 entry_tag 和 exit_tag 统计
- [ ] 保存所有回测结果

## P1：强烈建议

- [ ] 增加动态止损
- [ ] 增加盈利保护
- [ ] 增加 BTC 4h 市场过滤
- [ ] 增加 CooldownPeriod 和 StoplossGuard

## P2：后续优化

- [ ] 增加 MaxDrawdown
- [ ] 增加 LowProfitPairs
- [ ] 小幅放宽弱买点
- [ ] 按 tag 删除低质量信号

---

# 13. 成功标准

该优化方案成功的标准不是“收益最高”，而是：

```text
最大回撤下降 20%-40%
亏损单平均亏损下降
平均持仓时间下降
坏单不再长期死扛
Profit Factor 不低于原始 NFI
交易数在风险不升高的情况下小幅增加
```

如果能做到以上几点，即使总收益没有明显提高，也说明策略质量提升了。

---

# 14. 失败信号

如果出现以下情况，说明优化方向有问题：

```text
交易数增加，但回撤更大
止损频繁触发，胜率大幅下降
时间止损卖飞大量盈利单
Profit Factor 明显下降
某些 pair 贡献大部分亏损
新增 weak buy tag 表现很差
```

处理方式：

```text
先删除新增弱信号
再放宽时间止损
然后重新评估止损阈值
最后检查市场过滤是否过严或过松
```

---

# 15. 推荐实施顺序总结

```text
第 1 步：原始 NFI 回测
第 2 步：加硬止损
第 3 步：加时间止损
第 4 步：加盈利保护
第 5 步：加市场过滤
第 6 步：加 Protections
第 7 步：按 tag 统计
第 8 步：再考虑增加交易笔数
```

---

# 16. 参考资料

- Freqtrade Strategy Callbacks：`custom_exit()`、`custom_stoploss()`、`custom_roi()`、`confirm_trade_entry()` 等回调说明  
  https://www.freqtrade.io/en/stable/strategy-callbacks/

- Freqtrade Backtesting：回测流程和数据要求  
  https://www.freqtrade.io/en/stable/backtesting/

- Freqtrade Hyperopt：参数优化流程  
  https://www.freqtrade.io/en/stable/hyperopt/

- Freqtrade Protections / Plugins：`CooldownPeriod`、`StoplossGuard`、`MaxDrawdown`、`LowProfitPairs`  
  https://www.freqtrade.io/en/stable/plugins/

- Freqtrade Bot Basics：交易流程中 entry、exit、custom callbacks 的调用位置  
  https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md
