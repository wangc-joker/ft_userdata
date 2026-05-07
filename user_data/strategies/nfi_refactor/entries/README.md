# Entries

迁移目标：

```text
long entry modes
short entry modes
entry tags
mode-specific signal enable flags
```

Parity 阶段必须保持 tag 一致，否则 custom exit / position adjustment 可能失效。

## 已抽取

```text
confirm_entry.py
```

包含原版 `confirm_trade_entry` 以及 grind / top coins / scalp 三个入场确认 helper。
这一层不产生信号，只负责在信号出现后做模式币池、槽位、滑点等最终确认。
