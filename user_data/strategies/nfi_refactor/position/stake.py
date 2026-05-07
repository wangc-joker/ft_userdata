"""Stake sizing helpers extracted from NostalgiaForInfinityX7."""

from datetime import datetime
from typing import Optional


def custom_stake_amount(
  strategy,
  pair: str,
  current_time: datetime,
  current_rate: float,
  proposed_stake: float,
  min_stake: Optional[float],
  max_stake: float,
  leverage: float,
  entry_tag: Optional[str],
  side: str,
  **kwargs,
) -> float:
  enter_tags = entry_tag.split()
  if side == "long":
    # Rebuy mode
    if all(c in strategy.long_rebuy_mode_tags for c in enter_tags) or (
      any(c in strategy.long_rebuy_mode_tags for c in enter_tags)
      and all(c in (strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags) for c in enter_tags)
    ):
      stake_multiplier = strategy.system_v3_rebuy_mode_stake_multiplier
      stake = proposed_stake * stake_multiplier
      if stake > min_stake:
        return stake
      else:
        return min_stake
    # Rapid mode
    if (strategy.system_name_use == strategy.system_v3_name) and (
      all(c in strategy.long_rapid_mode_tags for c in enter_tags)
      or (
        any(c in strategy.long_rapid_mode_tags for c in enter_tags)
        and all(
          c in (strategy.long_rapid_mode_tags + strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags)
          for c in enter_tags
        )
      )
    ):
      stake_multiplier = (
        strategy.rapid_mode_stake_multiplier_futures[0]
        if strategy.is_futures_mode
        else strategy.rapid_mode_stake_multiplier_spot[0]
      )
      if (proposed_stake * stake_multiplier) > min_stake:
        return proposed_stake * stake_multiplier
      else:
        return min_stake
    # Grind mode
    elif all(c in strategy.long_grind_mode_tags for c in enter_tags):
      for _, item in enumerate(
        strategy.grind_mode_stake_multiplier_futures if strategy.is_futures_mode else strategy.grind_mode_stake_multiplier_spot
      ):
        if (proposed_stake * item) > min_stake:
          stake_multiplier = item
          return proposed_stake * stake_multiplier
    # Btc mode
    elif all(c in strategy.long_btc_mode_tags for c in enter_tags):
      stake_multiplier = (
        strategy.grind_mode_stake_multiplier_futures[0]
        if strategy.is_futures_mode
        else strategy.grind_mode_stake_multiplier_spot[0]
      )
      return proposed_stake * stake_multiplier
    else:
      if strategy.system_name_use == strategy.system_v3_2_name:
        stake_multiplier = strategy.system_v3_2_stake_multiplier
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake
      elif strategy.system_name_use == strategy.system_v3_1_name:
        stake_multiplier = strategy.system_v3_1_stake_multiplier
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake
      else:
        stake_multiplier = (
          strategy.regular_mode_stake_multiplier_futures[0]
          if strategy.is_futures_mode
          else strategy.regular_mode_stake_multiplier_spot[0]
        )
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake
  else:
    # Rebuy mode
    if all(c in strategy.short_rebuy_mode_tags for c in enter_tags) or (
      any(c in strategy.short_rebuy_mode_tags for c in enter_tags)
      and all(c in (strategy.short_rebuy_mode_tags + strategy.short_grind_mode_tags) for c in enter_tags)
    ):
      stake_multiplier = strategy.system_v3_rebuy_mode_stake_multiplier
      stake = proposed_stake * stake_multiplier
      if stake > min_stake:
        return stake
      else:
        return min_stake
    # Grind mode
    elif all(c in strategy.short_grind_mode_tags for c in enter_tags):
      for _, item in enumerate(
        strategy.grind_mode_stake_multiplier_futures if strategy.is_futures_mode else strategy.grind_mode_stake_multiplier_spot
      ):
        if (proposed_stake * item) > min_stake:
          stake_multiplier = item
          return proposed_stake * stake_multiplier
    # Rapid mode
    if (strategy.system_name_use == strategy.system_v3_name) and (
      all(c in strategy.short_rapid_mode_tags for c in enter_tags)
      or (
        any(c in strategy.short_rapid_mode_tags for c in enter_tags)
        and all(
          c in (strategy.short_rapid_mode_tags + strategy.short_rebuy_mode_tags + strategy.short_grind_mode_tags)
          for c in enter_tags
        )
      )
    ):
      stake_multiplier = (
        strategy.rapid_mode_stake_multiplier_futures[0]
        if strategy.is_futures_mode
        else strategy.rapid_mode_stake_multiplier_spot[0]
      )
      if (proposed_stake * stake_multiplier) > min_stake:
        return proposed_stake * stake_multiplier
      else:
        return min_stake
    else:
      if strategy.system_name_use == strategy.system_v3_2_name:
        stake_multiplier = strategy.system_v3_2_stake_multiplier
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake
      elif strategy.system_name_use == strategy.system_v3_1_name:
        stake_multiplier = strategy.system_v3_1_stake_multiplier
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake
      else:
        stake_multiplier = (
          strategy.regular_mode_stake_multiplier_futures[0]
          if strategy.is_futures_mode
          else strategy.regular_mode_stake_multiplier_spot[0]
        )
        if (proposed_stake * stake_multiplier) > min_stake:
          return proposed_stake * stake_multiplier
        else:
          return min_stake

  return proposed_stake

def correct_min_stake(strategy, min_stake: float) -> float:
  if strategy.config["exchange"]["name"] in ["bybit"]:
    if strategy.is_futures_mode:
      if min_stake < 5.0 / strategy.futures_mode_leverage:
        min_stake = 5.0 / strategy.futures_mode_leverage
  return min_stake

