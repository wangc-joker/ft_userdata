# Exits

迁移目标：

```text
custom_exit
profit target cache
stoploss modes
derisk exits
grind exits
```

NFI 的收益很大程度来自退出和仓位管理，不能只迁移入场。

## 已抽取

```text
custom_exit.py
```

包含原版 `custom_exit` 编排层。它根据 entry tag 把交易路由到 normal / pump /
quick / rebuy / rapid / grind / top coins / scalp / short 等具体退出函数，并保持原版
exit reason 文本。
