"""Shared exit signal aggregator long-side library extracted from NFI.""" 
def long_exit_signals(
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
      (last_candle["RSI_14"] > 84.0)
      and (last_candle["close"] > last_candle["BBU_20_2.0"])
      and (previous_candle_1["close"] > previous_candle_1["BBU_20_2.0"])
      and (previous_candle_2["close"] > previous_candle_2["BBU_20_2.0"])
      and (previous_candle_3["close"] > previous_candle_3["BBU_20_2.0"])
      and (previous_candle_4["close"] > previous_candle_4["BBU_20_2.0"])
    ):
      if last_candle["close"] > last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_1_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_1_2_1"

    # Sell signal 2
    elif (
      (last_candle["RSI_14"] > 86.0)
      and (last_candle["close"] > last_candle["BBU_20_2.0"])
      and (previous_candle_1["close"] > previous_candle_1["BBU_20_2.0"])
      and (previous_candle_2["close"] > previous_candle_2["BBU_20_2.0"])
    ):
      if last_candle["close"] > last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_2_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_2_2_1"

    # Sell signal 3
    elif last_candle["RSI_14"] > 88.0:
      if last_candle["close"] > last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_3_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_3_2_1"

    # Sell signal 4
    elif (last_candle["RSI_14"] > 84.0) and (last_candle["RSI_14_1h"] > 80.0):
      if last_candle["close"] > last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_4_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_4_2_1"

    # Sell signal 6
    elif (
      (last_candle["close"] < last_candle["EMA_200"])
      and (last_candle["close"] > last_candle["EMA_50"])
      and (last_candle["RSI_14"] > 79.0)
    ):
      if current_profit > 0.01:
        return True, f"exit_{mode_name}_6_1"

    # # Sell signal 7
    # elif (last_candle["RSI_14_1h"] > 79.0) and (last_candle["crossed_below_EMA_12_26"]):
    #   if last_candle["close"] > last_candle["EMA_200"]:
    #     if current_profit > 0.01:
    #       return True, f"exit_{mode_name}_7_1_1"
    #   else:
    #     if current_profit > 0.01:
    #       return True, f"exit_{mode_name}_7_2_1"

    # Sell signal 8
    elif last_candle["close"] > last_candle["BBU_20_2.0_1h"] * 1.14:
      if last_candle["close"] > last_candle["EMA_200"]:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_8_1_1"
      else:
        if current_profit > 0.01:
          return True, f"exit_{mode_name}_8_2_1"

    #  Here ends exit signal conditions for long_exit_signals

    return False, None

