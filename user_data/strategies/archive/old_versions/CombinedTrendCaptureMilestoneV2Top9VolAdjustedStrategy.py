import pandas as pd

from CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy import (
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy,
)


class CombinedTrendCaptureMilestoneV2Top9VolAdjustedStrategy(
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
):
    """
    Reduce stake on unusually volatile candles.
    This keeps the original signal logic unchanged and only lowers exposure
    when ATR-based hourly volatility is abnormally high.
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
        weighted_stake = super().custom_stake_amount(
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
            return weighted_stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return weighted_stake

        atr_pct = dataframe.iloc[-1].get("atr_pct")
        if pd.isna(atr_pct):
            return weighted_stake

        if atr_pct >= 0.050:
            vol_multiplier = 0.65
        elif atr_pct >= 0.040:
            vol_multiplier = 0.78
        elif atr_pct >= 0.030:
            vol_multiplier = 0.88
        else:
            vol_multiplier = 1.0

        adjusted_stake = weighted_stake * vol_multiplier
        if min_stake is not None:
            adjusted_stake = max(adjusted_stake, min_stake)
        return min(adjusted_stake, max_stake)
