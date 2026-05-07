"""Quick long entry condition #45 extracted from NFI."""

def append_long_45(df, long_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI long condition #45, a quick-mode long entry."""
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    long_entry_logic.append(df["protections_long_global"] == True)

    # 5m & 15m down move, 4h still high
    long_entry_logic.append(
      (df["RSI_3"] > 3.0) | (df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 15m & 1h down move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 3.0) | (df["RSI_3_1h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
    # 5m & 4h & 1d down move
    long_entry_logic.append((df["RSI_3"] > 3.0) | (df["RSI_3_4h"] > 20.0) | (df["RSI_3_1d"] > 20.0))
    # 15m & 1h down move, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 3.0) | (df["RSI_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 60.0)
    )
    # 15m & 4h down move
    long_entry_logic.append((df["RSI_3_15m"] > 3.0) | (df["RSI_3_4h"] > 10.0))
    # 15m & 4h down move, 4h still not low enough
    long_entry_logic.append((df["RSI_3_15m"] > 3.0) | (df["RSI_3_4h"] > 30.0) | (df["RSI_14_4h"] < 35.0))
    # 15m down move, 4h still high, 15m downtrend
    long_entry_logic.append((df["RSI_3_15m"] > 3.0) | (df["AROONU_14_4h"] < 40.0) | (df["CMF_20_15m"] > -0.35))
    # 15m & 1h down move
    long_entry_logic.append((df["RSI_3_15m"] > 5.0) | (df["RSI_3_1h"] > 15.0))
    # 15m & 1h down move, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 5.0) | (df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
    )
    # 15m down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_15m"] > 5.0) | (df["AROONU_14_1h"] < 30.0))
    # 15m down move, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 5.0) | (df["AROONU_14_4h"] < 90.0))
    # 15m & 1h & 1d down move
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 10.0) | (df["RSI_3_1d"] > 10.0))
    # 15m & 1h down move, 1d overbought
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 20.0) | (df["ROC_9_1d"] < 30.0))
    # 15m & 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 80.0))
    # 15m & 1h down move, 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_1h"] > 65.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
    )
    # 15m & 4h down move, 4h still not low enough
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_4h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 30.0)
    )
    # 15m & 4h down move, 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_4h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0)
    )
    # 15m & 4h down move, 4h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_4h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 40.0)
    )
    # 15m down move, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 100.0)
    )
    # 15m down move, 1h high & overbought
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_1h"] < 10.0))
    # 15m down move, 1h high, 4h overbought
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_4h"] < 20.0))
    # 15m down move, 4h & 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["AROONU_14_4h"] < 75.0) | (df["AROONU_14_1d"] < 100.0)
    )
    # 15m down move, 4h high, 1h overbought
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 10.0))
    # 15m down move, 4h high & overbought
    long_entry_logic.append((df["RSI_3_15m"] > 10.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
    # 15m & 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 15.0) | (df["AROONU_14_4h"] < 70.0))
    # 15m down move, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 15.0) | (df["AROONU_14_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
    )
    # 15m down move, 4h high, 1d overbought
    long_entry_logic.append((df["RSI_3_15m"] > 15.0) | (df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1d"] < 50.0))
    # 15m & 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_15m"] > 30.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 70.0))
    # 1h down move, 4h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 3.0) | (df["AROONU_14_4h"] < 30.0))
    # 1h & 4h down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 5.0) | (df["RSI_3_4h"] > 30.0) | (df["AROONU_14_1h"] < 20.0))
    # 1h down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 5.0) | (df["AROONU_14_1h"] < 30.0))
    # 1h down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 5.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 25.0))
    # 1h & 4h down move
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 15.0))
    # 1h & 4h down move, 4h still not low enough
    long_entry_logic.append(
      (df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 30.0)
    )
    # 1h & 4h down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 25.0) | (df["AROONU_14_4h"] < 50.0))
    # 1h & 4h down move, 4h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 30.0) | (df["RSI_14_4h"] < 40.0))
    # 1h & 4h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_4h"] < 60.0))
    # 1h & 1d down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_1d"] > 10.0) | (df["AROONU_14_4h"] < 40.0))
    # 1h & 1d down move, 5m moving down
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_1d"] > 15.0) | (df["ROC_2"] > -0.0))
    # 1h & 1d down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_1d"] > 30.0) | (df["AROONU_14_4h"] < 50.0))
    # 15m & 1d down move, 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_1d"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0)
    )
    # 1h & 4h down move, 4h still not low enough
    long_entry_logic.append(
      (df["RSI_3_1h"] > 3.0) | (df["RSI_3_4h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 30.0)
    )
    # 1h down move, 1h still not low enough, 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 20.0) | (df["AROONU_14_1d"] < 85.0)
    )
    # 1h down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 25.0))
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["AROONU_14_4h"] < 85.0))
    # 1h down move, 1d high & overbought
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["AROONU_14_1d"] < 70.0) | (df["ROC_9_1d"] < 50.0))
    # 1h & 4h down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["RSI_3_4h"] > 15.0) | (df["AROONU_14_4h"] < 40.0))
    # 1h & 4h down move, 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 15.0) | (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0)
    )
    # 1h & 4h & 1d down move
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["RSI_3_4h"] > 20.0) | (df["RSI_3_1d"] > 30.0))
    # 1h & 4h down move, 1d high
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["RSI_3_4h"] > 30.0) | (df["AROONU_14_1d"] < 100.0))
    # 1h down move, 1h still high
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["AROONU_14_1h"] < 50.0))
    # 1h down move, 1d high, 4h downtrend
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["AROONU_14_1d"] < 70.0) | (df["ROC_9_4h"] > -20.0))
    # 1h down move, 1h still high
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0))
    # 1h & 4h down move, 1d overbought
    long_entry_logic.append((df["RSI_3_1h"] > 20.0) | (df["RSI_3_4h"] > 20.0) | (df["ROC_9_1d"] < 20.0))
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 20.0) | (df["AROONU_14_4h"] < 90.0))
    # 1h down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0))
    # 1h & 4h down move, 1h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 60.0)
    )
    # 1h & 4h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 25.0) | (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_4h"] < 70.0))
    # 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_1h"] > 25.0) | (df["AROONU_14_1h"] < 70.0))
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
    # 1h & 1d down move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 30.0) | (df["RSI_3_1d"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["RSI_14_4h"] < 80.0))
    # 14 down move, 1h high
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_1h"] < 80.0))
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 80.0))
    # 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
    # 1h down move, 4h & 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0)
    )
    # 1h down move, 1h still high, 1d overbought
    long_entry_logic.append((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 50.0) | (df["ROC_9_1d"] < 50.0))
    # 1h down move, 1h & 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0))
    # 1h down move, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 4h down move, 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 5.0) | (df["AROONU_14_1d"] < 100.0))
    # 4h & 1d down move, 1d still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 10.0) | (df["RSI_3_1d"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 50.0)
    )
    # 4h downmove, 4h still high
    long_entry_logic.append((df["RSI_3_4h"] > 10.0) | (df["AROONU_14_4h"] < 40.0))
    # 4h down move, 1h still high, 1d downtrend
    long_entry_logic.append(
      (df["RSI_3_4h"] > 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0) | (df["ROC_9_1d"] > -20.0)
    )
    # 4h down move, 1h & 1d downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 10.0) | (df["ROC_9_1h"] > -20.0) | (df["ROC_9_1d"] > -20.0))
    # 4h & 1d down move, 1d still high
    long_entry_logic.append((df["RSI_3_4h"] > 15.0) | (df["RSI_3_1d"] > 35.0) | (df["RSI_14_1d"] < 50.0))
    # 4h down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_4h"] > 15.0) | (df["AROONU_14_1h"] < 30.0))
    # 4h & 1d down move, 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 20.0) | (df["RSI_3_1d"] > 20.0) | (df["AROONU_14_1d"] < 80.0))
    # 4h down move, 4h still high, 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 20.0) | (df["AROONU_14_4h"] < 50.0) | (df["AROONU_14_1d"] < 100.0))
    # 4h down move, 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0))
    # 4h down move, 4h & 1d downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 25.0) | (df["ROC_9_4h"] > -20.0) | (df["ROC_9_1d"] > -20.0))
    # 4h down move, 4h & 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 30.0) | (df["AROONU_14_4h"] < 80.0) | (df["AROONU_14_1d"] < 100.0))
    # 4h down move, 1h high
    long_entry_logic.append((df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0))
    # 4h down move, 4h still high
    long_entry_logic.append((df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0))
    # 4h down move, 1h high
    long_entry_logic.append((df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
    # 4h down move, 4h high
    long_entry_logic.append((df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
    # 1d down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1d"] > 5.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0))
    # 1d down move, 1h still not low enough
    long_entry_logic.append((df["RSI_3_1d"] > 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0))
    # 1d down move, 4h still high
    long_entry_logic.append((df["RSI_3_1d"] > 15.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0))
    # 1d down move, 1h high & overbought
    long_entry_logic.append(
      (df["RSI_3_1d"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0) | (df["ROC_9_1h"] < 10.0)
    )
    # 15m still high, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_14_15m"] < 40.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 1h & 4h high, 4h overbought
    long_entry_logic.append((df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
    # 4h high, 1d overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1d"] < 80.0))
    # 4h high, 1h & 1d downtrend
    long_entry_logic.append((df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1h"] > -20.0) | (df["ROC_9_1d"] > -20.0))
    # 4h high, 1h & 4h overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 80.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 10.0))
    # 4h high & overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 80.0))
    # 1d high, 4h & 1d downtrend
    long_entry_logic.append((df["AROONU_14_1d"] < 80.0) | (df["ROC_9_4h"] > -20.0) | (df["ROC_9_1d"] > -20.0))
    # 1h high, 4h overbought
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_4h"] < 80.0))
    # 4h high, 1h & 1d downtrend
    long_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_4h"] < 70.0) | (df["ROC_9_1h"] > -20.0) | (df["ROC_9_1d"] > -20.0)
    )
    # 4h high, 1h & 4h overbought
    long_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 10.0)
    )
    # 4h high, 4h & 1d overbought
    long_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_4h"] < 30.0) | (df["ROC_9_1d"] < 30.0)
    )
    # 1d top wick, 4h still high
    long_entry_logic.append((df["top_wick_pct_1d"] < 40.0) | (df["AROONU_14_4h"] < 50.0))
    # pump, 4h still high
    long_entry_logic.append(
      (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # pump, drop but not yet near the previous lows
    long_entry_logic.append(
      (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
      | (df["close"] > (df["high_max_6_4h"] * 0.75))
      | (df["close"] < (df["low_min_24_4h"] * 1.25))
    )
    # pump, drop but not yet near the previous lows
    long_entry_logic.append(
      (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 2.0)
      | (df["close"] > (df["high_max_24_4h"] * 0.70))
      | (df["close"] < (df["low_min_12_1d"] * 1.25))
    )
    # big drop in last hour
    long_entry_logic.append(df["close"] > (df["close_max_12"] * 0.50))
    # big drop in last hour, 1d down move
    long_entry_logic.append((df["close"] > (df["close_max_12"] * 0.80)) | (df["RSI_3_1d"] > 15.0))
    # big drop in the last 12 hours, 4h still high
    long_entry_logic.append((df["close"] > (df["high_max_12_1h"] * 0.50)) | (df["AROONU_14_4h"] < 50.0))
    # big drop in the last 6 days, 1h still high
    long_entry_logic.append((df["close"] > (df["high_max_6_1d"] * 0.25)) | (df["AROONU_14_1h"] < 50.0))
    # big drop in the last 12 days, 1h down move
    long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.45)) | (df["RSI_3_1h"] > 5.0))
    # big drop in the last 12 days, 4h down move
    long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.40)) | (df["RSI_3_4h"] > 15.0))
    # big drop in the last 12 days, 1h still high
    long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.25)) | (df["AROONU_14_1h"] < 75.0))
    # big drop in the last 20 days, 1h down move
    long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.35)) | (df["RSI_3_1h"] > 10.0))
    # big drop in the last 20 days, 1h down move
    long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.25)) | (df["RSI_3_1h"] > 15.0))
    # big drop in the last 20 days, 1h down move
    long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (df["RSI_3_1h"] > 20.0))
    # big drop in the last 20 days, 1d high, 1d downtrend
    long_entry_logic.append(
      (df["close"] > (df["high_max_20_1d"] * 0.20))
      | (df["STOCHRSIk_14_14_3_3_1d"] < 70.0)
      | (df["ROC_9_1d"] > -15.0)
    )
    # big drop in the last 30 days, 4h down move, 4h still high
    long_entry_logic.append(
      (df["close"] > (df["high_max_30_1d"] * 0.25)) | (df["RSI_3_4h"] > 45.0) | (df["RSI_14_4h"] < 40.0)
    )

    # Logic
    long_entry_logic.append(df["RSI_3"] < 50.0)
    long_entry_logic.append(df["AROONU_14_15m"] < 25.0)
    long_entry_logic.append(df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
    long_entry_logic.append(df["close_15m"] < (df["EMA_20_15m"] * 0.924))
