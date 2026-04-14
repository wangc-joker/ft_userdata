from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanExecutionRankedStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Execution-layer ranking:
    when multiple pairs fire at the same candle, only keep the strongest same-side
    candidates, instead of treating every signal equally.
    """

    entry_top_n = 3

    @staticmethod
    def _entry_score(entry_tag: str | None, candle) -> float:
        if not entry_tag:
            return 0.0

        if entry_tag == "long_1d_center_compression":
            score = 0.0
            score += 2.0 if bool(candle.get("daily_momentum_long_1d", False)) else 0.0
            score += 1.3 if bool(candle.get("ema_slow_slope_up_1d", False)) else 0.0
            score += 1.0 if candle.get("close_1d", 0.0) > candle.get("ema_fast_1d", 0.0) else 0.0
            score += 0.9 if bool(candle.get("breakout_above_recent_1d", False)) else 0.0
            score += 0.8 if bool(candle.get("range_tight_1d", False)) else 0.0
            score += max(0.0, min(1.2, (float(candle.get("rsi_1d", 50.0)) - 55.0) / 12.0))
            return score

        if entry_tag == "short_1d_center_compression":
            score = 0.0
            score += 2.0 if bool(candle.get("daily_momentum_short_1d", False)) else 0.0
            score += 1.3 if bool(candle.get("ema_slow_slope_down_1d", False)) else 0.0
            score += 1.0 if candle.get("close_1d", 0.0) < candle.get("ema_fast_1d", 0.0) else 0.0
            score += 0.9 if bool(candle.get("breakout_below_recent_1d", False)) else 0.0
            score += 0.8 if bool(candle.get("range_tight_1d", False)) else 0.0
            score += max(0.0, min(1.2, (45.0 - float(candle.get("rsi_1d", 50.0))) / 12.0))
            return score

        if entry_tag == "short_1h_center":
            score = 0.0
            score += 1.8 if bool(candle.get("daily_momentum_short_1d", False)) else 0.0
            score += 1.1 if bool(candle.get("ema_slow_slope_down_1d", False)) else 0.0
            score += 0.9 if bool(candle.get("center_down", False)) else 0.0
            score += 0.8 if candle.get("close", 0.0) < candle.get("ema_fast", 0.0) else 0.0
            score += 0.8 if candle.get("close_1d", 0.0) < candle.get("ema_fast_1d", 0.0) else 0.0
            score += 0.7 if bool(candle.get("breakout_below_recent", False)) else 0.0
            score += 0.5 if bool(candle.get("range_contracting", False)) else 0.0
            score += max(0.0, min(1.0, (45.0 - float(candle.get("rsi", 50.0))) / 15.0))
            return score

        return 0.0

    def _same_candle_candidates(self, current_time, side: str):
        candidates: list[tuple[str, str, float]] = []

        for pair in sorted(self.allowed_pairs):
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if dataframe.empty:
                continue

            candle = dataframe.iloc[-1]
            candle_time = candle.get("date")
            if candle_time is None or candle_time != current_time:
                continue

            if side == "long" and int(candle.get("enter_long", 0)) == 1:
                entry_tag = candle.get("enter_tag")
            elif side == "short" and int(candle.get("enter_short", 0)) == 1:
                entry_tag = candle.get("enter_tag")
            else:
                continue

            score = self._entry_score(entry_tag, candle)
            candidates.append((pair, entry_tag, score))

        candidates.sort(key=lambda item: item[2], reverse=True)
        return candidates

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> bool:
        if not self.dp or not entry_tag:
            return True

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return True

        candle = dataframe.iloc[-1]
        candidate_score = self._entry_score(entry_tag, candle)
        candidates = self._same_candle_candidates(current_time, side)
        if len(candidates) <= self.entry_top_n:
            return True

        ranked = [item for item in candidates if item[2] > 0]
        if len(ranked) <= self.entry_top_n:
            return True

        allowed = ranked[: self.entry_top_n]
        return any(item[0] == pair and item[1] == entry_tag for item in allowed) and candidate_score >= allowed[-1][2]
