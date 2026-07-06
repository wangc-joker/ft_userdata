# DualTrend 前两年 short_pullback_restart 同单对比

日期: 2026-07-01

## 目的

在前两年窗口内，专门比较 `short_pullback_restart` 这条主空头信号的同类交易，确认:

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

相对 `DualTrendRawStrategy`，到底是:

1. 成功减少了坏单亏损
2. 还是过早截断了大盈利单
3. 哪一边对总收益影响更大

## 口径

- 配置: `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 时间: `2022-11-11 16:00:00` 到 `2024-11-11 00:00:00`
- `1h + 5m detail`
- 仅分析:
  - `enter_tag = short_pullback_restart`
  - `is_short = True`
- 同单匹配规则:
  - `pair + open_date` 完全一致

## Raw vs Baseline

- 共同可对齐交易数: `114`
- `Raw` 更好: `39`
- `Baseline` 更好: `74`
- 完全相同: `1`

### 汇总

- 共同交易利润和:
  - `Raw`: `+545.37 USDT`
  - `Baseline`: `+359.34 USDT`
  - 差值: `Raw +186.03 USDT`

### 结构判断

- `Baseline` 让 `Raw` 的亏损单变得更轻或转正:
  - `74` 笔
- `Baseline` 把 `Raw` 的盈利单削弱:
  - `35` 笔
- `Raw` 是 `roi=10%`，但 `Baseline` 没拿到 `roi`:
  - `16` 笔
- `Raw` 的大盈利单被明显截断:
  - `16` 笔

### 典型“被截断的大空头”

- `BNB 2024-08-31 17:00 UTC`
  - `Raw`: `+10.0%`, `roi`
  - `Baseline`: `-0.0%`, `trailing_stop_loss`
- `SUI 2023-10-09 09:00 UTC`
  - `Raw`: `+10.0%`, `roi`
  - `Baseline`: `-0.33%`, `trailing_stop_loss`
- `DOGE 2023-03-04 19:00 UTC`
  - `Raw`: `+10.0%`, `roi`
  - `Baseline`: `+0.01%`, `trailing_stop_loss`
- `TAO 2024-06-10 05:00 UTC`
  - `Raw`: `+10.0%`, `roi`
  - `Baseline`: `+0.01%`, `trailing_stop_loss`
- `NEAR 2022-12-16 09:00 UTC`
  - `Raw`: `+10.0%`, `roi`
  - `Baseline`: `-0.10%`, `trailing_stop_loss`

### 典型“被 Baseline 救回来的坏单”

- `ADA 2024-07-07 14:00 UTC`
  - `Raw`: `-4.56%`, `stop_loss`
  - `Baseline`: `+5.03%`, `partial_exit`
- `ADA 2024-01-18 11:00 UTC`
  - `Raw`: `-0.67%`, `stale_loss_72h`
  - `Baseline`: `+5.00%`, `partial_exit`
- `DOGE 2024-09-05 04:00 UTC`
  - `Raw`: `-0.60%`, `stale_loss_72h`
  - `Baseline`: `+5.05%`, `partial_exit`

## Raw vs Guard

- 共同可对齐交易数: `112`
- `Raw` 更好: `38`
- `Guard` 更好: `73`
- 完全相同: `1`

### 汇总

- 共同交易利润和:
  - `Raw`: `+544.65 USDT`
  - `Guard`: `+361.60 USDT`
  - 差值: `Raw +183.05 USDT`

### 结构判断

- `Guard` 让 `Raw` 的亏损单变得更轻或转正:
  - `73` 笔
- `Guard` 把 `Raw` 的盈利单削弱:
  - `34` 笔
- `Raw` 是 `roi=10%`，但 `Guard` 没拿到 `roi`:
  - `15` 笔
- `Raw` 的大盈利单被明显截断:
  - `15` 笔

### 典型“被截断的大空头”

和 `Baseline` 基本一致，最典型的仍是这些:

- `BNB 2024-08-31 17:00 UTC`
- `SUI 2023-10-09 09:00 UTC`
- `DOGE 2023-03-04 19:00 UTC`
- `TAO 2024-06-10 05:00 UTC`
- `NEAR 2022-12-16 09:00 UTC`

它们大多表现为:

- `Raw`: 直接跑到 `roi 10%`
- `Guard`: 在 `trailing_stop_loss` 或 `partial_exit` 提前离场

## 核心结论

这一轮结论非常明确:

1. `Baseline / Guard` 确实更擅长处理坏单。  
   它们在共同交易里，赢 `Raw` 的次数更多。

2. 但 `Raw` 的少数大盈利空头价值更高。  
   虽然 `Raw` 赢的笔数更少，但赢的金额更大。

3. 前两年总收益差距，主要不是“坏单太多”，而是“大盈利单被截断”。  
   `Baseline` 和 `Guard` 都把一批本来能跑到 `10% roi` 的空头单，提前截在:
   - `0%` 附近
   - `5% partial_exit`
   - 或很浅的 `trailing_stop_loss`

4. 所以前两年优化方向不该再偏向“继续加强防守”。  
   根因已经很清楚:
   - 防守没错
   - 但对强趋势空头的放行不够

## 下一步建议

如果继续优化 `Baseline / Guard`，最值得做的不是再加过滤器，而是只做一个问题:

`当 short_pullback_restart 已经明显走强时，如何识别“该继续放行到 10%+”的强单，而不是按当前规则过早 trailing / partial exit。`

更具体地说，下一轮应该只验证:

- 哪些空头单在浮盈达到 `5%` 后，后面还能继续扩展到 `10% roi`
- 这些单在达到 `5%` 时，有没有共同特征
- 是否可以做一个“强单放行条件”，只放宽这类单，而不去全面放松所有单子的退出
