import pandas as pd
from pandas import DataFrame

import talib.abstract as ta

from Top9RegimeMainStrategy import Top9RegimeMainStrategy


class Top9RegimeMainBreakoutProbeStrategy(Top9RegimeMainStrategy):
    """
    Add a dedicated long breakout branch for:
    - prior-high compression
    - upward migration of the trading center
    - final expansion breakout
    """

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0

        dataframe["trade_center_5"] = typical_price.rolling(5).mean()
        dataframe["trade_center_10"] = typical_price.rolling(10).mean()
        dataframe["trade_center_box_6"] = (
            dataframe["high"].rolling(6).max() + dataframe["low"].rolling(6).min()
        ) / 2.0
        dataframe["trade_center_box_prev_6"] = dataframe["trade_center_box_6"].shift(6)
        dataframe["trade_floor_6"] = dataframe["low"].rolling(6).min()
        dataframe["trade_floor_prev_6"] = dataframe["trade_floor_6"].shift(6)

        dataframe["trade_center_shift_up"] = (
            (dataframe["trade_center_5"] > dataframe["trade_center_5"].shift(3))
            & (dataframe["trade_center_10"] > dataframe["trade_center_10"].shift(5))
            & (dataframe["trade_center_box_6"] > dataframe["trade_center_box_prev_6"] * 1.003)
            & (dataframe["trade_floor_6"] > dataframe["trade_floor_prev_6"] * 1.002)
        )

        dataframe["trade_center_4h_proxy"] = typical_price.rolling(16).mean()
        dataframe["trade_center_4h_shift_up"] = (
            dataframe["trade_center_4h_proxy"] > dataframe["trade_center_4h_proxy"].shift(4)
        )

        dataframe["major_high_72"] = dataframe["high"].shift(1).rolling(72).max()
        dataframe["major_high_168"] = dataframe["high"].shift(1).rolling(168).max()
        dataframe["near_major_high"] = (
            dataframe["close"].shift(1) >= dataframe["major_high_168"] * 0.982
        ) | (
            dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.985
        )

        dataframe["compression_range_8"] = (
            dataframe["high"].shift(1).rolling(8).max()
            - dataframe["low"].shift(1).rolling(8).min()
        ) / dataframe["close"]
        dataframe["compression_range_24"] = (
            dataframe["high"].shift(1).rolling(24).max()
            - dataframe["low"].shift(1).rolling(24).min()
        ) / dataframe["close"]
        dataframe["high_base_compression"] = (
            (dataframe["compression_range_8"] < dataframe["compression_range_24"] * 0.72)
            & (dataframe["compression_range_8"] < 0.085)
            & (dataframe["close"].shift(1) > dataframe["trade_center_5"].shift(1))
        )

        dataframe["base_tight"] = (
            dataframe["high"].shift(1).rolling(6).max()
            - dataframe["low"].shift(1).rolling(6).min()
        ) / dataframe["close"] < 0.055

        dataframe["major_breakout"] = (
            (dataframe["high"] > dataframe["major_high_72"] * 1.01)
            & (dataframe["close"] > dataframe["major_high_72"] * 1.008)
            & (dataframe["close"] > dataframe["major_high_168"] * 1.002)
        )

        dataframe["breakout_volume_expansion"] = (
            dataframe["volume"] > dataframe["volume_mean"] * 1.35
        )
        dataframe["bull_body_expansion"] = (
            (dataframe["close"] > dataframe["open"])
            & ((dataframe["close"] - dataframe["open"]) / dataframe["close"] > 0.018)
        )

        dataframe["long_breakout_probe"] = (
            ~dataframe["downtrend_1d"].eq(True)
            & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.98)
            & dataframe["trade_center_shift_up"].eq(True)
            & dataframe["trade_center_4h_shift_up"].eq(True)
            & dataframe["near_major_high"].eq(True)
            & dataframe["high_base_compression"].eq(True)
            & dataframe["base_tight"].eq(True)
            & dataframe["major_breakout"].eq(True)
            & dataframe["breakout_volume_expansion"].eq(True)
            & dataframe["bull_body_expansion"].eq(True)
            & (dataframe["rsi"] > 54)
            & (dataframe["rsi_1d"] > 48)
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        breakout_entry = dataframe["long_breakout_probe"].eq(True)
        dataframe.loc[
            breakout_entry,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_highbase_breakout")

        return dataframe
