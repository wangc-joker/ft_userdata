from pandas import DataFrame

from Top9RegimeMainStrategy import Top9RegimeMainStrategy
from shared.pair_groups import LONG_REVERSAL_PAIRS_193, SHORT_REVERSAL_PAIRS_193
from signals.reversal import apply_reversal_entry_signals, populate_reversal_indicators


class Top9RegimeMainReversalStrategy(Top9RegimeMainStrategy):
    """
    Fixed 193.48-style reversal extension of the current Top9 main strategy.

    Adds two new branches:
    - long_reversal_breakout: daily selloff exhaustion + 1h high-base breakout
    - short_reversal_breakdown: daily rally exhaustion + 1h low-base breakdown

    This version keeps the long leg on BTC / ETH only and preserves the broader
    short leg that proved more useful in the 193.48 run.
    """

    reversal_tags = {
        "long_reversal_breakout",
        "short_reversal_breakdown",
    }

    # Pair-level gating for the 193.48 fixed version.
    long_reversal_pairs = LONG_REVERSAL_PAIRS_193
    short_reversal_pairs = SHORT_REVERSAL_PAIRS_193

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        return populate_reversal_indicators(dataframe, metadata["pair"])

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return apply_reversal_entry_signals(
            dataframe,
            metadata["pair"],
            self.long_reversal_pairs,
            self.short_reversal_pairs,
        )

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

        if entry_tag == "long_reversal_breakout":
            stake *= 1.15
        elif entry_tag == "short_reversal_breakdown":
            stake *= 1.12

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        if trade.enter_tag == "long_reversal_breakout":
            if current_profit < 0.08:
                return None
        elif trade.enter_tag == "short_reversal_breakdown":
            if current_profit < 0.08:
                return None

        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )
