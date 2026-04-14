from DoubleShunStrategy import DoubleShunStrategy


class QuantEdgeStrategy(DoubleShunStrategy):
    """
    Professionalized version of the validated DoubleShun core:
    - keeps the strongest regime / structure logic that already held up on 3 years of data
    - adds portfolio protections to reduce streak damage and drawdown clustering
    - leaves the saved DoubleShun strategy untouched
    """

    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
    }

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 4,
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 48,
                "trade_limit": 2,
                "stop_duration_candles": 12,
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 96,
                "trade_limit": 10,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.10,
            },
        ]
