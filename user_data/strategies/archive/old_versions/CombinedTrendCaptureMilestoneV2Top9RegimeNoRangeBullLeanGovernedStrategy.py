from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanGovernedStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Pair governance layer:
    - keep the validated BullLean state logic
    - add mild, fixed branch-by-pair weights from long-window observations
    - favor consistently strong pairs, trim historically noisy ones
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

        multiplier = 1.0

        if entry_tag == "long_1d_center_compression":
            if pair in {"BTC/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT", "ZEC/USDT:USDT"}:
                multiplier *= 1.04
            elif pair in {"ADA/USDT:USDT", "TRX/USDT:USDT", "XRP/USDT:USDT"}:
                multiplier *= 0.95
            elif pair == "DOGE/USDT:USDT":
                multiplier *= 0.88

        elif entry_tag == "short_1d_center_compression":
            if pair in {"BTC/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT"}:
                multiplier *= 1.03
            elif pair in {"ETH/USDT:USDT", "XRP/USDT:USDT"}:
                multiplier *= 0.96
            elif pair == "DOGE/USDT:USDT":
                multiplier *= 0.84

        elif entry_tag == "short_1h_center":
            if pair in {"BTC/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT"}:
                multiplier *= 1.02
            elif pair in {"ADA/USDT:USDT", "TRX/USDT:USDT", "ZEC/USDT:USDT"}:
                multiplier *= 0.98
            elif pair in {"ETH/USDT:USDT", "XRP/USDT:USDT"}:
                multiplier *= 0.94
            elif pair == "DOGE/USDT:USDT":
                multiplier *= 0.86

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
