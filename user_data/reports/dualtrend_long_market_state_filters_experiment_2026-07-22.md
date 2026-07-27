# DualTrend 多头市场状态过滤实验（2026-07-22）

## 目的与口径

本轮不再扩宽多头形态，也不围绕 LongMicro 仅 7 笔交易调参数。目标是先用有独立逻辑依据的市场状态变量，对当前五年多头交易做入场前分层；只有被过滤组本身为负、且跨标签或年份方向合理，才进入策略实现和组合回测。

数据源为修正后的 Positive13/max3 五年 LongMicro 归档：

- `user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13_five_year-2026-07-20_05-54-29.zip`
- 有效多头 59 笔：日线 `long_1d_center_compression` 52 笔，Micro 7 笔
- 所有状态只使用开仓前已经完成的 K 线，未使用未来数据
- 所列利润是归档交易的离线归因，不等于共享资金、动态仓位和 max3 槽位下的组合回测

三条规则均在查看结果前固定，没有做阈值扫描。

## 1. PAIR/BTC 相对强度

固定规则仅作用于非 BTC 多头：

```text
EMA24(PAIR/BTC) > EMA72(PAIR/BTC)
且 EMA24 高于 6 小时前
```

BTC 自身原样放行。42 笔非 BTC 多头全部具备特征：

| 分组 | Trades | Profit | PF | 单笔均值 |
|---|---:|---:|---:|---:|
| 通过 | 32 | +497.36 USDT | 4.677 | +15.54 USDT |
| 拒绝 | 10 | +79.16 USDT | 2.735 | +7.92 USDT |

通过组质量较高，但拒绝组仍明显盈利。日线 tag 的拒绝组为 7 笔、`+63.88 USDT`、PF `4.896`，PF 还高于通过组的 `4.204`。Micro 的 3 笔拒绝交易合计 `+15.28 USDT`，其中包含一笔 `+44.51 USDT` 的 BNB ROI 赢家。

结论：相对强度适合作为描述变量，不适合作为当前多头硬过滤；不继续移动均线周期或斜率窗口。

## 2. Positive13 4H 市场广度

每个币沿用策略现有 4H 上升趋势定义：

```text
close > EMA50 > EMA200
且 EMA50 高于 3 根 4H K 线前
```

固定要求至少 13 个配置币中的 7 个同时上升：

| 分组 | Trades | Profit | PF | 单笔均值 |
|---|---:|---:|---:|---:|
| 通过 | 37 | +280.95 USDT | 2.628 | +7.59 USDT |
| 拒绝 | 22 | +426.29 USDT | 6.503 | +19.38 USDT |

结果方向与预期相反。日线 tag 在弱广度下的 17 笔交易为 `+412.81 USDT`、PF `10.084`；广度通过组只有 `+218.16 USDT`、PF `2.266`。这说明日线压缩突破常抓到的是市场全面扩散前的领先信号，等待多数币确认会明显滞后。

结论：淘汰“多数币 4H 同步转强后才做多”的过滤方向，不反向拟合成弱广度入场规则。

## 3. BTC 日线熊市保护

固定规则只在 BTC 明确处于日线熊市时禁止多头：

```text
BTC close < EMA50 < EMA200
且 EMA50 低于 3 天前
```

五年 59 笔中，53 笔具备完整 EMA200 历史；2021 年初段 6 笔因本地 BTC 日线历史不足而不可判定。规则仅拒绝 1 笔：2025-12-12 的 PAXG 日线多头，该单盈利 `+41.42 USDT`。7 笔 Micro 均未被过滤。

结论：样本覆盖过稀且唯一被拒绝交易为赢家，不实现该保护。

## 最终结论

- 三条预设规则都没有满足进入组合回测的前置门槛，因此没有新增实验策略类，也没有修改当前候选。
- 当前研究主候选继续是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`，稳定对照仍是 `DualTrendPyramidSecondAdd20V1Strategy`。
- 原日线多头不像典型追随大盘广度的信号，更接近稀疏的早期压缩突破；强行增加“全市场已经很强”的确认会丢掉高质量领先单。
- 下一轮不重复调相对强度均线、广度阈值或 BTC 日线均线周期。优先继续 dry-run 样本外观察，或研究不改变入场形态的独立资金槽位和机会成本控制。

## 保留证据

- `user_data/analysis/relative_strength_2026-07-22/analyze_relative_strength.py`
- `user_data/analysis/relative_strength_2026-07-22/diagnostic.md`
- `user_data/analysis/relative_strength_2026-07-22/trade_features.csv`
- `user_data/analysis/relative_strength_2026-07-22/analyze_market_breadth.py`
- `user_data/analysis/relative_strength_2026-07-22/market_breadth_diagnostic.md`
- `user_data/analysis/relative_strength_2026-07-22/market_breadth_trade_features.csv`
- `user_data/analysis/relative_strength_2026-07-22/analyze_btc_daily_bear_guard.py`
- `user_data/analysis/relative_strength_2026-07-22/btc_daily_bear_guard_diagnostic.md`
- `user_data/analysis/relative_strength_2026-07-22/btc_daily_bear_trade_features.csv`
