"""Long-side custom-exit mode match predicates."""


def matches_long_normal(strategy, enter_tags):
  return any(c in strategy.long_normal_mode_tags for c in enter_tags)


def matches_long_pump(strategy, enter_tags):
  return any(c in strategy.long_pump_mode_tags for c in enter_tags)


def matches_long_quick(strategy, enter_tags):
  return any(c in strategy.long_quick_mode_tags for c in enter_tags)


def matches_long_rebuy(strategy, enter_tags):
  return all(c in strategy.long_rebuy_mode_tags for c in enter_tags) or (
    any(c in strategy.long_rebuy_mode_tags for c in enter_tags)
    and all(c in (strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags) for c in enter_tags)
  )


def matches_long_high_profit(strategy, enter_tags):
  return any(c in strategy.long_high_profit_mode_tags for c in enter_tags)


def matches_long_rapid(strategy, enter_tags):
  return all(c in strategy.long_rapid_mode_tags for c in enter_tags) or (
    any(c in strategy.long_rapid_mode_tags for c in enter_tags)
    and all(
      c
      in (
        strategy.long_rapid_mode_tags + strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags + strategy.long_scalp_mode_tags
      )
      for c in enter_tags
    )
  )


def matches_long_grind(strategy, enter_tags):
  return all(c in strategy.long_grind_mode_tags for c in enter_tags)


def matches_long_btc(strategy, enter_tags):
  return all(c in strategy.long_btc_mode_tags for c in enter_tags)


def matches_long_top_coins(strategy, enter_tags):
  return any(c in strategy.long_top_coins_mode_tags for c in enter_tags)


def matches_long_scalp(strategy, enter_tags):
  return all(c in strategy.long_scalp_mode_tags for c in enter_tags) or (
    any(c in strategy.long_scalp_mode_tags for c in enter_tags)
    and all(
      c in (strategy.long_scalp_mode_tags + strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags) for c in enter_tags
    )
  )


def matches_any_long_mode(strategy, enter_tags):
  return any(
    c
    in (
      strategy.long_normal_mode_tags
      + strategy.long_pump_mode_tags
      + strategy.long_quick_mode_tags
      + strategy.long_rebuy_mode_tags
      + strategy.long_high_profit_mode_tags
      + strategy.long_rapid_mode_tags
      + strategy.long_grind_mode_tags
      + strategy.long_btc_mode_tags
      + strategy.long_top_coins_mode_tags
      + strategy.long_scalp_mode_tags
    )
    for c in enter_tags
  )
