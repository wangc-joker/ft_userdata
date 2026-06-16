# DualTrend Long V1 做多入场形态图解

生成时间：2026-06-15

对应策略：

- `D:\test\ft_userdata\user_data\strategies\DualTrendCompressionRestartLongV1Strategy.py`

对应配置：

- `D:\test\ft_userdata\user_data\config.backtest.dualtrend.long_v1.1000u.max3.3y.json`

图表目录：

- `D:\test\ft_userdata\user_data\strategies\research\long_v1_entry_visuals`

## 1. 核心形态

Long V1 等待的不是普通追涨，而是：

1. 大周期同向：交易币本身 4h 趋势向上，BTC 4h 趋势也向上。
2. 1h 出现压缩：最近 12 根 1h K 线区间变窄，价格没有乱冲。
3. 压缩前有回踩：价格从 24h 前高附近回落，但回踩低点不能破坏 4h EMA50 附近结构。
4. 重启阳线：当前 K 线突破压缩区间上沿，并且收盘靠近 K 线高位。
5. 风险可控：止损距离不能太近，也不能太远；ATR 和 24h 涨幅不能过热。

一句话：顺大势，等回踩，等窄幅整理后重新向上启动。

## 2. 入场逻辑图

![Long V1 入场逻辑](D:/test/ft_userdata/user_data/strategies/research/long_v1_entry_visuals/long_v1_entry_logic_diagram.svg)

## 3. 点位判断

图里的关键点位：

- 黑线/黑三角：实际入场点。
- 红虚线：初始结构止损，来自 `pullback_low_12 - 0.2 * ATR`，再受最大止损距离限制。
- 绿虚线：固定 ROI 目标，当前 Long V1 为 +5%。
- 紫线：过去 12 根 1h 的压缩区间高低点。
- 橙线：过去 24h 前高，用来判断是否经历过上涨后的回踩。
- 青线：过去 12h 回踩低点，止损锚点主要来自这里。
- 下方小图：4h 趋势结构，入场时要求价格处于 4h EMA50/EMA200 上方环境。

## 4. 过滤条件

正式 Long V1 当前过滤：

| 条件 | 当前值 | 含义 |
|---|---:|---|
| 交易币种 | BNB/XRP/DOGE/ZEC | 剔除做多拖累币 |
| entry_tag | long_pullback_restart | 只保留回踩再启动 |
| BTC 过滤 | BTC 4h 向上 | 避免逆市场做多 |
| ROI | 5% | 不贪长趋势，先吃一段启动 |
| close_position | >= 0.72 | 当前 K 线收盘靠近高位 |
| ATR% | <= 5% | 避免过度波动 |
| 24h return | -2% 到 +12% | 避免太弱或太过热 |
| pullback_depth | <= 5% | 回踩不能太深 |
| close vs 4h EMA50 | close > EMA50_4h | 结构不能跌回弱势区 |

## 5. 真实样例图

### BNB

![BNB Long V1 入场](D:/test/ft_userdata/user_data/strategies/research/long_v1_entry_visuals/long_v1_entry_1_bnb_20251005_0300.svg)

BNB 是 Long V1 全样本中最主要贡献币。典型形态是 4h 趋势保持向上，1h 回踩后横住，再用强势阳线突破压缩高点。

### DOGE

![DOGE Long V1 入场](D:/test/ft_userdata/user_data/strategies/research/long_v1_entry_visuals/long_v1_entry_2_doge_20251005_0300.svg)

DOGE 交易次数少，但严格过滤后胜率较高。需要注意 DOGE 波动更大，因此 ATR 和 24h 涨幅过滤很关键。

### XRP

![XRP Long V1 入场](D:/test/ft_userdata/user_data/strategies/research/long_v1_entry_visuals/long_v1_entry_3_xrp_20260505_1300.svg)

XRP 全样本贡献接近持平，近期有贡献。它适合继续观察，但不是 Long V1 的主要利润来源。

### ZEC

![ZEC Long V1 入场](D:/test/ft_userdata/user_data/strategies/research/long_v1_entry_visuals/long_v1_entry_4_zec_20260502_2100.svg)

ZEC 的样例更像“压缩后快速启动”，但交易次数也少，适合作为辅助品种，不适合作为主引擎。

## 6. 不适合入场的形态

下面几种形态 Long V1 会尽量过滤：

- 4h 趋势还没站上去，只是 1h 反弹。
- BTC 4h 不同向，市场整体不配合。
- 24h 已经过热，继续追容易吃回落。
- 回踩太深，说明结构可能已经坏掉。
- 突破 K 线收盘不强，冲高回落明显。
- 止损距离过大，盈亏比变差。

## 7. 当前判断

Long V1 的做多模型已经不是“看到突破就追”，而是偏保守的顺势回踩重启。

但它仍然弱于 Short V2，原因是：

- 多头样本更依赖大盘环境。
- 有效信号数量少。
- 主要利润集中在 BNB，其他币更像辅助分散。

所以 Long V1 更适合作为观察版或轻仓 dry-run，不建议现在直接提高权重。

