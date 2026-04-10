from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy
):
    """
    Keep the regime-aware hourly short sizing, then add small pair-specific trims
    for the weaker hourly short names.

    Goal:
    - preserve BTC / SOL / BNB / ZEC hourly-short upside
    - reduce noise from ADA / XRP / DOGE when the market state is not clearly bearish
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

        if entry_tag != "short_1h_center" or not self.dp:
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
        if pair == "DOGE/USDT:USDT":
            multiplier *= 0.88 if bear else 0.78
        elif pair == "XRP/USDT:USDT":
            multiplier *= 0.95 if bear else 0.86
        elif pair == "ADA/USDT:USDT":
            multiplier *= 0.96 if bear else 0.88

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
