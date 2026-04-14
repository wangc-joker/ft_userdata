from typing import Optional

from freqtrade.persistence import Trade

from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanEarlyFailStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Add conservative early-failure exits for the two main pain points:
    - long_1d_center_compression when daily structure quickly weakens
    - short_1h_center when hourly short structure is invalidated early
    """

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        base_exit = super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )
        if base_exit:
            return base_exit

        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        candle = dataframe.iloc[-1]
        entry_tag = trade.enter_tag or ""

        if (
            entry_tag == "long_1d_center_compression"
            and not trade.is_short
            and current_profit < -0.006
        ):
            daily_structure_failed = (
                candle.get("close_1d", 0.0) < candle.get("ema_fast_1d", 0.0)
                and bool(candle.get("center_down_1d", False))
                and not bool(candle.get("daily_momentum_long_1d", False))
            )
            hourly_followthrough_failed = (
                candle.get("close", 0.0) < candle.get("ema_fast", 0.0)
                and candle.get("rsi", 50.0) < 48
            )
            if daily_structure_failed and hourly_followthrough_failed:
                return "early_fail_long_1d"

        if (
            entry_tag == "short_1h_center"
            and trade.is_short
            and current_profit < -0.005
        ):
            hourly_structure_failed = (
                candle.get("close", 0.0) > candle.get("ema_fast", 0.0)
                and bool(candle.get("center_up", False))
                and candle.get("rsi", 50.0) > 52
            )
            daily_tailwind_lost = (
                candle.get("close_1d", 0.0) > candle.get("ema_fast_1d", 0.0)
                or not bool(candle.get("daily_momentum_short_1d", False))
            )
            if hourly_structure_failed and daily_tailwind_lost:
                return "early_fail_short_1h"

        return None
