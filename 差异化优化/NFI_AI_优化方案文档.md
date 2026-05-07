# NFI + AI 优化方案文档

> 适用对象：已经运行 NostalgiaForInfinity / NFI / NFI-X 系列策略，并希望引入 FreqAI 或机器学习模块改善风控、退出、入场过滤和交易频率的用户。  
> 核心目标：**不用 AI 替代 NFI，而是让 AI 成为 NFI 的风控层、过滤层和退出辅助层**。  
> 风险提示：AI 不会自动创造稳定收益。本文是技术实施方案，不构成投资建议。所有 AI 模型必须经过回测、Walk-forward、dry-run 和小资金实盘验证。

---

## 1. 核心结论

NFI + AI 的正确方向不是：

```text
AI 直接预测涨跌 → AI 自动买卖
```

而是：

```text
NFI 产生候选交易
AI 判断交易质量
AI 过滤危险低吸
AI 识别坏单
AI 辅助提前退出
AI 控制持仓时间和浮亏
```

你当前的两个目标：

1. **小亏损，避免死扛**
2. **在不增加亏损的情况下扩大交易笔数**

可以用 AI 辅助改善，但实现顺序必须正确：

```text
先用 AI 降低坏单损失
再用 AI 过滤弱买点
最后才考虑增加交易数量
```

---

## 2. 为什么 NFI 适合加 AI 风控层

NFI 的核心问题不是完全没有买点，而是：

```text
它不知道什么时候 dip 是机会，什么时候 dip 是下跌趋势的开始。
```

传统 NFI 主要根据技术指标低吸，比如 RSI、EMA 偏离、Bollinger Band、成交量、趋势位置等。AI 最适合补充的不是更多技术指标，而是：

```text
市场状态识别
危险低吸识别
坏单提前识别
未来回撤概率预测
未来收益/风险比预测
```

---

## 3. NFI + AI 总体架构

推荐结构：

```text
NFI 原始策略
    ↓
产生候选买点
    ↓
FreqAI / ML 模型预测：
    - 未来收益
    - 未来最大回撤
    - 好交易概率
    - 坏单概率
    - 市场状态
    ↓
confirm_trade_entry()
    - AI 入场过滤
    ↓
custom_exit()
    - AI 坏单提前退出
    - AI 辅助止盈
    ↓
custom_stoploss()
    - AI 动态收紧止损
    ↓
custom_roi()
    - AI 动态止盈阈值
```

---

# 4. AI 不应该做什么

## 4.1 不建议 AI 直接开单

不要让 AI 在没有 NFI 信号时独立买入。

原因：

```text
AI 直接预测涨跌很容易过拟合
模型容易学习到历史噪音
实盘行情分布会变化
训练数据不足时效果不稳定
```

## 4.2 不建议一开始做强化学习

强化学习在交易里难度很高，样本效率低，实盘稳定性差。对于当前小资金实盘阶段，不建议作为第一版方案。

## 4.3 不建议优化太多特征和参数

特征越多，不代表越好。NFI + AI 最容易陷入：

```text
无限加指标
无限调参数
回测越来越好
实盘越来越差
```

---

# 5. AI 应该介入的四个环节

## 5.1 环节一：confirm_trade_entry() 入场过滤

用途：

```text
NFI 给出买入信号后，AI 判断是否允许真实开仓。
```

适合解决：

```text
危险低吸
弱行情抄底
BTC 大盘走坏时继续买山寨
波动率异常时误入场
```

示例逻辑：

```text
NFI 买入信号 = True
AI 预测未来收益 > 1.5%
AI 预测未来最大回撤 > -3%
AI 好交易概率 > 55%
市场状态不是 panic
→ 允许入场
否则拒绝
```

---

## 5.2 环节二：custom_exit() 坏单提前退出

用途：

```text
持仓后，如果 AI 判断这笔单继续恶化概率高，则提前小亏退出。
```

这是最适合你当前痛点的 AI 环节。

示例逻辑：

```text
当前亏损 -1.5% 到 -4%
AI 预测未来收益为负
AI 预测未来最大回撤继续扩大
持仓时间超过 N 根 K 线
→ 提前退出
```

---

## 5.3 环节三：custom_stoploss() 动态止损

用途：

```text
根据 AI 判断动态收紧最大亏损。
```

示例逻辑：

```text
正常情况下最大止损 -8%
AI 看坏时收紧到 -3.5%
盈利后止损上移保护利润
持仓越久，允许亏损越小
```

---

## 5.4 环节四：custom_roi() 动态止盈

用途：

```text
AI 判断未来空间不大时，降低止盈要求，提前退出。
AI 判断趋势仍强时，允许持仓更久。
```

示例逻辑：

```text
AI 预测未来收益低：ROI 降低，尽快落袋
AI 预测未来收益高：ROI 提高，继续持有
```

---

# 6. AI 目标变量设计

AI 目标变量比模型本身更重要。不要只预测“涨/跌”，建议预测以下三个目标。

---

## 6.1 目标一：未来收益

预测未来 N 根 K 线后的收益。

```python
label_period = 12

df["&-future_return"] = (
    df["close"].shift(-label_period) / df["close"] - 1
)
```

用途：

```text
判断这笔交易未来是否有上涨空间。
```

建议周期：

| Timeframe | label_period |
|---|---|
| 5m | 12-24 根，即 1-2 小时 |
| 15m | 8-16 根，即 2-4 小时 |
| 1h | 6-12 根，即 6-12 小时 |

---

## 6.2 目标二：未来最大回撤

预测未来 N 根 K 线内最低价相对当前价格的跌幅。

```python
label_period = 12

future_min = df["low"].shift(-1).rolling(label_period).min()
df["&-future_drawdown"] = future_min / df["close"] - 1
```

用途：

```text
判断这笔交易是否容易先深跌。
```

这对解决 NFI 死扛问题最重要。

---

## 6.3 目标三：好交易分类

定义一个“好交易”的标签：

```python
df["&-good_trade"] = (
    (df["&-future_return"] > 0.015) &
    (df["&-future_drawdown"] > -0.03)
).astype(int)
```

含义：

```text
未来有至少 1.5% 空间
并且中途最大回撤不超过 3%
```

这个标签比单纯预测涨跌更适合实盘。

---

## 6.4 目标四：坏单分类

定义一个“坏单”标签：

```python
df["&-bad_trade"] = (
    (df["&-future_return"] < -0.005) |
    (df["&-future_drawdown"] < -0.04)
).astype(int)
```

用途：

```text
帮助 custom_exit() 提前小亏出场。
```

---

# 7. AI 特征工程设计

FreqAI 的特征工程通常在策略中的 `feature_engineering_*` 函数内完成，特征名一般使用 `%` 前缀，目标/标签使用 `&` 前缀。

## 7.1 不要只喂 NFI 已经使用的指标

NFI 本身已经大量使用 RSI、EMA、BB、成交量等指标。AI 如果只重复这些指标，增益有限。

更推荐加入：

```text
市场环境类特征
波动率特征
趋势斜率特征
成交量异常特征
BTC 信息周期特征
持仓风险特征
```

---

## 7.2 市场环境类特征

建议加入 BTC 相关特征：

```text
BTC 1h return
BTC 4h return
BTC 4h EMA200 位置
BTC 4h RSI
BTC 4h ATR
BTC 4h trend slope
```

用途：

```text
避免山寨币在 BTC 走弱时继续低吸。
```

---

## 7.3 趋势强弱特征

```python
df["%-ema_20_dist"] = df["close"] / df["ema_20"] - 1
df["%-ema_50_dist"] = df["close"] / df["ema_50"] - 1
df["%-ema_200_dist"] = df["close"] / df["ema_200"] - 1
df["%-ema_50_slope"] = df["ema_50"].pct_change(12)
df["%-ema_200_slope"] = df["ema_200"].pct_change(12)
```

用途：

```text
判断当前是上涨回调，还是下跌趋势。
```

---

## 7.4 波动率特征

```python
df["%-atr_pct"] = df["atr"] / df["close"]
df["%-volatility_24"] = df["close"].pct_change().rolling(24).std()
df["%-range_pct"] = (df["high"] - df["low"]) / df["close"]
```

用途：

```text
避免波动率突然放大时盲目抄底。
```

---

## 7.5 成交量异常特征

```python
df["%-volume_zscore"] = (
    (df["volume"] - df["volume"].rolling(48).mean()) /
    df["volume"].rolling(48).std()
)
df["%-volume_ratio"] = df["volume"] / df["volume"].rolling(48).mean()
```

用途：

```text
识别恐慌砸盘或异常放量。
```

---

## 7.6 回撤速度特征

```python
df["%-return_3"] = df["close"].pct_change(3)
df["%-return_6"] = df["close"].pct_change(6)
df["%-return_12"] = df["close"].pct_change(12)
df["%-drawdown_24"] = df["close"] / df["close"].rolling(24).max() - 1
```

用途：

```text
判断下跌是否过快，避免接飞刀。
```

---

# 8. 推荐模型选择

## 8.1 第一阶段推荐

| 模型 | 推荐度 | 原因 |
|---|---|---|
| LightGBM Regressor / Classifier | 高 | 训练快，适合表格特征 |
| CatBoost | 高 | 对非线性关系较好 |
| XGBoost | 中高 | 成熟稳定 |
| RandomForest | 中 | 简单但可能效果一般 |

## 8.2 不建议第一阶段使用

| 模型 | 原因 |
|---|---|
| LSTM | 数据量要求高，容易过拟合 |
| Transformer | 复杂度高，实盘维护难 |
| Reinforcement Learning | 样本效率低，稳定性差 |
| 深度神经网络 | 对特征和数据质量要求高 |

---

# 9. 第一版落地方案：AI 只做退出

这是最建议你先做的版本。

## 9.1 目标

解决：

```text
亏损死扛
持仓时间过长
浮亏过高
坏单不认错
```

## 9.2 策略结构

```text
NFI 正常买入
NFI 正常管理持仓
AI 每根 K 线预测坏单概率
如果亏损单变坏 → custom_exit() 提前退出
```

## 9.3 示例退出逻辑

```python
def custom_exit(self, pair, trade, current_time, current_rate,
                current_profit, **kwargs):

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last = dataframe.iloc[-1]

    trade_duration_min = (current_time - trade.open_date_utc).total_seconds() / 60

    ai_ready = last.get("do_predict", 0) == 1
    predicted_return = last.get("&-future_return", 0)
    predicted_drawdown = last.get("&-future_drawdown", 0)
    bad_trade_score = last.get("&-bad_trade", 0)

    # AI 看坏 + 当前已经亏损，提前退出
    if ai_ready:
        if current_profit < -0.02 and predicted_return < -0.005:
            return "ai_negative_return_exit"

        if current_profit < -0.015 and predicted_drawdown < -0.035:
            return "ai_drawdown_risk_exit"

        if current_profit < -0.02 and bad_trade_score > 0.55:
            return "ai_bad_trade_exit"

    # 时间止损兜底
    if trade_duration_min > 24 * 60 and current_profit < -0.015:
        return "time_stop_24h_loss"

    if trade_duration_min > 48 * 60 and current_profit < 0:
        return "time_stop_48h_negative"

    return None
```

## 9.4 第一版验收指标

通过标准：

```text
亏损单平均亏损下降
最大浮亏下降
平均持仓时间下降
最大回撤下降
Profit Factor 不明显下降
```

不通过标准：

```text
AI 过早退出大量后续盈利单
总收益明显下降
交易数下降太多
亏损单减少但盈利单也被过度砍掉
```

---

# 10. 第二版落地方案：AI 动态止损

## 10.1 目标

在 AI 判断行情不利时，降低最大亏损阈值。

## 10.2 示例逻辑

```python
use_custom_stoploss = True
stoploss = -0.08

def custom_stoploss(self, pair, trade, current_time, current_rate,
                    current_profit, **kwargs):

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last = dataframe.iloc[-1]

    ai_ready = last.get("do_predict", 0) == 1
    predicted_drawdown = last.get("&-future_drawdown", 0)
    predicted_return = last.get("&-future_return", 0)

    # 盈利保护
    if current_profit > 0.04:
        return -0.01

    if current_profit > 0.02:
        return -0.02

    # AI 看坏，收紧止损
    if ai_ready:
        if current_profit < -0.015 and predicted_drawdown < -0.035:
            return -0.035

        if current_profit < -0.02 and predicted_return < -0.005:
            return -0.04

    # 默认止损
    return -0.08
```

## 10.3 注意

`custom_stoploss()` 更适合移动止损线；如果你想立即退出，应该使用 `custom_exit()`。

---

# 11. 第三版落地方案：AI 入场过滤

## 11.1 目标

过滤 NFI 的危险低吸信号，尤其在 BTC 或市场走弱时避免开仓。

## 11.2 示例逻辑

```python
def confirm_trade_entry(self, pair, order_type, amount, rate,
                        time_in_force, current_time, entry_tag,
                        side, **kwargs):

    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last = dataframe.iloc[-1]

    ai_ready = last.get("do_predict", 0) == 1

    if not ai_ready:
        # 第一版建议：AI 不可用时，只允许原始强信号，不允许弱信号
        if "weak" in str(entry_tag):
            return False
        return True

    predicted_return = last.get("&-future_return", 0)
    predicted_drawdown = last.get("&-future_drawdown", 0)
    good_trade_score = last.get("&-good_trade", 0)

    # 强信号可以放宽一点
    if "nfi_original" in str(entry_tag):
        if predicted_drawdown < -0.05:
            return False
        return True

    # 弱信号必须经过 AI 放行
    if "weak" in str(entry_tag):
        if predicted_return > 0.012 and predicted_drawdown > -0.03 and good_trade_score > 0.55:
            return True
        return False

    return True
```

---

# 12. 第四版落地方案：AI 扩大交易笔数

## 12.1 前提

必须先满足：

```text
AI Exit Filter 有效
最大回撤下降
亏损单平均亏损下降
平均持仓时间下降
Dry-run 正常
```

如果这些没有完成，不建议扩大交易笔数。

## 12.2 方法

不要让 AI 独立找买点，而是新增弱候选信号。

```text
NFI 原始强买点：继续保留
NFI 新增弱买点：必须 AI 放行
```

## 12.3 可放宽的信号

| 原始逻辑 | 可放宽方式 |
|---|---|
| RSI < 30 | 改为 RSI < 33 或 35，但必须 AI 放行 |
| close 低于 BB 下轨 | 改为接近下轨，但必须 AI 放行 |
| EMA 偏离较大 | 降低偏离要求，但必须 AI 放行 |
| volume 条件严格 | 仅小幅放宽 |

## 12.4 不建议放宽的条件

```text
BTC 大盘过滤
极端波动过滤
黑名单 pair
连续亏损后的保护
```

---

# 13. FreqAI 配置建议

## 13.1 第一版配置原则

```text
模型简单
特征适中
训练周期不要太短
不要高频重新训练
先稳定再复杂
```

## 13.2 建议参数方向

```json
"freqai": {
  "enabled": true,
  "purge_old_models": true,
  "train_period_days": 60,
  "backtest_period_days": 7,
  "identifier": "nfi_ai_exit_v1",
  "feature_parameters": {
    "include_timeframes": ["5m", "15m", "1h", "4h"],
    "include_corr_pairlist": ["BTC/USDT"],
    "label_period_candles": 12,
    "include_shifted_candles": 2,
    "DI_threshold": 1
  },
  "data_split_parameters": {
    "test_size": 0.25,
    "shuffle": false
  }
}
```

## 13.3 配置解释

| 参数 | 说明 |
|---|---|
| train_period_days | 用多少天数据训练 |
| backtest_period_days | 每次验证多少天 |
| include_timeframes | 多周期特征 |
| include_corr_pairlist | 加入 BTC 等相关币种 |
| label_period_candles | 预测未来多少根 K 线 |
| shuffle=false | 时间序列不要随机打乱 |

---

# 14. 回测验证方案

## 14.1 对比版本

必须至少对比以下版本：

| 版本 | 说明 |
|---|---|
| Baseline | 原始 NFI |
| NFI_V1 | 不加 AI，只加硬止损和时间止损 |
| NFI_AI_EXIT | AI 只做退出 |
| NFI_AI_STOP | AI 退出 + AI 动态止损 |
| NFI_AI_ENTRY | AI 退出 + AI 入场过滤 |
| NFI_AI_WEAK_ENTRY | AI 过滤弱买点，尝试增加交易数 |

## 14.2 回测命令示例

```bash
freqtrade backtesting \
  --strategy NFI_AI_Exit_V1 \
  --config config_freqai.json \
  --timerange 20240101-20240601 \
  --timeframe 5m \
  --freqaimodel LightGBMRegressor \
  --export trades
```

## 14.3 分行情测试

```text
上涨行情：验证不会错过大行情
震荡行情：验证交易频率和资金周转
下跌行情：验证是否减少死扛
急跌行情：验证是否避免接飞刀
```

## 14.4 必看指标

```text
Total profit
Profit factor
Max drawdown
Worst trade
Average losing trade
Average duration
Median duration
Total trades
Rejected entries
Exit reason 分布
Entry tag 表现
Pair 表现
AI exit 后是否出现大量卖飞
```

---

# 15. Walk-forward 验证

## 15.1 为什么 AI 必须 Walk-forward

AI 很容易过拟合。如果只看单一回测区间，结果不可信。

## 15.2 推荐流程

```text
训练 60 天
验证 7 天
向前滚动
重复至少 12 次
```

示例：

| 轮次 | 训练区间 | 验证区间 |
|---|---|---|
| 1 | 1月1日-3月1日 | 3月2日-3月8日 |
| 2 | 1月8日-3月8日 | 3月9日-3月15日 |
| 3 | 1月15日-3月15日 | 3月16日-3月22日 |

## 15.3 通过标准

```text
多数验证区间 Profit Factor > 1
最大回撤下降
AI 退出不是只在某个区间有效
不同 pair 不依赖单一币种盈利
下跌行情表现明显优于原始 NFI
```

---

# 16. AI 模型效果评估

## 16.1 不只看模型准确率

交易模型不能只看 accuracy。一个 60% 准确率模型，如果错误时亏很多，仍然没用。

重点看：

```text
AI 拒绝的交易后续表现
AI 放行的交易后续表现
AI 提前退出的交易，如果不退出会怎样
AI 退出后是否经常卖飞
AI 信号与实际收益/回撤的相关性
```

## 16.2 建议建立分析表

| 分析项 | 目的 |
|---|---|
| AI 允许入场交易 | 看 AI 放行质量 |
| AI 拒绝入场交易 | 看是否错过太多好单 |
| AI 提前退出交易 | 看是否减少亏损 |
| AI 卖飞交易 | 看是否过早退出 |
| AI bad_trade_score 分组 | 看分数是否有区分度 |

## 16.3 分组验证

按 AI 分数分桶：

```text
0.0-0.2
0.2-0.4
0.4-0.6
0.6-0.8
0.8-1.0
```

如果高分桶和低分桶的交易结果没有明显区别，说明模型没有实用价值。

---

# 17. 实盘灰度方案

## 17.1 灰度顺序

```text
第 1 周：只启用 AI 观察，不影响交易
第 2 周：启用 AI 退出，但不开启 AI 入场过滤
第 3 周：启用 AI 动态止损
第 4 周：启用 AI 过滤弱买点
第 5 周后：考虑小幅增加交易数
```

## 17.2 第 1 周影子模式

AI 只打标签，不实际退出：

```text
记录 AI 当时是否建议退出
记录如果退出会怎样
记录实际 NFI 后续表现
```

这一步很重要，可以判断 AI 是否有价值。

## 17.3 第 2 周小资金启用

只允许 AI 做：

```text
亏损单提前退出
```

不允许 AI：

```text
独立开单
扩大交易频率
加仓
```

## 17.4 暂停条件

出现以下情况立即关闭 AI 模块：

```text
连续 5 次 AI 提前退出后，价格快速反弹
AI 退出导致总收益明显低于原策略
AI 信号频繁缺失或异常
实盘和回测差异过大
总回撤超过预设阈值
```

---

# 18. 任务拆解

## P0：基础准备

- [ ] 复制当前 NFI 策略作为新策略文件
- [ ] 建立原始 NFI 基准回测
- [ ] 增加 entry_tag / exit_tag 统计
- [ ] 确认 FreqAI 环境可运行
- [ ] 准备 BTC 相关信息周期数据

## P1：AI Exit Filter

- [ ] 设计 `future_return`
- [ ] 设计 `future_drawdown`
- [ ] 设计 `bad_trade`
- [ ] 添加基础特征
- [ ] 在 `custom_exit()` 中调用 AI 结果
- [ ] 回测 AI 提前退出效果
- [ ] 做 shadow mode 分析

## P2：AI Stoploss

- [ ] 添加 `custom_stoploss()`
- [ ] AI 看坏时收紧止损
- [ ] 盈利后保护利润
- [ ] 对比最大回撤和卖飞率

## P3：AI Entry Filter

- [ ] 在 `confirm_trade_entry()` 中读取 AI 结果
- [ ] 原始强信号宽松通过
- [ ] 弱信号必须 AI 放行
- [ ] 统计 rejected entries
- [ ] 分析 AI 拒绝交易后续表现

## P4：AI 扩大交易数

- [ ] 新增 weak buy tag
- [ ] 小幅放宽 RSI / BB / EMA 条件
- [ ] 仅允许 AI 高分交易进入
- [ ] 单独统计 weak buy 表现
- [ ] 表现差立即删除 weak buy

---

# 19. 验收标准

## 19.1 AI Exit Filter 成功标准

```text
亏损单平均亏损下降 15%-30%
最大浮亏下降
平均持仓时间下降
最大回撤下降
Profit Factor 不明显下降
AI 卖飞率可接受
```

## 19.2 AI Entry Filter 成功标准

```text
AI 拒绝的交易整体表现差于 AI 放行交易
放行交易 Profit Factor 高于原始交易
最大回撤下降
总交易数不大幅下降
```

## 19.3 AI 扩大交易数成功标准

```text
交易数增加 10%-30%
Profit Factor 不低于原始 NFI
最大回撤不高于原始 NFI
新增 weak buy tag 单独盈利或至少不拖累
```

---

# 20. 失败处理方案

## 20.1 AI 退出太早

表现：

```text
很多单 AI 小亏退出后，随后快速反弹
```

处理：

```text
提高 bad_trade 阈值
延长确认 K 线数量
要求当前亏损达到更大幅度才允许 AI 退出
增加 BTC 市场状态确认
```

## 20.2 AI 过滤太严

表现：

```text
交易数大幅下降
错过大量盈利单
```

处理：

```text
强信号不做 AI 严格过滤
只过滤 weak 信号
降低 good_trade_score 阈值
缩短 label_period
```

## 20.3 AI 没有区分度

表现：

```text
高分交易和低分交易收益差不多
```

处理：

```text
减少重复技术指标
增加 BTC / 波动率 / 下跌速度特征
重新定义 target
检查数据泄露
检查训练周期是否过短
```

## 20.4 回测好，实盘差

表现：

```text
dry-run 或实盘明显低于回测
```

处理：

```text
降低模型复杂度
减少特征数量
增加 Walk-forward
关闭 AI 入场，只保留 AI 观察
检查手续费、滑点、交易对流动性
```

---

# 21. 最推荐的最终版本

对于你当前阶段，最推荐的版本是：

```text
NFI_AI_RiskFilter_V1
```

功能：

```text
NFI 原始买入
AI 不独立买入
AI 只做坏单提前退出
AI 动态收紧止损
BTC 大盘过滤
时间止损兜底
Protections 控制连续亏损
```

暂时不要做：

```text
AI 独立开单
AI 自动加仓
AI 高频交易
强化学习
大规模放宽买点
```

---

# 22. 推荐实施顺序总结

```text
第 1 步：原始 NFI 基准回测
第 2 步：NFI 非 AI 风控优化
第 3 步：FreqAI shadow mode，只记录不交易
第 4 步：启用 AI Exit Filter
第 5 步：启用 AI 动态止损
第 6 步：启用 AI 入场过滤
第 7 步：只对 weak buy 放宽交易数
第 8 步：Walk-forward + dry-run + 小资金实盘
```

---

# 23. 最终判断

NFI + AI 能不能解决你的问题？

结论：

```text
可以改善死扛和浮亏问题。
可以尝试在风险不增加的情况下增加交易数。
但 AI 不应该直接取代 NFI。
```

最现实、最稳的方案是：

```text
NFI 负责找机会
AI 负责判断机会质量
AI 负责识别坏单
风控负责保证活下来
```

如果 AI 加进去后不能降低回撤、不能缩短坏单持仓、不能区分好坏交易，那就不要为了“用了 AI”而保留 AI。

---

# 24. 参考资料

- FreqAI 官方说明：FreqAI 用于训练预测模型，根据输入信号生成市场预测  
  https://www.freqtrade.io/en/stable/freqai/

- FreqAI Feature Engineering：特征工程函数、`%` 特征前缀、`&` target 前缀  
  https://www.freqtrade.io/en/stable/freqai-feature-engineering/

- FreqAI Example Strategy：target 必须使用 `&` 前缀  
  https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/FreqaiExampleStrategy.py

- FreqAI Running：FreqAI 与 backtesting / hyperopt 的结合方式，建议重点优化 entry/exit 阈值  
  https://www.freqtrade.io/en/stable/freqai-running/

- Freqtrade Strategy Callbacks：`confirm_trade_entry()`、`custom_exit()`、`custom_stoploss()`、`custom_roi()` 等回调  
  https://www.freqtrade.io/en/stable/strategy-callbacks/

- Freqtrade Bot Basics：交易流程中 confirm entry、custom stoploss、custom exit 的调用位置  
  https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md

- Freqtrade Backtesting：回测流程和历史数据要求  
  https://www.freqtrade.io/en/stable/backtesting/

- Freqtrade Hyperopt：参数优化流程  
  https://www.freqtrade.io/en/stable/hyperopt/

- Freqtrade Protections / Plugins：`CooldownPeriod`、`StoplossGuard`、`MaxDrawdown`、`LowProfitPairs`  
  https://www.freqtrade.io/en/stable/plugins/
