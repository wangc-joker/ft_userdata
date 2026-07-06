# DualTrend Guard 主线前置过滤验证

日期: 2026-07-02

## 1. 目标

回到 `DualTrendGuardStrategy` 主线，只研究 `short_pullback_restart` 的前置过滤。

本轮明确不做：

- 不改退出逻辑
- 不改 ROI / trailing / 保本
- 不动 `short_compression_breakdown`
- 不单独适配某个币种

核心问题只有一个：

> 能不能在入场前拦掉更多假跌破 / 快速反抽坏信号，同时不明显伤害主线总收益？

## 2. 设计思路

前面坏信号诊断里，`short_pullback_restart` 最稳定的坏信号线索主要有两类：

1. `breakdown_depth` 太浅
2. 跌破后离 `4H EMA50` 还太近，容易抽回去

所以这轮只测 3 个“轻 guard”方向：

### Candidate A: 仅浅跌破过滤

- 条件：`breakdown_depth < 0.005`
- 目标：挡掉最浅的一批假跌破

### Candidate B: 浅跌破 + 贴近 4H EMA50

- 条件：
  - `breakdown_depth < 0.005`
  - `distance_to_ema50_4h >= -0.05`
- 目标：只拦“跌破不深、而且离 4H EMA50 还很近”的单

### Candidate C: 更轻的组合版

- 条件：
  - `breakdown_depth < 0.004`
  - `distance_to_ema50_4h >= -0.04`
- 目标：只拦最可疑的一小撮，尽量减少误杀

说明：

- 这些候选只是临时验证分支，回测后没有保留到主策略代码里。
- 当前代码已经回退，主线仍是原始 `DualTrendGuardStrategy`。

## 3. 回测口径

- 配置：
  `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top30.max6.json`
- 周期：`1h + 5m detail`
- 市场：Binance Futures isolated
- 时间窗：`2023-06-18 -> 2026-06-18`

回测结果文件：

- Baseline Guard:
  `backtest-result-2026-07-02_02-20-54.zip`
- Candidate A:
  `backtest-result-2026-07-02_02-19-56.zip`
- Candidate B:
  `backtest-result-2026-07-02_02-20-15.zip`
- Candidate C:
  `backtest-result-2026-07-02_02-28-50.zip`

## 4. 总表

| 策略 | 收益率 | PF | MaxDD | Trades | Winrate |
|---|---:|---:|---:|---:|---:|
| Guard Baseline | 157.61% | 2.0846 | 4.91% | 391 | 47.83% |
| Candidate A: depth `< 0.005` | 126.59% | 2.29 | 未优于基线 | 312 | 50.32% |
| Candidate B: depth `< 0.005` + dist `>= -0.05` | 141.48% | 2.18 | 未优于基线 | 347 | 51.01% |
| Candidate C: depth `< 0.004` + dist `>= -0.04` | 146.78% | 2.14 | 未优于基线 | 368 | 50.54% |

备注：

- 候选版的 PF 和 winrate 都提升了。
- 但 3 个版本的总收益都没有打赢主线。
- 说明方向上确实抓到了一些坏单，但误杀的盈利单仍然偏多。

## 5. Tag 拆解

### Guard Baseline

- `short_pullback_restart`
  - trades: `227`
  - profit: `827.61 USDT`
  - winrate: `51.5%`
- `short_compression_breakdown`
  - trades: `92`
  - profit: `220.97 USDT`
  - winrate: `51.1%`
- `long_1d_center_compression`
  - trades: `72`
  - profit: `527.49 USDT`

### Candidate A

- `short_pullback_restart`
  - trades: `142`
  - profit: `540.55 USDT`
  - winrate: `59.2%`

结论：

- 胜率提升明显
- 但直接砍掉了太多 `short_pullback_restart`
- 这个阈值太重

### Candidate B

- `short_pullback_restart`
  - trades: `178`
  - profit: `661.65 USDT`
  - winrate: `59.0%`

结论：

- 比 Candidate A 温和
- 但仍然比基线少了很多 `short_pullback_restart` 利润

### Candidate C

- `short_pullback_restart`
  - trades: `202`
  - profit: `738.63 USDT`
  - winrate: `56.9%`

结论：

- 三个候选里最接近可用
- 但仍然没有打赢基线 `827.61 USDT`
- 说明“浅跌破 + 靠近 EMA50”这个思路有信息量，但还不够干净

## 6. 这轮说明了什么

### 6.1 正面

`short_pullback_restart` 的坏信号确实有部分可以被前置特征识别：

- 浅跌破
- 跌破后离 4H EMA50 太近

这两条方向不是错的。

### 6.2 负面

即使用比较轻的阈值，当前这类 guard 还是有一个老问题：

- 抓坏单有效
- 但同时也会拦掉一部分后面还能走成利润单的 pullback short

所以它更像是“提高命中率”的工具，还不是“提高长期收益”的工具。

## 7. 结论

本轮不建议升级主线。

继续保持：

- `DualTrendBaselineStrategy`
- `DualTrendGuardStrategy`

其中主候选仍然是：

- `DualTrendGuardStrategy`

## 8. 下一步更值得做什么

如果还继续优化 Guard 主线，优先级建议如下：

1. 不再用单一硬阈值继续砍 `short_pullback_restart`
2. 改做“组合上下文确认”，但仍保持轻量
3. 优先研究这些更可能稳一点的方向：
   - `breakdown_depth` 和 `prev_3h / prev_6h` 的组合
   - `breakdown_depth` 和 BTC 4H 状态的组合
   - 压力期样本里是否存在明显的“反抽前结构特征”

如果目标是当前就落地主线，那本轮最合理的决定就是：

> 不升级，保持当前 `DualTrendGuardStrategy`。

---

## 9. 第二轮：上下文组合过滤验证

在第一轮里，单纯使用：

- 浅跌破
- 浅跌破 + 靠近 `4H EMA50`

虽然能提升命中率，但仍然伤害总收益。

所以第二轮改成更符合“假跌破”直觉的组合过滤：

### Candidate A

只拦这种 `short_pullback_restart`：

- `breakdown_depth <= 0.005`
- `prev_3h_return <= -0.006`
- `prev_6h_return <= -0.010`

也就是：

> 跌破本身不深，但前面 3h/6h 已经砸得比较狠，容易进入“砸完抽回”的坏信号区。

### Candidate B

更轻一点：

- `breakdown_depth <= 0.0045`
- `prev_3h_return <= -0.005`
- `prev_6h_return <= -0.008`

## 10. 第二轮结果

### 三年样本

时间窗：

- `2023-06-18 -> 2026-06-18`

| 策略 | 收益率 | PF | Trades | Winrate |
|---|---:|---:|---:|---:|
| Guard Baseline | 157.61% | 2.0846 | 391 | 47.83% |
| Candidate A | 157.64% | 2.12 | 383 | 47.78% |
| Candidate B | 150.03% | 2.05 | 382 | 47.12% |

观察：

- `Candidate A` 在三年样本里是**微幅胜出**
- 收益率几乎持平，但略高一点
- PF 也高于基线
- `Candidate B` 反而不行

这是第一轮里第一次出现“不是只提高 PF，而是总收益也没掉”的候选。

### 全可用样本

时间窗：

- `2022-11-11 16:00:00 -> 2026-06-30 00:00:00`

对比基线：

| 策略 | 收益率 | PF | Trades | Winrate |
|---|---:|---:|---:|---:|
| Guard Baseline | 187.28% | 2.0583 | 454 | 48.24% |
| Candidate A | 185.97% | 2.09 | 444 | 47.97% |

观察：

- 拉长样本后，`Candidate A` 没能继续打赢基线
- 收益率少了大约 `1.31%`
- PF 仍然略高
- trades 更少

这说明：

- 这条规则不是错的
- 它确实在筛一部分低质量 `short_pullback_restart`
- 但它的优势还不够稳定，没到能替换主线的程度

## 11. 第二轮结论

这轮“组合上下文过滤”比第一轮单阈值方案更接近可用。

尤其是 `Candidate A`：

- 三年窗有效
- 全样本只小幅落后
- 比前一轮那些候选稳得多

但当前结论仍然是：

> 暂不并入主线。

原因很简单：

1. 它没有在更长样本里稳定打赢 `DualTrendGuardStrategy`
2. 优势还不够大，不值得为了这点边际差把主线复杂度加上去

## 12. 这轮留下了什么有价值的线索

当前最值得保留的研究结论不是“直接上新 guard”，而是：

### 对 `short_pullback_restart` 来说，最像坏信号的情形之一是：

- 跌破很浅
- 且入场前 3h/6h 已经下杀过多

这个组合比单独看：

- 仅浅跌破
- 仅靠近 EMA50

更接近真实坏信号。

如果后面还要继续优化 Guard 主线，这条线值得保留为优先研究方向。
