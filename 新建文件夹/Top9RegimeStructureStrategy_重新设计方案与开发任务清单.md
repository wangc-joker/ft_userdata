# Top9RegimeStructureStrategy 重新设计方案与开发任务清单

## 1. 文档目标

本文档用于重新设计一个比当前 `Top9MainReversalZec216Strategy` 更适合长期实盘维护的策略框架。

当前已有策略回测非常漂亮：

```text
测试周期：2023-05-14 到 2026-05-07
初始资金：1000 USDT
最终资金：3036.95 USDT
总收益：+203.69%
最大账户回撤：11.98%
交易数：197
胜率：38.1%
Profit Factor：2.28
max_open_trades：2
交易对：BTC/ETH/BNB/SOL/TRX/ADA/ZEC/XRP/DOGE
```

但它存在以下风险：

```text
继承链过长
历史最优版本固化痕迹明显
ZEC / reversal 特化较强
部分币种和 entry_tag 可能贡献过于集中
custom_exit 对 reversal 单可能过度保护
多层 stake multiplier 难以追踪
```

因此本方案不以“回测收益超过 +203%”为唯一目标，而是追求：

```text
逻辑更清晰
继承链更短
样本外更稳
收益来源更分散
实盘滑点更可控
仓位管理更透明
后续维护更容易
```

---

## 2. 新策略定位

建议新策略命名：

```text
Top9RegimeStructureStrategy
```

策略类型：

```text
1h / 1d 多周期结构策略
趋势突破 + 趋势回调 + 反转突破
支持 long / short
低频到中频
适合 Binance USDT 合约或现货模拟验证
```

核心思想：

```text
1d 判断大环境
4h 可选确认中期趋势
1h 执行入场和退出
成交量、结构、波动率做过滤
仓位由信号质量、市场状态、币种权重、近期表现统一决定
```

---

## 3. 设计目标

### 3.1 回测目标

新策略不强行追求超过旧策略的 +203%，而是设置更稳健的目标：

```text
总收益：100% - 180%
最大回撤：8% - 15%
Profit Factor：> 1.6
交易次数：> 200
至少 3 个交易对正贡献
至少 3 个 entry_tag 正贡献
样本外 PF：> 1.3
```

### 3.2 实盘目标

```text
实盘收益达到回测收益的 50%-70%
最大实盘回撤 < 20%
不依赖单个币种
不依赖单个信号
滑点和手续费压力测试后仍为正收益
```

---

## 4. 总体架构

```text
Top9RegimeStructureStrategy
│
├── Indicators
│   ├── 1h structure indicators
│   ├── 1d regime indicators
│   ├── optional 4h trend confirmation
│   ├── volume expansion
│   ├── volatility state
│   └── recent performance state
│
├── Regime
│   ├── BULL_STRONG
│   ├── BULL_WEAK
│   ├── BEAR
│   └── RANGE
│
├── Entries
│   ├── long_trend_breakout
│   ├── long_pullback_restart
│   ├── long_reversal_breakout
│   ├── short_trend_breakdown
│   └── short_pullback_fail
│
├── Filters
│   ├── regime filter
│   ├── pair filter
│   ├── low volume filter
│   ├── recent loss filter
│   └── optional spread/slippage filter
│
├── Stake
│   ├── base stake
│   ├── signal multiplier
│   ├── regime multiplier
│   ├── pair multiplier
│   ├── recent performance multiplier
│   └── final multiplier clamp
│
├── Exits
│   ├── structure exit
│   ├── trend flip exit
│   ├── reversal protected exit
│   ├── stale time exit
│   └── profit protection
│
└── Protections
    ├── CooldownPeriod
    ├── StoplossGuard
    ├── MaxDrawdown
    ├── pair cooldown
    └── optional volume-tier cap
```

---

## 5. 周期设计

### 5.1 主周期

```text
timeframe = 1h
```

1h 用于：

```text
具体入场
具体退出
结构突破
趋势回调
反转确认
```

### 5.2 信息周期

```text
informative timeframe = 1d
```

1d 用于：

```text
牛熊判断
趋势方向
过滤逆势交易
确定 long/short 权重
```

### 5.3 可选辅助周期

```text
optional informative timeframe = 4h
```

4h 用于：

```text
中期趋势确认
减少 1h 假突破
过滤极端震荡
```

第一版可以先不加 4h，避免复杂化。

---

## 6. 交易对设计

第一版建议仍然使用 Top9：

```text
BTC/USDT:USDT
ETH/USDT:USDT
BNB/USDT:USDT
SOL/USDT:USDT
TRX/USDT:USDT
ADA/USDT:USDT
ZEC/USDT:USDT
XRP/USDT:USDT
DOGE/USDT:USDT
```

但不要强行特化某个币。

### 6.1 初始 pair 权重

| Pair | 初始权重 | 说明 |
|---|---:|---|
| BTC | 1.0 | 核心币，稳定性高 |
| ETH | 1.0 | 核心币 |
| SOL | 1.0 | 趋势性强 |
| BNB | 0.9 | 稳定但波动较小 |
| XRP | 0.8 | 可交易但噪音较多 |
| ADA | 0.75 | 偏弱，先降权 |
| DOGE | 0.6 | 波动噪音大，明显降权 |
| TRX | 0.7 | 波动较小，机会少 |
| ZEC | 0.8 | 历史表现好，但防止过拟合，不加高权重 |

原则：

```text
不因为某个币历史收益高就大幅加权。
如果该币真的有效，应该由信号质量和样本外验证证明。
```

---

## 7. 市场状态设计

### 7.1 BULL_STRONG

条件示例：

```text
close_1d > ema_fast_1d > ema_slow_1d
rsi_1d > 58
ema_slow_slope_up_1d = True
```

允许：

```text
long_trend_breakout
long_pullback_restart
少量 long_reversal_breakout
禁止大部分 short
```

权重：

```text
Long multiplier = 1.1
Short multiplier = 0.2
```

---

### 7.2 BULL_WEAK

条件示例：

```text
close_1d > ema_slow_1d
但 RSI / slope 不满足强牛
```

允许：

```text
long_pullback_restart
long_reversal_breakout
少量 short_trend_breakdown
```

权重：

```text
Long multiplier = 0.9
Short multiplier = 0.5
```

---

### 7.3 BEAR

条件示例：

```text
close_1d < ema_fast_1d < ema_slow_1d
rsi_1d < 45
ema_slow_slope_down_1d = True
```

允许：

```text
short_trend_breakdown
short_pullback_fail
少量 long_reversal_breakout，但条件必须更严格
```

权重：

```text
Long multiplier = 0.4
Short multiplier = 1.0
```

---

### 7.4 RANGE

非强牛，非弱牛，非熊市时归为震荡。

允许：

```text
少量突破交易
降低 stake
提高突破和成交量条件
```

权重：

```text
Long multiplier = 0.6
Short multiplier = 0.6
```

---

## 8. 入场信号设计

## 8.1 long_trend_breakout

定位：

```text
强趋势中的突破跟随。
```

适用环境：

```text
BULL_STRONG
BULL_WEAK
```

条件示例：

```text
1d close > ema_fast_1d > ema_slow_1d
1d RSI > 55
ema_slow_slope_up_1d = True
1h close > recent_high * (1 + breakout_buffer)
1h volume > volume_mean * volume_multiplier
1h range 曾经收缩
当前 K 线实体不能太小
```

entry_tag：

```text
long_trend_breakout
```

初始权重：

```text
1.0
```

---

## 8.2 long_pullback_restart

定位：

```text
上涨趋势中的回调再启动。
```

适用环境：

```text
BULL_STRONG
BULL_WEAK
RANGE 中少量允许
```

条件示例：

```text
1d 不是熊市
1h close > ema_slow
过去 N 根 K 线曾回踩 ema_fast 或 ema_slow
当前 close 重新站上 ema_fast
RSI 从低位回升
volume 不异常萎缩
```

entry_tag：

```text
long_pullback_restart
```

初始权重：

```text
0.9
```

---

## 8.3 long_reversal_breakout

定位：

```text
下跌后的反转突破。
```

适用环境：

```text
BULL_WEAK
RANGE
BEAR 中严格限制
```

条件示例：

```text
1d 不再创新低
1d close 重新接近或站上 ema_fast
1d RSI 在 35-55 区间回升
1h 出现底部平台
1h close 突破 72h 高点
volume 明显放大
突破 K 线上影线不能太长
```

entry_tag：

```text
long_reversal_breakout
```

初始权重：

```text
0.8
```

注意：

```text
不要只限制在 ZEC。
所有币统一逻辑，后续通过拆解验证是否某些币要移除或降权。
```

---

## 8.4 short_trend_breakdown

定位：

```text
熊市中的下跌趋势延续。
```

适用环境：

```text
BEAR
RANGE 中少量允许
```

条件示例：

```text
1d close < ema_fast_1d < ema_slow_1d
1d RSI < 45
ema_slow_slope_down_1d = True
1h close < recent_low * (1 - breakdown_buffer)
volume 放大
```

entry_tag：

```text
short_trend_breakdown
```

初始权重：

```text
0.8
```

---

## 8.5 short_pullback_fail

定位：

```text
熊市中反弹失败后继续做空。
```

适用环境：

```text
BEAR
```

条件示例：

```text
1d 熊市
1h 反弹到 ema_fast / ema_slow 附近失败
center_down
RSI 重新下行
close < ema_fast
```

entry_tag：

```text
short_pullback_fail
```

初始权重：

```text
0.6
```

---

## 9. 入场过滤设计

### 9.1 regime filter

禁止明显逆势交易：

```text
BULL_STRONG：禁止大部分 short
BEAR：禁止普通 long，只允许严格 reversal long
RANGE：降低所有信号权重
```

### 9.2 volume filter

```text
volume > volume_mean * 1.1
```

对 breakout 类信号提高要求：

```text
volume > volume_mean * 1.5
```

### 9.3 volatility filter

过滤极端波动：

```text
过去 24h range 过大时降低 stake 或禁止新开仓
ATR_pct 过高时降低 stake
```

### 9.4 recent loss filter

按 pair / tag 最近表现过滤：

```text
同 pair 最近 3 笔全亏 → 冷却 48h
同 entry_tag 最近 5 笔总收益 < 0 → stake * 0.6
同 entry_tag 最近 6 笔 PF < 1 → 暂停该 tag 一段时间
```

第一版可以只做 stake 降权，不直接暂停。

---

## 10. 仓位设计

### 10.1 统一 stake 公式

不要使用多层父类反复乘 multiplier。

建议：

```text
final_stake = base_stake
            * signal_multiplier
            * regime_multiplier
            * pair_multiplier
            * recent_performance_multiplier
```

然后统一限制：

```text
final_multiplier = clamp(final_multiplier, 0.4, 1.3)
```

避免出现隐式叠加：

```text
1.35 * 1.12 * 1.15 * 1.05 ...
```

### 10.2 base stake

建议：

```text
base_stake = proposed_stake
```

如果使用资金 cap：

```text
base_stake = min(proposed_stake, account / max_open_trades)
```

### 10.3 signal multiplier

| entry_tag | multiplier |
|---|---:|
| long_trend_breakout | 1.0 |
| long_pullback_restart | 0.9 |
| long_reversal_breakout | 0.8 |
| short_trend_breakdown | 0.8 |
| short_pullback_fail | 0.6 |

### 10.4 regime multiplier

| Regime | Long | Short |
|---|---:|---:|
| BULL_STRONG | 1.1 | 0.2 |
| BULL_WEAK | 0.9 | 0.5 |
| RANGE | 0.6 | 0.6 |
| BEAR | 0.4 | 1.0 |

### 10.5 pair multiplier

| Pair | multiplier |
|---|---:|
| BTC | 1.0 |
| ETH | 1.0 |
| SOL | 1.0 |
| BNB | 0.9 |
| XRP | 0.8 |
| ADA | 0.75 |
| DOGE | 0.6 |
| TRX | 0.7 |
| ZEC | 0.8 |

### 10.6 recent performance multiplier

```text
正常：1.0
同 tag 最近表现差：0.7
同 pair 最近表现差：0.8
两者都差：0.6
```

### 10.7 最终限制

```text
final_multiplier = max(0.4, min(final_multiplier, 1.3))
```

---

## 11. 退出设计

## 11.1 通用结构退出

Long 退出：

```text
1d downtrend
1h center_down 且 close < ema_fast
close < structure_stop_long
```

Short 退出：

```text
1d uptrend
1h center_up 且 close > ema_fast
close > structure_stop_short
```

---

## 11.2 reversal 专用退出

旧策略逻辑：

```python
if trade.enter_tag in reversal_tags and current_profit < 0.08:
    return None
```

新策略不采用这种写法。

建议：

```python
if tag in reversal_tags:
    if current_profit <= -0.01:
        allow_parent_exit = True

    if 0 < current_profit < 0.06 and structure_not_broken:
        hold

    if current_profit >= 0.06:
        enable_profit_protection
```

核心原则：

```text
只保护盈利且结构没坏的 reversal 单；
不保护亏损 reversal 单；
不为了追求大波段无限忽略结构破坏。
```

---

## 11.3 时间退出

| 条件 | 动作 |
|---|---|
| 持仓 > 72h 且收益 < 0 | 退出 |
| 持仓 > 120h 且收益 < 1% | 退出 |
| 持仓 > 240h 且收益 < 3% | 退出 |
| 趋势单盈利且结构未坏 | 不强行退出 |

---

## 11.4 盈利保护

建议：

```text
盈利 > 4%：启动保护
盈利 > 8%：更严格保护
盈利回撤超过 40%-50%：退出
```

示例：

```text
最高盈利 10%，回撤到 5%-6% 时退出
```

第一版可以先不做复杂 trailing，只用结构退出。

---

## 12. 止损设计

### 12.1 固定最大止损测试

测试三档：

```text
-2%
-3%
-4%
```

当前旧策略是 `-2%`，比较紧。新策略需要验证是否能承受实盘滑点。

### 12.2 结构止损

Long：

```text
stop_price = max(structure_stop_long, open_rate * 0.97)
```

Short：

```text
stop_price = min(structure_stop_short, open_rate * 1.03)
```

含义：

```text
结构止损优先，但最大亏损不要超过约 3%。
```

---

## 13. Protections 设计

保留：

```text
CooldownPeriod
StoplossGuard
MaxDrawdown
```

建议初始参数：

```text
CooldownPeriod：2-4 candles
StoplossGuard lookback：48-72 candles
StoplossGuard duration：12-18 candles
MaxDrawdown lookback：72-144 candles
MaxDrawdown duration：18-36 candles
Max allowed drawdown：8%-12%
```

需要测试：

```text
MaxDD 8%
MaxDD 10%
MaxDD 12%
```

---

## 14. 开发路线

## V1：干净主策略

只实现：

```text
long_trend_breakout
long_pullback_restart
short_trend_breakdown
short_pullback_fail
```

不加 reversal。

目标：

```text
验证基础结构策略是否本身有收益。
```

验收标准：

```text
PF > 1.2
最大回撤 < 20%
至少 150 笔交易
不依赖单一币种
```

---

## V2：加入 reversal，但不特化 ZEC

加入：

```text
long_reversal_breakout
short_reversal_breakdown
```

规则：

```text
所有币统一逻辑
不允许 ZEC 特殊加权
不允许 DOGE 等过度特化
```

目标：

```text
验证 reversal 是否泛化。
```

验收标准：

```text
整体 PF 提升
最大回撤不明显上升
reversal 收益不是只来自 ZEC
```

---

## V3：轻度 pair 权重

加入：

```text
DOGE 降权
ADA/XRP 轻度降权
ZEC 不加权，只观察
```

目标：

```text
减少噪音币种拖累。
```

验收标准：

```text
收益略升或回撤下降
交易次数不要大幅减少
收益来源仍然分散
```

---

## V4：资金 cap + 实盘版本

加入：

```text
成交量分级
单笔 stake cap
pair exposure cap
tag exposure cap
滑点/成交额限制
```

目标：

```text
进入 dry-run / 小资金实盘。
```

验收标准：

```text
实盘订单规模可控
低流动性币不会被大仓位交易
回测和实盘成交偏差缩小
```

---

## 15. 回测与验证流程

### 15.1 基础回测

每个版本都跑：

```text
2023-05-14 ~ 2026-05-07
```

输出：

```text
总收益
最大回撤
PF
胜率
交易数
long/short 收益
按 pair 收益
按 entry_tag 收益
```

### 15.2 年份拆解

```text
2023
2024
2025
2026
```

验收：

```text
至少 3 个年份为正
没有单一年份贡献超过 60%
```

### 15.3 样本外验证

```text
训练参考：2023-05 ~ 2025-05
样本外：2025-05 ~ 2026-05
```

样本外要求：

```text
PF > 1.3
收益为正
最大回撤 < 20%
```

### 15.4 Walk-forward

```text
W1：2023-05 ~ 2024-05
W2：2024-05 ~ 2025-05
W3：2025-05 ~ 2026-05
```

验收：

```text
至少 2/3 阶段收益为正
PF 不应长期低于 1
```

### 15.5 成本压力测试

测试：

```text
手续费 * 1.5
手续费 * 2
滑点 0.05%
滑点 0.10%
滑点 0.20%
```

验收：

```text
压力测试后仍为正收益
PF > 1.2
```

---

## 16. 与旧策略对比方式

不要只比较总收益。

需要比较：

```text
总收益
最大回撤
PF
样本外收益
样本外 PF
交易数
收益集中度
最大单币贡献占比
最大 entry_tag 贡献占比
滑点压力后收益
持仓时间
最大单笔亏损
```

### 16.1 旧策略强项

```text
历史回测收益高
reversal 模块强
ZEC 历史贡献可能大
```

### 16.2 新策略强项

```text
逻辑更清晰
维护更简单
收益更分散
更少历史特化
更适合实盘长期运行
```

---

## 17. 是否算“比旧策略更好”的标准

新策略不一定要总收益超过旧策略。

如果出现以下情况，可以认为新策略更适合实盘：

```text
旧策略：+203%，最大回撤 12%，但收益高度集中在 ZEC/reversal
新策略：+150%，最大回撤 8%，收益分散，样本外稳定
```

新策略优先级：

```text
稳定性 > 可维护性 > 样本外表现 > 回测总收益
```

---

## 18. 最终准入标准

进入小资金实盘前，必须满足：

```text
整体 PF > 1.5
样本外 PF > 1.3
最大回撤 < 15%-20%
交易次数 > 150
至少 3 个交易对正贡献
至少 3 个 entry_tag 正贡献
滑点/手续费压力测试后仍为正
没有单一币种贡献超过总利润 60%
没有单一 tag 贡献超过总利润 70%
```

进入较大资金前，必须满足：

```text
小资金实盘 1-2 个月
实盘和回测偏差可接受
最大实盘回撤 < 15%
订单滑点可控
无异常订单行为
```

---

## 19. 开发任务清单

### 任务 1：创建新策略骨架

```text
Top9RegimeStructureStrategy.py
```

实现：

```text
timeframe = 1h
can_short = True
informative 1d
allowed_pairs = Top9
protections
```

---

### 任务 2：实现指标模块

```text
ema_fast / ema_slow
rsi
atr_pct
market_center
center_up / center_down
recent_high / recent_low
range_width
volume_mean
structure_stop_long / short
1d 同名指标
```

---

### 任务 3：实现 regime 分类

```text
BULL_STRONG
BULL_WEAK
BEAR
RANGE
```

输出字段：

```text
regime
regime_long_multiplier
regime_short_multiplier
```

---

### 任务 4：实现 V1 入场信号

```text
long_trend_breakout
long_pullback_restart
short_trend_breakdown
short_pullback_fail
```

---

### 任务 5：实现 stake 系统

```text
signal_multiplier
regime_multiplier
pair_multiplier
recent_performance_multiplier
final_multiplier clamp 0.4~1.3
```

---

### 任务 6：实现退出系统

```text
structure exit
trend flip exit
time stale exit
basic profit protection
```

---

### 任务 7：回测 V1

输出：

```text
整体结果
年份拆解
pair 拆解
tag 拆解
```

---

### 任务 8：实现 V2 reversal

```text
long_reversal_breakout
short_reversal_breakdown
reversal 专用退出
```

---

### 任务 9：回测 V2 并对比 V1

重点看：

```text
reversal 是否提升 PF
是否增加回撤
是否过度依赖 ZEC
```

---

### 任务 10：实现 V3 轻度 pair 权重

```text
DOGE 降权
ADA/XRP 降权
ZEC 仅观察，不加权
```

---

### 任务 11：实现 V4 资金 cap

```text
成交量分级
单笔 cap
pair exposure cap
tag exposure cap
```

---

### 任务 12：最终压力测试和 dry-run

```text
手续费/滑点压力测试
max_open_trades 1/2/3
dry-run 2 周
小资金实盘 1-2 个月
```

---

## 20. 结论

这个重新设计方案不是为了制造一个“回测收益更夸张”的策略，而是为了得到一个：

```text
更干净
更稳健
更容易维护
更容易解释
更适合实盘扩展
```

的新策略。

如果新策略最终回测收益低于旧策略，但具备：

```text
更低回撤
更稳定样本外
更分散收益来源
更低实盘偏差
```

那么它在实际交易价值上可能比当前 `Top9MainReversalZec216Strategy` 更好。
