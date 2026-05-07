"""Emergency stoploss exit helper long-side library extracted from NFI.""" 
def long_exit_stoploss(
    strategy,
    mode_name: str,
    current_rate: float,
    profit_stake: float,
    profit_ratio: float,
    profit_current_stake_ratio: float,
    profit_init_ratio: float,
    max_profit: float,
    max_loss: float,
    filled_entries,
    filled_exits,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade: "Trade",
    current_time: "datetime",
    buy_tag,
  ) -> tuple:
    is_backtest = strategy.is_backtest_mode()
    is_system_v3 = strategy.is_system_v3(trade)
    is_system_v3_1 = strategy.is_system_v3_1(trade)
    is_system_v3_2 = strategy.is_system_v3_2(trade)
    if not strategy.stops_enable:
      return False, None
    if is_system_v3_2:
      # Stoploss doom
      if strategy.system_v3_2_stops_enable and (
        profit_stake
        < -(
          filled_entries[0].cost
          * (
            strategy.system_v3_2_stop_threshold_doom_futures
            if strategy.is_futures_mode
            else strategy.system_v3_2_stop_threshold_doom_spot
          )
          / trade.leverage
        )
      ):
        return True, f"exit_{mode_name}_stoploss_doom"
    elif is_system_v3_1:
      # Stoploss doom
      if strategy.doom_stops_enable and (
        profit_stake
        < -(
          filled_entries[0].cost
          * (
            strategy.system_v3_1_stop_threshold_doom_futures
            if strategy.is_futures_mode
            else strategy.system_v3_1_stop_threshold_doom_spot
          )
          / trade.leverage
        )
      ):
        return True, f"exit_{mode_name}_stoploss_doom"
    elif is_system_v3:
      # Stoploss doom
      if strategy.doom_stops_enable and (
        profit_stake
        < -(
          filled_entries[0].cost
          * (
            strategy.system_v3_stop_threshold_doom_futures
            if strategy.is_futures_mode
            else strategy.system_v3_stop_threshold_doom_spot
          )
          / trade.leverage
        )
      ):
        return True, f"exit_{mode_name}_stoploss_doom"
    else:
      # Stoploss doom
      if (
        strategy.doom_stops_enable
        and (
          profit_stake
          < -(
            filled_entries[0].cost
            * (strategy.stop_threshold_doom_futures if strategy.is_futures_mode else strategy.stop_threshold_doom_spot)
          )
        )
        and (strategy.has_valid_entry_conditions(trade, current_rate, last_candle, previous_candle_1) == False)
        # temporary
        and (trade.open_date_utc.replace(tzinfo=None) >= datetime(2024, 9, 13) or is_backtest)
      ):
        return True, f"exit_{mode_name}_stoploss_doom"

    # Stoploss u_e
    if (
      strategy.u_e_stops_enable
      and (
        profit_stake
        < -(
          filled_entries[0].cost * (strategy.stop_threshold_futures if strategy.is_futures_mode else strategy.stop_threshold_spot)
          # / trade.leverage
        )
      )
      and (last_candle["close"] < last_candle["EMA_200"])
      and (last_candle["CMF_20"] < -0.0)
      and (((last_candle["EMA_200"] - last_candle["close"]) / last_candle["close"]) < 0.010)
      and (last_candle["RSI_14"] > previous_candle_1["RSI_14"])
      and (last_candle["RSI_14"] > (last_candle["RSI_14_1h"] + 24.0))
      # and (current_time - timedelta(minutes=720) > trade.open_date_utc)
      # temporary
      and (trade.open_date_utc.replace(tzinfo=None) >= datetime(2025, 4, 3) or is_backtest)
    ):
      return True, f"exit_{mode_name}_stoploss_u_e"

    #  Here ends exit signal conditions for long_exit_stoploss

    return False, None

