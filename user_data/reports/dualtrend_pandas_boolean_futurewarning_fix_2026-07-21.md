# DualTrend pandas 布尔 FutureWarning 修复

日期：2026-07-21

## 问题

LongMicro 模拟盘在 informative timeframe 合并后的布尔列上出现 pandas FutureWarning：

```text
Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated
```

典型位置包括 `DualTrendMainStrategies.py` 的 `legacy_center_down_1d`、`daily_momentum_long_1d`、`trend_up_4h`，以及 `DualTrendCompressionRestartShortV1Strategy.py` 的 `trend_down_4h`。

警告当下不改变结果，但未来 pandas 版本可能停止把 `object + None` 经 `fillna(False)` 隐式降为普通 bool。

## 修复

两个策略模块增加局部 `_filled_bool()`：

```python
return series.astype("boolean").fillna(default).astype(bool)
```

只替换 informative merge 后可能成为 object dtype 的布尔列。数值指标、参数、tag、止损、仓位和退出逻辑均未修改。未使用全局 `pd.set_option` 隐藏警告。

停止脚本同时将 Docker 已弃用的 `stop --time` 更新为 `stop --timeout`。启动脚本在 Docker daemon 不可用时会自动隐藏启动 Docker Desktop；状态脚本只检查当前容器启动周期的日志。

## 验证

- Python 编译通过。
- 代表性 `object/bool/None/0/1` 输入中，新旧布尔结果完全一致。
- LongMicro 观察容器在 0 持仓下重启，API 返回 `dry_run / running / 13 pairs / max3`。
- 当前启动周期没有来自本地策略文件的 FutureWarning、451、ERROR 或 Traceback。
- Freqtrade 2026.3 内部的 `freqtrade/strategy/strategy_helper.py:109` 也会产生同类 pandas FutureWarning；它不来自 DualTrend 策略。独立观察容器通过模块和消息前缀匹配精确屏蔽该警告，不修改容器内的上游代码，也不启用 pandas 的未来类型行为。
- Positive13/max3 近一年回测仍为 123 笔、`+72.49%`、`+724.90464335 USDT`、MaxDD `4.74%`。
- 与修复前归档按 `pair + open_date + is_short` 对齐：123 个共同键，123 笔在 close date、enter tag、exit reason、order count 和 profit_abs 上完全一致，双方独有交易均为 0。

证据归档：

- 修复前：`user_data/analysis/long_micro_validation_2026-07-20/corrected_positive13_near_year-2026-07-20_05-32-42.zip`
- 修复后：`user_data/analysis/futurewarning_fix_2026-07-21-2026-07-21_01-43-22.zip`

回测仍可能输出 DataFrame fragmentation 的 PerformanceWarning。那是列构建效率问题，与本次 object boolean downcast 警告不同，不应混为策略结果错误。
