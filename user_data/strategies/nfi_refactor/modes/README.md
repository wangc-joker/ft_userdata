# Modes

迁移目标：

```text
normal
pump
quick
rebuy
high profit
rapid
grind
btc
top coins
scalp
```

模式拆分后，每个模式应该可以单独开关和回测。

## 已抽取

```text
tags.py
coins.py
defaults.py
```

`tags.py` 包含原版 NFI 的 long / short mode tag 分组和模式名称。

`coins.py` 包含 `grind_mode_coins`、`top_coins_mode_coins`、`btc_mode_coins`
等特殊币种集合。后续动态币池逻辑应该优先接入这一层，而不是直接侵入入场逻辑。

`defaults.py` 包含时间周期、启动 K 线数量、期货杠杆默认值、滑点阈值等顶层默认参数。

当前这些模块尚未接入主策略，属于低风险静态抽取。
