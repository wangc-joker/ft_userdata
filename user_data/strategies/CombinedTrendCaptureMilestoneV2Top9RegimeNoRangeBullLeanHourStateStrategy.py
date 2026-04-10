from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Only retune the hourly short branch by market regime.

    The yearly breakdown showed `short_1h_center` was:
    - weak in 2022 / 2023
    - neutral in 2025
    - strong in 2024 / 2026

    So this version suppresses it harder in bull/neutral states and
    makes it more selective in bear states where it has historically
    carried more of the result.
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
        if bear:
            multiplier *= 1.06
        elif bull:
            multiplier *= 0.86
        else:
            multiplier *= 0.90

        if pair in {"ADA/USDT:USDT", "XRP/USDT:USDT"}:
            multiplier *= 0.95

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
