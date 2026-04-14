from Top9RegimeMainStrategy import Top9RegimeMainStrategy


class Top9RegimeMainTestLiveStrategy(Top9RegimeMainStrategy):
    """
    Test-live wrapper for the Top9 main strategy.

    This version keeps the current main signal chain intact, but applies
    pair-specific leverage so the 60 USDT test-live account can still trade
    BTC / ETH.
    """

    _pair_leverage = {
        "BTC/USDT:USDT": 8.0,
        "ETH/USDT:USDT": 2.0,
    }

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
        target = self._pair_leverage.get(pair, 1.0)
        return max(1.0, min(target, max_leverage))
