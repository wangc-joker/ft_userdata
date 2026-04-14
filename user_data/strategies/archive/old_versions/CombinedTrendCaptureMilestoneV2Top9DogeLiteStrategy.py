from .CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy import (
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy,
)


class CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy(
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
):
    """
    Keep the Top9 universe but trim DOGE exposure.
    DOGE boosts upside, but it also amplifies drawdown spikes.
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

        if pair == "DOGE/USDT:USDT":
            stake *= 0.60

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
