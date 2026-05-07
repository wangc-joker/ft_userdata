# Indicators

迁移目标：

```text
BTC informative indicators
pair informative indicators
base 5m indicators
```

Parity 阶段要求：

```text
先保持列名和原版 NFI 一致；
不要顺手改指标参数；
不要改 fillna / replace 行为；
```

## 已抽取

```text
btc_informative.py
pair_informative.py
base_timeframe.py
pipeline.py
```

原版 NFI 当前对 BTC informative 的实际行为是：

```text
读取 BTC 指定周期 dataframe；
除 date 外，所有列加 btc_ 前缀；
返回给 populate_indicators 合并使用；
```

注意：原文件里 BTC 1d 部分保留了 RSI/EMA 等注释代码，但实际没有启用。

`pair_informative.py` 包含交易对自身的 15m / 1h / 4h / 1d 高周期指标。
当前版本尽量保持原始 NFI 代码形态，以便先验证 parity；后续再把 RSI、布林带、
MFI、CMF、KST、ROC、蜡烛涨跌幅、上下影线等重复计算整理成公共 helper。

`base_timeframe.py` 包含 5m 主周期指标。原版 NFI 把回测年龄过滤和实盘数据可用性
保护也放在这个函数里，当前保持原样迁移；等 parity 稳定后再拆入 `protections`。

`pipeline.py` 包含原版 `populate_indicators` 的总装配流程：合并 BTC informative、
交易对 informative、5m 主周期指标，并生成原版全局保护列。当前保持大函数形态，
下一步再按 `protections` / `modes` 边界继续拆。
