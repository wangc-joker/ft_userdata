from CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy import (
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy,
)


class CombinedTrendCaptureMilestoneV2Top9TighterRiskStrategy(
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
):
    """
    Tighten portfolio-level protections without changing entry logic.
    The goal is to reduce prolonged drawdown periods and improve risk-adjusted returns.
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
                "stop_duration_candles": max(18, int(self.stop_guard_duration.value)),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.maxdd_lookback.value),
                "trade_limit": 8,
                "stop_duration_candles": max(30, int(self.maxdd_duration.value)),
                "max_allowed_drawdown": 0.08,
            },
        ]
