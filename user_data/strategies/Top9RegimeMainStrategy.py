from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy,
)


class Top9RegimeMainStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy
):
    """
    Short alias for the current Top9 main strategy.

    This keeps the full parent chain intact while giving dry-run / backtesting
    a cleaner strategy name to use.
    """

    def leverage(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        """
        Use higher leverage on BTC and ETH so a 20 USDT stake meets Binance's
        futures minimum notional requirements.

        BTC needs a stronger boost to clear the 100 USDT minimum notional at
        the current price and step size.
        ETH can clear its minimum with a much lower leverage, so we keep it
        lower for the minimal-risk test.
        """

        if pair == "BTC/USDT:USDT":
            return min(8.0, max_leverage)
        if pair == "ETH/USDT:USDT":
            return min(2.0, max_leverage)

        return min(1.0, max_leverage)

