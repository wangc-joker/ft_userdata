# DualTrend 20 币池 / max_open_trades=6 回测记录

> **后续状态（2026-07-20）：** 本文正文只记录 SecondAdd20 阶段。7 月 17 日 LongMicro 的 `+200.99%` 和 `+253.85%` 受参数名碰撞影响，已经失效；参数隔离后的 Top20/max6 三年与五年结果为 `+190.23%` 和 `+243.23%`。最新结论见 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md) 与 `dualtrend_long_micro_parameter_collision_audit_2026-07-20.md`。

日期：2026-07-15

## 测试目标

固定策略 `DualTrendPyramidSecondAdd20V1Strategy`，只扩大币池并提高最大同时开仓数：

- 币池：20 个固定合约交易对
- `max_open_trades = 6`
- 主周期：1h
- 细节周期：5m
- 不修改入场、止损、止盈、加仓逻辑

## 配置

配置文件：

`user_data/config.backtest.dualtrend.combined.top20.max6.pyramid20.json`

币池：

BTC、ETH、SOL、ZEC、DOGE、XRP、HYPE、BNB、SUI、ADA、AVAX、FIL、AAVE、LINK、APE、NEAR、DOT、ONDO、WLD、DASH。

本地数据检查结果：以上 20 个交易对的 `5m`、`1h`、`4h`、`1d` 数据均存在，无需同步。

## 回测结果

计划窗口：

- 三年：2023-06-18 -> 2026-06-18
- 近一年：2025-06-18 -> 2026-06-18
- 压力期：2026-03-01 -> 2026-05-31

Docker 恢复后已完成三组回测：

| 样本 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| 三年 | 339 | +180.62% | 2.445 | 5.29% | 53.10% |
| 近一年 | 135 | +53.55% | 2.751 | 3.07% | 58.52% |
| 压力期 | 18 | +5.43% | 3.454 | 1.50% | 55.56% |

三年按 entry_tag：

| Entry tag | Trades | Profit | PF | Winrate |
|---|---:|---:|---:|---:|
| `short_pullback_restart` | 224 | +112.06% | 2.366 | 58.5% |
| `long_1d_center_compression` | 48 | +42.30% | 3.553 | 29.2% |
| `short_compression_breakdown` | 67 | +26.26% | 1.994 | 52.2% |

## 与原 Positive13 / max3 对比

原配置下的 `DualTrendPyramidSecondAdd20V1Strategy`：

| 样本 | Positive13/max3 Profit | Positive13/max3 PF | Positive13/max3 MaxDD | Top20/max6 Profit | Top20/max6 PF | Top20/max6 MaxDD |
|---|---:|---:|---:|---:|---:|---:|
| 三年 | +199.22% | 2.682 | 4.82% | +180.62% | 2.445 | 5.29% |
| 近一年 | +68.02% | 3.395 | 4.75% | +53.55% | 2.751 | 3.07% |
| 压力期 | +5.11% | 3.077 | 1.75% | +5.43% | 3.454 | 1.50% |

注意：`max_open_trades=6` 会改变资金占用和交易竞争，不能把收益率简单理解为币池扩大后的纯信号质量变化。这里的结果说明扩池版本在压力期略好、回撤略低，但三年和近一年收益及 PF 均弱于原 Positive13/max3。

## Pair 拆解

三年主要贡献：

- XRP：`+39.13%`，45 笔，PF `3.50`
- BNB：`+31.08%`，29 笔，PF `5.14`
- ETH：`+30.25%`，31 笔，PF `4.30`
- BTC：`+21.82%`，37 笔，PF `2.57`
- DOGE：`+20.58%`，26 笔，PF `4.03`
- ADA：`+16.23%`，34 笔，PF `2.43`
- ZEC：`+14.71%`，15 笔，PF `11.70`

三年主要拖累：

- AAVE：`-1.34%`，1 笔
- FIL：`-1.05%`，1 笔
- APE：`-0.85%`，1 笔
- LINK：`-0.89%`，30 笔，PF `0.95`
- NEAR、SUI 虽然为正，但收益很小，PF 约 `1.14` 和 `1.14`

近一年拖累更明显的是：

- SUI：`-1.60%`，11 笔，PF `0.62`
- AAVE：`-0.64%`，1 笔
- SOL：`-0.47%`，15 笔，PF `0.91`

HYPE、AVAX、FIL、APE、DOT、ONDO、WLD、DASH 在三年样本中几乎没有有效交易，扩进来并没有带来收益来源。

## 结论

1. 当前策略逻辑可以迁移到更多币种，20 币版本三年、近一年和压力期均保持正收益，说明不是只依赖原来的 9 个币。
2. 但 20 币 + max6 不是收益增强版本：三年收益比 Positive13/max3 少 `18.60` 个百分点，PF 也下降。
3. 扩池版本的优点是压力期略好、账户回撤更低，且交易数量从 123 增加到 135，但新增交易没有抵消弱势币种的拖累。
4. 当前不建议直接把 20 币/max6 替换为主回测口径。建议继续保留 Positive13/max3 作为主候选。
5. 20 币/max6 可以作为泛化验证和未来模拟盘观察池，但如果进入 dry-run，应该重点监控 SOL、SUI、LINK、AAVE，而不是继续针对单币改策略。

## 原始阻塞记录

此前 Docker 已启动但 Binance API 不可达，导致回测在市场加载阶段退出。网络恢复后本轮已成功完成，之前的失败不影响本次数据结果。

本轮生成的回测文件位于：

`user_data/analysis/pyramid20_top20_max6_2026-07-14-*.zip`

以下内容为此前的失败记录，保留用于追踪：

`GET https://fapi.binance.com/fapi/v1/exchangeInfo`

主机和 Docker 容器到 Binance API 的 443 端口均无法建立连接，因此程序在读取本地历史数据之前退出。该问题是外部网络/API 连通性问题，不是数据缺失、策略错误或配置错误。

## 续跑命令

网络恢复后，使用以下命令即可继续三年回测：

```powershell
docker --context desktop-linux compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.dualtrend.combined.top20.max6.pyramid20.json --strategy-path /freqtrade/user_data/strategies --strategy-list DualTrendPyramidSecondAdd20V1Strategy --timeframe 1h --timeframe-detail 5m --timerange 20230618-20260618 --export trades --backtest-directory /freqtrade/user_data/analysis/pyramid20_top20_max6_2026-07-14
```

近一年和压力期只需将 `--timerange` 分别替换为 `20250618-20260618` 和 `20260301-20260531`。
