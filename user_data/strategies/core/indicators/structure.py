import talib.abstract as ta
from pandas import DataFrame


def populate_structure_indicators(
    dataframe: DataFrame,
    trend_ema_fast: int,
    trend_ema_slow: int,
    center_window: int,
    pullback_window: int,
    restart_window: int,
    triangle_window: int,
    compression_window: int,
    swing_window: int,
    pullback_depth: float,
    breakout_buffer: float,
    compression_limit: float,
    level_tolerance: float,
    level_proximity: float,
    volume_multiplier: float,
) -> DataFrame:
    half_window = max(2, triangle_window // 2)
    typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0

    dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=trend_ema_fast)
    dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=trend_ema_slow)
    dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
    dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
    dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
    dataframe["volume_mean"] = dataframe["volume"].rolling(max(5, triangle_window)).mean()

    dataframe["market_center"] = typical_price.rolling(center_window).mean()
    dataframe["center_up"] = dataframe["market_center"] > dataframe["market_center"].shift(2)
    dataframe["center_down"] = dataframe["market_center"] < dataframe["market_center"].shift(2)

    dataframe["uptrend"] = (
        (dataframe["close"] > dataframe["ema_slow"])
        & (dataframe["ema_fast"] > dataframe["ema_slow"])
        & dataframe["center_up"]
    )
    dataframe["downtrend"] = (
        (dataframe["close"] < dataframe["ema_slow"])
        & (dataframe["ema_fast"] < dataframe["ema_slow"])
        & dataframe["center_down"]
    )

    dataframe["recent_high"] = dataframe["high"].shift(1).rolling(triangle_window).max()
    dataframe["recent_low"] = dataframe["low"].shift(1).rolling(triangle_window).min()
    dataframe["recent_high_short"] = dataframe["high"].shift(1).rolling(half_window).max()
    dataframe["recent_low_short"] = dataframe["low"].shift(1).rolling(half_window).min()
    dataframe["prior_high_short"] = dataframe["high"].shift(half_window + 1).rolling(half_window).max()
    dataframe["prior_low_short"] = dataframe["low"].shift(half_window + 1).rolling(half_window).min()

    dataframe["rising_lows"] = dataframe["recent_low_short"] > dataframe["prior_low_short"]
    dataframe["falling_highs"] = dataframe["recent_high_short"] < dataframe["prior_high_short"]
    dataframe["flat_ceiling"] = (
        (dataframe["recent_high"] - dataframe["recent_high_short"]).abs() / dataframe["close"]
    ) < level_tolerance
    dataframe["flat_floor"] = (
        (dataframe["recent_low_short"] - dataframe["recent_low"]).abs() / dataframe["close"]
    ) < level_tolerance

    dataframe["range_width"] = (
        (
            dataframe["high"].shift(1).rolling(compression_window).max()
            - dataframe["low"].shift(1).rolling(compression_window).min()
        )
        / dataframe["close"]
    )
    dataframe["range_width_prev"] = dataframe["range_width"].shift(max(2, compression_window // 2))
    dataframe["range_tight"] = dataframe["range_width"] < compression_limit
    dataframe["range_contracting"] = dataframe["range_width"] < dataframe["range_width_prev"]
    dataframe["volume_expansion"] = dataframe["volume"] > dataframe["volume_mean"] * volume_multiplier

    dataframe["pullback_low"] = dataframe["low"].shift(1).rolling(pullback_window).min()
    dataframe["pullback_high"] = dataframe["high"].shift(1).rolling(pullback_window).max()
    dataframe["restart_high"] = dataframe["high"].shift(1).rolling(restart_window).max()
    dataframe["restart_low"] = dataframe["low"].shift(1).rolling(restart_window).min()

    dataframe["pullback_seen_long"] = dataframe["pullback_low"] <= (
        dataframe["ema_fast"] * (1 + pullback_depth)
    )
    dataframe["pullback_seen_short"] = dataframe["pullback_high"] >= (
        dataframe["ema_fast"] * (1 - pullback_depth)
    )
    dataframe["structure_intact_long"] = dataframe["pullback_low"] > (
        dataframe["ema_slow"] * (1 - pullback_depth * 2.0)
    )
    dataframe["structure_intact_short"] = dataframe["pullback_high"] < (
        dataframe["ema_slow"] * (1 + pullback_depth * 2.0)
    )

    dataframe["restart_ready_long"] = (
        dataframe["uptrend"]
        & dataframe["pullback_seen_long"]
        & dataframe["structure_intact_long"]
        & (dataframe["close"] > dataframe["ema_fast"])
        & (dataframe["rsi"] > dataframe["rsi"].shift(1))
    )
    dataframe["restart_ready_short"] = (
        dataframe["downtrend"]
        & dataframe["pullback_seen_short"]
        & dataframe["structure_intact_short"]
        & (dataframe["close"] < dataframe["ema_fast"])
        & (dataframe["rsi"] < dataframe["rsi"].shift(1))
    )

    dataframe["near_high_compression"] = (
        dataframe["close"].shift(1) >= dataframe["recent_high"] * (1 - level_proximity)
    )
    dataframe["near_low_compression"] = (
        dataframe["close"].shift(1) <= dataframe["recent_low"] * (1 + level_proximity)
    )
    dataframe["breakout_above_recent"] = (
        (dataframe["close"] > dataframe["recent_high"] * (1 + breakout_buffer))
        & (dataframe["close"].shift(1) <= dataframe["recent_high"].shift(1) * (1 + breakout_buffer))
    )
    dataframe["breakout_below_recent"] = (
        (dataframe["close"] < dataframe["recent_low"] * (1 - breakout_buffer))
        & (dataframe["close"].shift(1) >= dataframe["recent_low"].shift(1) * (1 - breakout_buffer))
    )
    dataframe["ema_slow_slope_up"] = dataframe["ema_slow"] > dataframe["ema_slow"].shift(3)
    dataframe["ema_slow_slope_down"] = dataframe["ema_slow"] < dataframe["ema_slow"].shift(3)
    dataframe["daily_momentum_long"] = (
        dataframe["uptrend"]
        & dataframe["ema_slow_slope_up"]
        & (dataframe["rsi"] > 55)
    )
    dataframe["daily_momentum_short"] = (
        dataframe["downtrend"]
        & dataframe["ema_slow_slope_down"]
        & (dataframe["rsi"] < 45)
    )

    dataframe["triangle_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["rising_lows"]
        & dataframe["flat_ceiling"]
        & dataframe["range_contracting"]
        & dataframe["breakout_above_recent"]
        & dataframe["volume_expansion"]
    )
    dataframe["triangle_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["falling_highs"]
        & dataframe["flat_floor"]
        & dataframe["range_contracting"]
        & dataframe["breakout_below_recent"]
        & dataframe["volume_expansion"]
    )

    dataframe["center_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["center_up"]
        & dataframe["range_contracting"]
        & dataframe["near_high_compression"]
        & (dataframe["market_center"] > dataframe["market_center"].shift(1))
        & dataframe["breakout_above_recent"]
        & (dataframe["close"] > dataframe["market_center"])
        & dataframe["volume_expansion"]
    )
    dataframe["center_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["center_down"]
        & dataframe["range_contracting"]
        & dataframe["near_low_compression"]
        & (dataframe["market_center"] < dataframe["market_center"].shift(1))
        & dataframe["breakout_below_recent"]
        & (dataframe["close"] < dataframe["market_center"])
        & dataframe["volume_expansion"]
    )

    dataframe["compression_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["range_tight"]
        & dataframe["range_contracting"]
        & dataframe["near_high_compression"]
        & dataframe["breakout_above_recent"]
        & dataframe["volume_expansion"]
    )
    dataframe["compression_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["range_tight"]
        & dataframe["range_contracting"]
        & dataframe["near_low_compression"]
        & dataframe["breakout_below_recent"]
        & dataframe["volume_expansion"]
    )

    dataframe["signal_long"] = (
        dataframe["triangle_breakout_long"]
        | dataframe["center_breakout_long"]
        | dataframe["compression_breakout_long"]
    )
    dataframe["signal_short"] = (
        dataframe["triangle_breakout_short"]
        | dataframe["center_breakout_short"]
        | dataframe["compression_breakout_short"]
    )

    dataframe["structure_stop_long"] = dataframe["low"].shift(1).rolling(swing_window).min()
    dataframe["structure_stop_short"] = dataframe["high"].shift(1).rolling(swing_window).max()

    return dataframe
