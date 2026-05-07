"""Grind position-adjustment tag set and matching helpers."""

from nfi_refactor.position.adjustment_context import any_tags_in


def get_long_grind_v2_or_v3_trigger_tags(strategy):
  return (
    strategy.long_normal_mode_tags
    + strategy.long_pump_mode_tags
    + strategy.long_quick_mode_tags
    + strategy.long_high_profit_mode_tags
    + strategy.long_rapid_mode_tags
    + strategy.long_top_coins_mode_tags
    + strategy.long_scalp_mode_tags
  )


def get_long_grind_v2_or_v3_known_tags(strategy):
  return (
    get_long_grind_v2_or_v3_trigger_tags(strategy)
    + strategy.long_rebuy_mode_tags
    + strategy.long_grind_mode_tags
    + strategy.long_btc_mode_tags
  )


def get_short_grind_v2_or_v3_trigger_tags(strategy):
  return (
    strategy.short_normal_mode_tags
    + strategy.short_pump_mode_tags
    + strategy.short_quick_mode_tags
    + strategy.short_high_profit_mode_tags
    + strategy.short_rapid_mode_tags
    + strategy.short_top_coins_mode_tags
    + strategy.short_scalp_mode_tags
  )


def get_short_grind_v2_or_v3_known_tags(strategy):
  return (
    get_short_grind_v2_or_v3_trigger_tags(strategy)
    + strategy.short_rebuy_mode_tags
    + strategy.short_grind_mode_tags
  )


def matches_long_grind_adjustment_v2_or_v3(strategy, enter_tags):
  trigger_tags = get_long_grind_v2_or_v3_trigger_tags(strategy)
  known_tags = get_long_grind_v2_or_v3_known_tags(strategy)
  return any_tags_in(enter_tags, trigger_tags) or not any_tags_in(enter_tags, known_tags)


def matches_short_grind_adjustment_v2_or_v3(strategy, enter_tags):
  trigger_tags = get_short_grind_v2_or_v3_trigger_tags(strategy)
  known_tags = get_short_grind_v2_or_v3_known_tags(strategy)
  return any_tags_in(enter_tags, trigger_tags) or not any_tags_in(enter_tags, known_tags)
