# NFI Refactor

这个目录用于把 `NostalgiaForInfinityX7.py` 重构成可维护模块。

原则：

```text
原版 NFI 是参考实现；
重构版必须先追求行为对齐；
不要在 parity 阶段顺手优化；
```

目标模块：

```text
nfi_refactor/
  indicators/
  market_context/
  protections/
  entries/
  exits/
  position/
  modes/
  state/
```

当前优先级：

```text
1. 指标层
2. BTC informative
3. pair informative
4. global protections
5. entry modes
6. exit and position adjustment
```

## 当前状态

第一版已完成：

```text
NFIRefactorStrategy = parity adapter
```

有效 parity 基线：

```text
config.backtest.dynamic.top40.302u.max2.halfyear.balanced.json
timerange 20251016-20260415

NostalgiaForInfinityX7:
61 trades, +580.90%, 0% drawdown

NFIRefactorStrategy:
61 trades, +580.90%, 0% drawdown
```
