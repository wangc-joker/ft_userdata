from entrypoints.top9_reversal_216_opt import Top9RegimeMainReversal216OptStrategy


class Top9RegimeMainReversal216NoLongAggressiveStrategy(
    Top9RegimeMainReversal216OptStrategy
):
    """
    Experimental 216 optimizer.

    Disable the long breakout branch and scale the short-reversal branch a bit
    more aggressively to test whether the historical sample benefits from a
    larger short-reversal allocation.
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
        if entry_tag == "short_reversal_breakdown":
            stake *= 1.5
        return stake
