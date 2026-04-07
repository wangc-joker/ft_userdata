from CombinedTrendCaptureMilestoneV1Top8Strategy import CombinedTrendCaptureMilestoneV1Top8Strategy


class CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy(CombinedTrendCaptureMilestoneV1Top8Strategy):
    stake_multipliers = {
        "long_1d_center_compression": 1.35,
        "short_1d_center_compression": 1.15,
        "short_1h_center": 0.80,
    }

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
        multiplier = self.stake_multipliers.get(entry_tag or "", 1.0)
        weighted_stake = proposed_stake * multiplier
        if min_stake is not None:
            weighted_stake = max(weighted_stake, min_stake)
        return min(weighted_stake, max_stake)
