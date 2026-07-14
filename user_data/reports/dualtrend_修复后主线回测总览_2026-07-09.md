# DualTrend 修复后主线回测总览

日期：2026-07-09

这份文档只看 `ret_6h` 修复后的最新统一回测结果，方便后面直接给 GPT 做整体评价，不再混入旧版本、旧配置、旧时间窗口的数据。

## 1. 统一测试口径

- 配置文件：
  - `D:\test\ft_userdata\user_data\config.backtest.dualtrend.combined.top50.positive13.max3.json`
- 币池：
  - Positive13
- `max_open_trades = 3`
- `timeframe = 1h`
- `timeframe_detail = 5m`
- 统一对象：
  1. `DualTrendRawStrategy`
  2. `DualTrendBaselineStrategy`
  3. `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

对应汇总 CSV：

- `D:\test\ft_userdata\user_data\analysis\ret6h_recheck_2026-07-09\summary.csv`

## 2. 三条策略怎么理解

### 2.1 `DualTrendRawStrategy`

定位：

- 原始基线
- 保留双顺核心
- 进攻性强
- 防守层最薄

### 2.2 `DualTrendBaselineStrategy`

定位：

- 主基线
- 在 Raw 基础上加保本与 +5% 分流
- 防守比 Raw 明显更厚
- 但收益天花板低一些

### 2.3 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`

定位：

- 当前主候选
- 在 close quality guard、结构 stop、盈利单加仓等层面更完整
- 当前看是收益和稳健性最平衡的一条

## 3. 修复后统一回测结果

### 3.1 总表

| 策略 | 窗口 | Trades | Profit | PF | MaxDD | Winrate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `DualTrendRawStrategy` | 3y | 295 | 199.63% | 2.00 | 7.06% | 34.2% |
| `DualTrendRawStrategy` | 1y | 112 | 51.07% | 1.98 | 7.05% | 38.4% |
| `DualTrendRawStrategy` | pressure | 17 | -4.36% | 0.40 | 6.07% | 17.6% |
| `DualTrendBaselineStrategy` | 3y | 330 | 144.61% | 2.15 | 5.77% | 50.0% |
| `DualTrendBaselineStrategy` | 1y | 131 | 42.40% | 2.34 | 4.84% | 55.0% |
| `DualTrendBaselineStrategy` | pressure | 18 | 1.98% | 1.46 | 2.65% | 38.9% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 3y | 313 | 191.75% | 2.60 | 5.03% | 50.8% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | 1y | 123 | 66.01% | 3.21 | 4.96% | 55.3% |
| `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy` | pressure | 15 | 4.82% | 2.96 | 1.75% | 40.0% |

### 3.2 窗口说明

- `3y`
  - `2023-06-18 -> 2026-06-18`

- `1y`
  - `2025-06-18 -> 2026-06-18`

- `pressure`
  - `2026-03-01 -> 2026-05-31`

## 4. 结果解读

## 4.1 Raw

优点：

- 三年总收益高，`199.63%`
- 原始进攻能力仍然强

缺点：

- 压力期直接转负，`-4.36%`
- PF 掉到 `0.40`
- 回撤也明显更高

解释：

- Raw 适合作为“收益上限参考线”
- 但不适合作为当前实战主线

## 4.2 Baseline

优点：

- 比 Raw 稳
- 压力期能保持正收益
- 胜率显著更高

缺点：

- 三年收益只有 `144.61%`
- 1 年也只有 `42.40%`
- 收益上限偏低

解释：

- Baseline 是一个不错的防守对照组
- 但已经不是当前最优主线

## 4.3 Current Candidate

优点：

- 三年 `191.75%`，接近 Raw
- 一年 `66.01%`，显著强于 Raw 和 Baseline
- 压力期 `4.82%`，明显优于 Raw 和 Baseline
- PF 三个窗口都很好：
  - `2.60`
  - `3.21`
  - `2.96`
- MaxDD 也控制得更漂亮：
  - `5.03%`
  - `4.96%`
  - `1.75%`

缺点：

- 交易数比 Baseline 少一些
- 不是绝对收益最高，但已经非常接近 Raw

解释：

- 这条线不是最激进
- 但综合收益、PF、回撤、压力期表现，明显是三条里最平衡的

## 5. 当前排序

如果只按“当前适合继续作为主线推进”的优先级：

1. `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
2. `DualTrendRawStrategy`
3. `DualTrendBaselineStrategy`

解释：

- 第 1 名是当前主候选，综合最强
- 第 2 名适合作为收益上限参考线
- 第 3 名适合作为稳健防守对照线

## 6. 关于这次 ret_6h 修复

这次修复后，数据已经重新核对过。

核心含义：

- 之前家里跑出 `140%+`，大概率不是市场问题
- 而是 `ret_6h` 没正确生成，导致强单放行逻辑退化

修复后：

- 主线结果回到正常区间
- 当前主候选仍然站得住

## 7. 给 GPT 的一句话版本

如果后面要把这份结果给 GPT 总评，可以直接这样描述：

> 当前 DualTrend 在统一口径下，Raw 是进攻上限参考，Baseline 是防守对照，CloseQualityGuard028PyramidWindow05To15LegBe015 是当前综合最优主候选。ret_6h 修复后，三年/一年/压力期结果已经重新核对，其中主候选在三年 191.75%、一年 66.01%、压力期 4.82%、PF 2.60/3.21/2.96、MaxDD 5.03%/4.96%/1.75%，目前最值得继续推进。
