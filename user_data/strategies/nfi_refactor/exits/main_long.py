"""Main profit ladder exit helper long-side library extracted from NFI.""" 
def long_exit_main(
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
    if last_candle["close"] > last_candle["EMA_200"]:
      if 0.01 > current_profit >= 0.001:
        if last_candle["RSI_14"] < 10.0:
          return True, f"exit_{mode_name}_o_0"
      elif 0.02 > current_profit >= 0.01:
        if last_candle["RSI_14"] < 28.0:
          return True, f"exit_{mode_name}_o_1"
      elif 0.03 > current_profit >= 0.02:
        if last_candle["RSI_14"] < 30.0:
          return True, f"exit_{mode_name}_o_2"
      elif 0.04 > current_profit >= 0.03:
        if last_candle["RSI_14"] < 32.0:
          return True, f"exit_{mode_name}_o_3"
      elif 0.05 > current_profit >= 0.04:
        if last_candle["RSI_14"] < 34.0:
          return True, f"exit_{mode_name}_o_4"
      elif 0.06 > current_profit >= 0.05:
        if last_candle["RSI_14"] < 36.0:
          return True, f"exit_{mode_name}_o_5"
      elif 0.07 > current_profit >= 0.06:
        if last_candle["RSI_14"] < 38.0:
          return True, f"exit_{mode_name}_o_6"
      elif 0.08 > current_profit >= 0.07:
        if last_candle["RSI_14"] < 40.0:
          return True, f"exit_{mode_name}_o_7"
      elif 0.09 > current_profit >= 0.08:
        if last_candle["RSI_14"] < 42.0:
          return True, f"exit_{mode_name}_o_8"
      elif 0.1 > current_profit >= 0.09:
        if last_candle["RSI_14"] < 44.0:
          return True, f"exit_{mode_name}_o_9"
      elif 0.12 > current_profit >= 0.1:
        if last_candle["RSI_14"] < 46.0:
          return True, f"exit_{mode_name}_o_10"
      elif 0.2 > current_profit >= 0.12:
        if last_candle["RSI_14"] < 44.0:
          return True, f"exit_{mode_name}_o_11"
      elif current_profit >= 0.2:
        if last_candle["RSI_14"] < 42.0:
          return True, f"exit_{mode_name}_o_12"
    elif last_candle["close"] < last_candle["EMA_200"]:
      if 0.01 > current_profit >= 0.001:
        if last_candle["RSI_14"] < 12.0:
          return True, f"exit_{mode_name}_u_0"
      elif 0.02 > current_profit >= 0.01:
        if last_candle["RSI_14"] < 30.0:
          return True, f"exit_{mode_name}_u_1"
      elif 0.03 > current_profit >= 0.02:
        if last_candle["RSI_14"] < 32.0:
          return True, f"exit_{mode_name}_u_2"
      elif 0.04 > current_profit >= 0.03:
        if last_candle["RSI_14"] < 34.0:
          return True, f"exit_{mode_name}_u_3"
      elif 0.05 > current_profit >= 0.04:
        if last_candle["RSI_14"] < 36.0:
          return True, f"exit_{mode_name}_u_4"
      elif 0.06 > current_profit >= 0.05:
        if last_candle["RSI_14"] < 38.0:
          return True, f"exit_{mode_name}_u_5"
      elif 0.07 > current_profit >= 0.06:
        if last_candle["RSI_14"] < 40.0:
          return True, f"exit_{mode_name}_u_6"
      elif 0.08 > current_profit >= 0.07:
        if last_candle["RSI_14"] < 42.0:
          return True, f"exit_{mode_name}_u_7"
      elif 0.09 > current_profit >= 0.08:
        if last_candle["RSI_14"] < 44.0:
          return True, f"exit_{mode_name}_u_8"
      elif 0.1 > current_profit >= 0.09:
        if last_candle["RSI_14"] < 46.0:
          return True, f"exit_{mode_name}_u_9"
      elif 0.12 > current_profit >= 0.1:
        if last_candle["RSI_14"] < 48.0:
          return True, f"exit_{mode_name}_u_10"
      elif 0.2 > current_profit >= 0.12:
        if last_candle["RSI_14"] < 46.0:
          return True, f"exit_{mode_name}_u_11"
      elif current_profit >= 0.2:
        if last_candle["RSI_14"] < 44.0:
          return True, f"exit_{mode_name}_u_12"

    #  Here ends exit signal conditions for long_exit_main

    return False, None

