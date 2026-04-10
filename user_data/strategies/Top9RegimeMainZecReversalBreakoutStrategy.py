import talib.abstract as ta
from pandas import DataFrame

from Top9RegimeMainStrategy import Top9RegimeMainStrategy


class Top9RegimeMainZecReversalBreakoutStrategy(Top9RegimeMainStrategy):
    """
    Main-strategy test branch:
    keep the official Top9 main logic intact, and add a single ZEC-only
    reversal-breakout path for the April 2026 style setup.
    """

    reversal_breakout_pairs = {"ZEC/USDT:USDT"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        candle_range = (dataframe["high"] - dataframe["low"]).clip(lower=1e-9)
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

        dataframe["major_high_72"] = dataframe["high"].shift(1).rolling(72).max()
        dataframe["major_high_168"] = dataframe["high"].shift(1).rolling(168).max()
        dataframe["near_major_high"] = (
            (dataframe["close"].shift(1) >= dataframe["major_high_168"] * 0.982)
            | (dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.985)
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
            (dataframe["compression_range_8"] < dataframe["compression_range_24"] * 0.78)
            & (dataframe["compression_range_8"] < 0.09)
            & (dataframe["close"].shift(1) > dataframe["trade_center_5"].shift(1))
        )

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
        dataframe["base_tight"] = dataframe["base_range_12"] < 0.08
        dataframe["mature_high_base"] = (
            dataframe["base_tight"]
            & (dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.985)
            & (dataframe["base_center_12"] > dataframe["base_center_12_prev"] * 1.002)
            & (dataframe["base_floor_12"] > dataframe["base_floor_12_prev"] * 1.001)
        )

        dataframe["launch_low_24"] = dataframe["low"].shift(1).rolling(24).min()
        dataframe["detached_from_bottom"] = (
            dataframe["close"].shift(1) > dataframe["launch_low_24"] * 1.05
        )
        dataframe["secondary_pullback_hold"] = (
            dataframe["base_floor_12"] > dataframe["launch_low_24"] * 1.03
        )

        dataframe["daily_low_7"] = dataframe["low_1d"].rolling(7).min()
        dataframe["daily_low_prev_7"] = dataframe["daily_low_7"].shift(7)
        dataframe["daily_center_5"] = (
            (dataframe["high_1d"] + dataframe["low_1d"] + dataframe["close_1d"]) / 3.0
        ).rolling(5).mean()
        dataframe["daily_center_prev_5"] = dataframe["daily_center_5"].shift(5)
        dataframe["daily_not_making_new_lows"] = (
            dataframe["daily_low_7"] >= dataframe["daily_low_prev_7"] * 0.995
        )
        dataframe["daily_not_breaking_down"] = (
            dataframe["close_1d"] >= dataframe["daily_low_7"] * 1.01
        )
        dataframe["daily_center_lifting"] = (
            dataframe["daily_center_5"] > dataframe["daily_center_prev_5"] * 1.006
        )
        dataframe["daily_bounce_from_low"] = (
            dataframe["close_1d"] >= dataframe["daily_low_7"] * 1.025
        )
        dataframe["daily_reversal_background_ok"] = (
            dataframe["daily_not_making_new_lows"].eq(True)
            & dataframe["daily_not_breaking_down"].eq(True)
            & (
                dataframe["daily_center_lifting"].eq(True)
                | dataframe["daily_bounce_from_low"].eq(True)
            )
            & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.985)
            & (dataframe["rsi_1d"] > 50)
            & (dataframe["rsi_1d"] < 68)
            & ~dataframe["downtrend_1d"].eq(True)
        )

        dataframe["strong_breakout"] = (
            (dataframe["close"] > dataframe["major_high_72"] * 1.03)
            & (dataframe["high"] > dataframe["major_high_72"] * 1.08)
        )
        dataframe["explosive_volume_ok"] = (
            dataframe["volume"] > dataframe["volume"].shift(1).rolling(20).mean() * 2.5
        )
        dataframe["explosive_body_ok"] = (
            (dataframe["close"] > dataframe["open"])
            & ((dataframe["close"] - dataframe["open"]) / dataframe["close"] > 0.05)
        )
        dataframe["close_near_high_ok"] = (
            (dataframe["high"] - dataframe["close"]) / candle_range < 0.28
        )
        dataframe["lower_wick_ok"] = (
            (dataframe["open"] - dataframe["low"]) / candle_range < 0.20
        )
        dataframe["hourly_not_overextended"] = dataframe["rsi"] < 92
        dataframe["volume_mean_20_local"] = dataframe["volume"].shift(1).rolling(20).mean()

        dataframe["long_zec_reversal_breakout"] = (
            dataframe["daily_reversal_background_ok"].eq(True)
            & dataframe["trade_center_shift_up"].eq(True)
            & dataframe["detached_from_bottom"].eq(True)
            & dataframe["secondary_pullback_hold"].eq(True)
            & dataframe["near_major_high"].eq(True)
            & dataframe["high_base_compression"].eq(True)
            & dataframe["mature_high_base"].eq(True)
            & dataframe["strong_breakout"].eq(True)
            & dataframe["explosive_volume_ok"].eq(True)
            & dataframe["explosive_body_ok"].eq(True)
            & dataframe["close_near_high_ok"].eq(True)
            & dataframe["lower_wick_ok"].eq(True)
            & dataframe["hourly_not_overextended"].eq(True)
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        if metadata["pair"] not in self.reversal_breakout_pairs:
            return dataframe

        breakout_entry = dataframe["long_zec_reversal_breakout"].eq(True)
        dataframe.loc[
            breakout_entry,
            ["enter_long", "enter_tag"],
        ] = (1, "long_zec_reversal_breakout")

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if entry_tag == "long_zec_reversal_breakout":
            stake *= 0.92
            if min_stake is not None:
                stake = max(stake, min_stake)
            return min(stake, max_stake)

        return stake
