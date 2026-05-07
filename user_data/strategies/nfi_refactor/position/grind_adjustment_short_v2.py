"""Extracted grind position-adjustment handler.

This module preserves source-equivalent experimental logic from the original
NFI grind adjustment extraction. It is intentionally not wired into the
strategy adapter until the known parity drift is investigated.
"""

from datetime import datetime, timedelta
from typing import Optional

from pandas import DataFrame
from freqtrade.persistence import Trade

def short_grind_adjust_trade_position_v2(
  strategy,
  trade: Trade,
  enter_tags,
  current_time: datetime,
  current_rate: float,
  current_profit: float,
  min_stake: Optional[float],
  max_stake: float,
  current_entry_rate: float,
  current_exit_rate: float,
  current_entry_profit: float,
  current_exit_profit: float,
  **kwargs,
):
  is_backtest = strategy.is_backtest_mode()
  min_stake = strategy.correct_min_stake(min_stake)
  df, _ = strategy.dp.get_analyzed_dataframe(trade.pair, strategy.timeframe)
  if len(df) < 2:
    return None
  last_candle = df.iloc[-1].squeeze()
  previous_candle = df.iloc[-2].squeeze()

  # we already waiting for an order to get filled
  if trade.has_open_orders:
    return None

  filled_orders = trade.select_filled_orders()
  filled_entries = trade.select_filled_orders(trade.entry_side)
  filled_exits = trade.select_filled_orders(trade.exit_side)
  count_of_entries = trade.nr_of_successful_entries
  count_of_exits = trade.nr_of_successful_exits

  exit_rate = current_rate
  if strategy.dp.runmode.value in ("live", "dry_run"):
    ticker = strategy.dp.ticker(trade.pair)
    if ("bid" in ticker) and ("ask" in ticker):
      if trade.is_short:
        if strategy.config["exit_pricing"]["price_side"] in ["ask", "other"]:
          if ticker["ask"] is not None:
            exit_rate = ticker["ask"]
      else:
        if strategy.config["exit_pricing"]["price_side"] in ["bid", "other"]:
          if ticker["bid"] is not None:
            exit_rate = ticker["bid"]

  profit_stake, profit_ratio, profit_current_stake_ratio, profit_init_ratio = strategy.calc_total_profit(
    trade, filled_entries, filled_exits, exit_rate
  )

  current_stake_amount = trade.amount * exit_rate
  slice_amount = filled_entries[0].cost
  slice_profit = (exit_rate - filled_orders[-1].safe_price) / filled_orders[-1].safe_price
  slice_profit_entry = (exit_rate - filled_entries[-1].safe_price) / filled_entries[-1].safe_price
  slice_profit_exit = (
    ((exit_rate - filled_exits[-1].safe_price) / filled_exits[-1].safe_price) if count_of_exits > 0 else 0.0
  )

  is_rebuy_mode = all(c in strategy.short_rebuy_mode_tags for c in enter_tags) or (
    any(c in strategy.short_rebuy_mode_tags for c in enter_tags)
    and all(c in (strategy.short_rebuy_mode_tags + strategy.short_grind_mode_tags) for c in enter_tags)
  )

  has_order_tags = False
  if hasattr(filled_orders[0], "ft_order_tag"):
    has_order_tags = True

  fee_open_rate = trade.fee_open if strategy.custom_fee_open_rate is None else strategy.custom_fee_open_rate
  fee_close_rate = trade.fee_close if strategy.custom_fee_close_rate is None else strategy.custom_fee_close_rate

  grind_1_max_sub_grinds = 0
  grind_1_stakes = (
    strategy.grinding_v2_grind_1_stakes_futures.copy()
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_1_stakes_spot.copy()
  )
  grind_1_sub_thresholds = (
    strategy.grinding_v2_grind_1_thresholds_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_1_thresholds_spot
  )
  if (slice_amount * grind_1_stakes[0] / (trade.leverage if strategy.is_futures_mode else 1.0)) < min_stake:
    multi = min_stake / slice_amount / grind_1_stakes[0] * trade.leverage
    for i, _ in enumerate(grind_1_stakes):
      grind_1_stakes[i] *= multi
  grind_1_max_sub_grinds = len(grind_1_stakes)
  grind_1_derisk_grinds = (
    strategy.grinding_v2_grind_1_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_1_derisk_spot
  )
  grind_1_profit_threshold = (
    strategy.grinding_v2_grind_1_profit_threshold_futures
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_1_profit_threshold_spot
  )

  grind_2_max_sub_grinds = 0
  grind_2_stakes = (
    strategy.grinding_v2_grind_2_stakes_futures.copy()
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_2_stakes_spot.copy()
  )
  grind_2_sub_thresholds = (
    strategy.grinding_v2_grind_2_thresholds_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_2_thresholds_spot
  )
  if (slice_amount * grind_2_stakes[0] / (trade.leverage if strategy.is_futures_mode else 1.0)) < min_stake:
    multi = min_stake / slice_amount / grind_2_stakes[0] * trade.leverage
    for i, _ in enumerate(grind_2_stakes):
      grind_2_stakes[i] *= multi
  grind_2_max_sub_grinds = len(grind_2_stakes)
  grind_2_derisk_grinds = (
    strategy.grinding_v2_grind_2_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_2_derisk_spot
  )
  grind_2_profit_threshold = (
    strategy.grinding_v2_grind_2_profit_threshold_futures
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_2_profit_threshold_spot
  )

  grind_3_max_sub_grinds = 0
  grind_3_stakes = (
    strategy.grinding_v2_grind_3_stakes_futures.copy()
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_3_stakes_spot.copy()
  )
  grind_3_sub_thresholds = (
    strategy.grinding_v2_grind_3_thresholds_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_3_thresholds_spot
  )
  if (slice_amount * grind_3_stakes[0] / (trade.leverage if strategy.is_futures_mode else 1.0)) < min_stake:
    multi = min_stake / slice_amount / grind_3_stakes[0] * trade.leverage
    for i, _ in enumerate(grind_3_stakes):
      grind_3_stakes[i] *= multi
  grind_3_max_sub_grinds = len(grind_3_stakes)
  grind_3_derisk_grinds = (
    strategy.grinding_v2_grind_3_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_3_derisk_spot
  )
  grind_3_profit_threshold = (
    strategy.grinding_v2_grind_3_profit_threshold_futures
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_3_profit_threshold_spot
  )

  grind_4_max_sub_grinds = 0
  grind_4_stakes = (
    strategy.grinding_v2_grind_4_stakes_futures.copy()
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_4_stakes_spot.copy()
  )
  grind_4_sub_thresholds = (
    strategy.grinding_v2_grind_4_thresholds_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_4_thresholds_spot
  )
  if (slice_amount * grind_4_stakes[0] / (trade.leverage if strategy.is_futures_mode else 1.0)) < min_stake:
    multi = min_stake / slice_amount / grind_4_stakes[0] * trade.leverage
    for i, _ in enumerate(grind_4_stakes):
      grind_4_stakes[i] *= multi
  grind_4_max_sub_grinds = len(grind_4_stakes)
  grind_4_derisk_grinds = (
    strategy.grinding_v2_grind_4_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_4_derisk_spot
  )
  grind_4_profit_threshold = (
    strategy.grinding_v2_grind_4_profit_threshold_futures
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_4_profit_threshold_spot
  )

  grind_5_max_sub_grinds = 0
  grind_5_stakes = (
    strategy.grinding_v2_grind_5_stakes_futures.copy()
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_5_stakes_spot.copy()
  )
  grind_5_sub_thresholds = (
    strategy.grinding_v2_grind_5_thresholds_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_5_thresholds_spot
  )
  if (slice_amount * grind_5_stakes[0] / (trade.leverage if strategy.is_futures_mode else 1.0)) < min_stake:
    multi = min_stake / slice_amount / grind_5_stakes[0] * trade.leverage
    for i, _ in enumerate(grind_5_stakes):
      grind_5_stakes[i] *= multi
  grind_5_max_sub_grinds = len(grind_5_stakes)
  grind_5_derisk_grinds = (
    strategy.grinding_v2_grind_5_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_grind_5_derisk_spot
  )
  grind_5_profit_threshold = (
    strategy.grinding_v2_grind_5_profit_threshold_futures
    if strategy.is_futures_mode
    else strategy.grinding_v2_grind_5_profit_threshold_spot
  )

  is_derisk_1 = False
  is_derisk_1_found = False  # derisk_level_1 de-risk exit
  derisk_1_order = None
  is_derisk_2 = False
  is_derisk_2_found = False  # derisk_level_2 de-risk exit
  derisk_2_order = None
  is_derisk_3 = False
  is_derisk_3_found = False  # derisk_level_3 de-risk exit
  derisk_3_order = None
  buyback_1_sub_grind_count = 0
  buyback_1_total_amount = 0.0
  buyback_1_total_cost = 0.0
  buyback_1_current_open_rate = 0.0
  buyback_1_current_grind_stake = 0.0
  buyback_1_current_grind_stake_profit = 0.0
  buyback_1_is_exit_found = False
  buyback_1_found = False
  buyback_1_buy_orders = []
  buyback_1_orders = []
  buyback_1_distance_ratio = 0.0
  buyback_1_exit_order = None
  buyback_1_exit_distance_ratio = 0.0
  buyback_2_sub_grind_count = 0
  buyback_2_total_amount = 0.0
  buyback_2_total_cost = 0.0
  buyback_2_current_open_rate = 0.0
  buyback_2_current_grind_stake = 0.0
  buyback_2_current_grind_stake_profit = 0.0
  buyback_2_is_exit_found = False
  buyback_2_found = False
  buyback_2_buy_orders = []
  buyback_2_orders = []
  buyback_2_distance_ratio = 0.0
  buyback_2_exit_order = None
  buyback_2_exit_distance_ratio = 0.0
  buyback_3_sub_grind_count = 0
  buyback_3_total_amount = 0.0
  buyback_3_total_cost = 0.0
  buyback_3_current_open_rate = 0.0
  buyback_3_current_grind_stake = 0.0
  buyback_3_current_grind_stake_profit = 0.0
  buyback_3_is_exit_found = False
  buyback_3_found = False
  buyback_3_buy_orders = []
  buyback_3_orders = []
  buyback_3_distance_ratio = 0.0
  buyback_3_exit_order = None
  buyback_3_exit_distance_ratio = 0.0
  grind_1_sub_grind_count = 0
  grind_1_total_amount = 0.0
  grind_1_total_cost = 0.0
  grind_1_current_open_rate = 0.0
  grind_1_current_grind_stake = 0.0
  grind_1_current_grind_stake_profit = 0.0
  grind_1_is_exit_found = False
  grind_1_found = False
  grind_1_buy_orders = []
  grind_1_orders = []
  grind_1_distance_ratio = 0.0
  grind_1_exit_order = None
  grind_1_exit_distance_ratio = 0.0
  grind_2_sub_grind_count = 0
  grind_2_total_amount = 0.0
  grind_2_total_cost = 0.0
  grind_2_current_open_rate = 0.0
  grind_2_current_grind_stake = 0.0
  grind_2_current_grind_stake_profit = 0.0
  grind_2_is_exit_found = False
  grind_2_found = False
  grind_2_buy_orders = []
  grind_2_orders = []
  grind_2_distance_ratio = 0.0
  grind_2_exit_order = None
  grind_2_exit_distance_ratio = 0.0
  grind_3_sub_grind_count = 0
  grind_3_total_amount = 0.0
  grind_3_total_cost = 0.0
  grind_3_current_open_rate = 0.0
  grind_3_current_grind_stake = 0.0
  grind_3_current_grind_stake_profit = 0.0
  grind_3_is_exit_found = False
  grind_3_found = False
  grind_3_buy_orders = []
  grind_3_orders = []
  grind_3_distance_ratio = 0.0
  grind_3_exit_order = None
  grind_3_exit_distance_ratio = 0.0
  grind_4_sub_grind_count = 0
  grind_4_total_amount = 0.0
  grind_4_total_cost = 0.0
  grind_4_current_open_rate = 0.0
  grind_4_current_grind_stake = 0.0
  grind_4_current_grind_stake_profit = 0.0
  grind_4_is_exit_found = False
  grind_4_found = False
  grind_4_buy_orders = []
  grind_4_orders = []
  grind_4_distance_ratio = 0.0
  grind_4_exit_order = None
  grind_4_exit_distance_ratio = 0.0
  grind_5_sub_grind_count = 0
  grind_5_total_amount = 0.0
  grind_5_total_cost = 0.0
  grind_5_current_open_rate = 0.0
  grind_5_current_grind_stake = 0.0
  grind_5_current_grind_stake_profit = 0.0
  grind_5_is_exit_found = False
  grind_5_found = False
  grind_5_buy_orders = []
  grind_5_orders = []
  grind_5_distance_ratio = 0.0
  grind_5_exit_order = None
  grind_5_exit_distance_ratio = 0.0
  for order in reversed(filled_orders):
    if (order.ft_order_side == "sell") and (order is not filled_orders[0]):
      order_tag = ""
      if has_order_tags:
        if order.ft_order_tag is not None:
          order_tag = order.ft_order_tag
      if not buyback_1_is_exit_found and order_tag == "buyback_1_entry":
        buyback_1_sub_grind_count += 1
        buyback_1_total_amount += order.safe_filled
        buyback_1_total_cost += order.safe_filled * order.safe_price
        buyback_1_buy_orders.append(order.id)
        buyback_1_orders.append(order)
        if not buyback_1_found:
          buyback_1_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          buyback_1_found = True
      elif not buyback_2_is_exit_found and order_tag == "buyback_2_entry":
        buyback_2_sub_grind_count += 1
        buyback_2_total_amount += order.safe_filled
        buyback_2_total_cost += order.safe_filled * order.safe_price
        buyback_2_buy_orders.append(order.id)
        buyback_2_orders.append(order)
        if not buyback_2_found:
          buyback_2_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          buyback_2_found = True
      elif not buyback_3_is_exit_found and order_tag == "buyback_3_entry":
        buyback_3_sub_grind_count += 1
        buyback_3_total_amount += order.safe_filled
        buyback_3_total_cost += order.safe_filled * order.safe_price
        buyback_3_buy_orders.append(order.id)
        buyback_3_orders.append(order)
        if not buyback_3_found:
          buyback_3_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          buyback_3_found = True
      elif not grind_1_is_exit_found and order_tag == "grind_1_entry":
        grind_1_sub_grind_count += 1
        grind_1_total_amount += order.safe_filled
        grind_1_total_cost += order.safe_filled * order.safe_price
        grind_1_buy_orders.append(order.id)
        grind_1_orders.append(order)
        if not grind_1_found:
          grind_1_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          grind_1_found = True
      elif not grind_2_is_exit_found and order_tag == "grind_2_entry":
        grind_2_sub_grind_count += 1
        grind_2_total_amount += order.safe_filled
        grind_2_total_cost += order.safe_filled * order.safe_price
        grind_2_buy_orders.append(order.id)
        grind_2_orders.append(order)
        if not grind_2_found:
          grind_2_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          grind_2_found = True
      elif not grind_3_is_exit_found and order_tag == "grind_3_entry":
        grind_3_sub_grind_count += 1
        grind_3_total_amount += order.safe_filled
        grind_3_total_cost += order.safe_filled * order.safe_price
        grind_3_buy_orders.append(order.id)
        grind_3_orders.append(order)
        if not grind_3_found:
          grind_3_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          grind_3_found = True
      elif not grind_4_is_exit_found and order_tag == "grind_4_entry":
        grind_4_sub_grind_count += 1
        grind_4_total_amount += order.safe_filled
        grind_4_total_cost += order.safe_filled * order.safe_price
        grind_4_buy_orders.append(order.id)
        grind_4_orders.append(order)
        if not grind_4_found:
          grind_4_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          grind_4_found = True
      elif not grind_5_is_exit_found and order_tag == "grind_5_entry":
        grind_5_sub_grind_count += 1
        grind_5_total_amount += order.safe_filled
        grind_5_total_cost += order.safe_filled * order.safe_price
        grind_5_buy_orders.append(order.id)
        grind_5_orders.append(order)
        if not grind_5_found:
          grind_5_distance_ratio = (exit_rate - order.safe_price) / order.safe_price
          grind_5_found = True
    elif order.ft_order_side == "buy":
      if (
        order is filled_exits[-1]
        and (order.safe_remaining * exit_rate / (trade.leverage if strategy.is_futures_mode else 1.0)) > min_stake
      ):
        partial_sell = True
        # break
      order_tag = ""
      if has_order_tags:
        if order.ft_order_tag is not None:
          sell_order_tag = order.ft_order_tag
          order_mode = sell_order_tag.split(" ", 1)
          if len(order_mode) > 0:
            order_tag = order_mode[0]
      if order_tag in ["derisk_level_1", "d"]:
        if not is_derisk_1_found:
          is_derisk_1_found = True
          is_derisk_1 = True
          derisk_1_order = order
      elif order_tag in ["derisk_level_2"]:
        if not is_derisk_2_found:
          is_derisk_2_found = True
          is_derisk_2 = True
          derisk_2_order = order
      elif order_tag in ["derisk_level_3"]:
        if not is_derisk_3_found:
          is_derisk_3_found = True
          is_derisk_3 = True
          derisk_3_order = order
      elif not buyback_1_is_exit_found and order_tag in ["buyback_1_exit", "buyback_1_derisk"]:
        buyback_1_is_exit_found = True
        buyback_1_exit_order = order
      elif not buyback_2_is_exit_found and order_tag in ["buyback_2_exit", "buyback_2_derisk"]:
        buyback_2_is_exit_found = True
        buyback_2_exit_order = order
      elif not buyback_3_is_exit_found and order_tag in ["buyback_3_exit", "buyback_3_derisk"]:
        buyback_3_is_exit_found = True
        buyback_3_exit_order = order
      elif not grind_1_is_exit_found and order_tag in ["grind_1_exit", "grind_1_derisk"]:
        grind_1_is_exit_found = True
        grind_1_exit_order = order
      elif not grind_2_is_exit_found and order_tag in ["grind_2_exit", "grind_2_derisk"]:
        grind_2_is_exit_found = True
        grind_2_exit_order = order
      elif not grind_3_is_exit_found and order_tag in ["grind_3_exit", "grind_3_derisk"]:
        grind_3_is_exit_found = True
        grind_3_exit_order = order
      elif not grind_4_is_exit_found and order_tag in ["grind_4_exit", "grind_4_derisk"]:
        grind_4_is_exit_found = True
        grind_4_exit_order = order
      elif not grind_5_is_exit_found and order_tag in ["grind_5_exit", "grind_5_derisk"]:
        grind_5_is_exit_found = True
        grind_5_exit_order = order
      elif order_tag in ["derisk_global"]:
        if not buyback_1_is_exit_found:
          buyback_1_is_exit_found = True
          buyback_1_exit_order = order
        if not buyback_2_is_exit_found:
          buyback_2_is_exit_found = True
          buyback_2_exit_order = order
        if not buyback_3_is_exit_found:
          buyback_3_is_exit_found = True
          buyback_3_exit_order = order
        if not grind_1_is_exit_found:
          grind_1_is_exit_found = True
          grind_1_exit_order = order
        if not grind_2_is_exit_found:
          grind_2_is_exit_found = True
          grind_2_exit_order = order
        if not grind_3_is_exit_found:
          grind_3_is_exit_found = True
          grind_3_exit_order = order
        if not grind_4_is_exit_found:
          grind_4_is_exit_found = True
          grind_4_exit_order = order
        if not grind_5_is_exit_found:
          grind_5_is_exit_found = True
          grind_5_exit_order = order

  if buyback_1_sub_grind_count > 0:
    buyback_1_current_open_rate = buyback_1_total_cost / buyback_1_total_amount
    buyback_1_current_grind_stake = buyback_1_total_amount * exit_rate * (1 - trade.fee_close)
    buyback_1_current_grind_stake_profit = buyback_1_current_grind_stake - buyback_1_total_cost
  if buyback_2_sub_grind_count > 0:
    buyback_2_current_open_rate = buyback_2_total_cost / buyback_2_total_amount
    buyback_2_current_grind_stake = buyback_2_total_amount * exit_rate * (1 - trade.fee_close)
    buyback_2_current_grind_stake_profit = buyback_2_current_grind_stake - buyback_2_total_cost
  if buyback_3_sub_grind_count > 0:
    buyback_3_current_open_rate = buyback_3_total_cost / buyback_3_total_amount
    buyback_3_current_grind_stake = buyback_3_total_amount * exit_rate * (1 - trade.fee_close)
    buyback_3_current_grind_stake_profit = buyback_3_current_grind_stake - buyback_3_total_cost
  if grind_1_sub_grind_count > 0:
    grind_1_current_open_rate = grind_1_total_cost / grind_1_total_amount
    grind_1_current_grind_stake = grind_1_total_amount * exit_rate * (1 - trade.fee_close)
    grind_1_current_grind_stake_profit = grind_1_current_grind_stake - grind_1_total_cost
  if grind_2_sub_grind_count > 0:
    grind_2_current_open_rate = grind_2_total_cost / grind_2_total_amount
    grind_2_current_grind_stake = grind_2_total_amount * exit_rate * (1 - trade.fee_close)
    grind_2_current_grind_stake_profit = grind_2_current_grind_stake - grind_2_total_cost
  if grind_3_sub_grind_count > 0:
    grind_3_current_open_rate = grind_3_total_cost / grind_3_total_amount
    grind_3_current_grind_stake = grind_3_total_amount * exit_rate * (1 - trade.fee_close)
    grind_3_current_grind_stake_profit = grind_3_current_grind_stake - grind_3_total_cost
  if grind_4_sub_grind_count > 0:
    grind_4_current_open_rate = grind_4_total_cost / grind_4_total_amount
    grind_4_current_grind_stake = grind_4_total_amount * exit_rate * (1 - trade.fee_close)
    grind_4_current_grind_stake_profit = grind_4_current_grind_stake - grind_4_total_cost
  if grind_5_sub_grind_count > 0:
    grind_5_current_open_rate = grind_5_total_cost / grind_5_total_amount
    grind_5_current_grind_stake = grind_5_total_amount * exit_rate * (1 - trade.fee_close)
    grind_5_current_grind_stake_profit = grind_5_current_grind_stake - grind_5_total_cost

  if grind_1_is_exit_found:
    grind_1_exit_distance_ratio = (exit_rate - grind_1_exit_order.safe_price) / grind_1_exit_order.safe_price
  if grind_2_is_exit_found:
    grind_2_exit_distance_ratio = (exit_rate - grind_2_exit_order.safe_price) / grind_2_exit_order.safe_price
  if grind_3_is_exit_found:
    grind_3_exit_distance_ratio = (exit_rate - grind_3_exit_order.safe_price) / grind_3_exit_order.safe_price
  if grind_4_is_exit_found:
    grind_4_exit_distance_ratio = (exit_rate - grind_4_exit_order.safe_price) / grind_4_exit_order.safe_price
  if buyback_1_is_exit_found:
    buyback_1_exit_distance_ratio = (exit_rate - buyback_1_exit_order.safe_price) / buyback_1_exit_order.safe_price
  elif is_derisk_1_found:
    buyback_1_exit_distance_ratio = (exit_rate - derisk_1_order.safe_price) / derisk_1_order.safe_price
  if buyback_2_is_exit_found:
    buyback_2_exit_distance_ratio = (exit_rate - buyback_2_exit_order.safe_price) / buyback_2_exit_order.safe_price
  elif is_derisk_2_found:
    buyback_2_exit_distance_ratio = (exit_rate - derisk_2_order.safe_price) / derisk_2_order.safe_price
  if buyback_3_is_exit_found:
    buyback_3_exit_distance_ratio = (exit_rate - buyback_3_exit_order.safe_price) / buyback_3_exit_order.safe_price
  elif is_derisk_3_found:
    buyback_3_exit_distance_ratio = (exit_rate - derisk_3_order.safe_price) / derisk_3_order.safe_price

  # all buybacks & grinds
  current_open_grind_stake_profit = (
    buyback_1_current_grind_stake_profit
    + buyback_2_current_grind_stake_profit
    + buyback_3_current_grind_stake_profit
    + grind_1_current_grind_stake_profit
    + grind_2_current_grind_stake_profit
    + grind_3_current_grind_stake_profit
    + grind_4_current_grind_stake_profit
    + grind_5_current_grind_stake_profit
  )
  num_open_grinds_and_buybacks = (
    buyback_1_sub_grind_count
    + buyback_2_sub_grind_count
    + buyback_3_sub_grind_count
    + grind_1_sub_grind_count
    + grind_2_sub_grind_count
    + grind_3_sub_grind_count
    + grind_4_sub_grind_count
    + grind_5_sub_grind_count
  )

  # Rebuy mode, the first entry is lower than normal slot stake
  if is_rebuy_mode:
    slice_amount /= strategy.rebuy_mode_stake_multiplier
  # not reached the max allowed stake for all grinds
  is_not_trade_max_stake = (current_stake_amount < (slice_amount * strategy.grinding_v2_max_stake)) and (
    num_open_grinds_and_buybacks < strategy.grinding_v2_max_grinds_and_buybacks
  )

  is_short_extra_checks_entry = (
    (current_time - timedelta(minutes=5) > filled_entries[-1].order_filled_utc)
    and ((current_time - timedelta(hours=2) > filled_orders[-1].order_filled_utc) or (slice_profit > 0.06))
    and (
      (current_stake_amount < (filled_entries[0].cost * 0.50))
      or (current_time - timedelta(hours=6) > filled_orders[-1].order_filled_utc)
      or (slice_profit > 0.06)
    )
  )
  is_short_buyback_entry = strategy.short_buyback_entry_v2(last_candle, previous_candle, slice_profit, True)
  is_short_grind_entry = (
    strategy.short_grind_entry_v2(last_candle, previous_candle, slice_profit, True)
    or (
      (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
      and (num_open_grinds_and_buybacks == 0)
      and (
        (last_candle["RSI_3"] < 90.0)
        and (last_candle["RSI_3_15m"] < 80.0)
        and (last_candle["RSI_3_1h"] < 80.0)
        and (last_candle["RSI_3_1h"] < 80.0)
        and (last_candle["AROOND_14"] < 50.0)
        and (last_candle["AROOND_14_15m"] < 50.0)
      )
    )
    or (
      strategy.is_futures_mode
      and trade.liquidation_price is not None
      and (
        (trade.is_short and current_rate > trade.liquidation_price * 0.90)
        or (not trade.is_short and current_rate < trade.liquidation_price * 1.10)
      )
      and (slice_profit > 0.03)
      and (last_candle["RSI_3"] < 90.0)
      and (last_candle["RSI_3_15m"] < 80.0)
      # and (last_candle["RSI_3_1h"] < 80.0)
      # and (last_candle["RSI_3_1h"] < 80.0)
      and (last_candle["AROOND_14"] < 50.0)
      and (last_candle["AROOND_14_15m"] < 50.0)
    )
  )

  # De-risk level 1

  # flag it
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_1_enable
    and (not is_derisk_1_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_1_flag") is None)
    and (
      profit_stake
      < (
        slice_amount
        * (
          strategy.grinding_v2_derisk_level_1_futures[0]
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_1_spot[0]
        )
      )
      / trade.leverage
    )
  ):
    trade.set_custom_data(key="grinding_v2_derisk_level_1_flag", value=True)
    trade.set_custom_data(key="grinding_v2_derisk_level_1_profit", value=profit_stake)
    trade.set_custom_data(key="grinding_v2_derisk_level_1_time", value=current_time.isoformat())

  flag_is_derisk_level_1 = False
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_1_enable
    and (not is_derisk_1_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_1_flag") is True)
  ):
    flag_profit = trade.get_custom_data(key="grinding_v2_derisk_level_1_profit")
    flag_time = datetime.fromisoformat(trade.get_custom_data(key="grinding_v2_derisk_level_1_time"))
    if current_time - timedelta(hours=96) > flag_time:
      if profit_stake > flag_profit:
        trade.set_custom_data(key="grinding_v2_derisk_level_1_flag", value=None)
      else:
        flag_is_derisk_level_1 = True

  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_1_enable
    and (not is_derisk_1_found)
    and not is_rebuy_mode
    and (
      flag_is_derisk_level_1
      or (
        profit_stake
        < (
          slice_amount
          * (
            strategy.grinding_v2_derisk_level_1_futures[1]
            if strategy.is_futures_mode
            else strategy.grinding_v2_derisk_level_1_spot[1]
          )
        )
        / trade.leverage
      )
    )
  ):
    sell_amount = (
      (
        filled_entries[0].safe_filled
        * (
          strategy.grinding_v2_derisk_level_1_stake_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_1_stake_spot
        )
      )
      * exit_rate
      / trade.leverage
    )
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      strategy.dp.send_msg(
        strategy.notification_msg(
          "de-risk",
          tag="Level 1",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
        )
      )
      log.info(
        f"De-risk Level 1 [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
      )
      return -ft_sell_amount, "derisk_level_1"

  # De-risk level 2

  # flag it
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_2_enable
    and (not is_derisk_2_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_2_flag") is None)
    and (
      profit_stake
      < (
        slice_amount
        * (
          strategy.grinding_v2_derisk_level_2_futures[0]
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_2_spot[0]
        )
      )
      / trade.leverage
    )
  ):
    trade.set_custom_data(key="grinding_v2_derisk_level_2_flag", value=True)
    trade.set_custom_data(key="grinding_v2_derisk_level_2_profit", value=profit_stake)
    trade.set_custom_data(key="grinding_v2_derisk_level_2_time", value=current_time.isoformat())

  flag_is_derisk_level_2 = False
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_2_enable
    and (not is_derisk_2_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_2_flag") is True)
  ):
    flag_profit = trade.get_custom_data(key="grinding_v2_derisk_level_2_profit")
    flag_time = datetime.fromisoformat(trade.get_custom_data(key="grinding_v2_derisk_level_2_time"))
    if current_time - timedelta(hours=96) > flag_time:
      if profit_stake > flag_profit:
        trade.set_custom_data(key="grinding_v2_derisk_level_2_flag", value=None)
      else:
        flag_is_derisk_level_2 = True

  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_2_enable
    and (not is_derisk_2_found)
    and not is_rebuy_mode
    and (
      flag_is_derisk_level_2
      or (
        profit_stake
        < (
          slice_amount
          * (
            strategy.grinding_v2_derisk_level_2_futures[1]
            if strategy.is_futures_mode
            else strategy.grinding_v2_derisk_level_2_spot[1]
          )
        )
        / trade.leverage
      )
    )
  ):
    sell_amount = (
      (
        filled_entries[0].safe_filled
        * (
          strategy.grinding_v2_derisk_level_2_stake_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_2_stake_spot
        )
      )
      * exit_rate
      / trade.leverage
    )
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      strategy.dp.send_msg(
        strategy.notification_msg(
          "de-risk",
          tag="Level 2",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
        )
      )
      log.info(
        f"De-risk Level 2 [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
      )
      return -ft_sell_amount, "derisk_level_2"

  # De-risk level 3

  # flag it
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_3_enable
    and (not is_derisk_3_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_3_flag") is None)
    and (
      profit_stake
      < (
        slice_amount
        * (
          strategy.grinding_v2_derisk_level_3_futures[0]
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_3_spot[0]
        )
      )
      / trade.leverage
    )
  ):
    trade.set_custom_data(key="grinding_v2_derisk_level_3_flag", value=True)
    trade.set_custom_data(key="grinding_v2_derisk_level_3_profit", value=profit_stake)
    trade.set_custom_data(key="grinding_v2_derisk_level_3_time", value=current_time.isoformat())

  flag_is_derisk_level_3 = False
  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_3_enable
    and (not is_derisk_3_found)
    and not is_rebuy_mode
    and (trade.get_custom_data(key="grinding_v2_derisk_level_3_flag") is True)
  ):
    flag_profit = trade.get_custom_data(key="grinding_v2_derisk_level_3_profit")
    flag_time = datetime.fromisoformat(trade.get_custom_data(key="grinding_v2_derisk_level_3_time"))
    if current_time - timedelta(hours=96) > flag_time:
      if profit_stake > flag_profit:
        trade.set_custom_data(key="grinding_v2_derisk_level_3_flag", value=None)
      else:
        flag_is_derisk_level_3 = True

  if (
    strategy.derisk_enable
    and strategy.grinding_v2_derisk_level_3_enable
    and (not is_derisk_3_found)
    and not is_rebuy_mode
    and (
      flag_is_derisk_level_3
      or (
        profit_stake
        < (
          slice_amount
          * (
            strategy.grinding_v2_derisk_level_3_futures[1]
            if strategy.is_futures_mode
            else strategy.grinding_v2_derisk_level_3_spot[1]
          )
        )
        / trade.leverage
      )
    )
  ):
    sell_amount = (
      (
        filled_entries[0].safe_filled
        * (
          strategy.grinding_v2_derisk_level_3_stake_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_derisk_level_3_stake_spot
        )
      )
      * exit_rate
      / trade.leverage
    )
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      strategy.dp.send_msg(
        strategy.notification_msg(
          "de-risk",
          tag="Level 3",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
        )
      )
      log.info(
        f"De-risk Level 3 [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
      )
      return -ft_sell_amount, "derisk_level_3"

  # De-risk global
  if (
    strategy.grinding_v2_derisk_global_enable
    and is_derisk_1_found
    and (
      current_open_grind_stake_profit
      < (
        slice_amount
        * (strategy.grinding_v2_derisk_global_futures if strategy.is_futures_mode else strategy.grinding_v2_derisk_global_spot)
      )
      / trade.leverage
    )
  ):
    sell_amount = trade.amount * exit_rate / trade.leverage - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      strategy.dp.send_msg(
        strategy.notification_msg(
          "de-risk",
          tag="Global",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
        )
      )
      log.info(
        f"De-risk Global [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
      )
      return -ft_sell_amount, "derisk_global"

  # Grinding 1

  if (
    (strategy.grinding_v2_grind_1_enable)
    and (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
    and is_short_grind_entry
    and is_short_extra_checks_entry
    and (grind_1_sub_grind_count < grind_1_max_sub_grinds)
    and (grind_1_sub_grind_count == 0 or (-grind_1_distance_ratio < grind_1_sub_thresholds[grind_1_sub_grind_count]))
    and is_not_trade_max_stake
  ):
    buy_amount = slice_amount * grind_1_stakes[grind_1_sub_grind_count] / trade.leverage
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "grinding-entry",
        tag="grind_1_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Grinding entry (grind_1_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "grind_1_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if grind_1_sub_grind_count > 0:
    grind_profit = -(exit_rate - grind_1_current_open_rate) / grind_1_current_open_rate
    if (grind_profit > (grind_1_profit_threshold + fee_open_rate + fee_close_rate)) and strategy.short_grind_exit_v2(
      last_candle, previous_candle, slice_profit, True
    ):
      sell_amount = grind_1_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "grinding-exit",
            tag="grind_1_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=grind_1_total_amount,
          )
        )
        log.info(
          f"Grinding exit (grind_1_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_1_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "grind_1_exit"
        for grind_entry_id in grind_1_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_grind_1_use_derisk
  #   and (grind_1_sub_grind_count > 0)
  #   and ((-(exit_rate - grind_1_current_open_rate) / grind_1_current_open_rate) < grind_1_derisk_grinds)
  #   and (grind_1_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_grind_1_use_derisk
    and (grind_1_sub_grind_count > 0)
    and (grind_1_current_grind_stake_profit < (slice_amount * grind_1_derisk_grinds))
    and (grind_1_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = grind_1_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if grind_1_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - grind_1_current_open_rate) / grind_1_current_open_rate)
          if grind_1_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "grinding-derisk",
          tag="grind_1_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          grind_profit_stake=grind_profit * sell_amount * trade.leverage,
          grind_profit_pct=grind_profit,
          coin_amount=grind_1_total_amount,
        )
      )
      log.info(
        f"Grinding de-risk (grind_1_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_1_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "grind_1_derisk"
      for grind_entry_id in grind_1_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # Grinding 2

  if (
    (strategy.grinding_v2_grind_2_enable)
    # and (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
    and is_short_grind_entry
    and is_short_extra_checks_entry
    and (grind_2_sub_grind_count < grind_2_max_sub_grinds)
    and (grind_2_sub_grind_count == 0 or (-grind_2_distance_ratio < grind_2_sub_thresholds[grind_2_sub_grind_count]))
    and is_not_trade_max_stake
  ):
    buy_amount = slice_amount * grind_2_stakes[grind_2_sub_grind_count] / trade.leverage
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "grinding-entry",
        tag="grind_2_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Grinding entry (grind_2_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "grind_2_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if grind_2_sub_grind_count > 0:
    grind_profit = -(exit_rate - grind_2_current_open_rate) / grind_2_current_open_rate
    if (grind_profit > (grind_2_profit_threshold + fee_open_rate + fee_close_rate)) and strategy.short_grind_exit_v2(
      last_candle, previous_candle, slice_profit, True
    ):
      sell_amount = grind_2_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "grinding-exit",
            tag="grind_2_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=grind_2_total_amount,
          )
        )
        log.info(
          f"Grinding exit (grind_2_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_2_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "grind_2_exit"
        for grind_entry_id in grind_2_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_grind_2_use_derisk
  #   and (grind_2_sub_grind_count > 0)
  #   and ((-(exit_rate - grind_2_current_open_rate) / grind_2_current_open_rate) < grind_2_derisk_grinds)
  #   and (grind_2_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_grind_2_use_derisk
    and (grind_2_sub_grind_count > 0)
    and (grind_2_current_grind_stake_profit < (slice_amount * grind_2_derisk_grinds))
    and (grind_2_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = grind_2_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if grind_2_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - grind_2_current_open_rate) / grind_2_current_open_rate)
          if grind_2_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "grinding-derisk",
          tag="grind_2_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          grind_profit_stake=grind_profit * sell_amount * trade.leverage,
          grind_profit_pct=grind_profit,
          coin_amount=grind_2_total_amount,
        )
      )
      log.info(
        f"Grinding de-risk (grind_2_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_2_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "grind_2_derisk"
      for grind_entry_id in grind_2_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # Grinding 3

  if (
    (strategy.grinding_v2_grind_3_enable)
    # and (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
    and is_short_grind_entry
    and is_short_extra_checks_entry
    and (grind_3_sub_grind_count < grind_3_max_sub_grinds)
    and (grind_3_sub_grind_count == 0 or (-grind_3_distance_ratio < grind_3_sub_thresholds[grind_3_sub_grind_count]))
    and is_not_trade_max_stake
  ):
    buy_amount = slice_amount * grind_3_stakes[grind_3_sub_grind_count] / trade.leverage
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "grinding-entry",
        tag="grind_3_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Grinding entry (grind_3_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "grind_3_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if grind_3_sub_grind_count > 0:
    grind_profit = -(exit_rate - grind_3_current_open_rate) / grind_3_current_open_rate
    if (grind_profit > (grind_3_profit_threshold + fee_open_rate + fee_close_rate)) and strategy.short_grind_exit_v2(
      last_candle, previous_candle, slice_profit, True
    ):
      sell_amount = grind_3_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "grinding-exit",
            tag="grind_3_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=grind_3_total_amount,
          )
        )
        log.info(
          f"Grinding exit (grind_3_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_3_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "grind_3_exit"
        for grind_entry_id in grind_3_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_grind_3_use_derisk
  #   and (grind_3_sub_grind_count > 0)
  #   and ((-(exit_rate - grind_3_current_open_rate) / grind_3_current_open_rate) < grind_3_derisk_grinds)
  #   and (grind_3_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_grind_3_use_derisk
    and (grind_3_sub_grind_count > 0)
    and (grind_3_current_grind_stake_profit < (slice_amount * grind_3_derisk_grinds))
    and (grind_3_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = grind_3_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if grind_3_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - grind_3_current_open_rate) / grind_3_current_open_rate)
          if grind_3_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "grinding-derisk",
          tag="grind_3_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          grind_profit_stake=grind_profit * sell_amount * trade.leverage,
          grind_profit_pct=grind_profit,
          coin_amount=grind_3_total_amount,
        )
      )
      log.info(
        f"Grinding de-risk (grind_3_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_3_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "grind_3_derisk"
      for grind_entry_id in grind_3_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # Grinding 4

  if (
    (strategy.grinding_v2_grind_4_enable)
    # and (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
    and (
      is_short_grind_entry
      # or (
      #   is_derisk_1_found
      #   # only queue 4 grinds open
      #   and (num_open_grinds_and_buybacks == grind_4_sub_grind_count)
      #   and (last_candle["protections_short_global"] == True)
      #   and (
      #     (slice_profit > 0.04)
      #     and (last_candle["RSI_3"] < 90.0)
      #     and (last_candle["RSI_3_15m"] < 80.0)
      #     and (last_candle["AROOND_14"] < 50.0)
      #     and (last_candle["AROOND_14_15m"] < 50.0)
      #   )
      # )
    )
    and is_short_extra_checks_entry
    and (grind_4_sub_grind_count < grind_4_max_sub_grinds)
    and (grind_4_sub_grind_count == 0 or (-grind_4_distance_ratio < grind_4_sub_thresholds[grind_4_sub_grind_count]))
    and is_not_trade_max_stake
  ):
    buy_amount = slice_amount * grind_4_stakes[grind_4_sub_grind_count] / trade.leverage
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "grinding-entry",
        tag="grind_4_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Grinding entry (grind_4_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "grind_4_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if grind_4_sub_grind_count > 0:
    grind_profit = -(exit_rate - grind_4_current_open_rate) / grind_4_current_open_rate
    if (grind_profit > (grind_4_profit_threshold + fee_open_rate + fee_close_rate)) and strategy.short_grind_exit_v2(
      last_candle, previous_candle, slice_profit, True
    ):
      sell_amount = grind_4_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "grinding-exit",
            tag="grind_4_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=grind_4_total_amount,
          )
        )
        log.info(
          f"Grinding exit (grind_4_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_4_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "grind_4_exit"
        for grind_entry_id in grind_4_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_grind_4_use_derisk
  #   and (grind_4_sub_grind_count > 0)
  #   and ((-(exit_rate - grind_4_current_open_rate) / grind_4_current_open_rate) < grind_4_derisk_grinds)
  #   and (grind_4_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_grind_4_use_derisk
    and (grind_4_sub_grind_count > 0)
    and (grind_4_current_grind_stake_profit < (slice_amount * grind_4_derisk_grinds))
    and (grind_4_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = grind_4_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if grind_4_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - grind_4_current_open_rate) / grind_4_current_open_rate)
          if grind_4_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "grinding-derisk",
          tag="grind_4_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          grind_profit_stake=grind_profit * sell_amount * trade.leverage,
          grind_profit_pct=grind_profit,
          coin_amount=grind_4_total_amount,
        )
      )
      log.info(
        f"Grinding de-risk (grind_4_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_4_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "grind_4_derisk"
      for grind_entry_id in grind_4_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # Grinding 5

  if (
    (strategy.grinding_v2_grind_5_enable)
    and (is_derisk_1_found or is_derisk_2_found or is_derisk_3_found)
    and (
      is_short_grind_entry
      or (
        is_derisk_1_found
        and (slice_profit_entry > 0.10)
        and (slice_profit_exit > 0.04)
        and (last_candle["protections_short_global"] == True)
        # and (
        #   (slice_profit > 0.04)
        #   and (last_candle["RSI_3"] < 90.0)
        #   and (last_candle["RSI_3_15m"] < 80.0)
        #   and (last_candle["AROOND_14"] < 50.0)
        #   and (last_candle["AROOND_14_15m"] < 50.0)
        # )
      )
    )
    and is_short_extra_checks_entry
    and (grind_5_sub_grind_count < grind_5_max_sub_grinds)
    and (grind_5_sub_grind_count == 0 or (-grind_5_distance_ratio < grind_5_sub_thresholds[grind_5_sub_grind_count]))
    and is_not_trade_max_stake
  ):
    buy_amount = slice_amount * grind_5_stakes[grind_5_sub_grind_count] / trade.leverage
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "grinding-entry",
        tag="grind_5_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Grinding entry (grind_5_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "grind_5_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if grind_5_sub_grind_count > 0:
    grind_profit = -(exit_rate - grind_5_current_open_rate) / grind_5_current_open_rate
    if (grind_profit > (grind_5_profit_threshold + fee_open_rate + fee_close_rate)) and strategy.short_grind_exit_v2(
      last_candle, previous_candle, slice_profit, True
    ):
      sell_amount = grind_5_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "grinding-exit",
            tag="grind_5_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=grind_5_total_amount,
          )
        )
        log.info(
          f"Grinding exit (grind_5_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_5_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "grind_5_exit"
        for grind_entry_id in grind_5_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_grind_5_use_derisk
  #   and (grind_5_sub_grind_count > 0)
  #   and ((-(exit_rate - grind_5_current_open_rate) / grind_5_current_open_rate) < grind_5_derisk_grinds)
  #   and (grind_5_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_grind_5_use_derisk
    and (grind_5_sub_grind_count > 0)
    and (grind_5_current_grind_stake_profit < (slice_amount * grind_5_derisk_grinds))
    and (grind_5_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = grind_5_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if grind_5_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - grind_5_current_open_rate) / grind_5_current_open_rate)
          if grind_5_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "grinding-derisk",
          tag="grind_5_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          grind_profit_stake=grind_profit * sell_amount * trade.leverage,
          grind_profit_pct=grind_profit,
          coin_amount=grind_5_total_amount,
        )
      )
      log.info(
        f"Grinding de-risk (grind_5_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {grind_5_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "grind_5_derisk"
      for grind_entry_id in grind_5_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # Buyback 1

  if (
    strategy.grinding_v2_buyback_1_enable
    and is_derisk_1_found
    and is_short_buyback_entry
    and is_short_extra_checks_entry
    and (buyback_1_current_open_rate == 0)
    and (
      -buyback_1_exit_distance_ratio
      < (
        strategy.grinding_v2_buyback_1_distance_ratio_futures
        if strategy.is_futures_mode
        else strategy.grinding_v2_buyback_1_distance_ratio_spot
      )
    )
    and is_not_trade_max_stake
  ):
    buy_amount = (
      slice_amount
      * (strategy.grinding_v2_buyback_1_stake_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_1_stake_spot)
      / trade.leverage
    )
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "buyback-entry",
        tag="buyback_1_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Buyback entry (buyback_1_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "buyback_1_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if buyback_1_sub_grind_count > 0:
    grind_profit = -(exit_rate - buyback_1_current_open_rate) / buyback_1_current_open_rate
    if (
      grind_profit
      > (
        (
          strategy.grinding_v2_buyback_1_profit_threshold_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_1_profit_threshold_spot
        )
        + fee_open_rate
        + fee_close_rate
      )
    ) and strategy.short_grind_exit_v2(last_candle, previous_candle, slice_profit, True):
      sell_amount = buyback_1_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "buyback-exit",
            tag="buyback_1_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=buyback_1_total_amount,
          )
        )
        log.info(
          f"Buyback exit (buyback_1_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_1_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "buyback_1_exit"
        for grind_entry_id in buyback_1_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_buyback_1_use_derisk
  #   and (buyback_1_sub_grind_count > 0)
  #   and (
  #     (-(exit_rate - buyback_1_current_open_rate) / buyback_1_current_open_rate)
  #     < (
  #       strategy.grinding_v2_buyback_1_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_1_derisk_spot
  #     )
  #   )
  #   and (buyback_1_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_buyback_1_use_derisk
    and (buyback_1_sub_grind_count > 0)
    and (
      buyback_1_current_grind_stake_profit
      < (
        slice_amount
        * (
          strategy.grinding_v2_buyback_1_derisk_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_1_derisk_spot
        )
      )
    )
    and (buyback_1_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = buyback_1_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if buyback_1_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - buyback_1_current_open_rate) / buyback_1_current_open_rate)
          if buyback_1_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "buyback-derisk",
          tag="buyback_1_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          coin_amount=buyback_1_total_amount,
        )
      )
      log.info(
        f"Buyback de-risk (buyback_1_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_1_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "buyback_1_derisk"
      for grind_entry_id in buyback_1_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # # Buyback 2

  if (
    strategy.grinding_v2_buyback_2_enable
    and is_derisk_2_found
    and is_short_buyback_entry
    and is_short_extra_checks_entry
    and (buyback_2_current_open_rate == 0)
    and (
      -buyback_2_exit_distance_ratio
      < (
        strategy.grinding_v2_buyback_2_distance_ratio_futures
        if strategy.is_futures_mode
        else strategy.grinding_v2_buyback_2_distance_ratio_spot
      )
    )
    and is_not_trade_max_stake
  ):
    buy_amount = (
      slice_amount
      * (strategy.grinding_v2_buyback_2_stake_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_2_stake_spot)
      / trade.leverage
    )
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "buyback-entry",
        tag="buyback_2_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Buyback entry (buyback_2_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "buyback_2_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if buyback_2_sub_grind_count > 0:
    grind_profit = -(exit_rate - buyback_2_current_open_rate) / buyback_2_current_open_rate
    if (
      grind_profit
      > (
        (
          strategy.grinding_v2_buyback_2_profit_threshold_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_2_profit_threshold_spot
        )
        + fee_open_rate
        + fee_close_rate
      )
    ) and strategy.short_grind_exit_v2(last_candle, previous_candle, slice_profit, True):
      sell_amount = buyback_2_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "buyback-exit",
            tag="buyback_2_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=buyback_2_total_amount,
          )
        )
        log.info(
          f"Buyback exit (buyback_2_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_2_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "buyback_2_exit"
        for grind_entry_id in buyback_2_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_buyback_2_use_derisk
  #   and (buyback_2_sub_grind_count > 0)
  #   and (
  #     (-(exit_rate - buyback_2_current_open_rate) / buyback_2_current_open_rate)
  #     < (
  #       strategy.grinding_v2_buyback_2_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_2_derisk_spot
  #     )
  #   )
  #   and (buyback_2_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_buyback_2_use_derisk
    and (buyback_2_sub_grind_count > 0)
    and (
      buyback_2_current_grind_stake_profit
      < (
        slice_amount
        * (
          strategy.grinding_v2_buyback_2_derisk_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_2_derisk_spot
        )
      )
    )
    and (buyback_2_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = buyback_2_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if buyback_2_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - buyback_2_current_open_rate) / buyback_2_current_open_rate)
          if buyback_2_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "buyback-derisk",
          tag="buyback_2_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          coin_amount=buyback_2_total_amount,
        )
      )
      log.info(
        f"Buyback de-risk (buyback_2_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_2_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "buyback_2_derisk"
      for grind_entry_id in buyback_2_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  # # Buyback 3

  if (
    strategy.grinding_v2_buyback_3_enable
    and is_derisk_3_found
    and is_short_buyback_entry
    and is_short_extra_checks_entry
    and (buyback_3_current_open_rate == 0)
    and (
      -buyback_3_exit_distance_ratio
      < (
        strategy.grinding_v2_buyback_3_distance_ratio_futures
        if strategy.is_futures_mode
        else strategy.grinding_v2_buyback_3_distance_ratio_spot
      )
    )
    and is_not_trade_max_stake
  ):
    buy_amount = (
      slice_amount
      * (strategy.grinding_v2_buyback_3_stake_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_3_stake_spot)
      / trade.leverage
    )
    if buy_amount < (min_stake * 1.5):
      buy_amount = min_stake * 1.5
    if buy_amount > max_stake:
      return None
    strategy.dp.send_msg(
      strategy.notification_msg(
        "buyback-entry",
        tag="buyback_3_entry",
        pair=trade.pair,
        rate=current_rate,
        stake_amount=buy_amount,
        profit_stake=profit_stake,
        profit_ratio=profit_ratio,
        stake_currency=strategy.config["stake_currency"],
      )
    )
    log.info(
      f"Buyback entry (buyback_3_entry) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
    )
    order_tag = "buyback_3_entry"
    if has_order_tags:
      return buy_amount, order_tag
    else:
      return buy_amount

  if buyback_3_sub_grind_count > 0:
    grind_profit = -(exit_rate - buyback_3_current_open_rate) / buyback_3_current_open_rate
    if (
      grind_profit
      > (
        (
          strategy.grinding_v2_buyback_3_profit_threshold_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_3_profit_threshold_spot
        )
        + fee_open_rate
        + fee_close_rate
      )
    ) and strategy.short_grind_exit_v2(last_candle, previous_candle, slice_profit, True):
      sell_amount = buyback_3_total_amount * exit_rate / trade.leverage
      if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
        sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
      ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
      if sell_amount > min_stake and ft_sell_amount > min_stake:
        strategy.dp.send_msg(
          strategy.notification_msg(
            "buyback-exit",
            tag="buyback_3_exit",
            pair=trade.pair,
            rate=exit_rate,
            stake_amount=sell_amount,
            profit_stake=profit_stake,
            profit_ratio=profit_ratio,
            stake_currency=strategy.config["stake_currency"],
            grind_profit_stake=grind_profit * sell_amount * trade.leverage,
            grind_profit_pct=grind_profit,
            coin_amount=buyback_3_total_amount,
          )
        )
        log.info(
          f"Buyback exit (buyback_3_exit) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_3_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}% ({grind_profit * sell_amount * trade.leverage} {strategy.config['stake_currency']})"
        )
        order_tag = "buyback_3_exit"
        for grind_entry_id in buyback_3_buy_orders:
          order_tag += " " + str(grind_entry_id)
        if has_order_tags:
          return -ft_sell_amount, order_tag
        else:
          return -ft_sell_amount

  # if (
  #   strategy.grinding_v2_buyback_3_use_derisk
  #   and (buyback_3_sub_grind_count > 0)
  #   and (
  #     (-(exit_rate - buyback_3_current_open_rate) / buyback_3_current_open_rate)
  #     < (
  #       strategy.grinding_v2_buyback_3_derisk_futures if strategy.is_futures_mode else strategy.grinding_v2_buyback_3_derisk_spot
  #     )
  #   )
  #   and (buyback_3_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  # ):
  if (
    strategy.grinding_v2_buyback_3_use_derisk
    and (buyback_3_sub_grind_count > 0)
    and (
      buyback_3_current_grind_stake_profit
      < (
        slice_amount
        * (
          strategy.grinding_v2_buyback_3_derisk_futures
          if strategy.is_futures_mode
          else strategy.grinding_v2_buyback_3_derisk_spot
        )
      )
    )
    and (buyback_3_orders[-1].order_date_utc.replace(tzinfo=None) >= datetime(2025, 8, 3) or is_backtest)
  ):
    sell_amount = buyback_3_total_amount * exit_rate / trade.leverage
    if ((current_stake_amount / trade.leverage) - sell_amount) < (min_stake * 1.55):
      sell_amount = (trade.amount * exit_rate / trade.leverage) - (min_stake * 1.55)
    ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
    if sell_amount > min_stake and ft_sell_amount > min_stake:
      grind_profit = 0.0
      if buyback_3_current_open_rate > 0.0:
        grind_profit = (
          -((exit_rate - buyback_3_current_open_rate) / buyback_3_current_open_rate)
          if buyback_3_is_exit_found
          else profit_ratio
        )
      strategy.dp.send_msg(
        strategy.notification_msg(
          "buyback-derisk",
          tag="buyback_3_derisk",
          pair=trade.pair,
          rate=exit_rate,
          stake_amount=sell_amount,
          profit_stake=profit_stake,
          profit_ratio=profit_ratio,
          stake_currency=strategy.config["stake_currency"],
          coin_amount=buyback_3_total_amount,
        )
      )
      log.info(
        f"Buyback de-risk (buyback_3_derisk) [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Coin amount: {buyback_3_total_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}% | Grind profit: {(grind_profit * 100.0):.2f}%"
      )
      order_tag = "buyback_3_derisk"
      for grind_entry_id in buyback_3_buy_orders:
        order_tag += " " + str(grind_entry_id)
      if has_order_tags:
        return -ft_sell_amount, order_tag
      else:
        return -ft_sell_amount

  return None


