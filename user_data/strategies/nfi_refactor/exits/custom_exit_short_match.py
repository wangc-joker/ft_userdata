"""Short-side custom-exit mode match predicates."""


def matches_short_normal(strategy, enter_tags):
  return any(c in strategy.short_normal_mode_tags for c in enter_tags)


def matches_short_pump(strategy, enter_tags):
  return any(c in strategy.short_pump_mode_tags for c in enter_tags)


def matches_short_quick(strategy, enter_tags):
  return any(c in strategy.short_quick_mode_tags for c in enter_tags)


def matches_short_rebuy(strategy, enter_tags):
  return all(c in strategy.short_rebuy_mode_tags for c in enter_tags)


def matches_short_high_profit(strategy, enter_tags):
  return any(c in strategy.short_high_profit_mode_tags for c in enter_tags)


def matches_short_rapid(strategy, enter_tags):
  return any(c in strategy.short_rapid_mode_tags for c in enter_tags)


def matches_short_scalp(strategy, enter_tags):
  return all(c in strategy.short_scalp_mode_tags for c in enter_tags) or (
    any(c in strategy.short_scalp_mode_tags for c in enter_tags)
    and all(
      c in (strategy.short_scalp_mode_tags + strategy.short_rebuy_mode_tags + strategy.short_grind_mode_tags) for c in enter_tags
    )
  )


def matches_any_short_mode(strategy, enter_tags):
  return any(
    c
    in (
      strategy.short_normal_mode_tags
      + strategy.short_pump_mode_tags
      + strategy.short_quick_mode_tags
      + strategy.short_rebuy_mode_tags
      + strategy.short_high_profit_mode_tags
      + strategy.short_rapid_mode_tags
      + strategy.short_grind_mode_tags
      + strategy.short_scalp_mode_tags
    )
    for c in enter_tags
  )
