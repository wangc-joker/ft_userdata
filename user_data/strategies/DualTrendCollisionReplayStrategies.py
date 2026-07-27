from __future__ import annotations

from typing import Optional

from DualTrendMainStrategies import DualTrendPyramidSecondAdd20LongMicroV1Strategy


class DualTrendPyramidSecondAdd20LongMicroCollisionReplayV1Strategy(
    DualTrendPyramidSecondAdd20LongMicroV1Strategy
):
    """Diagnostic alias that removes wallet contention from max-slot replay."""

    collision_replay_stake_amount = 1000.0

    @property
    def protections(self):
        return []

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        validated_stake = super().custom_stake_amount(
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
        if validated_stake <= 0:
            return 0.0

        stake = min(float(max_stake), self.collision_replay_stake_amount)
        if min_stake is not None and stake < float(min_stake):
            return 0.0
        return max(0.0, stake)
