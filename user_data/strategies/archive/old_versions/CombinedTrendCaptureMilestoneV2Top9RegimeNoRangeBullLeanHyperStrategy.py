from freqtrade.strategy import BooleanParameter, DecimalParameter, IntParameter

from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHyperStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy
):
    """
    Narrow hyperopt wrapper around the proven BullLean logic.
    Freeze the validated base parameters and only tune the small number of
    regime / DOGE weight adjustments that have a realistic chance to improve
    the current system.
    """

    enable_long_1h_triangle = BooleanParameter(default=True, space="buy", optimize=False)
    enable_long_1d_triangle = BooleanParameter(default=True, space="buy", optimize=False)
    enable_long_1d_center = BooleanParameter(default=True, space="buy", optimize=False)
    enable_short_1h_center = BooleanParameter(default=True, space="buy", optimize=False)
    enable_short_1h_compression = BooleanParameter(default=True, space="buy", optimize=False)
    enable_short_1d_triangle = BooleanParameter(default=False, space="buy", optimize=False)
    enable_short_1d_center = BooleanParameter(default=True, space="buy", optimize=False)

    trend_ema_fast = IntParameter(5, 20, default=6, space="buy", optimize=False)
    trend_ema_slow = IntParameter(20, 80, default=46, space="buy", optimize=False)
    center_window = IntParameter(4, 12, default=5, space="buy", optimize=False)
    pullback_window = IntParameter(3, 8, default=6, space="buy", optimize=False)
    restart_window = IntParameter(2, 6, default=4, space="buy", optimize=False)
    triangle_window = IntParameter(4, 12, default=5, space="buy", optimize=False)
    compression_window = IntParameter(4, 12, default=11, space="buy", optimize=False)
    pullback_depth = DecimalParameter(0.002, 0.025, default=0.009, decimals=3, space="buy", optimize=False)
    breakout_buffer = DecimalParameter(0.001, 0.012, default=0.009, decimals=3, space="buy", optimize=False)
    compression_limit = DecimalParameter(0.006, 0.040, default=0.006, decimals=3, space="buy", optimize=False)
    level_tolerance = DecimalParameter(0.002, 0.020, default=0.016, decimals=3, space="buy", optimize=False)
    level_proximity = DecimalParameter(0.002, 0.020, default=0.015, decimals=3, space="buy", optimize=False)
    volume_multiplier = DecimalParameter(1.00, 2.20, default=1.13, decimals=2, space="buy", optimize=False)
    hourly_long_rsi = IntParameter(48, 62, default=54, space="buy", optimize=False)
    daily_long_rsi = IntParameter(50, 65, default=55, space="buy", optimize=False)
    daily_short_rsi = IntParameter(35, 50, default=46, space="buy", optimize=False)

    swing_window = IntParameter(2, 8, default=3, space="sell", optimize=False)
    cooldown_candles = IntParameter(2, 8, default=2, space="protection", optimize=False)
    stop_guard_lookback = IntParameter(24, 72, default=67, space="protection", optimize=False)
    stop_guard_duration = IntParameter(6, 18, default=16, space="protection", optimize=False)
    maxdd_lookback = IntParameter(48, 144, default=65, space="protection", optimize=False)
    maxdd_duration = IntParameter(12, 36, default=27, space="protection", optimize=False)

    bull_long_boost = DecimalParameter(1.00, 1.10, default=1.05, decimals=2, space="buy", optimize=True)
    bull_short_trim = DecimalParameter(0.82, 0.95, default=0.88, decimals=2, space="buy", optimize=True)
    bear_daily_short_boost = DecimalParameter(1.00, 1.08, default=1.03, decimals=2, space="buy", optimize=True)
    doge_risk_weight = DecimalParameter(0.45, 0.75, default=0.60, decimals=2, space="buy", optimize=True)

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

        if not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        bull = (
            candle.get("close_1d", 0) > candle.get("ema_fast_1d", 0) > candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) >= 57
            and bool(candle.get("ema_slow_slope_up_1d", False))
        )
        bear = (
            candle.get("close_1d", 0) < candle.get("ema_fast_1d", 0) < candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) <= 45
            and bool(candle.get("ema_slow_slope_down_1d", False))
        )

        multiplier = 1.0
        if entry_tag == "long_1d_center_compression" and bull:
            multiplier *= float(self.bull_long_boost.value)
        elif entry_tag == "short_1h_center" and bull:
            multiplier *= float(self.bull_short_trim.value)
        elif entry_tag == "short_1d_center_compression" and bear:
            multiplier *= float(self.bear_daily_short_boost.value)

        if pair == "DOGE/USDT:USDT":
            multiplier *= float(self.doge_risk_weight.value)

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
