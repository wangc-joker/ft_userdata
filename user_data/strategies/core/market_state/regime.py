from freqtrade.persistence import Trade


def classify_daily_regime(dataframe):
    bull = (
        (dataframe["close_1d"] > dataframe["ema_fast_1d"])
        & (dataframe["ema_fast_1d"] > dataframe["ema_slow_1d"])
        & (dataframe["rsi_1d"] >= 57)
        & dataframe["ema_slow_slope_up_1d"].eq(True)
    )
    bear = (
        (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        & (dataframe["ema_fast_1d"] < dataframe["ema_slow_1d"])
        & (dataframe["rsi_1d"] <= 45)
        & dataframe["ema_slow_slope_down_1d"].eq(True)
    )
    ranging = ~(bull | bear)
    return bull, bear, ranging


def classify_intraday_regime(candle):
    bull = (
        candle.get("close_1d", 0) > candle.get("ema_fast_1d", 0) > candle.get("ema_slow_1d", 0)
        and candle.get("rsi_1d", 50) >= 57
        and bool(candle.get("ema_slow_slope_up_1d", False))
    )
    bear = (
        candle.get("close_1d", 0) < candle.get("ema_fast_1d", 0) < candle.get("ema_slow_1d", 0)
        and candle.get("rsi_1d", 50) <= 45
        and bool(candle.get("ema_slow_slope_down_1d", False))
    )
    ranging = not (bull or bear)
    return bull, bear, ranging


def recent_trade_multiplier(current_time, entry_tag: str | None, pair: str) -> float:
    if not entry_tag:
        return 1.0

    closed = [
        trade
        for trade in Trade.get_trades_proxy(is_open=False)
        if trade.close_date_utc
        and trade.close_date_utc <= current_time
        and (trade.enter_tag or "") == entry_tag
    ]
    closed.sort(key=lambda trade: trade.close_date_utc, reverse=True)
    recent_tag = closed[:6]

    multiplier = 1.0
    if len(recent_tag) >= 4:
        tag_profit = sum((trade.close_profit or 0.0) for trade in recent_tag)
        tag_losses = sum(1 for trade in recent_tag if (trade.close_profit or 0.0) <= 0)
        if tag_profit < -0.04:
            multiplier *= 0.74
        elif tag_profit < -0.015 or tag_losses >= 5:
            multiplier *= 0.84
        elif tag_profit < 0:
            multiplier *= 0.92

    same_pair = [trade for trade in recent_tag if trade.pair == pair][:4]
    if len(same_pair) >= 3:
        pair_profit = sum((trade.close_profit or 0.0) for trade in same_pair)
        if pair_profit < -0.03:
            multiplier *= 0.82
        elif pair_profit < 0:
            multiplier *= 0.92

    return multiplier
