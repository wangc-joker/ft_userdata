# Position

迁移目标：

```text
custom_stake_amount
leverage
adjust_trade_position
rebuy
grind
derisk
```

Parity 阶段仓位行为必须优先保持一致。

## 已抽取

```text
leverage.py
stake.py
```

根据 entry tag 选择默认杠杆、rebuy 杠杆或 grind 杠杆。

`stake.py` 包含原版 `custom_stake_amount` 和 `correct_min_stake`。它根据 entry tag、
long/short 方向、系统版本、现货/合约模式选择首仓下单倍率。
