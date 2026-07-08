# DualTrend 当前状态 2026-07-07

## 当前保留的策略主线

### 1. 基线参考

- 文件：`user_data/strategies/DualTrendMainStrategies.py`
- 策略名：`DualTrendRawStrategy`

用途：

- 作为最原始的当前 DualTrend 组合基线参考
- 保留双顺核心，不带后续 guard / reach5 / structured stop 的增强

### 2. 当前 short 主候选

- 文件：`user_data/strategies/DualTrendMainStrategies.py`
- 策略名：`DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`

当前定位：

- 这是目前最值得继续推进的 short 主候选
- 它是在 `Guard028` 基础上，只对 `short_compression_breakdown` 做了更紧的结构止损

截至目前三年核心结果：

- `319 trades`
- `+162.46%`
- `PF 2.44`
- `MaxDD 5.05%`
- `Winrate 53.3%`

它已经验证过：

1. 三年优于 `Guard028`
2. 近一年不恶化
3. 压力期不恶化
4. 比若干提前止盈 / 结构止盈候选更稳

### 3. 结构基础文件

- `user_data/strategies/DualTrendCompressionRestartShortV1Strategy.py`
- `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1Strategy.py`
- `user_data/strategies/core/`

用途：

- 作为当前主文件依赖的短线结构基础、长短组合基础、以及共用模块

### 4. 兼容入口

- `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py`

用途：

- 只做兼容导出
- 旧引用不至于直接失效
- 新工作统一以 `DualTrendMainStrategies.py` 为主

## 当前保留的核心报告

### 策略总览

- `user_data/reports/dualtrend_5y_strategy_overview_2026-07-03.md`
- `user_data/reports/dualtrend_strategy_quick_guide_2026-07-01.md`
- `user_data/reports/strategy_file_map_2026-07-01.md`
- `user_data/reports/cleanup_2026-07-01.md`

### 当前主线相关

- `user_data/reports/dualtrend_guard028_structured_stop_research_2026-07-06.md`
- `user_data/reports/dualtrend_guard028_compression_tight_reach5_refine_2026-07-07.md`
- `user_data/reports/dualtrend_position_management_plan_2026-07-06.md`

### 当前状态汇总

- `user_data/reports/dualtrend_current_state_2026-07-07.md`

## 已确认不继续推进的方向

以下方向已经做过验证，但目前不优于主线：

1. 全局结构止盈
2. 提前 partial / 提前 trail 的止盈候选
3. 盈利后结构失败退出
4. 用更纯的 adverse-only 规则替代 current 的 reach5 结构放行
5. 继续在 current reach5 上做很小的阈值松紧微调

## 下一步研究主题

下一步改为研究：

- **盈利单加仓**

建议约束：

1. 不改核心入场
2. 不先动 pair pool
3. 不先动 `max_open_trades`
4. 只研究：
   - 哪些已经盈利并证明方向正确的单子值得加仓
   - 加仓后是否会提升收益而不明显放大回撤
