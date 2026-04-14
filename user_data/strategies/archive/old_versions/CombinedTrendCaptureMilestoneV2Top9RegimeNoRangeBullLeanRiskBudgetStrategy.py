from freqtrade.persistence import Trade

from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanRiskBudgetStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Add a mild portfolio risk-budget layer on top of BullLean.

    The goal is not to suppress signals, but to reduce stake when the book is
    already crowded in the same direction / branch / coin cluster.
    """

    major_pairs = {"BTC/USDT:USDT", "ETH/USDT:USDT", "BNB/USDT:USDT", "SOL/USDT:USDT"}
    beta_pairs = {"DOGE/USDT:USDT", "XRP/USDT:USDT", "ADA/USDT:USDT", "TRX/USDT:USDT"}

    @classmethod
    def _pair_bucket(cls, pair: str) -> str:
        if pair in cls.major_pairs:
            return "major"
        if pair in cls.beta_pairs:
            return "beta"
        return "other"

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

        open_trades = [
            trade
            for trade in Trade.get_trades_proxy(is_open=True)
            if trade.open_date_utc and trade.open_date_utc <= current_time
        ]
        if not open_trades:
            return stake

        same_side = [trade for trade in open_trades if trade.trade_direction == side]
        opposite_side = [trade for trade in open_trades if trade.trade_direction != side]
        same_bucket = [
            trade for trade in same_side if self._pair_bucket(trade.pair) == self._pair_bucket(pair)
        ]
        same_tag = [trade for trade in same_side if (trade.enter_tag or "") == (entry_tag or "")]

        multiplier = 1.0

        # Whole-book directional crowding.
        if len(same_side) >= 2:
            multiplier *= 0.82
        elif len(same_side) == 1:
            multiplier *= 0.92

        # Avoid stacking the same style of trade repeatedly.
        if len(same_tag) >= 1:
            multiplier *= 0.90

        # Keep beta-coin clusters from dominating the book.
        if self._pair_bucket(pair) == "beta":
            if len(same_bucket) >= 2:
                multiplier *= 0.82
            elif len(same_bucket) == 1:
                multiplier *= 0.92
        elif self._pair_bucket(pair) == "major" and len(same_bucket) >= 2:
            multiplier *= 0.90

        # If the book already has meaningful same-side exposure and no hedge on,
        # be slightly more conservative on fresh additions.
        if len(same_side) >= 1 and len(opposite_side) == 0:
            multiplier *= 0.94

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
