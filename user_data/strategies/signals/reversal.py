from pandas import DataFrame


def populate_reversal_indicators(dataframe: DataFrame, pair: str) -> DataFrame:
    typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
    candle_range = (dataframe["high"] - dataframe["low"]).clip(lower=1e-9)
    volume_mean_20 = dataframe["volume"].shift(1).rolling(20).mean()

    # Long reversal: daily selloff exhaustion -> 1h detach -> high-base breakout.
    daily_major_low_60 = dataframe["low_1d"].shift(1).rolling(60).min()
    daily_recent_pullback_low_20 = dataframe["low_1d"].shift(20).rolling(20).min()

    dataframe["reversal_daily_long_background_ok"] = (
        (dataframe["low_1d"] > daily_major_low_60 * 1.015)
        & (dataframe["low_1d"] > daily_recent_pullback_low_20 * 1.005)
        & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.975)
        & (dataframe["close_1d"] > dataframe["ema_fast_1d"])
        & dataframe["ema_slow_slope_up_1d"].eq(True)
        & (dataframe["rsi_1d"] > 38)
        & (dataframe["rsi_1d"] < 70)
    )

    long_launch_low_24 = dataframe["low"].shift(1).rolling(24).min()
    long_center_5 = typical_price.rolling(5).mean()
    long_center_10 = typical_price.rolling(10).mean()
    dataframe["reversal_long_regime_ok"] = (
        (dataframe["close"] > long_launch_low_24 * 1.008)
        & (long_center_5 > long_center_5.shift(2))
        & (long_center_10 > long_center_10.shift(4))
        & (dataframe["low"].shift(1).rolling(8).min() > long_launch_low_24 * 1.003)
    )

    long_ref_high_72 = dataframe["high"].shift(1).rolling(72).max()
    long_base_high_12 = dataframe["high"].shift(1).rolling(12).max()
    long_base_low_12 = dataframe["low"].shift(1).rolling(12).min()
    long_base_range_pct = (long_base_high_12 - long_base_low_12) / dataframe["close"]
    long_base_center = (long_base_high_12 + long_base_low_12) / 2.0
    long_base_center_prev = long_base_center.shift(6)
    long_base_floor = dataframe["low"].shift(1).rolling(6).min()
    long_base_floor_prev = long_base_floor.shift(6)

    dataframe["reversal_long_reaccumulation_ok"] = (
        (dataframe["close"].shift(1) >= long_ref_high_72 * 0.97)
        & (long_base_range_pct < 0.095)
        & (long_base_center > long_base_center_prev * 1.002)
        & (long_base_floor > long_base_floor_prev * 1.001)
    )

    dataframe["reversal_long_breakout_candle_ok"] = (
        (dataframe["close"] > long_ref_high_72 * 1.012)
        & (dataframe["high"] > long_ref_high_72 * 1.035)
        & (dataframe["volume"] > volume_mean_20 * 1.8)
        & (((dataframe["close"] - dataframe["open"]) / dataframe["close"]) > 0.03)
        & (((dataframe["high"] - dataframe["close"]) / candle_range) < 0.33)
        & (((dataframe["open"] - dataframe["low"]) / candle_range) < 0.20)
        & (dataframe["rsi"] < 94)
    )

    dataframe["reversal_long_risk_filter_ok"] = (
        (dataframe["rsi"] < 94)
        & (dataframe["high"].shift(1) < long_ref_high_72 * 1.02)
    )

    dataframe["reversal_long_breakout"] = (
        dataframe["reversal_daily_long_background_ok"]
        & dataframe["reversal_long_regime_ok"]
        & dataframe["reversal_long_reaccumulation_ok"]
        & dataframe["reversal_long_breakout_candle_ok"]
        & dataframe["reversal_long_risk_filter_ok"]
    )
    dataframe["reversal_long_hold_active"] = (
        dataframe["reversal_long_breakout"]
        .rolling(6, min_periods=1)
        .max()
        .shift(1)
        .fillna(False)
        .astype(bool)
    )

    # Short reversal: daily rally exhaustion -> 1h detach from the top -> low-base breakdown.
    daily_major_high_60 = dataframe["high_1d"].shift(1).rolling(60).max()
    daily_recent_rally_high_20 = dataframe["high_1d"].shift(20).rolling(20).max()

    dataframe["reversal_daily_short_background_ok"] = (
        (dataframe["high_1d"] < daily_major_high_60 * 0.985)
        & (dataframe["high_1d"] < daily_recent_rally_high_20 * 0.995)
        & (dataframe["close_1d"] <= dataframe["ema_slow_1d"] * 1.015)
        & (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        & dataframe["ema_slow_slope_down_1d"].eq(True)
        & (dataframe["rsi_1d"] > 34)
        & (dataframe["rsi_1d"] < 58)
    )

    short_launch_high_24 = dataframe["high"].shift(1).rolling(24).max()
    short_center_5 = typical_price.rolling(5).mean()
    short_center_10 = typical_price.rolling(10).mean()
    dataframe["reversal_short_regime_ok"] = (
        (dataframe["close"] < short_launch_high_24 * 0.98)
        & (short_center_5 < short_center_5.shift(3))
        & (short_center_10 < short_center_10.shift(5))
        & (dataframe["high"].shift(1).rolling(8).max() < short_launch_high_24 * 0.99)
    )

    short_ref_low_72 = dataframe["low"].shift(1).rolling(72).min()
    short_base_high_12 = dataframe["high"].shift(1).rolling(12).max()
    short_base_low_12 = dataframe["low"].shift(1).rolling(12).min()
    short_base_range_pct = (short_base_high_12 - short_base_low_12) / dataframe["close"]
    short_base_center = (short_base_high_12 + short_base_low_12) / 2.0
    short_base_center_prev = short_base_center.shift(6)
    short_base_ceiling = dataframe["high"].shift(1).rolling(6).max()
    short_base_ceiling_prev = short_base_ceiling.shift(6)

    dataframe["reversal_short_redistribution_ok"] = (
        (dataframe["close"].shift(1) <= short_ref_low_72 * 1.03)
        & (short_base_range_pct < 0.10)
        & (short_base_center < short_base_center_prev * 0.997)
        & (short_base_ceiling < short_base_ceiling_prev * 0.999)
    )

    dataframe["reversal_short_breakdown_candle_ok"] = (
        (dataframe["close"] < short_ref_low_72 * 0.992)
        & (dataframe["low"] < short_ref_low_72 * 0.97)
        & (dataframe["volume"] > volume_mean_20 * 1.8)
        & (((dataframe["open"] - dataframe["close"]) / dataframe["close"]) > 0.025)
        & (((dataframe["close"] - dataframe["low"]) / candle_range) < 0.35)
        & (((dataframe["high"] - dataframe["open"]) / candle_range) < 0.25)
        & (dataframe["rsi"] > 6)
    )

    dataframe["reversal_short_risk_filter_ok"] = (
        (dataframe["rsi"] > 6)
        & (dataframe["low"].shift(1) > short_ref_low_72 * 0.98)
    )

    dataframe["reversal_short_breakdown"] = (
        dataframe["reversal_daily_short_background_ok"]
        & dataframe["reversal_short_regime_ok"]
        & dataframe["reversal_short_redistribution_ok"]
        & dataframe["reversal_short_breakdown_candle_ok"]
        & dataframe["reversal_short_risk_filter_ok"]
    )

    if pair == "DOGE/USDT:USDT":
        dataframe["reversal_short_breakdown"] = (
            dataframe["reversal_short_breakdown"]
            & (dataframe["high_1d"] < daily_major_high_60 * 0.982)
            & (dataframe["rsi_1d"] > 40)
            & (dataframe["rsi_1d"] < 54)
            & (dataframe["close"] < short_launch_high_24 * 0.975)
            & (dataframe["high"].shift(1).rolling(8).max() < short_launch_high_24 * 0.985)
            & (dataframe["close"].shift(1) <= short_ref_low_72 * 1.02)
            & (short_base_range_pct < 0.085)
            & (short_base_center < short_base_center_prev * 0.995)
            & (short_base_ceiling < short_base_ceiling_prev * 0.998)
            & (dataframe["low"] < short_ref_low_72 * 0.965)
            & (dataframe["volume"] > volume_mean_20 * 2.0)
            & (((dataframe["open"] - dataframe["close"]) / dataframe["close"]) > 0.03)
            & (((dataframe["close"] - dataframe["low"]) / candle_range) < 0.30)
            & (((dataframe["high"] - dataframe["open"]) / candle_range) < 0.22)
        )

    dataframe["reversal_short_hold_active"] = (
        dataframe["reversal_short_breakdown"]
        .rolling(6, min_periods=1)
        .max()
        .shift(1)
        .fillna(False)
        .astype(bool)
    )

    return dataframe


def apply_reversal_entry_signals(
    dataframe: DataFrame,
    pair: str,
    long_reversal_pairs,
    short_reversal_pairs,
) -> DataFrame:
    long_mask = dataframe["reversal_long_breakout"].fillna(False)
    long_hold_mask = dataframe["reversal_long_hold_active"].fillna(False)
    short_mask = dataframe["reversal_short_breakdown"].fillna(False)
    short_hold_mask = dataframe["reversal_short_hold_active"].fillna(False)

    if pair not in long_reversal_pairs:
        long_mask = long_mask & False
        long_hold_mask = long_hold_mask & False
    if pair not in short_reversal_pairs:
        short_mask = short_mask & False
        short_hold_mask = short_hold_mask & False

    if "enter_short" in dataframe.columns:
        suppress_short = long_mask | long_hold_mask
        dataframe.loc[suppress_short, ["enter_short", "enter_tag"]] = (0, None)

    if "enter_long" in dataframe.columns:
        suppress_long = short_mask | short_hold_mask
        dataframe.loc[suppress_long, ["enter_long", "enter_tag"]] = (0, None)

    dataframe.loc[long_mask, ["enter_long", "enter_tag"]] = (1, "long_reversal_breakout")
    dataframe.loc[long_hold_mask, ["enter_long", "enter_tag"]] = (1, "long_reversal_breakout")
    if "enter_short" in dataframe.columns:
        dataframe.loc[short_mask, ["enter_short", "enter_tag"]] = (1, "short_reversal_breakdown")
        dataframe.loc[short_hold_mask, ["enter_short", "enter_tag"]] = (
            1,
            "short_reversal_breakdown",
        )

    return dataframe
