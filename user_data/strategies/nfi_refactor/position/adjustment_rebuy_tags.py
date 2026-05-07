"""Rebuy position-adjustment tag matching helpers."""

from nfi_refactor.position.adjustment_context import all_tags_in, any_tags_in


def matches_long_rebuy_adjustment(strategy, enter_tags):
  return all_tags_in(enter_tags, strategy.long_rebuy_mode_tags) or (
    any_tags_in(enter_tags, strategy.long_rebuy_mode_tags)
    and all_tags_in(enter_tags, strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags)
  )


def matches_short_rebuy_adjustment(strategy, enter_tags):
  return all_tags_in(enter_tags, strategy.short_rebuy_mode_tags) or (
    any_tags_in(enter_tags, strategy.short_rebuy_mode_tags)
    and all_tags_in(enter_tags, strategy.short_rebuy_mode_tags + strategy.short_grind_mode_tags)
  )
