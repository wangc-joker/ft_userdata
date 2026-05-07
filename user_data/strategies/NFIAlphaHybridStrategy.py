from NFIRefactorStrategy import NFIRefactorStrategy
from nfi_refactor.alpha_hybrid.reversal216 import (
    LONG_REVERSAL_PAIRS_216,
    REVERSAL_LONG_GRIND_TAGS,
    REVERSAL_SHORT_GRIND_TAGS,
    REVERSAL_SHORT_TAG,
    REVERSAL_TAGS,
    SHORT_REVERSAL_PAIRS_216,
    apply_reversal216_entries,
    populate_reversal216_indicators,
)


class NFIReversal216ShortAggressiveHybridStrategy(NFIRefactorStrategy):
    """NFI management plus the true Reversal216 no-long aggressive entry branch."""

    reversal_tags = REVERSAL_TAGS
    long_reversal_pairs = LONG_REVERSAL_PAIRS_216
    short_reversal_pairs = SHORT_REVERSAL_PAIRS_216
    reversal216_trend_ema_fast = 6
    reversal216_trend_ema_slow = 46
    reversal216_short_stake_multiplier = 1.68

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.long_grind_mode_tags = list(self.long_grind_mode_tags) + REVERSAL_LONG_GRIND_TAGS
        self.short_grind_mode_tags = list(self.short_grind_mode_tags) + REVERSAL_SHORT_GRIND_TAGS

    def version(self) -> str:
        return "nfi-reversal216-short-aggressive-hybrid-0.1.0"

    def populate_indicators(self, df, metadata: dict):
        df = super().populate_indicators(df, metadata)
        return populate_reversal216_indicators(self, df, metadata)

    def populate_entry_trend(self, df, metadata: dict):
        df = super().populate_entry_trend(df, metadata)
        return apply_reversal216_entries(
            df,
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
        if entry_tag == REVERSAL_SHORT_TAG:
            stake *= self.reversal216_short_stake_multiplier
        return stake

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        if trade.enter_tag in self.reversal_tags and current_profit < 0.08:
            return None

        return super().custom_exit(
            pair,
            trade,
            current_time,
            current_rate,
            current_profit,
            **kwargs,
        )
