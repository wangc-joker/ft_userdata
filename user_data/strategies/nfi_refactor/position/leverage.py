"""Leverage selection extracted from NostalgiaForInfinityX7."""


def leverage(strategy, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag, side, **kwargs):
    enter_tags = entry_tag.split()
    if all(c in strategy.long_rebuy_mode_tags for c in enter_tags):
        return strategy.futures_mode_leverage_rebuy_mode
    elif all(c in strategy.long_grind_mode_tags for c in enter_tags):
        return strategy.futures_mode_leverage_grind_mode
    return strategy.futures_mode_leverage
