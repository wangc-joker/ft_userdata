"""NFI long entry condition #21."""

def append_long_21(df, long_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI long condition #21, the pump-mode long entry."""
    # Protections
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    # long_entry_logic.append(df["protections_long_global"] == True)

    long_entry_logic.append(
      # 5m down move, 4h high, 1h overbought
      ((df["RSI_3"] > 10.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 30.0))
      # 15m down move, 1h & 4h overbought
      & ((df["RSI_3_15m"] > 5.0) | (df["ROC_9_1h"] < 25.0) | (df["ROC_9_4h"] < 50.0))
      # 15m & 1h down move, 1d overbought
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 20.0) | (df["ROC_9_1d"] < 80.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 80.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
      # 15m & 1h down move, 4h overbought
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 45.0) | (df["ROC_9_4h"] < 50.0))
      # 15m & 1h down move, 4h overbought
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 60.0) | (df["ROC_9_4h"] < 70.0))
      # 15m & 4h down move, 4h high
      & ((df["RSI_3_15m"] > 10.0) | (df["RSI_3_4h"] > 55.0) | (df["AROONU_14_4h"] < 90.0))
      # 15m down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 10.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 80.0))
      # 15m down move, 1h high, 1d downtrend
      & ((df["RSI_3_15m"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["ROC_9_1d"] > -50.0))
      # 15m down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 15m down move, 1d high, 1d downtrend
      & ((df["RSI_3_15m"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0) | (df["ROC_9_1d"] > -15.0))
      # 15m & 1h down move, 4h overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 35.0) | (df["ROC_9_4h"] < 100.0))
      # 15m & 1d down move, 1h high
      & ((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1d"] > 35.0) | (df["AROONU_14_1h"] < 90.0))
      # 15m down move, 15m still high, 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_15m"] < 40.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 1h & 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 40.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 1h high, 4h overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 60.0) | (df["ROC_9_4h"] < 80.0))
      # 15m down move, 4h high, 4h downtrend
      & ((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_4h"] < 90.0) | (df["CMF_20_4h"] > -0.25))
      # 15m down move, 1h & 4h high
      & ((df["RSI_3_15m"] > 15.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_4h"] < 50.0))
      # 15m down move, 4h & 1d overbought
      & ((df["RSI_3_15m"] > 15.0) | (df["ROC_9_4h"] < 60.0) | (df["ROC_9_1d"] < 80.0))
      # 15m down move, 1h & 4h high
      & ((df["RSI_3_15m"] > 20.0) | (df["AROONU_14_1h"] < 60.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 4h high, 1h overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_1h"] < 10.0))
      # 15m down move, 4h & 1d overbought
      & ((df["RSI_3_15m"] > 20.0) | (df["ROC_9_4h"] < 80.0) | (df["ROC_9_1d"] < 200.0))
      # 15m & 1h down move, 1d overbought
      & ((df["RSI_3_15m"] > 25.0) | (df["RSI_3_1h"] > 25.0) | (df["ROC_9_1d"] < 80.0))
      # 15m & 1h down move, 1h high
      & ((df["RSI_3_15m"] > 25.0) | (df["RSI_3_1h"] > 55.0) | (df["AROONU_14_1h"] < 90.0))
      # 15m down move, 15m still high, 1d downtrend
      & ((df["RSI_3_15m"] > 25.0) | (df["AROONU_14_15m"] < 40.0) | (df["ROC_9_1d"] > -25.0))
      # 15m down move, 1h & 4h high
      & ((df["RSI_3_15m"] > 25.0) | (df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_4h"] < 100.0))
      # 15m down move, 4h high, 1h overbought
      & ((df["RSI_3_15m"] > 25.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 20.0))
      # 15m down move, 4h high, 1d overbought
      & ((df["RSI_3_15m"] > 25.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1d"] < 100.0))
      # 15m down move, 1h high & overbought
      & ((df["RSI_3_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0) | (df["ROC_9_1h"] < 20.0))
      # 15m down move, 1h & 4h overbought
      & ((df["RSI_3_15m"] > 25.0) | (df["ROC_9_1h"] < 40.0) | (df["ROC_9_4h"] < 40.0))
      # 15m down move, 4h high & overbought
      & ((df["RSI_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_4h"] < 200.0))
      # 15m down move, 1h & 4h overbought
      & ((df["RSI_3_15m"] > 30.0) | (df["ROC_9_1h"] < 60.0) | (df["ROC_9_4h"] < 80.0))
      # 15m down move, 4h & 1d overbought
      & ((df["RSI_3_15m"] > 40.0) | (df["ROC_9_4h"] < 100.0) | (df["ROC_9_1d"] < 100.0))
      # 1h down move, 4h overbought, 1d downtrend
      & ((df["RSI_3_1h"] > 15.0) | (df["ROC_9_4h"] < 50.0) | (df["ROC_9_1d"] > -30.0))
      # 1h & 4h down move, 4h high
      & ((df["RSI_3_1h"] > 20.0) | (df["ROC_9_4h"] < 50.0) | (df["AROONU_14_4h"] < 80.0))
      # 1h & 4h down move, 1h still high
      & ((df["RSI_3_1h"] > 20.0) | (df["ROC_9_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0))
      # 1h & 4h down move, 4h overbought
      & ((df["RSI_3_1h"] > 20.0) | (df["ROC_9_4h"] < 50.0) | (df["ROC_9_4h"] < 10.0))
      # 1h down move, 1h & 4h high
      & ((df["RSI_3_1h"] > 20.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 100.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 20.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 10.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 20.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 50.0))
      # 1h down move, 1h still high, 1d overbought
      & ((df["RSI_3_1h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0) | (df["ROC_9_4h"] < 10.0))
      # 1h down move, 4h & 1d overbought
      & ((df["RSI_3_1h"] > 20.0) | (df["ROC_9_4h"] < 40.0) | (df["ROC_9_1d"] < 100.0))
      # 1h down move, 1d high, 4h overbought
      & ((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_4h"] < 60.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 35.0) | (df["AROONU_14_1h"] < 80.0) | (df["ROC_9_1d"] > -40.0))
      # 1h down move, 4h high, 1d downtrend
      & ((df["RSI_3_1h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_1d"] > -50.0))
      # 1h down move, 1h & 1d overbought
      & ((df["RSI_3_1h"] > 40.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_1d"] < 60.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 80.0) | (df["ROC_9_4h"] < 25.0))
      # 1h down move, 4h high, 1h overbought
      & ((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_1h"] < 20.0))
      # 1h down move, 4h high, 1h overbought
      & ((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 10.0))
      # 1h down move, 1d high, 1d downtrend
      & ((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] > -25.0))
      # 1h down move, 1h high & overbought
      & ((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_1h"] < 90.0) | (df["ROC_9_1h"] < 10.0))
      # 1h down move, 1h high, 1d downtrend
      & ((df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["ROC_9_1d"] > -20.0))
      # 1h down move, 1h & 1d overbought
      & ((df["RSI_3_1h"] > 50.0) | (df["ROC_9_1h"] < 25.0) | (df["ROC_9_1d"] < 200.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 55.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_4h"] < 40.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 55.0) | (df["AROONU_14_4h"] < 85.0) | (df["ROC_9_4h"] < 80.0))
      # 1h down move, 4h high & overbought
      & ((df["RSI_3_1h"] > 60.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 100.0))
      # 1h down move, 1h & 1d overbought
      & ((df["RSI_3_1h"] > 60.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_1d"] < 250.0))
      # 1h down move, 1h high, 4h overbought
      & ((df["RSI_3_1h"] > 65.0) | (df["AROONU_14_1h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 1h down move, 1h overbought
      & ((df["RSI_3_1h"] > 65.0) | (df["ROC_9_1h"] < 40.0))
      # 4h down move, 1h high & overbought
      & ((df["RSI_3_4h"] > 3.0) | (df["AROONU_14_1h"] < 85.0) | (df["ROC_9_1h"] < 60.0))
      # 1d down move, 4h high & overbought
      & ((df["RSI_3_1d"] > 5.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 50.0))
      # 1d down move, 1h high
      & ((df["RSI_3_1d"] > 10.0) | (df["AROONU_14_1h"] < 70.0))
      # 1d down move, 4h high, 1h overbought
      & ((df["RSI_3_1d"] > 20.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 25.0))
      # 1d down move, 4h high, 4h overbought
      & ((df["RSI_3_1d"] > 20.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 40.0))
      # 1d down move, 1h & 4h overbought
      & ((df["RSI_3_1d"] > 30.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_4h"] < 60.0))
      # 1d down move, 4h high & overbought
      & ((df["RSI_3_1d"] > 35.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
      # 1d down move, 1h & 4h high
      & ((df["RSI_3_1d"] > 40.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 100.0))
      # 1d down move, 4h & 1d high
      & ((df["RSI_3_1d"] > 40.0) | (df["AROONU_14_4h"] < 70.0) | (df["AROONU_14_1d"] < 100.0))
      # 1d down move, 4h high & overbought
      & ((df["RSI_3_1d"] > 45.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 1d down move, 1h high, 1d overbought
      & ((df["RSI_3_1d"] > 60.0) | (df["AROONU_14_1h"] < 75.0) | (df["ROC_9_1d"] < 20.0))
      # 1d down move, 1h & 4h high
      & ((df["RSI_3_1d"] > 65.0) | (df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_4h"] < 100.0))
      # 1d downtrend, 1d high & overbought
      & ((df["CMF_20_1d"] > -0.40) | (df["AROONU_14_1d"] < 85.0) | (df["ROC_9_1d"] < 20.0))
      # 15m not low enough, 1h high, 1d overbought
      & ((df["AROONU_14_15m"] < 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0) | (df["ROC_9_1d"] < 200.0))
      # 1h still high, 1h & 4h overbought
      & ((df["AROONU_14_1h"] < 50.0) | (df["ROC_9_1h"] < 40.0) | (df["ROC_9_4h"] < 40.0))
      # 1h & 4h high, 4h overbought
      & ((df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
      # 1h & 4h high, 4h overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0))
      # 1h & 4h high, 1h overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_1h"] < 30.0))
      # 1h & 4h high, 1d overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_1d"] < 100.0))
      # 1h & 1d high, 4h overbought
      & ((df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_4h"] < 30.0))
      # 1h & 4h high, 1h overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_1h"] < 10.0))
      # 1h high & overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["ROC_9_1h"] < 80.0))
      # 1h high, 1h & 4h overbought
      & ((df["AROONU_14_1h"] < 80.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 10.0))
      # 1h high, 4h overbought, 1d downtrend
      & ((df["AROONU_14_1h"] < 80.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] > -50.0))
      # 1h & 4h high, 15m downtrend
      & ((df["AROONU_14_1h"] < 85.0) | (df["AROONU_14_4h"] < 85.0) | (df["ROC_9_15m"] > -40.0))
      # 1h & 4h high, 1h overbought
      & ((df["AROONU_14_1h"] < 90.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_1h"] < 10.0))
      # 4h high, 1h overbought, 1d downtrend
      & ((df["AROONU_14_4h"] < 80.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_1d"] > -30.0))
      # 4h & 1d high, 4h downtrend
      & ((df["AROONU_14_4h"] < 85.0) | (df["AROONU_14_1d"] < 100.0) | (df["CMF_20_4h"] > -0.30))
      # 4h & 1d high, 1h overbought
      & ((df["AROONU_14_4h"] < 85.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_1h"] < 20.0))
      # 4h & 1d high, 4h overbought
      & ((df["AROONU_14_4h"] < 85.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_4h"] < 60.0))
      # 4h high, 1h & 4h overbought
      & ((df["AROONU_14_4h"] < 85.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 20.0))
      # 4h high, 1d high & overbought
      & ((df["AROONU_14_4h"] < 90.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 30.0))
      # 4h high, 1h & 4h overbought
      & ((df["AROONU_14_4h"] < 90.0) | (df["ROC_9_1h"] < 40.0) | (df["ROC_9_4h"] < 40.0))
      # 4h high, 4h & 1d overbought
      & ((df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 30.0) | (df["ROC_9_1d"] < 100.0))
      # 4h high, 1h & 4h overbought
      & ((df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 40.0) | (df["ROC_9_4h"] < 80.0))
      # 1d high, 1h & 4h overbought
      & ((df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 20.0))
      # 1h high, 1h & 4h overbought
      & ((df["STOCHRSIk_14_14_3_3_1h"] < 60.0) | (df["ROC_9_1h"] < 40.0) | (df["ROC_9_4h"] < 40.0))
      # 1h high, 1h overbought
      & ((df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1h"] < 10.0))
      # 1h high, 4h overbought. 1d downtrend
      & ((df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_4h"] < 40.0) | (df["CMF_20_1d"] > -0.25))
      # 4h high, 1h & 4h overbought
      & ((df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 20.0))
      # 4h high & 4h & 1d overbought
      & ((df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_4h"] < 20.0) | (df["ROC_9_1d"] < 20.0))
      # 1d high, 1h & 4h overbought
      & ((df["STOCHRSIk_14_14_3_3_1d"] < 80.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 20.0))
      # 1d hihg, 1h & 1d overbought
      & ((df["STOCHRSIk_14_14_3_3_1d"] < 90.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_1d"] < 100.0))
      # 1d high, 4h & 1d overbought
      & ((df["STOCHRSIk_14_14_3_3_1d"] < 90.0) | (df["ROC_9_4h"] < 40.0) | (df["ROC_9_1d"] < 100.0))
    )

    # Logic
    long_entry_logic.append(
      (df["AROONU_14"] < 25.0)
      & (df["STOCHRSIk_14_14_3_3"] < 20.0)
      & (df["AROONU_14_15m"] < 50.0)
      & (df["close"] < df["EMA_16"] * 0.960)
      & (((df["EMA_50"] - df["EMA_200"]) / df["close"] * 100.0) > 6.0)
    )

