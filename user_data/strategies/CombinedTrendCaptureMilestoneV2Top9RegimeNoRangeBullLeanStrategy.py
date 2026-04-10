from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy
):
    """
    Mildly more aggressive in bull markets:
    - lift daily long continuation a bit more
    - trim hourly shorts harder when the daily regime is bullish
    """

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

        if not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
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

        multiplier = 1.0
        if entry_tag == "long_1d_center_compression" and bull:
            multiplier *= 1.05
        elif entry_tag == "short_1h_center" and bull:
            multiplier *= 0.88
        elif entry_tag == "short_1d_center_compression" and bear:
            multiplier *= 1.03

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
