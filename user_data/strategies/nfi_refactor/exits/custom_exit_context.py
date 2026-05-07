"""Custom exit context preparation extracted from NFI."""


def prepare_custom_exit_context(strategy, pair: str, trade, current_rate: float):
  df, _ = strategy.dp.get_analyzed_dataframe(pair, strategy.timeframe)
  if len(df) < 6:
    return None
  last_candle = df.iloc[-1].squeeze()
  previous_candle_1 = df.iloc[-2].squeeze()
  previous_candle_2 = df.iloc[-3].squeeze()
  previous_candle_3 = df.iloc[-4].squeeze()
  previous_candle_4 = df.iloc[-5].squeeze()
  previous_candle_5 = df.iloc[-6].squeeze()

  enter_tag = "empty"
  if hasattr(trade, "enter_tag") and trade.enter_tag is not None:
    enter_tag = trade.enter_tag
  enter_tags = enter_tag.split()

  filled_entries = trade.select_filled_orders(trade.entry_side)
  filled_exits = trade.select_filled_orders(trade.exit_side)

  profit_stake = 0.0
  profit_ratio = 0.0
  profit_current_stake_ratio = 0.0
  profit_init_ratio = 0.0
  profit_stake, profit_ratio, profit_current_stake_ratio, profit_init_ratio = strategy.calc_total_profit(
    trade, filled_entries, filled_exits, current_rate
  )

  return {
    "last_candle": last_candle,
    "previous_candle_1": previous_candle_1,
    "previous_candle_2": previous_candle_2,
    "previous_candle_3": previous_candle_3,
    "previous_candle_4": previous_candle_4,
    "previous_candle_5": previous_candle_5,
    "enter_tag": enter_tag,
    "enter_tags": enter_tags,
    "filled_entries": filled_entries,
    "filled_exits": filled_exits,
    "profit_stake": profit_stake,
    "profit_ratio": profit_ratio,
    "profit_current_stake_ratio": profit_current_stake_ratio,
    "profit_init_ratio": profit_init_ratio,
    "max_profit": 0.0,
    "max_loss": 0.0,
  }
