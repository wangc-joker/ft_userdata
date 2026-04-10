from pandas import DataFrame

from Top9RegimeMainExhaustionProbeStrategy import Top9RegimeMainExhaustionProbeStrategy


class Top9RegimeMainExhaustionProbeBaseOnlyStrategy(Top9RegimeMainExhaustionProbeStrategy):
    """
    Breakout probe focused on 1h base maturity only.

    Key ideas:
    - remove the 4h center-lift filter
    - require a longer 1h high-base so the trading center is actually stable
    - require a more meaningful breakout above the prior high
    """

    breakout_core_pairs = {
        "BTC/USDT:USDT",
        "BNB/USDT:USDT",
        "ZEC/USDT:USDT",
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        candle_range = (dataframe["high"] - dataframe["low"]).clip(lower=1e-9)

        dataframe["base_high_12"] = dataframe["high"].shift(1).rolling(12).max()
        dataframe["base_low_12"] = dataframe["low"].shift(1).rolling(12).min()
        dataframe["base_range_12"] = (
            dataframe["base_high_12"] - dataframe["base_low_12"]
        ) / dataframe["close"]
        dataframe["base_center_12"] = (
            dataframe["base_high_12"] + dataframe["base_low_12"]
        ) / 2.0
        dataframe["base_center_12_prev"] = dataframe["base_center_12"].shift(6)
        dataframe["base_floor_12"] = dataframe["low"].shift(1).rolling(12).min()
        dataframe["base_floor_12_prev"] = dataframe["base_floor_12"].shift(6)

        dataframe["mature_high_base"] = (
            (dataframe["base_range_12"] < 0.075)
            & (dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.985)
            & (dataframe["base_center_12"] > dataframe["base_center_12_prev"] * 1.002)
            & (dataframe["base_floor_12"] > dataframe["base_floor_12_prev"] * 1.001)
        )

        dataframe["breakout_close_near_high"] = (
            (dataframe["high"] - dataframe["close"]) / candle_range < 0.28
        )
        dataframe["breakout_body_strength"] = (
            (dataframe["close"] - dataframe["open"]) / dataframe["close"] > 0.022
        )
        dataframe["breakout_distance_ok"] = (
            (dataframe["close"] > dataframe["major_high_72"] * 1.012)
            & (dataframe["high"] > dataframe["major_high_72"] * 1.018)
        )
        dataframe["breakout_daily_bias_ok"] = (
            dataframe["bear_exhaustion_1d"].eq(True)
            | (
                (~dataframe["downtrend_1d"].eq(True))
                & (dataframe["rsi_1d"] > 50)
                & (dataframe["daily_center_lifting"].eq(True))
            )
        )

        dataframe["long_breakout_probe"] = (
            (~dataframe["downtrend_1d"].eq(True) | dataframe["bear_exhaustion_1d"].eq(True))
            & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.98)
            & dataframe["trade_center_shift_up"].eq(True)
            & dataframe["near_major_high"].eq(True)
            & dataframe["high_base_compression"].eq(True)
            & dataframe["base_tight"].eq(True)
            & dataframe["major_breakout"].eq(True)
            & dataframe["breakout_volume_expansion"].eq(True)
            & dataframe["bull_body_expansion"].eq(True)
            & (dataframe["rsi"] > 54)
            & (dataframe["rsi_1d"] > 48)
            & dataframe["mature_high_base"].eq(True)
            & dataframe["breakout_close_near_high"].eq(True)
            & dataframe["breakout_body_strength"].eq(True)
            & dataframe["breakout_distance_ok"].eq(True)
            & dataframe["breakout_daily_bias_ok"].eq(True)
        )

        return dataframe
