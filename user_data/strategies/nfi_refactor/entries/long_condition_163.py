"""NFI long entry condition #163."""

def append_long_163(df, long_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI long condition #163, the scalp-mode long entry."""
    # Protections
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    long_entry_logic.append(df["protections_long_global"] == True)

    long_entry_logic.append((df["RSI_3"] > 10.0) & (df["RSI_3_15m"] > 10.0) & (df["RSI_3_1h"] > 20.0))

    long_entry_logic.append(
      # 5m & 15m & 4h down mnove, 4h high
      ((df["RSI_3"] > 15.0) | (df["RSI_3_15m"] > 20.0) | (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_4h"] < 80.0))
      # 5m & 15m & 1d down move, 1h high
      & ((df["RSI_3"] > 15.0) | (df["RSI_3_15m"] > 25.0) | (df["RSI_3_1d"] > 25.0) | (df["AROONU_14_1h"] < 90.0))
      # 5m & 1h down move, 15m still high, 4h high
      & (
        (df["RSI_3"] > 20.0) | (df["RSI_3_1h"] > 40.0) | (df["RSI_14_15m"] < 40.0) | (df["AROONU_14_4h"] < 100.0)
      )
      # 5m & 1h & 15m down move, 1h still not low enough
      & ((df["RSI_3"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["RSI_3_1d"] > 15.0) | (df["AROONU_14_1h"] < 30.0))
      # 15m & 4h down move, 4h high
      & ((df["RSI_3"] > 15.0) | (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0))
      # 5m & 4h down move, 15m high
      & ((df["RSI_3"] > 15.0) | (df["RSI_3_4h"] > 45.0) | (df["AROONU_14_15m"] < 60.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 12.0) | (df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 100.0))
      # 15m & 1h & 4h & 1d down move
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 25.0) | (df["RSI_3_1d"] > 25.0))
      # 15m & 1h down move, 1h & 4h high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_3_1h"] > 25.0)
        | (df["AROONU_14_1h"] < 75.0)
        | (df["AROONU_14_4h"] < 100.0)
      )
      # 15m & 1h & 4h down move, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["RSI_3_4h"] > 35.0) | (df["ROC_9_1d"] < 40.0))
      # 15m & 1h & 4h down move, 1h downtrend, 4h high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_3_1h"] > 30.0)
        | (df["RSI_3_4h"] > 55.0)
        | (df["CMF_20_1h"] > -0.10)
        | (df["AROONU_14_4h"] < 80.0)
      )
      # 15m & 1h down move, 15m high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_15m"] < 60.0))
      # 15m & 1h down move, 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["RSI_14_4h"] < 85.0))
      # 15m & 1h down move, 15m still high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_15m"] < 40.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 70.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0))
      # 15m & 1h down move, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 30.0) | (df["ROC_9_1d"] < 30.0))
      # 15m & 1h & 4h down move, 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 35.0) | (df["RSI_3_4h"] > 65.0) | (df["MFI_14_4h"] < 85.0))
      # 15m & 1h & 1d down move, 15m high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_3_1h"] > 35.0)
        | (df["RSI_3_1d"] > 40.0)
        | (df["AROONU_14_15m"] < 60.0)
      )
      # 15m & 1h down move, 15m high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 35.0) | (df["AROONU_14_15m"] < 70.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 85.0))
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_3_1h"] > 40.0)
        | (df["AROONU_14_15m"] < 30.0)
        | (df["AROONU_14_1h"] < 80.0)
        | (df["AROONU_14_4h"] < 80.0)
      )
      # 15m & 1h down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 45.0) | (df["RSI_14_4h"] < 70.0) | (df["ROC_9_4h"] < 50.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0))
      # 15m & 4h down move, 15m high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 30.0) | (df["AROONU_14_15m"] < 60.0))
      # 15m & 4h down move, 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 30.0) | (df["AROONU_14_4h"] < 80.0))
      # 15m & 4h down move, 1h still high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_1h"] < 40.0))
      # 15m & 4h down move, 1d high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0))
      # 15m & 4h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 60.0))
      # 15m & 4h down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
      # 15m down move, 4h & 1d up move, 1d downtrend
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_4h"] < 90.0) | (df["RSI_3_1d"] < 80.0) | (df["CMF_20_1d"] > -0.2))
      # 15m & 1d down move, 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0))
      # 15m & 1h down move, 1h & 4h still high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_3_1d"] > 15.0)
        | (df["AROONU_14_1h"] < 50.0)
        | (df["AROONU_14_4h"] < 50.0)
      )
      # 15m & 1d down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 15.0) | (df["AROONU_14_1h"] < 100.0))
      # 15m & 1d down move, 1d high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 20.0) | (df["AROONU_14_1d"] < 80.0))
      # 15m & 1d down move, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 40.0) | (df["ROC_9_1d"] < 50.0))
      # 15m & 1d down move, 1d high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 50.0) | (df["AROONU_14_1d"] < 70.0))
      # 15m & 1d down move, 1d high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0))
      # 15m down move, 15m & 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_4h"] < 90.0))
      # 15m down move, 15m & 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_15m"] < 75.0) | (df["AROONU_14_1h"] < 100.0))
      # 15m down move, 1h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 90.0) | (df["ROC_9_1d"] < 80.0))
      # 15m down move, 1h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 100.0) | (df["ROC_9_1d"] < 40.0))
      # 15m down move, 4h still high, 4h downtrend
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_4h"] < 40.0) | (df["ROC_9_4h"] > -20.0))
      # 15m down move, 1d high & overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 100.0))
      # 15m down move, 15m still not low enough, 4h high
      & (
        (df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      )
      # 15m down move, 15m & 1h high
      & (
        (df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      )
      # 15m down move, 1h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["ROC_9_1d"] < 30.0))
      # 15m down move, 1h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["ROC_9_1d"] < 150.0))
      # 15m down move, 1h high & overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1h"] < 20.0))
      # 15m down move, 1h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1d"] < 100.0))
      # 15m down move, 4h high, 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_1d"] < 25.0))
      # 15m down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_4h"] < 25.0))
      # 15m down move, 4h high
      & (
        (df["RSI_3_15m"] > 15.0)
        | (df["RSI_14_4h"] < 70.0)
        | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
        | (df["EMA_9"] < (df["EMA_26"] * 0.972))
      )
      # 15m down move, 4h high and downtrend
      & ((df["RSI_3_15m"] > 15.0) | (df["CMF_20_4h"] > -0.2) | (df["AROONU_14_4h"] < 80.0))
      # 15m down move, 1h high, 4h overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 90.0) | (df["ROC_9_4h"] < 20.0))
      # 15m down move, 4h & 1d downtrend
      & ((df["RSI_3_15m"] > 15.0) | (df["ROC_9_4h"] > -20.0) | (df["ROC_9_1d"] > -20.0))
      # 15m & 1h down move, 1h downtrend, 1h downtrend, 15m still high, 1h high
      & (
        (df["RSI_3_15m"] > 20.0)
        | (df["RSI_3_1h"] > 35.0)
        | (df["CMF_20_1h"] > -0.10)
        | (df["AROONU_14_15m"] < 40.0)
        | (df["AROONU_14_1h"] < 85.0)
      )
      # 15m & 1h down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["RSI_3_1h"] > 45.0) | (df["RSI_14_4h"] < 70.0) | (df["ROC_9_4h"] < 50.0))
      # 15m & 4h down move, 15m high
      & ((df["RSI_3_15m"] > 20.0) | (df["RSI_3_4h"] > 25.0) | (df["AROONU_14_15m"] < 60.0))
      # 15m & 4h down move, 1h high
      & ((df["RSI_3_15m"] > 20.0) | (df["RSI_3_4h"] > 35.0) | (df["AROONU_14_1h"] < 100.0))
      # 15m & 1d down move, 4h high
      & ((df["RSI_3_15m"] > 20.0) | (df["RSI_3_1d"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0))
      # 15m down move, 15m still high, 4h high
      & (
        (df["RSI_3_15m"] > 20.0)
        | (df["RSI_14_15m"] < 40.0)
        | (df["RSI_14_4h"] < 75.0)
        | (df["AROONU_14_4h"] < 100.0)
      )
      # 15m down move, 4h downtrend, 4h overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["CMF_20_4h"] > -0.0) | (df["ROC_9_4h"] < 40.0))
      # 15m down move, 1h & 4h high, 1f overbought
      & (
        (df["RSI_3_15m"] > 20.0)
        | (df["AROONU_14_1h"] < 85.0)
        | (df["RSI_14_4h"] < 70.0)
        | (df["ROC_9_1d"] < 80.0)
      )
      # 15m down move, 1h & 4h high
      & ((df["RSI_3_15m"] > 20.0) | (df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 1d high, 4h overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_4h"] < 30.0))
      # 15m down move, 1h high & overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1h"] < 10.0))
      # 15m & 1d down move, 1d high
      & ((df["RSI_3_15m"] > 25.0) | (df["RSI_3_1d"] > 40.0) | (df["AROONU_14_1d"] < 80.0))
      # 15m down move, 4h high, 1d downtrend
      & ((df["RSI_3_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_1d"] > -30.0))
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (df["RSI_3_15m"] > 30.0)
        | (df["RSI_3_1h"] > 45.0)
        | (df["RSI_14_15m"] < 30.0)
        | (df["RSI_14_1h"] < 50.0)
        | (df["RSI_14_4h"] < 70.0)
        | (df["AROONU_14_15m"] < 20.0)
        | (df["AROONU_14_1h"] < 60.0)
        | (df["AROONU_14_4h"] < 100.0)
      )
      # 15m & 4h down move, 4h overbought
      & ((df["RSI_3_15m"] > 30.0) | (df["RSI_3_4h"] > 60.0) | (df["ROC_9_4h"] < 60.0))
      # 15m & 4h down move, 4h high
      & ((df["RSI_3_15m"] > 35.0) | (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
      # 1h & 4h down move, 1d high
      & ((df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0))
      # 1h & 4h down move, 4h high
      & ((df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_4h"] < 70.0))
      # 1h & 4h down move, 4h high
      & ((df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 45.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
      # 1h & 4h down move, 1d high
      & ((df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 65.0) | (df["AROONU_14_1d"] < 100.0))
      # 1h & 1d down move, 1d high
      & ((df["RSI_3_1h"] > 25.0) | (df["RSI_3_1d"] > 40.0) | (df["AROONU_14_1d"] < 70.0))
      # 1h down move, 15m downtrend, 4h still high
      & ((df["RSI_3_1h"] > 25.0) | (df["CMF_20_15m"] > -0.4) | (df["AROONU_14_4h"] < 50.0))
      # 1h down move, 4h downtrend, 4h high
      & ((df["RSI_3_1h"] > 25.0) | (df["CMF_20_4h"] > -0.25) | (df["AROONU_14_4h"] < 70.0))
      # 1h down move, 15m still high, 1d downtrend
      & ((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_15m"] < 40.0) | (df["ROC_9_1d"] > -20.0))
      # 1h down move, 1h & 4h high
      & ((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_1h"] < 60.0) | (df["AROONU_14_4h"] < 100.0))
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_1h"] < 90.0) | (df["CMF_20_1d"] > -0.2))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 20.0))
      # 1h down move, 1h still not low enough, 1d downtrend
      & ((df["RSI_3_1h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0) | (df["ROC_9_1d"] > -40.0))
      # 1h down move, 4h high, 1d overbought
      & ((df["RSI_3_1h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_1d"] < 25.0))
      # 1h & 4h down move, 1h still high
      & ((df["RSI_3_1h"] > 30.0) | (df["RSI_3_4h"] > 30.0) | (df["AROONU_14_1h"] < 40.0))
      # 1h & 1d down move, 1d still high
      & ((df["RSI_3_1h"] > 30.0) | (df["RSI_3_1d"] > 30.0) | (df["AROONU_14_1d"] < 40.0))
      # 1h down move, 15m & 4h high
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_15m"] < 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 95.0))
      # 1h down move, 15m & 4h high
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_4h"] < 90.0))
      # 1h down move, 1h high
      & ((df["RSI_3_1h"] > 30.0) | (df["MFI_14_1h"] < 80.0) | (df["AROONU_14_1h"] < 90.0))
      # 1h down move, 1h still high, 1d overbought
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 50.0) | (df["ROC_9_1d"] < 40.0))
      # 1h down move, 1h & 4h high
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 100.0))
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 90.0) | (df["CMF_20_1d"] > -0.2))
      # 1h down move, 1h highm 1d overbought
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 90.0) | (df["ROC_9_1d"] < 40.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 30.0))
      # 1h down move, 1d high, 4h overbought
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_4h"] < 20.0))
      # 1h & 4h down move, 1h still high, 4h high
      & ((df["RSI_3_1h"] > 35.0) | (df["RSI_3_4h"] > 60.0) | (df["RSI_14_1h"] < 50.0) | (df["RSI_14_4h"] < 70.0))
      # 1h down move, 15m still not low enough, 1h high
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_15m"] < 30.0) | (df["AROONU_14_1h"] < 80.0))
      # 1h down move, 1h & 1d high
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 60.0) | (df["AROONU_14_1d"] < 100.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_4h"] < 25.0))
      # 1h down move, 1h & 4h high
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0))
      # 1h down move, 1h & 1d high
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_1d"] < 90.0))
      # 1h & 1d down move, 1d high
      & ((df["RSI_3_1h"] > 40.0) | (df["RSI_3_1d"] > 55.0) | (df["AROONU_14_1d"] < 100.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_4h"] < 40.0))
      # 1h down move, 1h & 4h high
      & ((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 80.0))
      # 1h down move, 1h high, 1d overbought
      & ((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 85.0) | (df["ROC_9_1d"] < 80.0))
      # 1h down move, 1h high, 15m downtrend
      & ((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 90.0) | (df["ROC_9_15m"] > -10.0))
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1d"] > -40.0))
      # 1h & 4h down move, 1d overbought
      & ((df["RSI_3_1h"] > 45.0) | (df["RSI_3_4h"] > 65.0) | (df["ROC_9_1d"] < 200.0))
      # 1h & 1d down move, 4h high
      & ((df["RSI_3_1h"] > 45.0) | (df["RSI_3_1d"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 100.0) | (df["ROC_9_4h"] < 10.0))
      # 1h & 4h down move, 1h & 4h high
      & (
        (df["RSI_3_1h"] > 50.0)
        | (df["RSI_3_4h"] > 65.0)
        | (df["AROONU_14_1h"] < 85.0)
        | (df["AROONU_14_4h"] < 100.0)
      )
      # 1h down move, 15m & 1h high
      & ((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_15m"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
      # 1h down move, 4h & 1d high
      & ((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_4h"] < 90.0) | (df["AROONU_14_1d"] < 90.0))
      # 1h down move, 4h high, 1h overbought
      & ((df["RSI_3_1h"] > 55.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 20.0))
      # 1h down move, 15m & 1h high, 1d downtrend
      & (
        (df["RSI_3_1h"] > 60.0)
        | (df["AROONU_14_15m"] < 65.0)
        | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
        | (df["CMF_20_1d"] > -0.0)
      )
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0) | (df["ROC_9_1d"] > -20.0))
      # 4h down move, 15m high
      & ((df["RSI_3_4h"] > 3.0) | (df["AROONU_14_15m"] < 50.0))
      # 4h & 1d down move, 1d high
      & ((df["RSI_3_4h"] > 10.0) | (df["RSI_3_1d"] > 50.0) | (df["AROONU_14_1d"] < 90.0))
      # 4h down move, 15m still not low enough, 4h downtrend
      & ((df["RSI_3_4h"] > 10.0) | (df["AROONU_14_15m"] < 30.0) | (df["CMF_20_4h"] > -0.30))
      # 4h down move, 15m & 1h still not low enough
      & ((df["RSI_3_4h"] > 10.0) | (df["AROONU_14_15m"] < 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 25.0))
      # 4h down move, 4h still high
      & ((df["RSI_3_4h"] > 10.0) | (df["AROONU_14_4h"] < 40.0))
      # 4h down move, 1h still high, 4h downtrend
      & ((df["RSI_3_4h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["CMF_20_4h"] > -0.3))
      # 4h down move, 4h high
      & ((df["RSI_3_4h"] > 14.0) | (df["AROONU_14_4h"] < 60.0))
      # 4h down move, 1d high & overbought
      & ((df["RSI_3_4h"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0) | (df["ROC_9_1d"] < 20.0))
      # 4h down move, 15m still high, 1d overbought
      & ((df["RSI_3_4h"] > 20.0) | (df["AROONU_14_15m"] < 40.0) | (df["ROC_9_1d"] < 20.0))
      # 4h & 1d down move, 1h & 4h low
      & ((df["RSI_3_4h"] > 25.0) | (df["RSI_3_1d"] > 25.0) | (df["CMF_20_1h"] > -0.3) | (df["CMF_20_4h"] > -0.4))
      # 4h down move, 4h still high 1d downtrend
      & ((df["RSI_3_4h"] > 25.0) | (df["AROONU_14_4h"] < 50.0) | (df["ROC_9_1d"] > -20.0))
      # 4h down move, 1d high & overbought
      & ((df["RSI_3_4h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0) | (df["ROC_9_1d"] < 25.0))
      # 4h down move, 4h & 1d high
      & ((df["RSI_3_4h"] > 35.0) | (df["AROONU_14_4h"] < 70.0) | (df["AROONU_14_1d"] < 100.0))
      # 4h down move, 15m still high, 1d overbought
      & ((df["RSI_3_4h"] > 40.0) | (df["AROONU_14_15m"] < 50.0) | (df["ROC_9_1d"] < 50.0))
      # 4h down move, 4h high, 1d overbought
      & ((df["RSI_3_4h"] > 40.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_1d"] < 20.0))
      # 4h down move, 1h high, 1d downtrend
      & ((df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1d"] > -20.0))
      # 4h down move, 4h & 1d overbought
      & ((df["RSI_3_4h"] > 40.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] < 50.0))
      # 4h down move, 4h high, 1d overbought
      & ((df["RSI_3_4h"] > 45.0) | (df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1d"] < 20.0))
      # 4h down move, 1d high, 4h overbought
      & ((df["RSI_3_4h"] > 45.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_4h"] < 10.0))
      # 4h down move, 4h still high, 1d downtrend
      & ((df["RSI_3_4h"] > 50.0) | (df["RSI_14_4h"] < 40.0) | (df["ROC_9_1d"] > -30.0))
      # 4h down move, 4h high & overbought
      & ((df["RSI_3_4h"] > 50.0) | (df["AROONU_14_4h"] < 85.0) | (df["ROC_9_4h"] < 10.0))
      # 4h down move, 15m still high, 1d overbought
      & ((df["RSI_3_4h"] > 55.0) | (df["AROONU_14_15m"] < 40.0) | (df["ROC_9_1d"] < 100.0))
      # 4h & 1d down move, 4h high, 1d overbought
      & (
        (df["RSI_3_4h"] > 60.0) | (df["RSI_3_1d"] > 60.0) | (df["AROONU_14_4h"] < 75.0) | (df["ROC_9_1d"] < 40.0)
      )
      # 4h down move, 4h & 1d high
      & ((df["RSI_3_4h"] > 70.0) | (df["AROONU_14_4h"] < 90.0) | (df["AROONU_14_1d"] < 100.0))
      # 1d down move, 4h high
      & ((df["RSI_3_1d"] > 3.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 60.0))
      # 1d down move, 1h high
      & ((df["RSI_3_1d"] > 5.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
      # 1d down move, 15m & 1h still high
      & ((df["RSI_3_1d"] > 10.0) | (df["RSI_14_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0))
      # 1d down move, 1h & 4h high
      & ((df["RSI_3_1d"] > 10.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 90.0))
      # 1d down move, 1h & 4h still high
      & ((df["RSI_3_1d"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0) | (df["AROONU_14_4h"] < 40.0))
      # 1d down move, 1h high & overbought
      & ((df["RSI_3_1d"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1h"] < 20.0))
      # 1d down move, 1d high & overbought
      & ((df["RSI_3_1d"] > 40.0) | (df["AROONU_14_1d"] < 70.0) | (df["ROC_9_1d"] < 20.0))
      # 1d down move, 4h high & overbought
      & ((df["RSI_3_1d"] > 45.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 1d down move, 1h high, 1d overbought
      & ((df["RSI_3_1d"] > 60.0) | (df["AROONU_14_1h"] < 80.0) | (df["ROC_9_1d"] < 80.0))
      # 1d down move, 15m still high, 1d overbought
      & ((df["RSI_3_1d"] > 65.0) | (df["AROONU_14_15m"] < 40.0) | (df["ROC_9_1d"] < 100.0))
      # 1d down move, 4h & 1d high
      & ((df["RSI_3_1d"] > 65.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] < 10.0))
      # 5m still high, 1h down move, 15m still high, 1h high
      & (
        (df["RSI_3"] < 40.0)
        | (df["RSI_3_1h"] > 30.0)
        | (df["AROONU_14_15m"] < 50.0)
        | (df["AROONU_14_4h"] < 90.0)
      )
      # 5m still high, 15m high
      & ((df["RSI_3"] < 45.0) | (df["AROONU_14_15m"] < 70.0))
      # 5m still high, 1h down move, 4h high
      & ((df["RSI_3"] < 50.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 1h high
      & ((df["RSI_14_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
      # 15m down move, 4h & 1d high
      & (
        (df["RSI_14_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0)
      )
      # 1h downtrend, 4h high, 1d downtrend
      & ((df["CMF_20_1h"] > -0.2) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["CMF_20_1d"] > -0.25))
      # 15m & 1h high, 1d overbought
      & ((df["AROONU_14_15m"] < 60.0) | (df["AROONU_14_1h"] < 100.0) | (df["ROC_9_1d"] < 20.0))
      # 4h high, 4h & 1d overbought
      & ((df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 20.0) | (df["ROC_9_1d"] < 20.0))
      # 4h & 1d high, 1d overbought
      & ((df["AROONU_14_4h"] < 85.0) | (df["AROONU_14_1d"] < 85.0) | (df["ROC_9_1d"] < 60.0))
      # 4h & 1d high, 1d overbought
      & ((df["AROONU_14_4h"] < 100.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 30.0))
      # 1d still high, 4h & 1d downtrend
      & ((df["AROONU_14_1d"] < 50.0) | (df["ROC_9_4h"] > -20.0) | (df["ROC_9_1d"] > -30.0))
      # 4h top wick, 15m & 1h down move
      & ((df["top_wick_pct_4h"] < 10.0) | (df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 40.0))
      # 4h top wick, 1h down move, 1h high
      & ((df["top_wick_pct_4h"] < 10.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 70.0))
      # 1d red, 1h down move, 1h still high
      & ((df["change_pct_1d"] > -15.0) | (df["RSI_3_1h"] > 25.0) | (df["AROONU_14_1h"] < 50.0))
      # 1d P&D, 1h high
      & (
        (df["change_pct_1d"] > -15.0)
        | (df["change_pct_1d"].shift(288) < 15.0)
        | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      )
      # 1d P&D, 1d downtrend
      & ((df["change_pct_1d"] > -5.0) | (df["change_pct_1d"].shift(288) < 30.0) | (df["CMF_20_1d"] > -0.1))
      # 1d P&D, 15m high
      & ((df["change_pct_1d"] > -10.0) | (df["change_pct_1d"].shift(288) < 40.0) | (df["AROONU_14_15m"] < 50.0))
      # 1d P&D, 1h high
      & (
        (df["change_pct_1d"] > -10.0)
        | (df["change_pct_1d"].shift(288) < 40.0)
        | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
      )
      # 1d red with top wick, 1h high
      & ((df["change_pct_1d"] > -10.0) | (df["top_wick_pct_1d"] < 10.0) | (df["AROONU_14_1h"] < 80.0))
      # 1d green, 4m down move, 4h high
      & ((df["change_pct_1d"] < 25.0) | (df["RSI_3_4h"] > 55.0) | (df["AROONU_14_4h"] < 50.0))
      # 1d green with top wick, 1d low
      & ((df["change_pct_1d"] < 25.0) | (df["top_wick_pct_1d"] < 10.0) | (df["CMF_20_1d"] > -0.2))
      # 1d top wick, 1h still high
      & ((df["top_wick_pct_1d"] < 25.0) | (df["AROONU_14_1h"] < 50.0))
      # 1d top wick, 4h still high
      & ((df["top_wick_pct_1d"] < 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0))
      # 1d top wick, 1h down move
      & ((df["top_wick_pct_1d"] < 50.0) | (df["RSI_3_1h"] > 30.0))
      # big drop in the last 12 days, 1h down move, 1h high
      & ((df["close"] > (df["high_max_12_1d"] * 0.35)) | (df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 70.0))
      # big drop in the last 20 days, 1h down move, 1h high
      & (
        (df["close"] > (df["high_max_20_1d"] * 0.30))
        | (df["RSI_3_1h"] > 30.0)
        | (df["STOCHRSIk_14_14_3_3_1h"] < 75.0)
      )
      # big drop in the last 20 days, 1d high, 1d downtrend
      & (
        (df["close"] > (df["high_max_20_1d"] * 0.20))
        | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0)
        | (df["ROC_9_1d"] > -15.0)
      )
    )

    # Logic
    long_entry_logic.append(
      (df["RSI_14"] < 30.0)
      & (df["AROONU_14"] < 25.0)
      & (df["AROOND_14"] > 75.0)
      & (df["STOCHRSIk_14_14_3_3"] < 20.0)
      & (df["EMA_9"] < (df["EMA_26"] * 0.982))
      & (df["close"] < df["SMA_9"])
    )

