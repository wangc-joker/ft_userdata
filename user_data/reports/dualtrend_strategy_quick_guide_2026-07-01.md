# DualTrend 策略快速说明

日期：2026-07-01

## 目的

这份文档是当前 3 个 DualTrend 主策略的快速参考说明：

- `DualTrendRawStrategy`
- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

目标是：

- 以后快速回忆每个策略是干什么的
- 不用重读整份代码也能理解它们之间的差异
- 明确谁是原始版，谁是基线版，谁是当前主候选

---

## 1. 三个策略的共同基础

这 3 个策略都建立在同一套底层结构上：

- 做空部分来自 dual-trend compression-restart 框架
- 做多部分保留 `long_1d_center_compression` 这条逻辑
- 主周期是 `1h`
- 同时使用 `4h` 和 `1d` 的辅助周期信息
- 做空核心 entry tag 是：
  - `short_pullback_restart`
  - `short_compression_breakdown`
- 做多核心 tag 是：
  - `long_1d_center_compression`

它们共同遵循的几条大原则是：

1. 以趋势 + 结构为核心，不是纯指标金叉死叉
2. 以结构止损为主，不是单纯固定百分比止损
3. 会过滤掉低质量 K 线和不好的压缩结构
4. 做空是主收益引擎，做多是辅助增益

---

## 2. DualTrendRawStrategy

### 角色

这是原始组合版。

它代表的是当前这套 DualTrend 框架，在后续“分强弱出场逻辑”和“坏信号 guard”加进来之前，最干净的一版表达。

### 核心内容

- 包含已经验证过的 `short_pullback_restart` 形态过滤
- 包含现在的多空组合框架
- 包含已经吸收进体系里的全局 daily-center 风格过滤思路
- **不包含** 后面加上的 `reach5` 强弱分流逻辑
- **不包含** `compression flush guard`

### 适合拿来做什么

- 作为“原始入场框架”的参考版本
- 想单独研究 entry 逻辑时先看它
- 想判断后续新增逻辑到底是在增强，还是只是在增加复杂度时，用它做参照

### 怎么理解它

如果你想回答这个问题：

> “当前 DualTrend 组合框架，在没有后续出场分流和坏信号防守之前，最基础的样子是什么？”

那应该先看这个策略。

---

## 3. DualTrendBaselineStrategy

### 角色

这是建立在 `DualTrendRawStrategy` 之上的主基线版本。

它保留了原始的入场框架，但加上了当前这一代最核心的出场决策逻辑。

### 核心内容

它在 `DualTrendRawStrategy` 的基础上，增加了以下几件事：

1. **保本保护**
   - 当利润达到大约 `+2%` 之后，把止损抬到一个小幅保护利润的位置

2. **到达 5% 后的分流判断**
   - 当一笔单子达到大约 `+5%` 时，策略会判断这笔单子是“强单”还是“弱单”

3. **强弱单判别规则**
   - 使用开仓后的 adverse move，也就是“先逆着走了多少”来做分类
   - 如果在到达 `+5%` 之前，逆向波动足够小，就认为这笔单子更强
   - 当前强单阈值大约是 `1.25%`

4. **分流后的处理方式**
   - 强单：继续保留，按正常 `ROI 10%` 路径去跑
   - 弱单：直接退出，不强行去吃完整段行情

### 它为什么存在

这个版本是为了解决一个很实际的问题：

- 很多单子确实能先走出一段盈利
- 但不是所有到过盈利的单子，都值得继续死拿到完整目标位

所以它本质上是在回答：

> “一笔单子已经证明自己方向大致没错之后，能不能把真正强的延续单和普通的弱单分开处理？”

### 怎么理解它

它就是当前这一代策略体系里的“主基线”。

以后如果要测试一个新过滤器、新 guard，或者一个新的坏信号防守条件，通常都应该优先拿它来做对照。

---

## 4. DualTrendGuardStrategy

### 角色

这是当前的主候选版本。

它继承 `DualTrendBaselineStrategy` 的全部内容，然后再额外加了一个比较轻量的坏信号防守。

### 核心内容

它完整保留了 baseline 的所有逻辑：

- 同样的入场框架
- 同样的 `+2%` 保本保护
- 同样的 `+5%` 强弱分流
- 同样的“强单继续拿 / 弱单提前退”的处理方式

在这之上，它只多加了一件事：

### Compression Flush Guard

这个 guard 只作用于：

- `short_compression_breakdown`

它会拒绝那些在入场前就已经显得太“冲过头”的 breakdown 空单，典型特征是：

1. 短周期下跌已经发生得太快
   - 前 `3h` 收益已经太负
   - 前 `6h` 收益已经太负

2. ATR 状态已经偏热
   - `atr_pct_percentile` 已经偏高

### 这个 guard 的直觉

它的核心想法是：

- 有些 breakdown 空单，结构上看起来是对的
- 但实际上在你准备进场之前，价格已经跌得太急太快了
- 这种单子更容易变成假跌破、快速反抽，或者是追空追在末端

所以它实际上是在说：

> “如果这个 breakdown 看起来已经有点跌过头了，那就先别追这笔空。”

### 它为什么重要

从最近的验证结果来看，这个版本的改进主要来自于：

- `short_compression_breakdown`

同时对主要盈利引擎：

- `short_pullback_restart`

伤害很小，甚至基本没伤到。

这正是一个好 guard 应该做到的事情：

- 精准去掉坏信号
- 不破坏主收益来源

---

## 5. 三者的简单对比

| 策略 | 主要用途 | 入场逻辑 | 出场逻辑 | 额外 guard |
|---|---|---|---|---|
| `DualTrendRawStrategy` | 原始组合框架 | 当前多空组合入场 | 共享策略栈里的基础逻辑 | 无 |
| `DualTrendBaselineStrategy` | 当前主基线 | 与 Raw 相同 | `+2%` 保本，`+5%` 强弱分流，弱单提前退出 | 无 |
| `DualTrendGuardStrategy` | 当前最佳候选 | 与 Baseline 相同 | 与 Baseline 相同 | 拒绝过度 flushed 的 `short_compression_breakdown` |

---

## 6. 各自适合在什么场景下看

### 适合看 `DualTrendRawStrategy` 的场景

- 你想先看这套组合框架最原始的样子
- 你想专注研究 entry 逻辑，而不想先被后续分流出场逻辑干扰
- 你想先建立一个更简单的整体心智模型

### 适合看 `DualTrendBaselineStrategy` 的场景

- 你要找“当前真正的基线对照版本”
- 你要测试一个新想法是否真的让主线策略变好
- 你想看 guard 加入之前的主版本

### 适合看 `DualTrendGuardStrategy` 的场景

- 你要看当前主候选
- 你要看最近主要提升来自哪里
- 你要继续做 dry-run 准备或后续稳健性验证

---

## 7. 推荐阅读顺序

如果你以后隔一段时间回来，想最快重新理解这套系统，建议按这个顺序看：

1. `DualTrendRawStrategy`
2. `DualTrendBaselineStrategy`
3. `DualTrendGuardStrategy`

这个顺序也对应它真实的演化路径：

1. 原始框架
2. 基线出场智能
3. 针对坏信号的轻量 guard

---

## 8. 当前阶段的实际结论

目前可以这样理解：

- `DualTrendRawStrategy`：原始参考版
- `DualTrendBaselineStrategy`：当前标准基线版
- `DualTrendGuardStrategy`：当前更强的主候选，也是最值得继续验证的一条主线

如果后面继续做假跌破过滤、坏信号过滤、或者稳健性验证，正常应该比较的是：

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

而不是再回头和早期那些实验分支做主对照。
