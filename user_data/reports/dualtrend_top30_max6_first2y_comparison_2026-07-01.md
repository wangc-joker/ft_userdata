# DualTrend Top30 Max6 前两年对比记录

日期: 2026-07-01

## 目的

对比以下 3 个策略在统一口径下的前两年表现，确认为什么 `DualTrendBaselineStrategy` 和 `DualTrendGuardStrategy` 明显弱于 `DualTrendRawStrategy`。

- `DualTrendRawStrategy`
- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

统一口径:

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 主周期: `1h`
- 细粒度: `5m`
- 时间范围: `2022-11-11 16:00:00` 到 `2024-11-11 00:00:00`
- 模式: Binance Futures, isolated

## 总结果

| 策略 | 收益率 | PF | MaxDD | Trades | Winrate |
|---|---:|---:|---:|---:|---:|
| DualTrendRawStrategy | 67.65% | 1.64 | 8.55% | 207 | 27.54% |
| DualTrendBaselineStrategy | 51.39% | 1.76 | 7.91% | 218 | 46.33% |
| DualTrendGuardStrategy | 55.27% | 1.85 | 7.91% | 213 | 46.48% |

结论:

- `Raw` 前两年收益最高，但胜率低、回撤更高。
- `Baseline` / `Guard` 用更高胜率换掉了一部分大收益。
- `Guard` 比 `Baseline` 稍强，但仍未追上 `Raw`。

## 按年份拆解

| 策略 | 2022 | 2023 | 2024 |
|---|---:|---:|---:|
| DualTrendRawStrategy | +80.93 USDT | +108.33 USDT | +487.22 USDT |
| DualTrendBaselineStrategy | -4.30 USDT | +103.54 USDT | +414.69 USDT |
| DualTrendGuardStrategy | -4.30 USDT | +103.54 USDT | +453.50 USDT |

关键点:

- 最大差异来自 `2022-11-11 -> 2022-12-31` 这一段。
- `Raw` 在 2022 尾段拿到了 `+80.93 USDT`，而 `Baseline` / `Guard` 都是 `-4.30 USDT`。
- 这一个阶段就解释了 `Raw` 相对 `Baseline/Guard` 的大半领先。
- `Guard` 在 2024 比 `Baseline` 修复了一部分收益，但还没追平 `Raw`。

## 按 entry_tag 拆解

### DualTrendRawStrategy

- `short_pullback_restart`: `+536.67 USDT`, 115 笔
- `long_1d_center_compression`: `+159.05 USDT`, 40 笔
- `short_compression_breakdown`: `-19.22 USDT`, 52 笔

### DualTrendBaselineStrategy

- `short_pullback_restart`: `+330.70 USDT`, 125 笔
- `long_1d_center_compression`: `+196.87 USDT`, 43 笔
- `short_compression_breakdown`: `-13.64 USDT`, 50 笔

### DualTrendGuardStrategy

- `short_pullback_restart`: `+332.87 USDT`, 123 笔
- `long_1d_center_compression`: `+196.09 USDT`, 44 笔
- `short_compression_breakdown`: `+23.78 USDT`, 46 笔

结论:

- `Baseline` / `Guard` 并不是输在 long。
- `Baseline` / `Guard` 的 `long_1d_center_compression` 反而比 `Raw` 更强。
- 真正的核心差距在 `short_pullback_restart`:
  - `Raw`: `+536.67`
  - `Baseline`: `+330.70`
  - `Guard`: `+332.87`
- 也就是说，早期收益差距主要来自:
  - `Raw` 的空头主信号更能吃到大波段
  - `Baseline` / `Guard` 的防守型退出更早把利润削掉了

## 按 pair 拆解

### Raw 最强贡献

- `BNB`: `+245.86`
- `ZEC`: `+204.55`
- `DOGE`: `+154.44`
- `BTC`: `+93.27`

### Raw 主要拖累

- `XRP`: `-61.74`
- `NEAR`: `-32.17`
- `LTC`: `-26.55`

### Baseline 最强贡献

- `BNB`: `+138.00`
- `BTC`: `+127.15`
- `ZEC`: `+110.48`
- `DOGE`: `+107.01`

### Baseline 主要拖累

- `LINK`: `-46.48`
- `SUI`: `-30.83`
- `LTC`: `-15.80`

### Guard 最强贡献

- `BTC`: `+143.42`
- `BNB`: `+139.26`
- `ZEC`: `+111.95`
- `DOGE`: `+109.94`

### Guard 主要拖累

- `LINK`: `-47.36`
- `SUI`: `-31.25`
- `LTC`: `-15.80`

结论:

- `Raw` 优势集中在 `BNB / ZEC / DOGE` 这类能走出大空头波段的品种。
- `Baseline` / `Guard` 的主要拖累不是 `XRP/NEAR`，而变成了 `LINK / SUI / LTC`。
- 但 pair 不是主因，主因仍然是主空头信号的收益释放方式不同。

## 现阶段判断

前两年如果要继续优化 `Baseline` / `Guard`，优先级应该是:

1. 不碰 long 模块
2. 不先动 `short_compression_breakdown`
3. 重点回看 `short_pullback_restart`
4. 重点检查:
   - 早期保本是否过早
   - partial exit 是否过早削掉大盈利单
   - trailing 是否在 2022 末 / 2023 初过早收紧

## 当前建议

下一轮不要做大范围调参，直接围绕一个问题验证:

`Baseline/Guard` 相比 `Raw`，到底是哪些已经盈利 5% 以上的空头单，被过早保本/减仓/移动止损截断了。`

这会比继续做 pair 过滤更接近根因。
