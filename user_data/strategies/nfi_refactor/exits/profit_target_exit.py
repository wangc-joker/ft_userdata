from __future__ import annotations

"""Profit target exit decision helper extracted from NFI."""

from datetime import timedelta

def exit_profit_target(
  strategy,
  mode_name: str,
  pair: str,
  trade: Trade,
  current_time: datetime,
  current_rate: float,
  profit_stake: float,
  profit_ratio: float,
  profit_current_stake_ratio: float,
  profit_init_ratio: float,
  last_candle,
  previous_candle_1,
  previous_rate,
  previous_profit,
  previous_sell_reason,
  previous_time_profit_reached,
  enter_tags,
) -> tuple:
  is_backtest = strategy.is_backtest_mode()
  is_system_v3 = strategy.is_system_v3(trade)
  is_system_v3_1 = strategy.is_system_v3_1(trade)
  is_system_v3_2 = strategy.is_system_v3_2(trade)
  is_derisk = False
  if previous_sell_reason in [
    f"exit_{mode_name}_stoploss_doom",
    f"exit_{mode_name}_stoploss",
    f"exit_{mode_name}_stoploss_u_e",
  ]:
    filled_entries = trade.select_filled_orders(trade.entry_side)
    filled_exits = trade.select_filled_orders(trade.exit_side)
    has_order_tags = False
    if hasattr(filled_entries[0], "ft_order_tag"):
      has_order_tags = True
    for order in filled_exits:
      order_tag = ""
      if has_order_tags:
        if order.ft_order_tag is not None:
          sell_order_tag = order.ft_order_tag
          order_mode = sell_order_tag.split(" ", 1)
          if len(order_mode) > 0:
            order_tag = order_mode[0]
      if order_tag in ["d", "d1", "derisk_level_1", "derisk_level_2", "derisk_level_3"]:
        is_derisk = True
        break
    if not is_derisk:
      is_derisk = trade.amount < (filled_entries[0].safe_filled * 0.95)
  if previous_sell_reason in [f"exit_{mode_name}_stoploss_doom", f"exit_{mode_name}_stoploss"]:
    # return right away for system v3
    if is_system_v3 or is_system_v3_1 or is_system_v3_2:
      return True, previous_sell_reason

    is_rapid_mode = all(c in strategy.long_rapid_mode_tags for c in enter_tags)
    is_rebuy_mode = all(c in strategy.long_rebuy_mode_tags for c in enter_tags) or (
      any(c in strategy.long_rebuy_mode_tags for c in enter_tags)
      and all(c in (strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags) for c in enter_tags)
    )
    is_scalp_mode = all(c in strategy.long_scalp_mode_tags for c in enter_tags) or (
      any(c in strategy.long_scalp_mode_tags for c in enter_tags)
      and all(
        c in (strategy.long_scalp_mode_tags + strategy.long_rebuy_mode_tags + strategy.long_grind_mode_tags) for c in enter_tags
      )
    )
    if profit_init_ratio > 0.0:
      # profit is over the threshold, don't exit
      strategy._remove_profit_target(pair)
      return False, None
    elif is_derisk:
      strategy._remove_profit_target(pair)
      return False, None
    elif strategy.derisk_enable and (current_time - timedelta(minutes=60) > previous_time_profit_reached):
      if profit_ratio < previous_profit:
        return True, previous_sell_reason
      elif profit_ratio > previous_profit:
        strategy._remove_profit_target(pair)
        return False, None
    elif (
      not strategy.derisk_enable
      and not is_rapid_mode
      and not is_rebuy_mode
      and not is_scalp_mode
      and (
        profit_init_ratio
        <= -(strategy.stop_threshold_doom_futures if strategy.is_futures_mode else strategy.stop_threshold_doom_spot)
      )
    ):
      return True, previous_sell_reason
    elif (
      not strategy.derisk_enable
      and is_rapid_mode
      and (
        profit_init_ratio
        <= -(strategy.stop_threshold_rapid_futures if strategy.is_futures_mode else strategy.stop_threshold_rapid_spot)
      )
    ):
      return True, previous_sell_reason
    elif (
      not strategy.derisk_enable
      and is_rebuy_mode
      and (
        profit_init_ratio
        <= -(strategy.stop_threshold_futures_rebuy if strategy.is_futures_mode else strategy.stop_threshold_spot_rebuy)
      )
    ):
      return True, previous_sell_reason
    elif (
      not strategy.derisk_enable
      and is_scalp_mode
      and (
        profit_init_ratio
        <= -(strategy.stop_threshold_scalp_futures if strategy.is_futures_mode else strategy.stop_threshold_scalp_spot)
      )
    ):
      return True, previous_sell_reason
  elif previous_sell_reason in [f"exit_{mode_name}_stoploss_u_e"]:
    if profit_init_ratio > 0.0:
      # profit is over the threshold, don't exit
      strategy._remove_profit_target(pair)
      return False, None
    elif is_derisk:
      strategy._remove_profit_target(pair)
      return False, None
    elif profit_ratio < (previous_profit - (0.04 / trade.leverage)):
      return True, previous_sell_reason
  elif previous_sell_reason in [f"exit_profit_{mode_name}_max"]:
    if profit_init_ratio < -0.08:
      # profit is under the threshold, cancel it
      strategy._remove_profit_target(pair)
      return False, None
    if trade.is_short:
      is_scalp_mode = all(c in strategy.short_scalp_mode_tags for c in enter_tags)
      if is_scalp_mode:
        if 0.001 <= profit_init_ratio < 0.01:
          if profit_init_ratio < (previous_profit - 0.008):
            return True, f"exit_profit_{mode_name}_t_0_1"
        elif 0.01 <= profit_init_ratio < 0.02:
          if profit_init_ratio < (previous_profit - 0.01):
            return True, f"exit_profit_{mode_name}_t_1_1"
        elif 0.02 <= profit_init_ratio < 0.03:
          if profit_init_ratio < (previous_profit - 0.01):
            return True, f"exit_profit_{mode_name}_t_2_1"
        elif 0.03 <= profit_init_ratio < 0.04:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_3_1"
        elif 0.04 <= profit_init_ratio < 0.05:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_4_1"
        elif 0.05 <= profit_init_ratio < 0.06:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_5_1"
        elif 0.06 <= profit_init_ratio < 0.07:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_6_1"
        elif 0.07 <= profit_init_ratio < 0.08:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_7_1"
        elif 0.08 <= profit_init_ratio < 0.09:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_8_1"
        elif 0.09 <= profit_init_ratio < 0.10:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_9_1"
        elif 0.10 <= profit_init_ratio < 0.11:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_10_1"
        elif 0.11 <= profit_init_ratio < 0.12:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_11_1"
        elif 0.12 <= profit_init_ratio:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_12_1"
      elif 0.001 <= profit_init_ratio < 0.01:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_0_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_0_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_0_3"
      elif 0.01 <= profit_init_ratio < 0.02:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_1_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_1_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_1_3"
      elif 0.02 <= profit_init_ratio < 0.03:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_2_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_2_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_2_3"
      elif 0.03 <= profit_init_ratio < 0.04:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_3_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_3_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_3_3"
      elif 0.04 <= profit_init_ratio < 0.05:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_4_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_4_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_4_3"
      elif 0.05 <= profit_init_ratio < 0.06:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_5_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_5_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_5_3"
      elif 0.06 <= profit_init_ratio < 0.07:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_6_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_6_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_6_3"
      elif 0.07 <= profit_init_ratio < 0.08:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_7_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_7_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_7_3"
      elif 0.08 <= profit_init_ratio < 0.09:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_8_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_8_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_8_3"
      elif 0.09 <= profit_init_ratio < 0.10:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_9_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_9_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_9_3"
      elif 0.10 <= profit_init_ratio < 0.11:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_10_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_10_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_10_3"
      elif 0.11 <= profit_init_ratio < 0.12:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_11_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_11_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_11_3"
      elif 0.12 <= profit_init_ratio:
        if (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["RSI_14"] > 50.0)
          and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
          and (last_candle["CMF_20"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_12_1"
        elif (
          profit_init_ratio < (previous_profit - 0.03)
          and (last_candle["CMF_20"] > 0.0)
          and (last_candle["CMF_20_1h"] > 0.0)
          and (last_candle["CMF_20_4h"] > 0.0)
        ):
          return True, f"exit_profit_{mode_name}_t_12_2"
        elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] < -40.0):
          return True, f"exit_profit_{mode_name}_t_12_3"
    else:
      is_scalp_mode = all(c in strategy.long_scalp_mode_tags for c in enter_tags)
      if is_scalp_mode:
        if 0.001 <= profit_init_ratio < 0.01:
          if profit_init_ratio < (previous_profit - 0.008):
            return True, f"exit_profit_{mode_name}_t_0_1"
        elif 0.01 <= profit_init_ratio < 0.02:
          if profit_init_ratio < (previous_profit - 0.01):
            return True, f"exit_profit_{mode_name}_t_1_1"
        elif 0.02 <= profit_init_ratio < 0.03:
          if profit_init_ratio < (previous_profit - 0.01):
            return True, f"exit_profit_{mode_name}_t_2_1"
        elif 0.03 <= profit_init_ratio < 0.04:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_3_1"
        elif 0.04 <= profit_init_ratio < 0.05:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_4_1"
        elif 0.05 <= profit_init_ratio < 0.06:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_5_1"
        elif 0.06 <= profit_init_ratio < 0.07:
          if profit_init_ratio < (previous_profit - 0.015):
            return True, f"exit_profit_{mode_name}_t_6_1"
        elif 0.07 <= profit_init_ratio < 0.08:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_7_1"
        elif 0.08 <= profit_init_ratio < 0.09:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_8_1"
        elif 0.09 <= profit_init_ratio < 0.10:
          if profit_init_ratio < (previous_profit - 0.02):
            return True, f"exit_profit_{mode_name}_t_9_1"
        elif 0.10 <= profit_init_ratio < 0.11:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_10_1"
        elif 0.11 <= profit_init_ratio < 0.12:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_11_1"
        elif 0.12 <= profit_init_ratio:
          if profit_init_ratio < (previous_profit - 0.025):
            return True, f"exit_profit_{mode_name}_t_12_1"
      else:
        if 0.001 <= profit_init_ratio < 0.01:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_0_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_0_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_0_3"
        elif 0.01 <= profit_init_ratio < 0.02:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_1_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_1_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_1_3"
        elif 0.02 <= profit_init_ratio < 0.03:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_2_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_2_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_2_3"
        elif 0.03 <= profit_init_ratio < 0.04:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_3_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_3_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_3_3"
        elif 0.04 <= profit_init_ratio < 0.05:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_4_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_4_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_4_3"
        elif 0.05 <= profit_init_ratio < 0.06:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_5_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_5_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_5_3"
        elif 0.06 <= profit_init_ratio < 0.07:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_6_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_6_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_6_3"
        elif 0.07 <= profit_init_ratio < 0.08:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_7_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_7_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_7_3"
        elif 0.08 <= profit_init_ratio < 0.09:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_8_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_8_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_8_3"
        elif 0.09 <= profit_init_ratio < 0.10:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_9_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_9_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_9_3"
        elif 0.10 <= profit_init_ratio < 0.11:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_10_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_10_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_10_3"
        elif 0.11 <= profit_init_ratio < 0.12:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_11_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_11_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_11_3"
        elif 0.12 <= profit_init_ratio:
          if (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["RSI_14"] < 50.0)
            and (last_candle["RSI_14"] < previous_candle_1["RSI_14"])
            and (last_candle["CMF_20"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_12_1"
          elif (
            profit_init_ratio < (previous_profit - 0.03)
            and (last_candle["CMF_20"] < -0.0)
            and (last_candle["CMF_20_1h"] < -0.0)
            and (last_candle["CMF_20_4h"] < -0.0)
          ):
            return True, f"exit_profit_{mode_name}_t_12_2"
          elif profit_init_ratio < (previous_profit - 0.05) and (last_candle["ROC_9_4h"] > 40.0):
            return True, f"exit_profit_{mode_name}_t_12_3"
  else:
    return False, None

  return False, None

# Calc Total Profit
# ---------------------------------------------------------------------------------------------


