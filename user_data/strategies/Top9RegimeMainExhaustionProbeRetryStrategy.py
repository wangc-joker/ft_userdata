from pandas import DataFrame

from Top9RegimeMainExhaustionProbeBaseOnlyStrategy import (
    Top9RegimeMainExhaustionProbeBaseOnlyStrategy,
)


class Top9RegimeMainExhaustionProbeRetryStrategy(
    Top9RegimeMainExhaustionProbeBaseOnlyStrategy
):
    """
    Add a lighter "retry breakout" path:
    - first breakout attempt fails near the prior high
    - price does not collapse and quickly returns to the high-base
    - second breakout is allowed with lower weight
    """

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        dataframe["base_high_10"] = dataframe["high"].shift(1).rolling(10).max()
        dataframe["base_low_10"] = dataframe["low"].shift(1).rolling(10).min()
        dataframe["base_range_10"] = (
            dataframe["base_high_10"] - dataframe["base_low_10"]
        ) / dataframe["close"]
        dataframe["base_center_10"] = (
            dataframe["base_high_10"] + dataframe["base_low_10"]
        ) / 2.0
        dataframe["base_center_10_prev"] = dataframe["base_center_10"].shift(5)
        dataframe["base_floor_10"] = dataframe["low"].shift(1).rolling(10).min()
        dataframe["base_floor_10_prev"] = dataframe["base_floor_10"].shift(5)

        dataframe["mature_high_base"] = (
            (dataframe["base_range_10"] < 0.082)
            & (dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.984)
            & (dataframe["base_center_10"] > dataframe["base_center_10_prev"] * 1.001)
            & (dataframe["base_floor_10"] > dataframe["base_floor_10_prev"] * 0.999)
        )

        dataframe["failed_breakout_candle"] = (
            (dataframe["high"].shift(1) > dataframe["major_high_72"].shift(1) * 1.008)
            & (dataframe["close"].shift(1) < dataframe["major_high_72"].shift(1) * 1.002)
        )
        dataframe["failed_breakout_recent"] = (
            dataframe["failed_breakout_candle"].rolling(8).max().fillna(0).astype(bool)
        )
        dataframe["returned_to_high_base"] = (
            dataframe["close"].shift(1) >= dataframe["major_high_72"] * 0.992
        )

        dataframe["retry_breakout_probe"] = (
            (~dataframe["downtrend_1d"].eq(True) | dataframe["bear_exhaustion_1d"].eq(True))
            & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.98)
            & dataframe["trade_center_shift_up"].eq(True)
            & dataframe["near_major_high"].eq(True)
            & dataframe["mature_high_base"].eq(True)
            & dataframe["failed_breakout_recent"].eq(True)
            & dataframe["returned_to_high_base"].eq(True)
            & dataframe["breakout_close_near_high"].eq(True)
            & dataframe["breakout_body_strength"].eq(True)
            & dataframe["breakout_distance_ok"].eq(True)
            & dataframe["breakout_daily_bias_ok"].eq(True)
            & (dataframe["volume"] > dataframe["volume_mean"] * 1.15)
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        if metadata["pair"] not in self.breakout_core_pairs:
            return dataframe

        retry_entry = dataframe["retry_breakout_probe"].eq(True)
        dataframe.loc[
            retry_entry,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_highbase_retry")

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake,
        max_stake: float,
        leverage: float,
        entry_tag,
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

        if entry_tag == "long_1h_highbase_retry":
            stake *= 0.72
            if min_stake is not None:
                stake = max(stake, min_stake)
            return min(stake, max_stake)

        return stake
