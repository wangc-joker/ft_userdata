# DualTrend 保留策略清单（2026-07-08 历史快照）

> **历史状态：** 本文的“当前”只代表 2026-07-08，已被仓库根目录的 [`CURRENT_DUALTREND.md`](../../CURRENT_DUALTREND.md) 取代。当前研究主候选是 `DualTrendPyramidSecondAdd20LongMicroV1Strategy`。

更新日期：2026-07-08

这份文档用于快速说明目前仓库里还保留哪些策略文件、每个策略大概负责什么、当前主线候选是谁。后面不管是继续优化、回测，还是让 GPT 帮你复盘，都可以先看这份。

## 1. 当前保留的策略文件

### 1.1 核心基础文件

1. `D:\test\ft_userdata\user_data\strategies\DualTrendCompressionRestartShortV1Strategy.py`
2. `D:\test\ft_userdata\user_data\strategies\DualTrendCombinedLongDailyCenterShortV1Strategy.py`
3. `D:\test\ft_userdata\user_data\strategies\DualTrendMainStrategies.py`

### 1.2 说明

- `DualTrendCompressionRestartShortV1Strategy.py`
  是最底层的空头双顺基础策略，核心 short 入场逻辑都从这里长出来。
- `DualTrendCombinedLongDailyCenterShortV1Strategy.py`
  在空头基础上叠加了做多的 `long_1d_center_compression`。
- `DualTrendMainStrategies.py`
  是当前主线策略的“组装层”，大多数实际回测用的策略名都在这里。

## 2. 当前策略结构

可以把现在的结构理解成三层：

1. **底层原始信号层**
   - 定义 short / long 的核心入场形态
   - 定义基础止损、风控、仓位、指标

2. **中间组合层**
   - 把 long / short 合并
   - 加市场过滤、BTC 过滤、市场重心过滤

3. **主线候选层**
   - 在不改核心入场思想的前提下
   - 叠加 breakeven、guard、close quality、tight stop、盈利单加仓

## 3. 各文件里的主要策略类

## 3.1 `DualTrendCompressionRestartShortV1Strategy.py`

### `DualTrendCompressionRestartShortV1Strategy`

这是最核心的空头原型策略，包含两个 short tag：

1. `short_pullback_restart`
2. `short_compression_breakdown`

它负责的内容主要有：

- 双顺空头基础入场
- 压缩区识别
- pullback / breakdown 判定
- 基础风控
- 基础仓位逻辑
- 基础 custom stoploss / custom exit 框架

这个文件是后面大多数 short 策略的源头。

### `DualTrendCompressionRestartShortPullbackOnlyV1Strategy`

只保留：

- `short_pullback_restart`

适合做单独拆解回测，判断 pullback 这条线本身是不是稳定。

### `DualTrendCompressionRestartShortCompressionOnlyV1Strategy`

只保留：

- `short_compression_breakdown`

适合单独验证 compression breakdown 的贡献和拖累。

## 3.2 `DualTrendCombinedLongDailyCenterShortV1Strategy.py`

### `DualTrendCombinedLongDailyCenterShortV1Strategy`

这是在 short V1 基础上加了 long 的组合版本。

新增 long tag：

- `long_1d_center_compression`

它的意义是：

- short 仍然保留双顺空头主逻辑
- long 增加日线市场重心压缩后的做多形态

这是一份“long + short 合并原型”。

### `DualTrendCombinedLongDailyCenterTop9ShortV1Strategy`

是在合并版基础上缩小币池的一个变体。

### `DualTrendCombinedLongDailyCenterCore3ShortV1Strategy`

是在合并版基础上进一步缩小币池的一个变体。

这两个更多是历史验证辅助版本，不是现在的主线重心。

## 3.3 `DualTrendMainStrategies.py`

这个文件是当前最重要的策略总装文件。

### `DualTrendRawStrategy`

可以把它理解成：

- 当前主线体系里的“原始版”
- 已经不是最早的裸策略
- 但仍然是后续对照实验最常用的 baseline 之一

它主要代表：

- short 主逻辑保留
- long 逻辑保留
- 有基础全局过滤
- 但止盈止损管理还不算很厚

### `DualTrendBaselineStrategy`

这是在 Raw 基础上更进一步的“标准基线版”。

它主要加入了：

- breakeven 思路
- 到达一定利润后的条件分流

通常用于和更厚的 guard 版对比。

### `DualTrendGuardStrategy`

这是在 Baseline 基础上再加一层 guard 的版本。

它的作用主要是：

- 过滤一部分更差的压缩破位信号
- 让主线在压力期更稳一点

它是一个很重要的中间里程碑版本。

### `DualTrendCompressionCloseQualityGuardStrategy`

这是把 short compression 的收盘质量过滤进一步显式化的版本。

重点在：

- 更关注 breakdown K 的收盘质量
- 尽量减少一些“跌破但收得不够差”的假破位

### `DualTrendCompressionCloseQualityGuard028Strategy`

这是上面 close quality guard 的一个具体阈值版本。

其中 `028` 对应的是当前保留下来的核心阈值候选之一。

### `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

这是目前 short 主线里非常关键的一版。

它的特点是：

- 基于 `CloseQualityGuard028`
- 对 compression tag 进一步采用更结构化、更紧一些的止损控制

它对应的是：

- 不大改原始入场
- 主要在坏的 compression breakdown 上少亏一点

如果要看“当前 short 主候选”的近亲，这个版本很重要。

### `DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25Strategy`

这是开始研究“盈利单加仓”的第一层版本。

核心思想：

- 原单已经盈利
- 出现新的同向加仓机会时
- 允许加一层较小仓位

### `DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardStrategy`

在加仓基础上，又给加仓触发增加了 close guard。

### `DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBeStrategy`

在前面的基础上，又增加了加仓腿自己的 breakeven 保护。

### `DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBe015Strategy`

这是把加仓腿的保本触发调到更明确阈值后的版本。

### `DualTrendCompressionCloseQualityGuard028PyramidWindow03To12LegBe015Strategy`

这是加仓窗口更窄的版本，主要测试：

- 盈利多少时允许加仓
- 加仓是不是太早

### `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

这是目前保留下来的“盈利单加仓主候选”。

它的特点是：

- 只在已有盈利的基础仓上研究继续加仓
- 加仓窗口相对更稳
- 给加仓腿单独做了 breakeven 保护

如果后面继续研究“盈利单上继续做厚”，这版就是当前最值得接着做的。

## 4. 当前保留的兼容别名

为了避免旧回测命令、旧脚本、旧文档失效，文件里还保留了几个兼容别名：

1. `DualTrendCombinedShortPullbackShapeV1Strategy`
   - 对应 `DualTrendRawStrategy`

2. `DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`
   - 对应 `DualTrendBaselineStrategy`

3. `DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy`
   - 对应 `DualTrendGuardStrategy`

这些主要是为了兼容历史命名，不建议再继续作为新主名使用。

## 5. 当前建议的阅读顺序

如果后面要重新理解整套策略，建议按这个顺序看：

1. `DualTrendCompressionRestartShortV1Strategy.py`
   - 先看 short 的原始双顺逻辑

2. `DualTrendCombinedLongDailyCenterShortV1Strategy.py`
   - 再看 long 是怎么拼进来的

3. `DualTrendMainStrategies.py`
   - 最后看各种 baseline / guard / close quality / pyramid 版本怎么长出来

## 6. 当前主线怎么理解

如果只说现在最值得保留的几条主线，可以这样记：

### 主线 1：原始对照线

- `DualTrendRawStrategy`

用途：

- 做大多数新实验的基础对照

### 主线 2：标准防守线

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

用途：

- 观察 breakeven 与 guard 是否带来更稳的回撤表现

### 主线 3：当前 short 强候选

- `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

用途：

- 在不大改核心双顺入场的前提下
- 通过 close quality + compression tight stop 提升短空质量

### 主线 4：当前盈利单加仓候选

- `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

用途：

- 研究“已有盈利仓位上是否值得继续加仓”
- 并且让加仓腿具备独立保本保护

## 7. 这次清理掉了什么

这次主要清理掉的是：

- 失败的实验类
- 重复的中间研究版本
- 已经没有继续保留意义的临时策略包装文件
- `__pycache__`

保留原则是：

1. 保留主线基础文件
2. 保留现在还可能继续研究的有效候选
3. 删除明显失败、重复、临时、废弃实验版本

## 8. 后续建议

如果下一步继续研究，建议优先围绕下面几个方向推进：

1. `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`
   - 继续做 short 的止盈 / 减仓 / 结构退出管理

2. `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
   - 继续做盈利单加仓的扩展验证

3. `DualTrendRawStrategy` / `DualTrendBaselineStrategy`
   - 继续保留作长期对照线

---

一句话总结：

现在仓库已经从很多历史实验分支，收敛成了“基础原型 + 主线候选 + 盈利单加仓候选”这几条清晰的线，后面继续优化时会干净很多。
