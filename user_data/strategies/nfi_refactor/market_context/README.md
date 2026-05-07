# Market Context

迁移目标：

```text
BTC 多周期上下文；
交易对高周期上下文；
市场模式判断；
```

原版 NFI 使用：

```text
BTC 5m / 15m / 1h / 4h / 1d
pair 15m / 1h / 4h / 1d
```

## 已抽取

```text
informative_pairs.py
```

负责构造 Freqtrade 需要预加载的 `(pair, timeframe)` 列表：

```text
当前白名单币种 * pair 高周期
BTC/stake_currency * BTC 多周期
```

如果是 futures / margin，会自动使用 `BTC/USDT:USDT` 这类带结算币后缀的格式。
