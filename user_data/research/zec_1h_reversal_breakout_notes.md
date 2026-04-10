# ZEC 1h 反转突破支线记录

## 背景

主策略为 `Top9RegimeMainStrategy`，对应正式逻辑为
`CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy`。

当前主策略主样本表现:

- 区间: `2021-04-17` 到 `2026-04-10`
- 总收益: `164.07%`
- CAGR: `21.53%`
- Sharpe: `0.81`
- 最大回撤: `9.16%`

这条支线的起点是:

- `ZEC` 在 `2026-04-06` 到 `2026-04-08` 出现了一段用户主观上非常想参与的 1h 突破行情
- 主策略在这段区间 `0` 笔交易，没有参与
- 因此单独研究“日线空头衰竭/企稳 + 1h 前高附近压缩后向上突破”这一类机会

## 用户对 ZEC 这次结构的定义

用户认为 `2026-04-06` 到 `2026-04-08` 的 `ZEC` 结构具有以下特征:

- 日线空头衰竭，开始企稳
- 不再创新低
- 交易重心上移
- `1h` 在前高附近高位压缩
- 最终向上突破，应该参与

后续验证表明，这个判断是对的。

## 研究过程中的关键结论

### 1. 问题不在 1h 突破本身，而在日线偏置门过严

对比宽版与收窄版在 `2026-04-07 21:00 UTC` 这根目标突破 K 线上的差异后，确认:

- 真正卡住 `ZEC` 的不是 `1h` 底座、突破幅度或放量条件
- 关键卡点是 `breakout_daily_bias_ok = false`

也就是说:

- `1h` 结构已经足够像“可入场突破”
- 真正过严的是日线 bias gate

### 2. 这条支线已经能做到“抓到 ZEC”

宽版实验 `Top9RegimeMainBreakoutProbeStrategy` 能抓到这次 `ZEC`:

- `1` 笔
- 约 `+6.28%`

后续收窄版实验也能抓到:

- `Top9RegimeMainExhaustionProbeBiasRelaxedStrategy`
- `Top9RegimeMainExhaustionProbeZecOnlyStrategy`

两者在 `ZEC` 短窗口都能抓到约 `+6.19%`。

### 3. 但这条支线还不能替代主版本

关键原因:

- 一旦把日线偏置门放宽到能抓 `ZEC`
- 全样本误判会增加
- 主要副作用不在 `ZEC`，而在其他币种，尤其是此前已观察到的 `SOL`

已确认的阶段性结论:

- 用户对 `ZEC` 这次形态的判断是对的
- 这类机会确实存在，而且可以被策略结构化表达
- 但目前版本还不具备直接合并进正式主线的性价比

## 全样本实验结论

### BiasRelaxed 版本

策略:

- `Top9RegimeMainExhaustionProbeBiasRelaxedStrategy`

主样本区间:

- `2021-04-17` 到 `2026-04-10`

结果:

- 总收益: `130.71%`
- Sharpe: `0.79`
- 最大回撤: `11.73%`

结论:

- 能抓到 `ZEC`
- 但整体仍明显弱于主策略

### ZecOnly 版本

策略:

- `Top9RegimeMainExhaustionProbeZecOnlyStrategy`

主样本区间:

- `2021-04-17` 到 `2026-04-10`

结果:

- 总收益: `127.90%`
- Sharpe: `0.77`
- 最大回撤: `11.51%`

结论:

- 只给 `ZEC` 开 breakout 分支后，副作用缩小
- 但依然没有超过当前主策略

## 逐笔样本审查结论

对 `long_1h_highbase_breakout` 逐笔交易做过单独审查。

### BiasRelaxed

- 总共 `16` 笔
- `5` 笔盈利，`11` 笔亏损
- 整体接近打平，质量不够高

样本分布:

- `BTC`: `4` 笔，合计约 `+1.01%`
- `ZEC`: `6` 笔，合计约 `+1.10%`
- `BNB`: `6` 笔，合计约 `-2.87%`

说明:

- breakout 分支最大的拖累主要来自 `BNB`
- `ZEC` 这条线本身不是完全无效

### ZecOnly

- 总共 `6` 笔
- `2` 笔盈利，`4` 笔亏损
- 合计仍为正，约 `+1.10%`

说明:

- 这条 breakout 逻辑在 `ZEC` 上具备一定研究价值
- 但目前样本数量仍偏少，尚不足以成为正式分支

## 当前最值得保留的形态认识

这条研究支线真正识别到的，不是泛化的“追突破”，而是更具体的一类机会:

- 日线下跌动能衰减
- 日线不再持续创新低
- 日线交易重心开始企稳或缓慢抬升
- `1h` 在关键前高附近压缩
- 最终出现实体、放量、接近收盘高点的上破

可以把它概括为:

`日线空头衰竭/企稳 + 1h 高位压缩突破`

## K 线复盘补充

本次补充复盘使用了 Binance futures 的原始 K 线数据，已另存为:

- [zec_1d_20251105_20260410.csv](/D:/test/ft_userdata/user_data/research/zec_klines/zec_1d_20251105_20260410.csv)
- [zec_1h_20251105_20260410.csv](/D:/test/ft_userdata/user_data/research/zec_klines/zec_1h_20251105_20260410.csv)
- [zec_1h_focus_20260404_20260410.csv](/D:/test/ft_userdata/user_data/research/zec_klines/zec_1h_focus_20260404_20260410.csv)

### 1. 从 2025-11-05 到 2026-04-10 的日线大结构

更准确地看，这次 `2026-04-07` 到 `2026-04-09` 的上攻，并不是“长期下跌后的第一根反转阳线”，而是:

- `2025-11` 的大波动高位之后，`ZEC` 日线长期下行
- 阶段最低区出现在 `2026-03-07` 到 `2026-03-09`
- 其中最低 low 出现在 `2026-03-08`，为 `191.35`
- 之后在 `2026-03-16` 出现过一次强反抽，日高到 `289.31`
- 但这波并未直接转成主升，随后再次回落
- 关键在于，回落后的低点没有再跌破 `3 月` 那个极限低点

也就是说，`2026-04-06` 到 `2026-04-08` 这波真正对应的日线背景，不是“刚从最低点弹起”，而是:

- 第一轮恐慌下跌已经完成
- 第一轮强反抽已经出现过
- 二次回撤阶段没有再创新低
- 日线交易重心在 `3 月底` 到 `4 月初` 已经开始从 `200` 附近抬升到 `230` 到 `250` 区域

这比“日线空头衰竭、企稳”更准确，应该表述为:

`日线大跌后，经历过一次失败但有效的强反抽，二次回撤不创新低，随后进入更高位置的再起爆阶段`

### 2. 2026-04-06 到 2026-04-07 的 1h 起爆前结构

如果只看起爆前最后两天，结构也比“前高附近压缩”更具体。

#### 第一阶段: 先从低位区抬起，而不是贴地直接爆

`2026-04-06 00:00 UTC` 到 `2026-04-06 10:00 UTC`:

- 价格从约 `244.91` 一路抬升
- 最高打到 `260.91`
- 这说明市场已经先完成了从日线企稳到 `1h` 进攻试探的切换

这一步很重要，因为真正的起爆并不是从毫无准备的低位直接拉起，而是先有一段“脱离底部”的抬升。

#### 第二阶段: 回踩不破，交易重心继续抬升

`2026-04-06` 日内后半段并没有继续单边上冲，而是转入整理:

- 虽然 `2026-04-06 22:00 UTC` 一度下探到 `249.36`
- 但很快在 `2026-04-06 23:00 UTC` 收回到 `251.33`
- 没有把前面的结构重新打坏

这说明:

- 多头不是一冲就散
- 回踩虽然存在，但没有形成新的破位下跌
- 底部抬升后的结构完整性仍在

#### 第三阶段: 先出现一次 1h 结构换挡，再进入高位中继

真正的 `1h` 结构换挡，最早不是 `2026-04-07 21:00 UTC` 那根爆发 K，而是更早的:

- `2026-04-07 04:00 UTC`

这根 K 线:

- low 约 `253.58`
- high 约 `267.67`
- close 约 `261.65`
- 是一次明显的向上扩张

它的意义是:

- 市场正式脱离 `250` 附近的平台
- 价格开始进入更高一层的运行区间
- 后面的“起爆前压缩”其实是发生在更高位置的中继，不是底部原地蓄力

### 3. 更准确的“临近起爆前”描述

如果只描述最关键的起爆前结构，最准确的窗口应当放在:

- `2026-04-07 09:00 UTC` 到 `2026-04-07 20:00 UTC`

这 12 根 `1h` K 的关键特征:

- 区间高点约 `278.86`
- 区间低点约 `259.20`
- 区间振幅约 `7.1%`
- 第一根 close 约 `266.88`
- 最后一根 close 约 `276.83`
- 交易重心抬升约 `3.73%`

因此，这不是简单的“横着压缩”，而是:

- 价格已经被抬升到前高附近
- 整理区内部的收盘中枢继续上移
- 回撤没有重新掉回 `250` 一带
- 市场是在更高位置做中继整理

这一段更准确应描述为:

`高位前压缩 + 中枢上移 + 回踩变浅`

而不是单纯的“前高附近横盘”。

### 4. 目标起爆 K 线本身的特征

真正的起爆 K 线是:

- `2026-04-07 21:00 UTC`

它相对起爆前结构的特征非常鲜明:

- 突破前 `72h` 最高点约为 `278.86`
- 该 K 线 open 约 `276.83`
- high 约 `320.00`
- close 约 `309.47`
- low 约 `276.79`

也就是说:

- 它几乎从突破位附近直接起爆
- 下影极短
- 实体极强
- close 落在整根 K 线较高位置

量能上:

- 该 K 线 volume 约 `694,847`
- 是前 `20` 根 `1h` 平均量能的约 `6.13` 倍

实体强度上:

- 单根实体涨幅约 `10.55%`

这说明它不是一般意义上的“轻微上破”，而是:

- 高位中继完成后的强扩张
- 量价同时共振
- 几乎没有回踩确认，直接脱离整理带

### 5. 对原有描述的进一步修正

结合这次更完整的 K 线复盘，原来的描述可以进一步从:

`日线空头衰竭/企稳 + 1h 高位压缩突破`

细化为:

`日线大跌后的一次有效强反抽之后，二次回撤不创新低，随后 1h 先完成底部脱离和结构换挡，再在更高位置围绕前高做中继压缩，最终以极强放量实体 K 线完成起爆`

这个版本比原描述更准确，原因在于它明确区分了 4 个不同阶段:

- 日线极限下跌完成
- 第一轮强反抽已经出现
- 二次回撤不创新低
- `1h` 高位中继后强扩张起爆

### 6. 对未来策略表达的启发

如果未来要把这类机会重新结构化，不应只盯住“突破当天”的单根 K。

更值得表达的顺序是:

- 日线极端下跌后的阶段性低点已经出现
- 后续回撤没有再破那组低点
- `1h` 已出现一次先行结构换挡
- 起爆前整理区的收盘中枢持续抬升
- 真正突破时必须是明显放量、强实体、接近收盘高点

这意味着以后如果再做这条分支，核心抓的不是“底部突破”，而更像:

`二次确认后的高位中继起爆`

## 可编码条件清单

如果未来要把这类 `ZEC` 机会重新转成策略表达，建议按“先背景、再换挡、再中继、最后起爆”的顺序组织，而不是只写一个宽泛 breakout 条件。

### A. 日线背景层

目标不是抓“最低点反转”，而是抓“阶段低点出现后的二次确认”。

建议条件方向:

- 日线曾经历过一轮较深下跌
- 最近一段时间内已经出现过一次明显反抽
- 回撤后的日线 low 没有再跌破前一轮阶段低点
- 当前日线 close 已重新站回慢均线附近，或重新回到慢均线之上
- 日线不能还处在持续创新低的推进式空头里

更贴近这次 `ZEC` 的语义是:

- `not making new lows`
- `not breaking down again`
- `secondary pullback holds above major low`

### B. 1h 先行换挡层

真正值得关注的不是突破 K 本身，而是突破前是否已经出现过一次结构换挡。

建议条件方向:

- 在起爆前 `12` 到 `36` 小时内，至少出现过一次明显上冲
- 该上冲把价格从原整理区抬升到更高运行层
- 上冲后的回撤不能把结构重新打回原底部区
- 回撤后的低点抬高，说明交易重心已经切换

这一步是为了过滤掉两类差样本:

- 仍在底部乱震、没有真正脱离底部的假突破
- 纯消息脉冲、没有中继过程的一次性尖刺

### C. 1h 中继压缩层

这一步不是要求绝对窄幅，而是要求“高位整理时中枢继续上移”。

建议条件方向:

- 突破前最近 `8` 到 `16` 根 `1h` K 在前高附近运行
- 区间整体振幅受控
- 收盘中枢逐步抬高
- 回踩低点逐步抬高或至少不再深踩
- 整理区结束前，价格没有重新跌回前一个启动平台

也就是说，未来如果编码:

- 不要只写 `compression`
- 最好同时写 `compression + center lift + shallow pullback`

### D. 起爆 K 线质量层

这一层应该保持严格，因为真正好的样本在这里往往很鲜明。

建议条件方向:

- 突破 K 必须实体明显
- close 必须接近本根高位
- 必须有效站上前 `72h` 或前 `N` 根的关键高点
- 成交量必须显著扩张
- 最好不是“上影很长、收回区间内”的冲高回落 K

结合本次 `ZEC` 样本，量能应当是重点:

- 不是略微放量
- 而是明显高于突破前均量的扩张

### E. 需要额外防守的误判来源

结合之前的逐笔样本审查，未来如果再开支线，最好重点防下面几类误判:

- 日线已经明显过热后继续追高
- `1h` 虽然突破，但量能没有真正放大
- 突破前并不存在先行换挡，实际上还是底部乱震
- 非 `ZEC` 币种直接复用同一套 breakout 逻辑，尤其像 `BNB` 这种误判偏多的标的

### F. 最终建议的表达方式

未来如果要把这类机会写成一句策略描述，建议用下面这个版本，精度会比原先更高:

`日线大跌后出现阶段低点，第一次强反抽后回撤不再创新低；1h 先完成底部脱离和结构换挡，再在更高位置围绕前高做中继压缩，最终以放量强实体 K 线完成起爆。`

## 伪代码规则草稿

下面不是最终策略代码，只是为了把这类机会的结构表达顺序固定下来。

### 1. 日线背景判定

```python
daily_major_low_60 = low_1d.shift(1).rolling(60).min()
daily_rebound_high_20 = high_1d.shift(1).rolling(20).max()

daily_no_new_lows = low_1d > daily_major_low_60 * 1.02
daily_hold_after_rebound = low_1d > low_1d.shift(20).rolling(20).min() * 1.01
daily_back_above_slow = close_1d >= ema_slow_1d * 0.98
daily_not_breaking_down = close_1d >= low_1d.shift(1).rolling(10).min() * 1.01

daily_reversal_background_ok = (
    daily_no_new_lows
    and daily_hold_after_rebound
    and daily_back_above_slow
    and daily_not_breaking_down
)
```

语义上抓的是:

- 阶段低点已经出现
- 不是还在持续破底
- 反抽后回撤仍然稳住
- 日线已经重新靠近或站回慢均线

### 2. 1h 先行换挡判定

```python
hourly_launch_high_24 = high.shift(1).rolling(24).max()
hourly_launch_low_24 = low.shift(1).rolling(24).min()

hourly_detach_from_bottom = close > hourly_launch_low_24 * 1.05
hourly_center_5 = typical_price.rolling(5).mean()
hourly_center_10 = typical_price.rolling(10).mean()
hourly_center_shift_up = (
    hourly_center_5 > hourly_center_5.shift(3)
    and hourly_center_10 > hourly_center_10.shift(5)
)

hourly_pullback_holds = low.shift(1).rolling(8).min() > hourly_launch_low_24 * 1.02

hourly_regime_shift_ok = (
    hourly_detach_from_bottom
    and hourly_center_shift_up
    and hourly_pullback_holds
)
```

语义上抓的是:

- 价格已经脱离原底部区
- 运行中枢已经上移
- 回踩没有把结构重新打坏

### 3. 1h 高位中继压缩判定

```python
major_high_72 = high.shift(1).rolling(72).max()
base_high_12 = high.shift(1).rolling(12).max()
base_low_12 = low.shift(1).rolling(12).min()
base_range_pct = (base_high_12 - base_low_12) / close

base_close_center = close.shift(1).rolling(6).mean()
base_close_center_prev = base_close_center.shift(6)
base_floor = low.shift(1).rolling(6).min()
base_floor_prev = base_floor.shift(6)

near_prior_high = close.shift(1) >= major_high_72 * 0.97
controlled_range = base_range_pct < 0.08
center_lifting = base_close_center > base_close_center_prev * 1.01
pullback_shallow = base_floor > base_floor_prev * 1.005

high_base_reaccumulation_ok = (
    near_prior_high
    and controlled_range
    and center_lifting
    and pullback_shallow
)
```

语义上抓的是:

- 已经运行到前高附近
- 整理带振幅受控
- 整理时中枢还在抬升
- 回踩在变浅

### 4. 起爆 K 线质量判定

```python
breakout_ref_high = high.shift(1).rolling(72).max()
volume_mean_20 = volume.shift(1).rolling(20).mean()
candle_range = (high - low).clip(lower=1e-9)

strong_breakout = close > breakout_ref_high * 1.03
strong_extension = high > breakout_ref_high * 1.08
volume_expansion = volume > volume_mean_20 * 2.5
body_strength = (close - open) / close > 0.05
close_near_high = (high - close) / candle_range < 0.28
minimal_lower_wick = (open - low) / candle_range < 0.15

explosive_breakout_candle_ok = (
    strong_breakout
    and strong_extension
    and volume_expansion
    and body_strength
    and close_near_high
    and minimal_lower_wick
)
```

这里有意比普通 breakout 更严格，因为这条支线要抓的是“高质量起爆”，不是一般突破。

### 5. 过热与误判过滤

```python
daily_not_overheated = rsi_1d < 68
hourly_not_exhausted = rsi < 92
avoid_failed_spike = high.shift(1) < breakout_ref_high * 1.02
prefer_core_pair = pair in {"ZEC/USDT:USDT"}

breakout_risk_filter_ok = (
    daily_not_overheated
    and hourly_not_exhausted
    and avoid_failed_spike
    and prefer_core_pair
)
```

这一步的目的不是提高触发数，而是尽量减少未来像 `BNB` 这类样本带来的误判。

### 6. 最终信号拼接

```python
long_zec_reversal_breakout = (
    daily_reversal_background_ok
    and hourly_regime_shift_ok
    and high_base_reaccumulation_ok
    and explosive_breakout_candle_ok
    and breakout_risk_filter_ok
)
```

### 7. 这套伪代码的定位

这套规则草稿不是为了立刻合并进主策略，而是为了保留一份以后可重启研究的“结构化入口”。

它的定位更适合:

- 单独开支线实验
- 先只在 `ZEC` 上验证
- 逐笔检查命中样本质量
- 确认误判压住后，再考虑是否扩大到其他币种

## 当前不建议继续走的方向

- 不建议继续走“震荡高抛低吸层”方向
- 不建议直接通过进一步放宽日线 bias gate 来强行增加 breakout 机会
- 不建议在没有额外过滤的情况下把这条 breakout 分支并回主策略

原因是:

- 这会更容易把误判带回全样本
- 特别是在弱环境或非 `ZEC` 币种上容易失效

## 如果未来要重新优化，优先看什么

如果以后重新开启这条研究支线，优先方向不是“再放宽”，而是“提高 breakout 样本质量”。

建议优先检查:

- 哪些 breakout 交易赚钱
- 哪些 breakout 交易亏钱
- 尽量只保留高质量那一类

结合本次样本审查，后续可优先考虑的过滤思路:

- 更强的 `1h` 成交量扩张要求
- 避免日线已经过热的 breakout
- 避免把 `BNB` 这类误判较多的币直接纳入同一套 breakout 逻辑
- 继续保留“日线不再创新低/不再破位”这一类衰竭确认

## 当前最终结论

这条支线的最终定位如下:

- 它成功解释了为什么主策略错过了 `ZEC 2026-04-08` 那波突破
- 它验证了用户对那次形态的主观判断是正确的
- 它已经具备研究价值
- 但暂时不应进入正式主线

因此，当前最合适的处理方式是:

- 保持主策略纯净
- 保留这份文字记录
- 等以后如果需要，基于这份记录重新开启小范围定向优化
