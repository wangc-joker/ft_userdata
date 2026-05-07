"""Rebuy position-adjustment handlers extracted from NFI."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from freqtrade.persistence import Trade


log = logging.getLogger(__name__)


@dataclass
class RebuyAdjustmentContext:
  min_stake: float
  max_stake: float
  last_candle: object
  filled_orders: list
  filled_entries: list
  filled_exits: list
  count_of_exits: int
  has_order_tags: bool
  exit_rate: float
  profit_stake: float
  profit_ratio: float
  slice_amount: float
  slice_profit_entry: float


@dataclass
class RebuySubGrindState:
  partial_sell: bool
  sub_grind_count: int
  total_amount: float
  total_cost: float
  current_open_rate: float
  current_grind_stake: float
  current_grind_stake_profit: float


@dataclass
class RebuyModeConfig:
  stakes: list
  thresholds: list


@dataclass
class RebuyEntryAttempt:
  handled: bool
  adjustment: object


def get_rebuy_exit_rate(strategy, trade: Trade, current_rate: float) -> float:
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
  return exit_rate


def get_rebuy_mode_config(strategy, use_v3: bool = False) -> RebuyModeConfig:
  if use_v3:
    stakes = (
      strategy.system_v3_rebuy_mode_stakes_futures
      if strategy.is_futures_mode
      else strategy.system_v3_rebuy_mode_stakes_spot
    )
    thresholds = (
      strategy.system_v3_rebuy_mode_thresholds_futures
      if strategy.is_futures_mode
      else strategy.system_v3_rebuy_mode_thresholds_spot
    )
  else:
    stakes = strategy.rebuy_mode_stakes_futures if strategy.is_futures_mode else strategy.rebuy_mode_stakes_spot
    thresholds = (
      strategy.rebuy_mode_thresholds_futures if strategy.is_futures_mode else strategy.rebuy_mode_thresholds_spot
    )
  return RebuyModeConfig(stakes=stakes, thresholds=thresholds)


def get_rebuy_sub_grind_order_sides(is_short: bool) -> tuple:
  if is_short:
    return "sell", "buy"
  return "buy", "sell"


def build_rebuy_adjustment_context(
  strategy,
  trade: Trade,
  current_rate: float,
  min_stake: Optional[float],
  max_stake: float,
) -> Optional[RebuyAdjustmentContext]:
  # min/max stakes include leverage. The return amounts is before leverage.
  min_stake /= trade.leverage
  max_stake /= trade.leverage

  df, _ = strategy.dp.get_analyzed_dataframe(trade.pair, strategy.timeframe)
  if len(df) < 2:
    return None
  last_candle = df.iloc[-1].squeeze()

  # we already waiting for an order to get filled
  if trade.has_open_orders:
    return None

  filled_orders = trade.select_filled_orders()
  filled_entries = trade.select_filled_orders(trade.entry_side)
  filled_exits = trade.select_filled_orders(trade.exit_side)
  count_of_entries = trade.nr_of_successful_entries
  count_of_exits = trade.nr_of_successful_exits

  if count_of_entries == 0:
    return None

  has_order_tags = hasattr(filled_orders[0], "ft_order_tag")
  exit_rate = get_rebuy_exit_rate(strategy, trade, current_rate)
  profit_stake, profit_ratio, profit_current_stake_ratio, profit_init_ratio = strategy.calc_total_profit(
    trade, filled_entries, filled_exits, exit_rate
  )
  slice_amount = filled_entries[0].cost
  slice_profit_entry = (exit_rate - filled_entries[-1].safe_price) / filled_entries[-1].safe_price

  return RebuyAdjustmentContext(
    min_stake=min_stake,
    max_stake=max_stake,
    last_candle=last_candle,
    filled_orders=filled_orders,
    filled_entries=filled_entries,
    filled_exits=filled_exits,
    count_of_exits=count_of_exits,
    has_order_tags=has_order_tags,
    exit_rate=exit_rate,
    profit_stake=profit_stake,
    profit_ratio=profit_ratio,
    slice_amount=slice_amount,
    slice_profit_entry=slice_profit_entry,
  )


def build_rebuy_sub_grind_state(
  strategy,
  trade: Trade,
  filled_orders: list,
  exit_rate: float,
  min_stake: float,
  sub_entry_side: str,
  partial_exit_side: str,
) -> RebuySubGrindState:
  partial_sell = False
  sub_grind_count = 0
  total_amount = 0.0
  total_cost = 0.0
  current_open_rate = 0.0
  current_grind_stake = 0.0
  current_grind_stake_profit = 0.0

  for order in reversed(filled_orders):
    if (order.ft_order_side == sub_entry_side) and (order is not filled_orders[0]):
      sub_grind_count += 1
      total_amount += order.safe_filled
      total_cost += order.safe_filled * order.safe_price
    elif order.ft_order_side == partial_exit_side:
      if (order.safe_remaining * exit_rate / (trade.leverage if strategy.is_futures_mode else 1.0)) > min_stake:
        partial_sell = True
      break

  if sub_grind_count > 0:
    current_open_rate = total_cost / total_amount
    current_grind_stake = total_amount * exit_rate * (1 - trade.fee_close)
    current_grind_stake_profit = current_grind_stake - total_cost

  return RebuySubGrindState(
    partial_sell=partial_sell,
    sub_grind_count=sub_grind_count,
    total_amount=total_amount,
    total_cost=total_cost,
    current_open_rate=current_open_rate,
    current_grind_stake=current_grind_stake,
    current_grind_stake_profit=current_grind_stake_profit,
  )


def build_rebuy_entry_amount(
  slice_amount: float,
  stake_multiplier: float,
  leverage: float,
  min_stake: float,
  max_stake: float,
) -> Optional[float]:
  buy_amount = slice_amount * stake_multiplier / leverage
  if buy_amount < (min_stake * 1.5):
    buy_amount = min_stake * 1.5
  if buy_amount > max_stake:
    return None
  return buy_amount


def is_rebuy_slot_available(partial_sell: bool, sub_grind_count: int, max_sub_grinds: int) -> bool:
  return (not partial_sell) and (sub_grind_count < max_sub_grinds)


def long_rebuy_entry_allowed(last_candle, slice_profit_entry: float, threshold: float) -> bool:
  return (
    (slice_profit_entry < threshold)
    and (last_candle["RSI_3"] > 10.0)
    and (last_candle["RSI_3_15m"] > 10.0)
    and (last_candle["RSI_14"] < 40.0)
    and (last_candle["ROC_2"] > -0.0)
    and (last_candle["close"] < (last_candle["EMA_26"] * 0.988))
  )


def long_rebuy_v3_entry_allowed(last_candle, slice_profit_entry: float, threshold: float) -> bool:
  return (
    (slice_profit_entry < threshold)
    and (last_candle["protections_long_global"] == True)
    and (last_candle["RSI_3"] > 10.0)
    and (last_candle["RSI_3_15m"] > 10.0)
    and (last_candle["AROONU_14"] < 30.0)
    and (last_candle["AROONU_14_15m"] < 30.0)
    and (last_candle["close"] < (last_candle["EMA_26"] * 0.988))
  )


def short_rebuy_entry_allowed(last_candle, slice_profit_entry: float, threshold: float) -> bool:
  return (
    (-slice_profit_entry < threshold)
    and (last_candle["RSI_3"] < 90.0)
    and (last_candle["RSI_3_15m"] < 90.0)
    and (last_candle["RSI_14"] > 60.0)
    and (last_candle["ROC_2"] < 0.0)
    and (last_candle["close"] > (last_candle["EMA_26"] * 1.012))
  )


def short_rebuy_v3_entry_allowed(last_candle, slice_profit_entry: float, threshold: float) -> bool:
  return (
    (-slice_profit_entry < threshold)
    and (last_candle["protections_long_global"] == True)
    and (last_candle["RSI_3"] < 90.0)
    and (last_candle["RSI_3_15m"] < 90.0)
    and (last_candle["AROOND_14"] < 30.0)
    and (last_candle["AROOND_14_15m"] < 30.0)
    and (last_candle["close"] < (last_candle["EMA_26"] * 1.012))
  )


def return_rebuy_entry_adjustment(
  strategy,
  trade: Trade,
  current_time: datetime,
  current_rate: float,
  buy_amount: float,
  profit_stake: float,
  profit_ratio: float,
  has_order_tags: bool,
):
  strategy.dp.send_msg(
    strategy.notification_msg(
      "rebuy",
      tag="r",
      pair=trade.pair,
      rate=current_rate,
      stake_amount=buy_amount,
      profit_stake=profit_stake,
      profit_ratio=profit_ratio,
      stake_currency=strategy.config["stake_currency"],
    )
  )
  log.info(
    f"Rebuy (r) [{current_time}] [{trade.pair}] | Rate: {current_rate} | Stake amount: {buy_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
  )
  if has_order_tags:
    return buy_amount, "r"
  return buy_amount


def try_return_rebuy_entry_adjustment(
  strategy,
  trade: Trade,
  current_time: datetime,
  current_rate: float,
  slice_amount: float,
  stake_multiplier: float,
  min_stake: float,
  max_stake: float,
  profit_stake: float,
  profit_ratio: float,
  has_order_tags: bool,
):
  buy_amount = build_rebuy_entry_amount(
    slice_amount,
    stake_multiplier,
    trade.leverage,
    min_stake,
    max_stake,
  )
  if buy_amount is None:
    return None
  return return_rebuy_entry_adjustment(
    strategy,
    trade,
    current_time,
    current_rate,
    buy_amount,
    profit_stake,
    profit_ratio,
    has_order_tags,
  )


def try_build_rebuy_entry_attempt(
  strategy,
  trade: Trade,
  current_time: datetime,
  current_rate: float,
  filled_orders: list,
  exit_rate: float,
  min_stake: float,
  max_stake: float,
  last_candle,
  slice_amount: float,
  slice_profit_entry: float,
  profit_stake: float,
  profit_ratio: float,
  has_order_tags: bool,
  is_short: bool,
  use_v3: bool,
  entry_allowed,
) -> RebuyEntryAttempt:
  rebuy_mode_config = get_rebuy_mode_config(strategy, use_v3=use_v3)
  max_sub_grinds = len(rebuy_mode_config.stakes)
  sub_entry_side, partial_exit_side = get_rebuy_sub_grind_order_sides(is_short=is_short)
  sub_grind_state = build_rebuy_sub_grind_state(
    strategy,
    trade,
    filled_orders,
    exit_rate,
    min_stake,
    sub_entry_side=sub_entry_side,
    partial_exit_side=partial_exit_side,
  )
  sub_grind_count = sub_grind_state.sub_grind_count

  if not is_rebuy_slot_available(sub_grind_state.partial_sell, sub_grind_count, max_sub_grinds):
    return RebuyEntryAttempt(handled=False, adjustment=None)

  if not entry_allowed(
    last_candle,
    slice_profit_entry,
    rebuy_mode_config.thresholds[sub_grind_count],
  ):
    return RebuyEntryAttempt(handled=False, adjustment=None)

  adjustment = try_return_rebuy_entry_adjustment(
    strategy,
    trade,
    current_time,
    current_rate,
    slice_amount,
    rebuy_mode_config.stakes[sub_grind_count],
    min_stake,
    max_stake,
    profit_stake,
    profit_ratio,
    has_order_tags,
  )
  return RebuyEntryAttempt(handled=True, adjustment=adjustment)


def try_build_rebuy_entry_attempt_from_context(
  strategy,
  trade: Trade,
  current_time: datetime,
  current_rate: float,
  context: RebuyAdjustmentContext,
  is_short: bool,
  use_v3: bool,
  entry_allowed,
) -> RebuyEntryAttempt:
  return try_build_rebuy_entry_attempt(
    strategy,
    trade,
    current_time,
    current_rate,
    context.filled_orders,
    context.exit_rate,
    context.min_stake,
    context.max_stake,
    context.last_candle,
    context.slice_amount,
    context.slice_profit_entry,
    context.profit_stake,
    context.profit_ratio,
    context.has_order_tags,
    is_short=is_short,
    use_v3=use_v3,
    entry_allowed=entry_allowed,
  )


def return_rebuy_derisk_adjustment(
  strategy,
  trade: Trade,
  current_time: datetime,
  exit_rate: float,
  sell_amount: float,
  ft_sell_amount: float,
  profit_stake: float,
  profit_ratio: float,
  has_order_tags: bool,
):
  strategy.dp.send_msg(
    f"❌​​ ​**Rebuy De-risk:** `Level 3`\n"
    f"🪙​ **Pair:** `{trade.pair}`\n"
    f"〽️​ **Rate:** `{exit_rate}`\n"
    f"💰 **Stake amount:** `{sell_amount}`\n"
    f"💵​ **Profit (stake):** `{profit_stake}`\n"
    f"💸 **Profit (percent):** `{(profit_ratio * 100.0):.2f}%`"
  )
  log.info(
    f"Rebuy De-risk Level 3 [{current_time}] [{trade.pair}] | Rate: {exit_rate} | Stake amount: {sell_amount} | Profit (stake): {profit_stake} | Profit: {(profit_ratio * 100.0):.2f}%"
  )
  if has_order_tags:
    return -ft_sell_amount, "derisk_level_3"
  return -ft_sell_amount


def try_return_rebuy_derisk_adjustment(
  strategy,
  trade: Trade,
  current_time: datetime,
  exit_rate: float,
  min_stake: float,
  slice_amount: float,
  profit_stake: float,
  profit_ratio: float,
  has_order_tags: bool,
):
  derisk_threshold = strategy.rebuy_mode_derisk_futures if strategy.is_futures_mode else strategy.rebuy_mode_derisk_spot
  if not strategy.derisk_enable:
    return None
  if profit_stake >= (slice_amount * derisk_threshold):
    return None

  sell_amount = trade.amount * exit_rate / trade.leverage - (min_stake * 1.55)
  ft_sell_amount = sell_amount * trade.leverage * (trade.stake_amount / trade.amount) / exit_rate
  if sell_amount > min_stake and ft_sell_amount > min_stake:
    return return_rebuy_derisk_adjustment(
      strategy,
      trade,
      current_time,
      exit_rate,
      sell_amount,
      ft_sell_amount,
      profit_stake,
      profit_ratio,
      has_order_tags,
    )
  return None


def try_return_rebuy_derisk_adjustment_from_context(
  strategy,
  trade: Trade,
  current_time: datetime,
  context: RebuyAdjustmentContext,
):
  return try_return_rebuy_derisk_adjustment(
    strategy,
    trade,
    current_time,
    context.exit_rate,
    context.min_stake,
    context.slice_amount,
    context.profit_stake,
    context.profit_ratio,
    context.has_order_tags,
  )


def has_rebuy_derisk_exit(context: RebuyAdjustmentContext) -> bool:
  return (context.count_of_exits > 0) and (context.filled_exits[0].ft_order_tag in ["derisk_level_3"])


def return_rebuy_grind_v2_after_derisk(
  strategy,
  trade: Trade,
  enter_tags,
  current_time: datetime,
  current_rate: float,
  current_profit: float,
  current_entry_rate: float,
  current_exit_rate: float,
  current_entry_profit: float,
  current_exit_profit: float,
  context: RebuyAdjustmentContext,
  is_short: bool,
):
  adjustment_func = (
    strategy.short_grind_adjust_trade_position_v2
    if is_short
    else strategy.long_grind_adjust_trade_position_v2
  )
  return adjustment_func(
    trade,
    enter_tags,
    current_time,
    current_rate,
    current_profit,
    context.min_stake,
    context.max_stake,
    current_entry_rate,
    current_exit_rate,
    current_entry_profit,
    current_exit_profit,
  )


def run_rebuy_adjust_trade_position(
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
  is_short: bool,
  use_v3: bool,
  entry_allowed,
  allow_derisk: bool,
) -> Optional[float]:
  context = build_rebuy_adjustment_context(strategy, trade, current_rate, min_stake, max_stake)
  if context is None:
    return None

  # The first exit is de-risk (providing the trade is still open)
  if allow_derisk and has_rebuy_derisk_exit(context):
    return return_rebuy_grind_v2_after_derisk(
      strategy,
      trade,
      enter_tags,
      current_time,
      current_rate,
      current_profit,
      current_entry_rate,
      current_exit_rate,
      current_entry_profit,
      current_exit_profit,
      context,
      is_short=is_short,
    )

  entry_attempt = try_build_rebuy_entry_attempt_from_context(
    strategy,
    trade,
    current_time,
    current_rate,
    context,
    is_short=is_short,
    use_v3=use_v3,
    entry_allowed=entry_allowed,
  )
  if entry_attempt.handled:
    return entry_attempt.adjustment

  if not allow_derisk:
    return None

  derisk_adjustment = try_return_rebuy_derisk_adjustment_from_context(
    strategy,
    trade,
    current_time,
    context,
  )
  if derisk_adjustment is not None:
    return derisk_adjustment

  return None


def long_rebuy_adjust_trade_position(
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
) -> Optional[float]:
  return run_rebuy_adjust_trade_position(
    strategy,
    trade,
    enter_tags,
    current_time,
    current_rate,
    current_profit,
    min_stake,
    max_stake,
    current_entry_rate,
    current_exit_rate,
    current_entry_profit,
    current_exit_profit,
    is_short=False,
    use_v3=False,
    entry_allowed=long_rebuy_entry_allowed,
    allow_derisk=True,
  )

# Long Rebuy Adjust Trade Position v3
# ---------------------------------------------------------------------------------------------

def long_rebuy_adjust_trade_position_v3(
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
) -> Optional[float]:
  return run_rebuy_adjust_trade_position(
    strategy,
    trade,
    enter_tags,
    current_time,
    current_rate,
    current_profit,
    min_stake,
    max_stake,
    current_entry_rate,
    current_exit_rate,
    current_entry_profit,
    current_exit_profit,
    is_short=False,
    use_v3=True,
    entry_allowed=long_rebuy_v3_entry_allowed,
    allow_derisk=False,
  )

def short_rebuy_adjust_trade_position(
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
) -> Optional[float]:
  return run_rebuy_adjust_trade_position(
    strategy,
    trade,
    enter_tags,
    current_time,
    current_rate,
    current_profit,
    min_stake,
    max_stake,
    current_entry_rate,
    current_exit_rate,
    current_entry_profit,
    current_exit_profit,
    is_short=True,
    use_v3=False,
    entry_allowed=short_rebuy_entry_allowed,
    allow_derisk=True,
  )

# Short Rebuy Adjust Trade Position v3
# ---------------------------------------------------------------------------------------------

def short_rebuy_adjust_trade_position_v3(
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
) -> Optional[float]:
  return run_rebuy_adjust_trade_position(
    strategy,
    trade,
    enter_tags,
    current_time,
    current_rate,
    current_profit,
    min_stake,
    max_stake,
    current_entry_rate,
    current_exit_rate,
    current_entry_profit,
    current_exit_profit,
    is_short=True,
    use_v3=True,
    entry_allowed=short_rebuy_v3_entry_allowed,
    allow_derisk=False,
  )

