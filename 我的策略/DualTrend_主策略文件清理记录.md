# DualTrend 主策略文件清理记录

## 1. 清理目标

本次清理目标：

1. 保留当前主要策略候选；
2. 删除 long / short 验证分支、历史实验策略、旧 NFI / Top9 / Alpha 策略；
3. 删除多余 backtest / dry-run / live 配置；
4. 保证主策略仍可正常被 Freqtrade 加载和回测。

## 2. 当前主策略

当前保留的正式主候选：

```text
DualTrendCombinedGlobalV2Strategy
```

所在文件：

```text
D:/test/ft_userdata/user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
```

主候选含义：

1. long 侧：`long_daily_rsi = 58`
2. short 侧：拒绝 `1d legacy center` 明显向上，且价格在 `legacy_market_center_1d` 上方时继续做空

## 3. 保留的策略文件

当前 `user_data/strategies` 下保留：

```text
DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
DualTrendCombinedLongDailyCenterShortV1Strategy.py
DualTrendCompressionRestartShortV1Strategy.py
core/
README.md
FILE_PLACEMENT_RULES.md
```

说明：

1. `DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py` 是主候选入口；
2. `DualTrendCombinedLongDailyCenterShortV1Strategy.py` 是 combined 基础逻辑依赖；
3. `DualTrendCompressionRestartShortV1Strategy.py` 是 short V1 基础逻辑依赖；
4. `core/indicators/structure.py` 是 long 1D center 结构指标依赖；
5. 其他策略实验文件和历史策略目录已删除。

## 4. 保留的配置文件

当前 `user_data` 根目录下保留：

```text
config.backtest.dualtrend.combined.top40_302u.max3.json
config.json
config.dryrun.json
```

其中主 backtest 配置已更新为：

```text
"strategy": "DualTrendCombinedGlobalV2Strategy"
```

## 5. 删除内容

删除内容概览：

```text
旧策略 / 实验策略文件：20 个
旧策略目录：12 个
多余 json 配置：82 个
```

删除的主要类别：

1. long V1 / false-break / validation 实验策略；
2. short V2 / short filter validation 实验策略；
3. old long daily center / old short legacy borrow 验证策略；
4. NFI / Alpha / Top9 历史策略；
5. `research`、`archive`、`myStrage`、`nfi_refactor` 等历史实验目录；
6. 多余 backtest / dry-run / live 配置文件。

## 6. 验证结果

### 6.1 编译检查

以下文件编译通过：

```text
DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
DualTrendCombinedLongDailyCenterShortV1Strategy.py
DualTrendCompressionRestartShortV1Strategy.py
core/indicators/structure.py
```

### 6.2 Freqtrade 加载测试

使用当前主 backtest 配置执行短区间回测：

```text
2026-01-01 至 2026-02-01
```

策略成功加载：

```text
DualTrendCombinedGlobalV2Strategy
```

测试结果：

```text
Trades: 12
Profit: +123.293U / +12.33%
PF: 5.98
MaxDD: 1.79%
```

说明：

这只是加载与运行验证，不作为策略质量结论。

## 7. 当前环境状态

当前环境已经收敛为：

1. 一个主策略候选；
2. 一份主 backtest 配置；
3. 必要运行依赖；
4. 保留基础 `config.json` / `config.dryrun.json` 作为 Freqtrade 默认配置入口。

后续如果继续优化，建议在新文件中临时新增验证分支，验证结束后再把有效逻辑并回主候选，避免策略目录再次堆积。
