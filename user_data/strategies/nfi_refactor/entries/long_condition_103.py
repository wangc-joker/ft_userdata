"""Rapid long entry condition #103 extracted from NFI."""

def append_long_103(df, long_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI long condition #103, the rapid-mode long entry."""
    # Protections
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    long_entry_logic.append(df["protections_long_global"] == True)

    long_entry_logic.append(df["ROC_2"] > -0.0)
    # 15m down move, 4h high, 1d overbought
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0) | (df["ROC_9_1d"] < 80.0)
    )
    # 15m & 1h & 4h down move
    long_entry_logic.append((df["RSI_3_15m"] > 20.0) | (df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 20.0))
    # 15m & 4h down move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 10.0) | (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 15m & 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_15m"] > 15.0) | (df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 70.0))
    # 15m down move, 4h high & overbought
    long_entry_logic.append(
      (df["RSI_3_15m"] > 15.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0) | (df["ROC_9_4h"] < 30.0)
    )
    # 15m & 1h down move, 15m high
    long_entry_logic.append((df["RSI_3_15m"] > 20.0) | (df["RSI_3_1h"] > 45.0) | (df["AROONU_14_15m"] < 70.0))
    # 15m & 4h down move, 15m still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
    )
    # 15m down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["RSI_14_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
    )
    # 15m down move, 15m still high, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 20.0) | (df["RSI_14_15m"] < 40.0) | (df["AROONU_14_4h"] < 90.0))
    # 15m down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 15m down move, 15m & 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["AROONU_14_15m"] < 60.0) | (df["AROONU_14_1h"] < 70.0)
    )
    # 15m down move, 15m high, 4h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_4h"] < 50.0)
    )
    # 15m down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 15m down move, 4h overbought
    long_entry_logic.append((df["RSI_3_15m"] > 20.0) | (df["ROC_9_4h"] < 70.0))
    # 15m down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 25.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1h"] < 80.0)
    )
    # 15m down move, 4h & 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 25.0) | (df["AROONU_14_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0)
    )
    # 15m down move, 1h & 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0)
    )
    # 15m down move, 1h high & overbought
    long_entry_logic.append(
      (df["RSI_3_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0) | (df["ROC_9_1h"] < 20.0)
    )
    # 15m & 1h down move, 15m high
    long_entry_logic.append((df["RSI_3_15m"] > 30.0) | (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_15m"] < 70.0))
    # 15m down move, 15m & 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 30.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1h"] < 90.0)
    )
    # 15m down move, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 15m & 1h down move, 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 35.0) | (df["RSI_3_1h"] > 45.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
    )
    # 15m down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 35.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_4h"] < 80.0)
    )
    # 15m down move, 15m & 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 35.0) | (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
    )
    # 15m down move, 1h high, 4h overbought
    long_entry_logic.append((df["RSI_3_15m"] > 35.0) | (df["AROONU_14_1h"] < 85.0) | (df["ROC_9_4h"] < 80.0))
    # 1h & 4h down move, 1h still high
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 20.0) | (df["AROONU_14_1h"] < 40.0))
    # 1h & 4h down move, 15m still not low enough
    long_entry_logic.append(
      (df["RSI_3_1h"] > 10.0) | (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
    )
    # 1h down move, 1d high & overbought
    long_entry_logic.append((df["RSI_3_1h"] > 10.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_1d"] < 10.0))
    # 1h & 4h down move, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["RSI_3_4h"] > 20.0) | (df["AROONU_14_4h"] < 40.0))
    # 1h down move, 4h still high, 4h downtrend
    long_entry_logic.append((df["RSI_3_1h"] > 15.0) | (df["AROONU_14_4h"] < 50.0) | (df["ROC_9_4h"] > -20.0))
    # 1h down move, 15m still not low enough, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 20.0) | (df["AROONU_14_15m"] < 25.0) | (df["AROONU_14_4h"] < 80.0))
    # 1h down move, 4h & 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0)
    )
    # 1h down move, 4h high & overbought
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 70.0) | (df["ROC_9_4h"] < 10.0))
    # 1h down move, 4h high, 1d overbought
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1d"] < 40.0))
    # 1h down move, 4h & 1d overbought
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] < 40.0))
    # 1h down move, 4h & 1d overbought
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["ROC_9_4h"] < 30.0) | (df["ROC_9_1d"] < 40.0))
    # 1h down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 40.0) | (df["AROONU_14_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1h down move, 1h still high, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 50.0) | (df["AROONU_14_4h"] < 90.0))
    # 1h down move, 1d high & overbought
    long_entry_logic.append((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 30.0))
    # 1h down move, 15m & 1h still high
    long_entry_logic.append((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1h"] < 85.0))
    # 1h & 4h down move, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 60.0) | (df["RSI_3_4h"] > 60.0) | (df["AROONU_14_4h"] < 80.0))
    # 1h & 4h down move, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
    )
    # 4h down move, 1h & 4h downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 5.0) | (df["ROC_9_1h"] > -30.0) | (df["ROC_9_4h"] > -30.0))
    # 1h down move, 4h high & overbought
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0) | (df["ROC_9_4h"] < 20.0)
    )
    # 4h down move, 4h still high, 1d downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 20.0) | (df["AROONU_14_4h"] < 50.0) | (df["ROC_9_1d"] > -40.0))
    # 1h down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 4h down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["AROONU_14_4h"] < 70.0)
    )
    # 4h down move, 15m still not low enough, 4h high
    long_entry_logic.append((df["RSI_3_4h"] > 35.0) | (df["AROONU_14_15m"] < 30.0) | (df["AROONU_14_4h"] < 70.0))
    # 4h down move, 1h high, 4h downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 30.0) | (df["AROONU_14_1h"] < 70.0) | (df["ROC_9_4h"] > -10.0))
    # 4h down move, 4h still high, 1d downtrend
    long_entry_logic.append((df["RSI_3_4h"] > 50.0) | (df["RSI_14_4h"] < 40.0) | (df["ROC_9_1d"] > -30.0))
    # 4h down move, 4h high & overbought
    long_entry_logic.append((df["RSI_3_4h"] > 50.0) | (df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 20.0))
    # 4h down move, 4h still high, 1d downtrend
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0) | (df["ROC_9_1d"] > -30.0)
    )
    # 4h down move, 15m still high, 1h high
    long_entry_logic.append((df["RSI_3_4h"] > 60.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1h"] < 90.0))
    # 4h down move, 1h high, 1d overbought
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0) | (df["ROC_9_1d"] < 30.0)
    )
    # 1d down move, 1h high, 1d downtrend
    long_entry_logic.append((df["RSI_3_1d"] > 10.0) | (df["AROONU_14_1h"] < 80.0) | (df["ROC_9_1d"] > -10.0))
    # 1d down move, 4h high
    long_entry_logic.append((df["RSI_3_1d"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0))
    # 1d down move, 15m still high, 1h high
    long_entry_logic.append((df["RSI_3_1d"] > 15.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1h"] < 85.0))
    # 1d down move, 1h & 1d overbought
    long_entry_logic.append((df["RSI_3_1d"] > 45.0) | (df["ROC_9_1h"] < 80.0) | (df["ROC_9_1d"] < 80.0))
    # 15m still high, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_14_15m"] < 40.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 15m & 1h still high, 4h high
    long_entry_logic.append(
      (df["RSI_14_15m"] < 45.0) | (df["AROONU_14_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0)
    )
    # 15m still high, 4h high & overbought
    long_entry_logic.append((df["RSI_14_15m"] < 50.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 80.0))
    # 15m still high, 1h high, 4h still high
    long_entry_logic.append(
      (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 15m still high, 1d high
    long_entry_logic.append((df["AROONU_14_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0))
    # 15m & 1h
    long_entry_logic.append((df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1h"] < 90.0))
    # 15m & 1h & 4h high
    long_entry_logic.append(
      (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 1h & 1d high, 4h downtrend
    long_entry_logic.append((df["AROONU_14_1h"] < 40.0) | (df["AROONU_14_1d"] < 70.0) | (df["ROC_9_4h"] > -20.0))
    # 1h & 4h high, 4h overbought
    long_entry_logic.append((df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 90.0) | (df["ROC_9_4h"] < 10.0))
    # 1h high, 1h & 1d overbought
    long_entry_logic.append((df["AROONU_14_1h"] < 90.0) | (df["ROC_9_1h"] < 10.0) | (df["ROC_9_1d"] < 30.0))
    # 4h & 1d high, 1d overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 70.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 10.0))
    # 4h high, 4h & 1d overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 80.0) | (df["ROC_9_4h"] < 80.0) | (df["ROC_9_1d"] < 100.0))
    # 1d high, 4h & 1d overbought
    long_entry_logic.append((df["AROONU_14_1d"] < 100.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] < 50.0))
    # 15m still high, 1h high
    long_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] < 40.0)
      | (df["AROONU_14_1h"] < 90.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0)
    )
    # 15m still high, 1d high
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0))
    # 4h high, 4h & 1d overbought
    long_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_4h"] < 80.0) | (df["ROC_9_4h"] < 40.0) | (df["ROC_9_1d"] < 100.0)
    )
    # 1d green, 4h down move, 4h still high
    long_entry_logic.append((df["change_pct_1d"] < 40.0) | (df["RSI_3_4h"] > 35.0) | (df["AROONU_14_4h"] < 40.0))
    # 1d top wick, 4h high
    long_entry_logic.append((df["top_wick_pct_1d"] < 30.0) | (df["AROONU_14_4h"] < 90.0))
    # pump, 4h overbought
    long_entry_logic.append(
      (((df["high_max_6_1h"] - df["low_min_6_1h"]) / df["low_min_6_1h"]) < 0.5) | (df["ROC_9_4h"] < 50.0)
    )
    # pump, drop but not yet near the previous lows
    long_entry_logic.append(
      (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
      | (df["close"] > (df["high_max_6_4h"] * 0.85))
      | (df["close"] < (df["low_min_24_4h"] * 1.25))
    )
    # pump, 1h high
    long_entry_logic.append(
      (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 4.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 90.0)
    )
    # big drop in the last 2 days, 1d down move
    long_entry_logic.append((df["close"] > (df["high_max_12_4h"] * 0.30)) | (df["RSI_3_1d"] > 30.0))
    # big drop in the last 12 days, 1h still high
    long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.25)) | (df["AROONU_14_1h"] < 50.0))
    # big drop in the last 12 days, 1h still not low enough
    long_entry_logic.append(
      (df["close"] > (df["high_max_12_1d"] * 0.10)) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0)
    )
    # big drop in the last 12 days, 15m still high
    long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.20)) | (df["AROONU_14_15m"] < 50.0))
    # big drop in the last 20 days, 4h down move
    long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (df["RSI_3_4h"] > 20.0))

    # Logic
    long_entry_logic.append(df["RSI_4"] < 45.0)
    long_entry_logic.append(df["RSI_14"] > 35.0)
    long_entry_logic.append(df["RSI_20"] < df["RSI_20"].shift(1))
    long_entry_logic.append(df["AROONU_14"] < 25.0)
    long_entry_logic.append(df["close"] < df["SMA_16"] * 0.960)
