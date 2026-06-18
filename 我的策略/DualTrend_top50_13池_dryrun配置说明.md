# DualTrend Top50 正贡献13池 Dry-run 配置说明

日期: 2026-06-18

## 1. 当前 dry-run 主候选

基于前面的验证，当前主候选为：

- 策略：`DualTrendCombinedShortPullbackShapeV1Strategy`
- 币池：`Positive13`
- 槽位：`max_open_trades = 3`
- 交易模式：`Binance USDT-M futures`
- 保证金模式：`isolated`

## 2. Dry-run 配置文件

配置文件：

- [config.dryrun.dualtrend.combined.top50.positive13.max3.json](D:/test/ft_userdata/user_data/config.dryrun.dualtrend.combined.top50.positive13.max3.json)

## 3. 配置要点

### 3.1 币池

当前固定 13 币：

- `ETH/USDT:USDT`
- `ZEC/USDT:USDT`
- `BTC/USDT:USDT`
- `ADA/USDT:USDT`
- `BNB/USDT:USDT`
- `SOL/USDT:USDT`
- `DOGE/USDT:USDT`
- `XRP/USDT:USDT`
- `TAO/USDT:USDT`
- `SUI/USDT:USDT`
- `PAXG/USDT:USDT`
- `NEAR/USDT:USDT`
- `LINK/USDT:USDT`

### 3.2 核心参数

- `max_open_trades = 3`
- `stake_amount = unlimited`
- `tradable_balance_ratio = 0.99`
- `dry_run_wallet = 1000`
- `enable_protections = true`

### 3.3 API

- `listen_port = 8085`
- `username = freqtrader`

说明：

- 这里刻意没有复用你默认 dry-run 的 `8081`
- 这样不会和你现有其他实例撞端口

## 4. Docker 启动方式

如果用当前这个配置单独启动，建议命令：

```powershell
$env:FREQTRADE_COMMAND='trade'
$env:FREQTRADE_CONFIG='config.dryrun.dualtrend.combined.top50.positive13.max3.json'
$env:FREQTRADE_STRATEGY='DualTrendCombinedShortPullbackShapeV1Strategy'
$env:FREQTRADE_DB_URL='sqlite:////freqtrade/user_data/tradesv3.dualtrend.combined.positive13.dryrun.sqlite'
docker compose up -d
```

查看日志：

```powershell
docker compose logs -f freqtrade
```

停止：

```powershell
docker compose down
```

## 5. 当前建议

这版 dry-run 的定位不是继续调参，而是验证：

1. 实时信号频率是否与回测接近
2. long / short 实盘分布是否自然
3. 满槽时段是否明显增多
4. 实际费用、挂单成交、滑点下的体感是否和回测一致

## 6. 本轮已完成事项

本轮已完成：

1. 生成 `Positive13 + combined + max3` 的独立 dry-run 配置
2. 分配独立 API 端口 `8085`
3. 输出对应 Docker 启动方式
