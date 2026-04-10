from pandas import DataFrame

from Top9RegimeMainExhaustionProbeStrategy import Top9RegimeMainExhaustionProbeStrategy


class Top9RegimeMainExhaustionProbeStrictStrategy(Top9RegimeMainExhaustionProbeStrategy):
    """
    Narrow the exhaustion-breakout branch to reduce false positives:
    - focus on pairs that behave more like ZEC/BTC/BNB exhaustion breakouts
    - require stronger 4h center lift
    - require a decisive breakout candle that closes near the high
    - require a cleaner high-base before the breakout
    """

    breakout_core_pairs = {
        "BTC/USDT:USDT",
        "BNB/USDT:USDT",
        "ZEC/USDT:USDT",
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        candle_range = (dataframe["high"] - dataframe["low"]).clip(lower=1e-9)
        dataframe["breakout_close_near_high"] = (
            (dataframe["high"] - dataframe["close"]) / candle_range < 0.22
        )
        dataframe["breakout_body_strength"] = (
            (dataframe["close"] - dataframe["open"]) / dataframe["close"] > 0.024
        )
        dataframe["breakout_4h_shift_strong"] = (
            dataframe["trade_center_4h_proxy"] > dataframe["trade_center_4h_proxy"].shift(6) * 1.01
        )
        dataframe["breakout_base_clean"] = (
            dataframe["compression_range_8"] < 0.055
        ) & (
            dataframe["trade_floor_6"] > dataframe["trade_floor_prev_6"] * 1.004
        )
        dataframe["breakout_daily_bias_ok"] = (
            dataframe["bear_exhaustion_1d"].eq(True)
            | (
                (~dataframe["downtrend_1d"].eq(True))
                & (dataframe["rsi_1d"] > 52)
                & (dataframe["daily_center_lifting"].eq(True))
            )
        )

        dataframe["long_breakout_probe"] = (
            dataframe["long_breakout_probe"].eq(True)
            & dataframe["breakout_close_near_high"].eq(True)
            & dataframe["breakout_body_strength"].eq(True)
            & dataframe["breakout_4h_shift_strong"].eq(True)
            & dataframe["breakout_base_clean"].eq(True)
            & dataframe["breakout_daily_bias_ok"].eq(True)
        )

        return dataframe
