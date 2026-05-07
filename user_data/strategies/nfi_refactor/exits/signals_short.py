"""Shared exit signal aggregator short-side library extracted from NFI.""" 
def short_exit_signals(
    strategy,
    mode_name: str,
    current_profit: float,
    max_profit: float,
    max_loss: float,
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
    # Sell signal 1
    if (
      (last_candle["RSI_14"] < 16.0)
      and (last_candle["close"] < last_candle["BBL_20_2.0"])
      and (previous_candle_1["close"] < previous_candle_1["BBL_20_2.0"])
      and (previous_candle_2["close"] < previous_candle_2["BBL_20_2.0"])
      and (previous_candle_3["close"] < previous_candle_3["BBL_20_2.0"])
      and (previous_candle_4["close"] < previous_candle_4["BBL_20_2.0"])
    ):
      if last_candle["close"] < last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_1_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_1_2_1"

    # Sell signal 2
    elif (
      (last_candle["RSI_14"] < 14.0)
      and (last_candle["close"] < last_candle["BBL_20_2.0"])
      and (previous_candle_1["close"] < previous_candle_1["BBL_20_2.0"])
      and (previous_candle_2["close"] < previous_candle_2["BBL_20_2.0"])
    ):
      if last_candle["close"] < last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_2_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_2_2_1"

    # Sell signal 3
    elif last_candle["RSI_14"] < 12.0:
      if last_candle["close"] < last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_3_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_3_2_1"

    # Sell signal 4
    elif (last_candle["RSI_14"] < 16.0) and (last_candle["RSI_14_1h"] < 20.0):
      if last_candle["close"] < last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_4_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_4_2_1"

    # Sell signal 6
    elif (
      (last_candle["close"] > last_candle["EMA_200"])
      and (last_candle["close"] < last_candle["EMA_50"])
      and (last_candle["RSI_14"] < 21.0)
    ):
      if current_profit > 0.01:
        return True, f"exit_{mode_name}_6_1"

    # # Sell signal 7
    # elif (last_candle["RSI_14_1h"] < 21.0) and (last_candle["crossed_above_EMA_12_26"]):
    #   if last_candle["close"] < last_candle["EMA_200"]:
    #     if current_profit > 0.01:
    #       return True, f"exit_{mode_name}_7_1_1"
    #   else:
    #     if current_profit > 0.01:
    #       return True, f"exit_{mode_name}_7_2_1"

    # Sell signal 8
    elif last_candle["close"] < last_candle["BBL_20_2.0_1h"] * 0.86:
      if last_candle["close"] < last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_8_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_8_2_1"

    #  Here ends exit signal conditions for short_exit_signals

    return False, None
