from .CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy import (
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy,
)


class CombinedTrendCaptureMilestoneV2Top9BalancedRiskStrategy(
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
):
    """
    A milder risk-control layer than the tighter-risk experiment.
    The intention is to reduce deep drawdowns without suppressing too much upside.
    """

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": max(3, int(self.cooldown_candles.value)),
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": int(self.stop_guard_lookback.value),
                "trade_limit": 2,
                "stop_duration_candles": max(16, int(self.stop_guard_duration.value)),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.maxdd_lookback.value),
                "trade_limit": 9,
                "stop_duration_candles": max(27, int(self.maxdd_duration.value)),
                "max_allowed_drawdown": 0.09,
            },
        ]
