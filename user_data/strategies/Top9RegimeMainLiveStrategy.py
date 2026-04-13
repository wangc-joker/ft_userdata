from CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy,
)


class Top9RegimeMainLiveStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy
):
    """
    Live-test variant of the current Top9 main strategy.

    It keeps the same signal logic as the original main strategy, but adds
    pair-specific leverage so a small 60 USDT futures account can still pass
    minimum notional requirements on BTC / ETH.
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
        if pair == "BTC/USDT:USDT":
            return min(8.0, max_leverage)
        if pair == "ETH/USDT:USDT":
            return min(2.0, max_leverage)
        return 1.0
