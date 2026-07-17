# DualTrend Positive13 策略实盘前验证与优化执行方案

> **历史状态：** 本文记录较早的 Raw 兼容版实盘前方案，不再定义当前研究主线。最新状态见 [`CURRENT_DUALTREND.md`](../CURRENT_DUALTREND.md)；当前研究主候选是 `DualTrendPyramidSecondAdd20V1Strategy`，而现有 dry-run 入口仍是本文所述旧分支。

## 0. 当前背景

当前主候选策略为：

```text
Strategy: DualTrendCombinedShortPullbackShapeV1Strategy
Pair Pool: Positive13
max_open_trades: 3
trading_mode: futures
margin_mode: isolated
dry_run_wallet: 1000
```

当前已有验证结论：

1. `Positive13 + Combined + max_open_trades=3` 是当前主候选。

2. 三年样本与近一年样本表现均较稳定。

3. 手续费压力测试到 `1.5x / 2.0x` 后，策略没有结构性崩塌。

4. `max_open_trades=4/5` 会增加交易数，但收益质量下降，回撤变差。

5. `Combined` 明显优于 `Short-only`，说明 long 模块不是拖累。

6. same-pair 近距离 long/short 反向互打问题暂未出现。

7. 当前不急着拆双 bot，也不急着做 side-specific slots。

8. 下一步目标不是继续盲目提高回测收益，而是验证策略在更接近实盘环境下是否仍然稳定。

---

# 1. 最终目标

本轮 Codex 的最终目标是：

```text
把 DualTrendCombinedShortPullbackShapeV1Strategy 的 Positive13 + max3 版本，
推进为一个可 dry-run 的稳定候选版本。
```

需要输出：

1. 完整回测验证报告。

2. 成本 + 滑点压力测试报告。

3. max4/max5 多出来交易的质量诊断报告。

4. 2026-03 到 2026-05 压力月份诊断报告。

5. long 模块贡献与 pair 分层报告。

6. 是否需要进一步优化的明确结论。

7. 如果需要优化，给出具体改动方案和对照回测结果。

8. 最终 dry-run 推荐配置。

---

# 2. 总体执行原则

## 2.1 不要一开始就改策略

先验证，再优化。

执行顺序必须是：

```text
复现基线
→ 压力测试
→ 问题定位
→ 小范围优化
→ 对照验证
→ 决定是否进入 dry-run
```

不要直接调参数，不要直接放宽入场条件，不要为了提高收益牺牲 PF 和回撤。

## 2.2 每次修改都必须有对照组

每一个优化版本都必须和当前基线对比：

```text
Baseline:
DualTrendCombinedShortPullbackShapeV1Strategy
Positive13
max_open_trades = 3
```

对照维度至少包含：

```text
Trades
Profit Abs
Profit %
Profit Factor
Max Drawdown
Winrate
Long / Short
Entry Tag 拆解
Pair 拆解
年度表现
最近 12 个月月度表现
压力期表现
```

## 2.3 不允许只看总收益

判断一个版本是否更好，优先级如下：

```text
1. MaxDD 是否可控
2. PF 是否稳定
3. 压力期是否改善
4. 成本和滑点压力下是否还能盈利
5. 是否减少低质量交易
6. 最后才看总收益是否提高
```

---

# 3. 当前基线复现

## 3.1 目标

先确认 Codex 当前环境可以复现已有结果。

## 3.2 需要检查的文件

请先检查项目中是否存在以下文件：

```text
user_data/strategies/DualTrendCombinedShortPullbackShapeV1Strategy.py
user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json
user_data/config.backtest.dualtrend.combined.top50.positive13.max4.json
user_data/config.backtest.dualtrend.combined.top50.positive13.max5.json
```

如果实际路径不同，请在项目内搜索：

```text
DualTrendCombinedShortPullbackShapeV1Strategy
positive13
max_open_trades
```

## 3.3 复现回测

需要至少复现两个区间：

```text
三年区间:
2023-06-18 -> 2026-06-18

近一年区间:
2025-06-18 -> 2026-06-18
```

如果项目已有 Docker 命令，请复用现有命令。

如果没有，请先在项目中查找 README、scripts、Makefile、bat、sh 文件，确认当前回测命令格式。

不要臆造路径。先扫描项目结构，再执行。

## 3.4 输出报告

生成：

```text
user_data/reports/positive13_baseline_recheck.md
```

报告内容包括：

```text
1. 使用的策略文件
2. 使用的 config 文件
3. 使用的 pairlist
4. 回测区间
5. 三年结果
6. 近一年结果
7. entry_tag 拆解
8. pair 拆解
9. 年度表现
10. 月度表现
11. 是否与历史基线基本一致
```

## 3.5 通过标准

如果复现结果和历史结果差异很小，则进入下一阶段。

允许误差：

```text
Profit 差异 <= 3%
PF 差异 <= 0.05
MaxDD 差异 <= 1%
Trades 差异 <= 5 笔
```

如果差异超过以上范围，先不要优化，先排查：

```text
1. 数据是否一致
2. timerange 是否一致
3. pairlist 是否一致
4. fee 是否一致
5. startup_candle_count 是否一致
6. config 是否被修改
7. strategy 是否不是同一个版本
```

---

# 4. 阶段一：成本 + 滑点压力测试

## 4.1 目标

当前已经测过手续费 `1.5x / 2.0x`，但还没有叠加滑点。

本阶段目标是确认：

```text
策略不是只在理想成交条件下成立。
```

## 4.2 测试版本

基于 baseline config，创建以下压力测试配置：

```text
A. baseline
B. fee 2.0x
C. fee 2.0x + light slippage
D. fee 2.0x + medium slippage
E. fee 2.0x + heavy slippage
F. fee 2.0x + 延迟一根 K 线入场模拟
```

如果 Freqtrade 原生不方便模拟滑点，则实现一个分析脚本，在回测 trade 结果基础上二次扣减：

```text
long:
entry_price 上调 slippage
exit_price 下调 slippage

short:
entry_price 下调 slippage
exit_price 上调 slippage
```

建议滑点档位：

```text
light: 0.03%
medium: 0.05%
heavy: 0.10%
```

如果策略本身多为 1H 级别交易，这三个档位基本可以覆盖普通实盘成交压力。

## 4.3 输出文件

生成：

```text
user_data/reports/positive13_fee_slippage_stress.md
user_data/analysis/positive13_fee_slippage_stress.csv
```

## 4.4 报告表格

报告至少包含：

```text
方案 | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Worst Month | Worst Pair
```

分别输出：

```text
三年样本
近一年样本
2026-03-01 -> 2026-05-31 压力期
```

## 4.5 判断标准

### 通过

如果满足：

```text
三年 fee2x + medium slippage PF >= 1.60
三年 fee2x + medium slippage MaxDD <= 12%
近一年 fee2x + medium slippage PF >= 1.50
近一年 fee2x + medium slippage Profit > 0
```

则说明可以继续推进 dry-run。

### 警戒

如果：

```text
PF 下降到 1.30 - 1.50
或者 MaxDD 上升到 12% - 15%
```

不要直接放弃，进入问题定位：

```text
1. 看亏损是否集中在某些 pair
2. 看亏损是否集中在 long
3. 看亏损是否集中在某个 entry_tag
4. 看亏损是否集中在高波动时期
```

### 不通过

如果：

```text
fee2x + medium slippage 后近一年亏损
或者三年 PF < 1.30
或者 MaxDD > 15%
```

则暂缓 dry-run，必须先优化成交敏感性。

可尝试优化方向：

```text
1. 减少追价入场
2. 增加入场确认
3. 避免大波动 K 线后立刻入场
4. 避免 ATR 异常放大时入场
5. 对流动性较差的 pair 降权或禁用
```

---

# 5. 阶段二：max4 / max5 多出来交易诊断

## 5.1 背景

已有结果显示：

```text
max4 / max5 增加交易数，但没有明显增加收益。
PF 下降，MaxDD 上升。
```

这说明多出来的交易大概率是次级信号。

本阶段目标不是改成 max4/max5，而是找出：

```text
max4/max5 多出来的低质量交易有什么共同特征。
```

## 5.2 执行方式

分别跑：

```text
max3
max4
max5
```

区间：

```text
2023-06-18 -> 2026-06-18
2025-06-18 -> 2026-06-18
```

从回测结果中导出所有交易，按以下字段建立 trade 表：

```text
pair
open_date
close_date
side
entry_tag
profit_abs
profit_ratio
duration
open_rate
close_rate
max_open_trades_config
```

然后找出：

```text
max4 相对 max3 多出来的交易
max5 相对 max3 多出来的交易
```

匹配方法：

```text
使用 pair + open_date + side + entry_tag 作为近似唯一键。
如果 open_date 有轻微偏差，允许 1 根 K 线误差。
```

## 5.3 输出报告

生成：

```text
user_data/reports/positive13_extra_slots_diagnosis.md
user_data/analysis/positive13_extra_trades_max4_vs_max3.csv
user_data/analysis/positive13_extra_trades_max5_vs_max3.csv
```

## 5.4 诊断维度

对多出来的交易做统计：

```text
1. 按 pair 统计
2. 按 side 统计
3. 按 entry_tag 统计
4. 按月份统计
5. 按持仓时长统计
6. 按盈利/亏损统计
7. 按入场时总持仓数量统计
8. 按 BTC 当时 4H 趋势环境统计
9. 按 ATR/波动率分位统计
```

## 5.5 判断和优化

### 情况 A：多出来的亏损集中在某几个 pair

处理方式：

```text
这些 pair 不一定要从 Positive13 删除。
先考虑加 pair-level risk flag。
例如:
- 某些 pair 只允许 short
- 某些 pair 降低 stake
- 某些 pair 禁止在高波动环境入场
```

### 情况 B：多出来的亏损集中在 long

处理方式：

```text
不要删除整个 long 模块。
先做 long-specific filter。
候选过滤:
1. long 只允许 BTC 4H 不弱时触发
2. long 只允许 4H EMA50 向上时触发
3. long 要求突破后下一根 K 线不跌回压缩区
4. long 要求 close position 更强
5. long 只允许部分核心 pair
```

### 情况 C：多出来的亏损集中在 short_compression_breakdown

处理方式：

```text
考虑增加假跌破过滤:
1. breakdown K 线实体比例要求
2. close 必须接近低位
3. 跌破后不能快速收回
4. BTC 或大盘不能处于强反弹环境
5. 避免超跌末端继续追空
```

### 情况 D：多出来的亏损集中在高波动行情

处理方式：

```text
增加 volatility guard:
1. ATR 分位过高时暂停新单
2. 单根 K 线涨跌幅过大后等待 N 根
3. BTC 1H 极端波动时禁止新开仓
4. 资金费率极端时禁止反向拥挤交易
```

### 情况 E：没有明显共同特征

处理方式：

```text
保持 max3，不做额外优化。
不要为了消灭少数随机亏损而过拟合。
```

---

# 6. 阶段三：2026-03 到 2026-05 压力月份诊断

## 6.1 目标

之前回测中，2026-03 到 2026-05 是连续压力期。

本阶段目标：

```text
确认压力期亏损是正常策略回撤，还是存在可过滤的行情类型。
```

## 6.2 分析区间

```text
2026-03-01 -> 2026-05-31
```

同时对照：

```text
2026-01-01 -> 2026-02-28
2026-06-01 -> 2026-06-18
```

这样可以比较：

```text
赚钱阶段 vs 亏损阶段
```

## 6.3 输出文件

生成：

```text
user_data/reports/positive13_pressure_months_diagnosis.md
user_data/analysis/positive13_trades_202603_202605.csv
```

## 6.4 必须统计的内容

```text
1. 压力期总交易数
2. 压力期总收益
3. 压力期 PF
4. 压力期 MaxDD
5. long / short 分别表现
6. entry_tag 分别表现
7. pair 分别表现
8. 每笔亏损单的 MAE / MFE
9. 入场后 N 根 K 线内是否快速反向
10. 是否集中发生在 BTC 震荡期
11. 是否集中发生在 ATR 高分位
12. 是否集中发生在趋势末端
13. 是否集中发生在假突破/假跌破
```

## 6.5 单笔亏损分类

请给每笔亏损单打标签：

```text
false_breakout
false_breakdown
late_trend_chase
range_market
btc_regime_conflict
atr_spike
stop_too_tight
normal_loss
unknown
```

分类规则：

### false_breakout

```text
long 入场后 1-5 根 1H K 线内跌回突破区间
```

### false_breakdown

```text
short 入场后 1-5 根 1H K 线内重新收回跌破区间
```

### late_trend_chase

```text
入场前已经连续上涨/下跌较大幅度，ATR 或乖离明显偏高
```

### range_market

```text
4H 或 1D 趋势不明显，价格在区间内反复穿越均线
```

### btc_regime_conflict

```text
个币信号方向和 BTC 4H / 1D 大方向明显冲突
```

### atr_spike

```text
入场前后 ATR 分位明显高于过去 N 天常态
```

### stop_too_tight

```text
入场后先打止损，再很快走向原本预期方向
```

### normal_loss

```text
符合策略逻辑，亏损没有明显异常
```

## 6.6 根据结果优化

### 如果亏损主要是 false_breakout

优化 long：

```text
1. long 突破后等待下一根 1H 确认
2. 要求 close 不跌回压缩区
3. 提高 close position 阈值
4. 增加 4H EMA50 slope > 0
5. 增加 BTC 4H 非弱势过滤
```

### 如果亏损主要是 false_breakdown

优化 short：

```text
1. short breakdown 要求收盘位置更低
2. breakdown K 线实体占比更高
3. 跌破后不能快速收回
4. 过滤超跌末端追空
5. BTC 4H 强反弹时禁止新 short
```

### 如果亏损主要是 range_market

增加市场状态过滤：

```text
1. ADX 过滤
2. 4H EMA 斜率过滤
3. 1D 趋势方向过滤
4. 布林带宽度/ATR 过滤
5. 震荡市场只允许更强信号
```

### 如果亏损主要是 atr_spike

增加波动保护：

```text
1. ATR 分位过高时暂停新开仓
2. 单根 1H K 线涨跌幅超过阈值后等待 2-4 根
3. 插针 K 线后不立即追单
4. 止损距离根据 ATR 动态调整
```

### 如果亏损主要是 normal_loss

不要优化。

说明这是正常策略回撤，强行优化容易过拟合。

---

# 7. 阶段四：long 模块深度诊断

## 7.1 背景

已有对照显示：

```text
Combined 明显优于 Short-only。
```

因此现在不应该砍掉 long。

但是需要进一步判断：

```text
long 是所有 Positive13 都适合，
还是只适合其中一部分 pair。
```

## 7.2 输出文件

生成：

```text
user_data/reports/positive13_long_module_diagnosis.md
user_data/analysis/positive13_long_trades.csv
```

## 7.3 分析维度

只提取 long 交易，统计：

```text
1. long 总体表现
2. long 按 pair 表现
3. long 按年份表现
4. long 按月份表现
5. long 按持仓时间表现
6. long 按 MAE / MFE 表现
7. long 按 BTC 4H 环境表现
8. long 按 4H EMA50 slope 表现
9. long 按 1D 趋势环境表现
10. long 按 ATR 分位表现
```

## 7.4 判断标准

### 情况 A：long 只集中在少数 pair 盈利

如果发现：

```text
少数 pair 贡献大部分 long 利润
其他 pair 的 long 交易 PF < 1
```

则实现：

```text
long_pair_allowlist
```

示例：

```python
LONG_ALLOWED_PAIRS = {
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "BNB/USDT:USDT",
}
```

注意：

```text
具体名单必须根据实际统计结果生成，不要提前写死。
```

然后回测：

```text
版本 L1:
short 仍允许 Positive13 全部 pair
long 只允许 long_pair_allowlist
```

对比 baseline：

```text
如果 L1 的 PF 提高、MaxDD 降低、收益不明显下降，则保留。
如果 L1 收益下降明显且 PF 没有提高，则放弃。
```

### 情况 B：long 在多数 pair 都为正

保持当前 long，不改。

### 情况 C：long 只在 BTC 强势环境赚钱

增加 BTC regime filter：

```text
long 只有在 BTC 4H 不弱或 1D 不弱时允许。
```

候选条件：

```text
BTC close > BTC EMA50 on 4H
BTC EMA50 slope > 0
BTC 4H market regime != downtrend
```

### 情况 D：long 只在 4H 趋势向上时赚钱

增加 4H EMA slope filter：

```text
long 只有在当前 pair 的 4H EMA50 slope > 0 时允许。
```

### 情况 E：long 假突破较多

增加确认：

```text
long_signal_raw 出现后不立即进场
下一根 1H close 仍在突破区上方才入场
```

---

# 8. 阶段五：entry_tag 级别优化

## 8.1 目标

当前策略主要有三个 entry_tag：

```text
short_pullback_restart
short_compression_breakdown
long_1d_center_compression
```

需要分别诊断它们是否都值得保留，以及是否需要独立过滤。

## 8.2 输出文件

```text
user_data/reports/positive13_entry_tag_diagnosis.md
```

## 8.3 每个 tag 必须统计

```text
1. Trades
2. Profit Abs
3. Profit %
4. PF
5. MaxDD contribution
6. Winrate
7. Avg Profit
8. Avg Duration
9. Best Pair
10. Worst Pair
11. Best Year
12. Worst Year
13. Worst Month
14. fee2x + slippage 后表现
```

## 8.4 判断和优化

### short_pullback_restart

这是主引擎。

只有在发现明显问题时才优化。

可优化方向：

```text
1. 避免趋势末端追空
2. 加强 pullback 后重新转弱确认
3. 避免 BTC 强反弹环境做空
4. 根据 ATR 动态调整止损
```

### short_compression_breakdown

这是副引擎。

重点检查假跌破。

可优化方向：

```text
1. breakdown 收盘位置要求
2. breakdown 实体比例要求
3. 跌破前压缩时间要求
4. 跌破后不快速收回
5. 避免低流动性小币假跌破
```

### long_1d_center_compression

这是组合增益模块。

重点检查假突破和 pair 分层。

可优化方向：

```text
1. long pair allowlist
2. BTC 4H regime filter
3. pair 4H EMA50 slope filter
4. 突破后下一根确认
5. 提高 close position 阈值
```

---

# 9. 阶段六：动态币池验证

## 9.1 背景

Positive13 是从当前 top50 正贡献中收敛出来的，存在一定结果筛选成分。

需要验证：

```text
如果未来市场结构变化，固定 Positive13 是否仍然合理。
```

## 9.2 两种验证方式

### 方式 A：固定 Positive13 定期复查

这是简单实用版本。

规则：

```text
每 30 天重新生成当前 Binance USDT-M quoteVolume top50
检查 Positive13 是否仍然在 top50 或 top80 内
如果某个 pair 连续 60 天跌出 top80，则进入观察名单
如果某个 pair 流动性下降明显，则暂停交易
```

### 方式 B：历史动态 topN 回测

这是更严格版本。

规则：

```text
每月月初按当时 Binance USDT-M quoteVolume 生成 top50
用当月 top50 作为观察池
运行策略
汇总三年表现
```

如果无法获取历史 quoteVolume 快照，则使用可获得的数据近似，但必须在报告中注明限制。

## 9.3 输出文件

```text
user_data/reports/positive13_dynamic_universe_validation.md
```

## 9.4 判断标准

### 如果动态 top50 表现稳定

说明策略有更强泛化能力。

可以考虑：

```text
top50 观察池
Positive-like 自动筛选机制
定期更新交易池
```

### 如果动态 top50 表现明显变差

说明当前 Positive13 更像固定核心币池。

处理方式：

```text
1. dry-run 阶段继续使用固定 Positive13
2. 每月只做流动性检查
3. 不自动大幅换币
4. 新币必须经过回测和观察期后再加入
```

---

# 10. 阶段七：实盘 dry-run 规则

## 10.1 dry-run 前置条件

只有满足以下条件才建议进入 dry-run：

```text
1. baseline 复现通过
2. fee2x + medium slippage 后三年 PF >= 1.60
3. fee2x + medium slippage 后近一年 PF >= 1.50
4. MaxDD 压力后 <= 12%
5. 2026-03 到 2026-05 压力期没有发现致命结构问题
6. long 模块不是明显拖累
7. max3 仍然优于 max4/max5
8. same-pair 72h 内没有明显反向互打
```

## 10.2 dry-run 配置建议

```text
Pair Pool: Positive13
Strategy: DualTrendCombinedShortPullbackShapeV1Strategy
max_open_trades: 3
mode: futures
margin: isolated
leverage: 低杠杆
stake: 小资金模拟
```

## 10.3 dry-run 观察指标

每天记录：

```text
1. 当前持仓数
2. long 持仓数
3. short 持仓数
4. 是否满槽
5. 是否有 missed signal
6. 是否 long 占住 short 槽位
7. 实际成交价与信号价偏差
8. 手续费
9. 滑点
10. 资金费率
11. 单笔 MAE / MFE
12. 实际退出是否符合回测逻辑
```

每周输出：

```text
user_data/reports/dry_run_weekly_report_YYYYMMDD.md
```

## 10.4 dry-run 暂停条件

如果出现以下情况，暂停新开仓，只保留已有仓位按策略退出：

```text
1. dry-run 连续亏损明显超过回测同类阶段
2. 实际滑点明显高于 heavy slippage 假设
3. API 或交易所异常
4. 单日亏损超过预设阈值
5. 出现 same-pair 快速反向互打
6. long 明显占槽导致 short 频繁错过
7. 某个 pair 连续异常亏损
```

---

# 11. 优化版本命名规范

每个优化版本必须独立命名。

不要直接覆盖主策略。

示例：

```text
DualTrendCombinedShortPullbackShapeV1Strategy
DualTrendCombinedShortPullbackShapeV1LongFilterStrategy
DualTrendCombinedShortPullbackShapeV1VolGuardStrategy
DualTrendCombinedShortPullbackShapeV1PairLongAllowStrategy
DualTrendCombinedShortPullbackShapeV1RegimeFilterStrategy
```

配置文件命名：

```text
config.backtest.dualtrend.combined.positive13.max3.baseline.json
config.backtest.dualtrend.combined.positive13.max3.fee2x.json
config.backtest.dualtrend.combined.positive13.max3.slippage_medium.json
config.backtest.dualtrend.combined.positive13.max3.longfilter.json
config.backtest.dualtrend.combined.positive13.max3.volguard.json
```

报告命名：

```text
positive13_baseline_recheck.md
positive13_fee_slippage_stress.md
positive13_extra_slots_diagnosis.md
positive13_pressure_months_diagnosis.md
positive13_long_module_diagnosis.md
positive13_entry_tag_diagnosis.md
positive13_dynamic_universe_validation.md
positive13_final_dryrun_recommendation.md
```

---

# 12. 最终报告格式

最后必须生成：

```text
user_data/reports/positive13_final_dryrun_recommendation.md
```

内容必须包含：

## 12.1 当前最佳版本

```text
策略名
配置文件
pairlist 文件
max_open_trades
是否启用 long
是否启用 short
是否需要 side-specific slots
是否需要双 bot
```

## 12.2 核心结果表

```text
版本 | 区间 | Trades | Profit | PF | MaxDD | Winrate | Long/Short
```

至少包含：

```text
baseline 三年
baseline 近一年
fee2x 三年
fee2x 近一年
fee2x + medium slippage 三年
fee2x + medium slippage 近一年
最佳优化版本三年
最佳优化版本近一年
```

## 12.3 结论

必须明确回答：

```text
1. 是否建议进入 dry-run？
2. 如果建议，使用哪个 config？
3. 如果不建议，阻塞问题是什么？
4. 下一步优先优化哪个模块？
5. 是否保留 long？
6. 是否保留 max3？
7. 是否需要拆双 bot？
8. 是否需要动态币池？
```

---

# 13. 当前默认判断

在没有新证据之前，默认判断如下：

```text
1. 保留 Positive13
2. 保留 Combined
3. 保留 max_open_trades=3
4. 保留 long
5. 不升 max4/max5
6. 不拆双 bot
7. 不做 side-specific slots
8. 先做 fee2x + slippage 压力测试
9. 再做压力月份和 long 模块诊断
10. 最后进入 dry-run
```

---

# 14. Codex 执行清单

请按顺序执行：

```text
[ ] 1. 扫描项目结构，确认策略、config、pairlist、数据路径
[ ] 2. 复现 Positive13 + Combined + max3 三年回测
[ ] 3. 复现 Positive13 + Combined + max3 近一年回测
[ ] 4. 输出 baseline_recheck 报告
[ ] 5. 实现或复用 trade 结果解析脚本
[ ] 6. 实现 fee + slippage 压力测试脚本
[ ] 7. 输出 fee_slippage_stress 报告
[ ] 8. 回测 max3/max4/max5 并导出 trade 明细
[ ] 9. 分析 max4/max5 多出来的交易
[ ] 10. 输出 extra_slots_diagnosis 报告
[ ] 11. 导出 2026-03 到 2026-05 压力期交易
[ ] 12. 给亏损单分类
[ ] 13. 输出 pressure_months_diagnosis 报告
[ ] 14. 提取 long 交易做 pair、年份、月份、环境拆解
[ ] 15. 输出 long_module_diagnosis 报告
[ ] 16. 拆解三个 entry_tag 的质量
[ ] 17. 输出 entry_tag_diagnosis 报告
[ ] 18. 如有必要，实现最小优化版本
[ ] 19. 每个优化版本跑三年和近一年对照
[ ] 20. 生成 final_dryrun_recommendation 报告
```

---

# 15. 注意事项

1. 不要用未来收益决定历史交易池，动态币池验证必须明确避免未来函数。

2. 不要因为某个 pair 只有 1-3 笔亏损就永久删除。

3. 不要为了提高收益放宽入场条件。

4. 不要只优化 2026-03 到 2026-05，避免过拟合压力期。

5. 不要只看三年总收益，必须同时看近一年。

6. 不要覆盖原始策略，所有优化都用新策略类。

7. 不要只输出回测结果，要输出结论和下一步建议。

8. 如果优化版本收益更高但 PF 更低、MaxDD 更高，默认不接受。

9. 如果优化版本交易更少但 PF 更高、MaxDD 更低，可以接受。

10. 最终目标是稳定 dry-run，不是最大化历史收益。
