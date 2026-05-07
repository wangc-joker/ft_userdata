"""Long global protection condition chunk extracted from NFI."""

from pandas import DataFrame

def long_global_chunk_5(df: DataFrame):
  return (
    # 4h down move, 15m & 1h high
    ((df["RSI_3_4h"] > 3.0) | (df["AROONU_14_15m"] < 60.0) | (df["AROONU_14_1h"] < 90.0))
    # 4h down move, 15m high, 4h still high
    & (
      (df["RSI_3_4h"] > 3.0)
      | (df["AROONU_14_15m"] < 60.0)
      | (df["AROONU_14_4h"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
    )
    # 4h down move, 15m & 1h high, 4h downtrend
    & (
      (df["RSI_3_4h"] > 3.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["ROC_9_4h"] > -20.0)
    )
    # 4h & 1d down move, 15m still not low enough, 4h downtrend
    & (
      (df["RSI_3_4h"] > 5.0)
      | (df["RSI_3_1d"] > 5.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
      | (df["ROC_9_4h"] > -40.0)
    )
    # 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 4h & 15m still not low enough
    & (
      (df["RSI_3_4h"] > 5.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 20.0)
      | (df["RSI_14_4h"] < 20.0)
      | (df["CMF_20_1h"] > -0.20)
      | (df["CMF_20_4h"] > -0.20)
      | (df["AROONU_14_4h"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
    )
    # 4h down move, 1h & 4h downtrend, 1h still not low enough, 4h high
    & (
      (df["RSI_3_4h"] > 5.0)
      | (df["CMF_20_1h"] > -0.10)
      | (df["CMF_20_4h"] > -0.20)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 40.0)
    )
    # 4h down mnove, 15m & 1h & 4h downtrend, 15m high, 4h downtrend
    & (
      (df["RSI_3_4h"] > 10.0)
      | (df["CMF_20_15m"] > -0.25)
      | (df["CMF_20_1h"] > -0.10)
      | (df["CMF_20_4h"] > -0.10)
      | (df["AROONU_14_15m"] < 60.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0)
      | (df["ROC_9_4h"] > -30.0)
    )
    # 4h down move, 15m & 1h & 4h still high, 15m high
    & (
      (df["RSI_3_4h"] > 10.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_15m"] < 60.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0)
    )
    # 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 1d overbought
    & (
      (df["RSI_3_4h"] > 15.0)
      | (df["RSI_3_1d"] > 65.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 20.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["ROC_9_4h"] > -40.0)
      | (df["ROC_9_1d"] < 200.0)
    )
    # 4h & 1d down move, 1h still high, 4h high, 1d downtrend
    & (
      (df["RSI_3_4h"] > 25.0)
      | (df["RSI_3_1d"] > 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["AROONU_14_4h"] < 100.0)
      | (df["ROC_9_1d"] > -40.0)
    )
    # 4h down move, 1h & 4h still not low enough, 15m high, 4h downtrend
    & (
      (df["RSI_3_4h"] > 25.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["AROONU_14_15m"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
      | (df["ROC_9_4h"] > -50.0)
    )
    # 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1h still high, 4h downtrend
    & (
      (df["RSI_3_4h"] > 30.0)
      | (df["RSI_3_1d"] > 40.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 20.0)
      | (df["RSI_14_4h"] < 20.0)
      | (df["CMF_20_4h"] > -0.25)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["ROC_9_4h"] > -60.0)
    )
    # 4h down move, 15m & 1h & 4h still high, 15m high, 4h still not low enough, 1d overbought
    & (
      (df["RSI_3_4h"] > 35.0)
      | (df["RSI_14_15m"] < 50.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_15m"] < 60.0)
      | (df["AROONU_14_4h"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      | (df["ROC_9_1d"] < 50.0)
    )
    # 4h down move, 15m high, 15m & 1h & 4h high, 4h & 1d overbought
    & (
      (df["RSI_3_4h"] > 55.0)
      | (df["AROONU_14_15m"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      | (df["ROC_9_4h"] < 20.0)
      | (df["ROC_9_1d"] < 30.0)
    )
    # 1d down move, 15m & 1h still not low enough, 4h & 1d downtrend
    & (
      (df["RSI_3_1d"] > 3.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 20.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0)
      | (df["ROC_9_4h"] > -30.0)
      | (df["ROC_9_1d"] > -50.0)
    )
    # 1d down move, 1h & 4h still not low enough, 1h still high & overbought, 1d downtrend
    & (
      (df["RSI_3_1d"] > 3.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_1d"] > -30.0)
    )
    # 1d down move, 15m & 1h & 4h still not low enough, 15m still not low enough, 1h high
    & (
      (df["RSI_3_1d"] > 5.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["AROONU_14_15m"] < 30.0)
      | (df["AROONU_14_1h"] < 85.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
    )
    # 1d down move, 15m still not low enough, 1h high, 1d downtrend
    & (
      (df["RSI_3_1d"] > 5.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      | (df["ROC_2_1d"] > -40.0)
    )
    # 1d down move, 15m high, 1h & 4h downtrend
    & (
      (df["RSI_3_1d"] > 5.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0)
      | (df["ROC_9_1h"] > -60.0)
      | (df["ROC_9_4h"] > -60.0)
    )
    # 1d down move, 1h still high, 4h high
    & ((df["RSI_3_1d"] > 5.0) | (df["AROONU_14_1h"] < 40.0) | (df["AROONU_14_4h"] < 70.0))
    # 1d down move, 4h high, 1h & 4h downtrend
    & (
      (df["RSI_3_1d"] > 5.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      | (df["ROC_9_1h"] > -10.0)
      | (df["ROC_9_4h"] > -10.0)
    )
    # 1d down move, 1h high & overbought, 4h & 1d downtrend
    & (
      (df["RSI_3_1d"] > 10.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] > -40.0)
      | (df["ROC_9_1d"] > -40.0)
    )
    # 1d down move, 1h & 4h still high, 1h & 4h downtrend, 1h & 4h high, 1d downtrend
    & (
      (df["RSI_3_1d"] > 10.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["CMF_20_1h"] > -0.40)
      | (df["CMF_20_4h"] > -0.10)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["AROONU_14_4h"] < 85.0)
      | (df["ROC_9_1d"] > -40.0)
    )
    # 15m & 1h & 4h still high, 4h downtrend, 4h overbought
    & (
      (df["RSI_14_15m"] < 50.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["CMF_20_4h"] > -0.2)
      | (df["ROC_9_4h"] < 250.0)
    )
    # 4h red, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
    & (
      (df["change_pct_4h"] > -30.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_3_4h"] > 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_4h"] < 70.0)
    )
    # 4h P&D, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
    & (
      (df["change_pct_4h"] > -5.0)
      | (df["change_pct_4h"].shift(48) < 5.0)
      | (df["RSI_3_15m"] > 40.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_1h"] < 80.0)
      | (df["AROONU_14_4h"] < 100.0)
    )
    # 4h green with top wick, 15m & 1h down move, 15m still not low enough, 1h & 4h high
    & (
      (df["change_pct_4h"] < 10.0)
      | (df["top_wick_pct_4h"] < 10.0)
      | (df["RSI_3_15m"] > 5.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_1h"] < 60.0)
      | (df["AROONU_14_4h"] < 90.0)
    )
    # 4h green with top wick, 1h down move, 1h still high, 4h high, 1d overbought
    & (
      (df["change_pct_4h"] < 10.0)
      | (df["top_wick_pct_4h"] < 10.0)
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["AROONU_14_1h"] < 70.0)
      | (df["AROONU_14_4h"] < 90.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # 4h green with top wick, 15m & 1h down move, 1h still high, 4h high
    & (
      (df["change_pct_4h"] < 15.0)
      | (df["top_wick_pct_4h"] < 15.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 35.0)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["AROONU_14_4h"] < 100.0)
    )
    # 4h green with top wick, 15m & 1h down move, 1h & 4h high
    & (
      (df["change_pct_4h"] < 15.0)
      | (df["top_wick_pct_4h"] < 10.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["AROONU_14_1h"] < 80.0)
      | (df["AROONU_14_4h"] < 100.0)
    )
    # 4h green, 15m & 1h down move, 15m still not low enough, 1h & 4h high
    & (
      (df["change_pct_4h"] < 15.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 70.0)
      | (df["AROONU_14_1h"] < 70.0)
      | (df["AROONU_14_4h"] < 100.0)
    )
    # 1d red, 1h & 4h down move, 1h still high, 4d downtrend
    & (
      (df["change_pct_1d"] > -40.0)
      | (df["RSI_3_1h"] > 55.0)
      | (df["RSI_3_4h"] > 10.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["ROC_9_4h"] > -35.0)
    )
    # 1d P&D, 15m & 4h down move, 15m & 4h still high
    & (
      (df["change_pct_1d"] > -20.0)
      | (df["change_pct_1d"].shift(288) < 20.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 1d red, 15m & 1h & 4h down move, 1h still not low enough, 4h & 1d still high
    & (
      (df["change_pct_1d"] > -20.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_1h"] < 35.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_1d"] < 50.0)
    )
    # 1d red, 1h & 4h & 1d down move, 1h still not low enough, 4h & 1d still high, 1d downtrend
    & (
      (df["change_pct_1d"] > -20.0)
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_3_1d"] > 50.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["RSI_14_1d"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 40.0)
      | (df["ROC_9_1d"] > -20.0)
    )
    # 1d red, 15m & 1h & 4h down move, 1d high, 15m & 1h still high
    & (
      (df["change_pct_1d"] > -20.0)
      | (df["RSI_3_15m"] > 30.0)
      | (df["RSI_3_1h"] > 55.0)
      | (df["RSI_3_4h"] > 55.0)
      | (df["AROONU_14_1d"] < 85.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1d P&D, 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h still high
    & (
      (df["change_pct_1d"] > -15.0)
      | (df["change_pct_1d"].shift(288) < 15.0)
      | (df["RSI_3_15m"] > 50.0)
      | (df["RSI_3_1h"] > 50.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_15m"] < 50.0)
      | (df["AROONU_14_4h"] < 50.0)
    )
    # 1d P&D, 15m & 1h & 4h & 1d down move, 4h still not low enough
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["change_pct_1d"].shift(288) < 10.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 10.0)
      | (df["RSI_3_1d"] > 40.0)
      | (df["RSI_14_4h"] < 30.0)
    )
    # 1d P&D, 15m & 1h down move, 1h still not low enough, 4h still high, 15m downtrend, 1h still high
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["change_pct_1d"].shift(288) < 10.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["CMF_20_15m"] > -0.30)
      | (df["AROONU_14_1h"] < 50.0)
    )
    # 1d P&D, 15m down move, 1h high
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["change_pct_1d"].shift(288) < 20.0)
      | (df["top_wick_pct_1d"].shift(288) < 20.0)
      | (df["RSI_3_15m"] > 35.0)
      | (df["AROONU_14_1h"] < 70.0)
    )
    # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1d overbought
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["change_pct_1d"].shift(288) < 20.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["ROC_9_1d"] < 25.0)
    )
    # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["change_pct_1d"].shift(288) < 50.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["ROC_9_1h"] > -10.0)
      | (df["ROC_9_4h"] > -10.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 1d red with top wick, 15m & 1h down move, 1h downtrend, 1h high
    & (
      (df["change_pct_1d"] > -10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["CMF_20_1h"] > -0.2)
      | (df["AROONU_14_1h"] < 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
    # 1d P&D, 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
    & (
      (df["change_pct_1d"] > -5.0)
      | (df["change_pct_1d"].shift(288) < 10.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 1d P&D, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1h & 4h downtrend, 1d overbought
    & (
      (df["change_pct_1d"] > -5.0)
      | (df["change_pct_1d"].shift(288) < 10.0)
      | (df["RSI_3_15m"] > 25.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_3_4h"] > 30.0)
      | (df["AROONU_14_1h"] < 30.0)
      | (df["AROONU_14_4h"] < 30.0)
      | (df["ROC_9_1h"] > -25.0)
      | (df["ROC_9_4h"] > -25.0)
      | (df["ROC_9_1d"] < 50.0)
    )
    # 1d red, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1d high, 4h downtrend, 1d overbought
    & (
      (df["change_pct_1d"] > -5.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_1d"] < 85.0)
      | (df["ROC_9_4h"] > -30.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # 1d green with top wick, 15m & 1h & 1d down move, 1h still not low enough, 4h still high, 1d overbought
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_3_1d"] > 65.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 65.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_1h"] < 30.0)
      | (df["AROONU_14_4h"] < 60.0)
    )
    # 1d green with top wick, 15m down move, 1h & 4h high, 1d overbought
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_14_1h"] < 70.0)
      | (df["RSI_14_4h"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
      | (df["ROC_9_1d"] < 40.0)
    )
    # 1d green with top wick, 15m down move, 15m & 1h still high, 4h & 1d high, 4h overbought
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 75.0)
      | (df["AROONU_14_4h"] < 80.0)
      | (df["AROONU_14_1d"] < 90.0)
      | (df["ROC_9_4h"] < 25.0)
    )
    # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 65.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["AROONU_14_15m"] < 30.0)
      | (df["AROONU_14_4h"] < 60.0)
    )
    # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 80.0)
      | (df["AROONU_14_4h"] < 70.0)
      | (df["ROC_9_4h"] < 80.0)
    )
    # 1d green with top wick, 1h & 4h down move, 1h & 4h still high
    & (
      (df["change_pct_1d"] < 10.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_1h"] > 55.0)
      | (df["RSI_3_4h"] > 55.0)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["AROONU_14_4h"] < 50.0)
    )
    # 1d green with top wick, 15m & 1h down move, 15m & 1h & 4h still high, 4h high & overbought
    & (
      (df["change_pct_1d"] < 20.0)
      | (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_4h"] < 70.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # 1d green with top wick, 1h & 4h down move, 1h still not low enough, 4h still high, 4h & 1d overbought
    & (
      (df["change_pct_1d"] < 20.0)
      | (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_4h"] < 50.0)
      | (df["ROC_9_4h"] < 10.0)
      | (df["ROC_9_1d"] < 50.0)
    )
    # 1d green with top wick, 15m down move, 15m & 1h & 4h still high, 4h & 1d overbought
    & (
      (df["change_pct_1d"] < 25.0)
      | (df["top_wick_pct_1d"] < 25.0)
      | (df["RSI_3_15m"] > 40.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      | (df["ROC_9_4h"] < 20.0)
      | (df["ROC_9_1d"] < 50.0)
    )
    # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 4h high, 1d overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 10.0)
      | (df["RSI_3_15m"] > 30.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_3_4h"] > 70.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["AROONU_14_15m"] < 25.0)
      | (df["AROONU_14_4h"] < 70.0)
      | (df["ROC_9_1d"] < 40.0)
    )
    # 1d green with top wick, 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1d overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["AROONU_14_1h"] < 20.0)
      | (df["AROONU_14_4h"] < 50.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_15m"] > 35.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 80.0)
      | (df["AROONU_14_4h"] < 80.0)
      | (df["ROC_9_4h"] < 50.0)
    )
    # 1d green with top wick, 1h down move, 1h still high, 4h high & overbought, 1d overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_1h"] > 50.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["AROONU_14_4h"] < 70.0)
      | (df["ROC_9_4h"] < 40.0)
      | (df["ROC_9_1d"] < 50.0)
    )
    # 1d green with top wick, 15m & 1h down move, 1h & 4h still high, 4h overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 30.0)
      | (df["RSI_3_15m"] > 25.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_4h"] < 80.0)
      | (df["ROC_9_4h"] < 30.0)
    )
    # 1d green with top wick, 15m & 4h down move, 15m & 1h still high, 1d overbought
    & (
      (df["change_pct_1d"] < 30.0)
      | (df["top_wick_pct_1d"] < 30.0)
      | (df["RSI_3_15m"] > 50.0)
      | (df["RSI_3_4h"] > 60.0)
      | (df["AROONU_14_15m"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 1d green, 15m & 4h down move, 4h still high, 4h & 1d overbought
    & (
      (df["change_pct_1d"] < 50.0)
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["ROC_9_4h"] < 40.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
    & (
      (df["change_pct_1d"] < 50.0)
      | (df["top_wick_pct_1d"] < 50.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_3_4h"] > 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_4h"] < 70.0)
    )
    # 1d green with top wick, 1d down move, 4h still high & overbought
    & (
      (df["change_pct_1d"] < 50.0)
      | (df["top_wick_pct_1d"] < 50.0)
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_4h"] < 50.0)
      | (df["ROC_9_4h"] < 50.0)
    )
    # 1d green with top wick, 4h down move, 4h still high, 1d overbought
    & (
      (df["change_pct_1d"] < 50.0)
      | (df["top_wick_pct_1d"] < 50.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["ROC_9_1d"] < 200.0)
    )
    # 1d green, 15m & 4h down move, 15m & 1h & 4h still high, 15m high, 4h & 1d overbought
    & (
      (df["change_pct_1d"] < 50.0)
      | (df["RSI_3_15m"] > 50.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_15m"] < 60.0)
      | (df["ROC_9_4h"] < 30.0)
      | (df["ROC_9_1d"] < 200.0)
    )
    # 4h top wick, 15m down move, 15m still not low enough, 1h & 4h still high, 4h overbought
    & (
      (df["top_wick_pct_4h"] < 20.0)
      | (df["RSI_3_15m"] > 25.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      | (df["ROC_9_4h"] < 50.0)
    )
    # 4h top wick, 15m & 1h down move, 15m & 1h still high, 1h & 4h high
    & (
      (df["top_wick_pct_4h"] < 20.0)
      | (df["RSI_3_15m"] > 40.0)
      | (df["RSI_3_1h"] > 55.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 60.0)
      | (df["AROONU_14_15m"] < 40.0)
      | (df["AROONU_14_1h"] < 85.0)
      | (df["AROONU_14_4h"] < 100.0)
    )
    # 1d top wick, 1h & 4h down move, 15m downtrend, 4h still high, 1d overbought
    & (
      (df["top_wick_pct_1d"] < 20.0)
      | (df["RSI_3_1h"] > 10.0)
      | (df["RSI_3_4h"] > 45.0)
      | (df["CMF_20_15m"] > -0.2)
      | (df["AROONU_14_4h"] < 50.0)
      | (df["ROC_9_1d"] < 80.0)
    )
    # 1d top wick, 4h down move, 4h still high, 1d overbought
    & (
      (df["top_wick_pct_1d"] < 25.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_14_4h"] < 45.0)
      | (df["AROONU_14_4h"] < 40.0)
      | (df["ROC_9_1d"] < 200.0)
    )
    # 1d top wick, 15m & 1h & 4h down move, 15m & 1h downtrend, 4h still high
    & (
      (df["top_wick_pct_1d"] < 25.0)
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["CMF_20_15m"] > -0.25)
      | (df["CMF_20_1h"] > -0.25)
      | (df["AROONU_14_4h"] < 50.0)
    )
    # 1d top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high
    & (
      (df["top_wick_pct_1d"] < 25.0)
      | (df["RSI_3_15m"] > 30.0)
      | (df["RSI_3_1h"] > 60.0)
      | (df["RSI_3_4h"] > 60.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_15m"] < 30.0)
      | (df["AROONU_14_4h"] < 50.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 20.0)
    )
    # 1d top wick, 15m down move, 15m stil high, 1h & 4h high, 4h overbought
    & (
      (df["top_wick_pct_1d"] < 25.0)
      | (df["RSI_3_15m"] > 35.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 50.0)
      | (df["RSI_14_4h"] < 80.0)
      | (df["AROONU_14_1h"] < 80.0)
      | (df["AROONU_14_4h"] < 80.0)
      | (df["ROC_9_4h"] < 50.0)
    )
    # 1d top wick, 15m & 1h & 4h down move, 15m & 1h & 4h still high
    & (
      (df["top_wick_pct_1d"] < 80.0)
      | (df["RSI_3_15m"] > 40.0)
      | (df["RSI_3_1h"] > 65.0)
      | (df["RSI_3_4h"] > 65.0)
      | (df["RSI_14_15m"] < 40.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["AROONU_14_4h"] < 50.0)
    )
    # pump, drop but not yet near the previous lows, 15m & 1h & 4h & 1d down move, 1d overbought
    & (
      (((df["high_max_6_1d"] - df["low_min_6_1d"]) / df["low_min_6_1d"]) < 1.5)
      | (df["close"] > (df["high_max_6_4h"] * 0.70))
      | (df["close"] < (df["low_min_6_1d"] * 1.25))
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_3_1d"] > 45.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # pump, drop in lays days, 1h & 4h down move, 1h & 4h still not low enough, 1d overbought
    & (
      (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 3.0)
      | (df["close"] > (df["high_max_24_4h"] * 0.70))
      | (df["RSI_3_1h"] > 15.0)
      | (df["RSI_3_1d"] > 50.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # pump, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h downtrend, 1h high
    & (
      (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 3.0)
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["RSI_14_15m"] < 20.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 40.0)
      | (df["CMF_20_1h"] > -0.10)
      | (df["AROONU_14_1h"] < 70.0)
    )
    # pump, drop in last 6 days, 1h & 4h down move, 1h & 4h still not low enough, 4h downtrend, 4h & 1d downtrend
    & (
      (((df["high_max_30_1d"] - df["low_min_30_1d"]) / df["low_min_30_1d"]) < 10.0)
      | (df["close"] > (df["high_max_6_1d"] * 0.50))
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 60.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["CMF_20_4h"] > -0.10)
      | (df["ROC_9_4h"] > -15.0)
      | (df["ROC_9_1d"] > -25.0)
    )
    # drop in the last 4 hours, 1h & 4h high
    & ((df["close"] > (df["close_max_48"] * 0.30)) | (df["AROONU_14_1h"] < 85.0) | (df["AROONU_14_4h"] < 85.0))
    # drop in last 12 hours, 14m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
    & (
      (df["close"] > (df["high_max_12_1h"] * 0.50))
      | (df["RSI_3_15m"] > 20.0)
      | (df["RSI_3_1h"] > 35.0)
      | (df["RSI_3_4h"] > 55.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["RSI_14_4h"] < 50.0)
      | (df["AROONU_14_4h"] < 80.0)
      | (df["ROC_9_4h"] < 25.0)
    )
    # drop in last 12 hours, 1h & 4h down move, 1h & 4h downtrend
    & (
      (df["close"] > (df["high_max_12_1h"] * 0.35))
      | (df["RSI_3_1h"] > 15.0)
      | (df["RSI_3_4h"] > 5.0)
      | (df["ROC_9_1h"] > -50.0)
      | (df["ROC_9_4h"] > -50.0)
    )
    # drop in last 4 days, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h overbought
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.40))
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["RSI_14_1h"] < 40.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # drop in last 4 days, 15m & 1h & 4h & 1d down move, 4h high
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.40))
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 40.0)
      | (df["RSI_3_4h"] > 60.0)
      | (df["RSI_3_1d"] > 10.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
    )
    # drop in last 6 days, 15m & 1h & 4h & 1d down move, 1d high, 4h downtrend
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.35))
      | (df["RSI_3_15m"] > 5.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_3_1d"] > 30.0)
      | (df["AROONU_14_1d"] < 80.0)
      | (df["ROC_9_4h"] > -40.0)
    )
    # drop in last 4 days, 15m & 1d down move, 15m still not low enough, 1h still high, 1d high, 4h downtrend
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.35))
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1d"] > 30.0)
      | (df["AROONU_14_15m"] < 25.0)
      | (df["AROONU_14_1h"] < 40.0)
      | (df["AROONU_14_1d"] < 80.0)
      | (df["ROC_9_4h"] > -50.0)
    )
    # drop in last 4 days, 1h & 5h & 1d down move, 1h still high, 1h & 4h downtrend
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.25))
      | (df["RSI_3_1h"] > 20.0)
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_3_1d"] > 25.0)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["ROC_9_1h"] > -20.0)
      | (df["ROC_9_4h"] > -35.0)
    )
    # drop in last 4 days, 1d down move, 1h & 4h downtrend, 15m & 4h downtrend
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.25))
      | (df["RSI_3_1d"] > 15.0)
      | (df["CMF_20_1h"] > -0.20)
      | (df["CMF_20_4h"] > -0.20)
      | (df["ROC_9_15m"] > -15.0)
      | (df["ROC_9_4h"] > -20.0)
    )
    # drop in last 6 days, 15m & 1d down move, 1h still high, 4h high, 4h downtrend
    & (
      (df["close"] > (df["high_max_6_1d"] * 0.25))
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1d"] > 15.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      | (df["ROC_9_4h"] > -25.0)
    )
    # drop in last 6 days, 15m & 1h down move, 15m & 1h still not low enough, 15m & 1h & 4h & 1d downtrend
    & (
      (df["close"] > (df["high_max_6_1d"] * 0.25))
      | (df["RSI_3_15m"] > 25.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_14_15m"] < 30.0)
      | (df["CMF_20_15m"] > -0.10)
      | (df["CMF_20_1h"] > -0.10)
      | (df["CMF_20_4h"] > -0.40)
      | (df["CMF_20_1d"] > -0.50)
      | (df["AROONU_14_1h"] < 30.0)
    )
    # drop in last 4 days, 4h & 1d down move, 1h high
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.15))
      | (df["RSI_3_4h"] > 25.0)
      | (df["RSI_3_1d"] > 25.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
    )
    # drop in last 4 days, 1d down move, 1d downtrendm 1h still high, 1d downtrend
    & (
      (df["close"] > (df["high_max_24_4h"] * 0.15))
      | (df["RSI_3_1d"] > 20.0)
      | (df["CMF_20_1d"] > -0.30)
      | (df["AROONU_14_1h"] < 50.0)
      | (df["ROC_2_1d"] > -40.0)
    )
    # drop in last 6 days, 1d down move, 1h & 4h & 1d downtrend, 1d still high, 4h downtrend
    & (
      (df["close"] > (df["high_max_6_1d"] * 0.15))
      | (df["RSI_3_1d"] > 20.0)
      | (df["CMF_20_1h"] > -0.10)
      | (df["CMF_20_4h"] > -0.40)
      | (df["CMF_20_1d"] > -0.50)
      | (df["AROONU_14_1d"] < 50.0)
      | (df["ROC_9_4h"] > -30.0)
    )
    # drop in last 12 days. 15m & 1h & 4h & 1d down move, 4h still high, 1d downtrend
    & (
      (df["close"] > (df["high_max_12_1d"] * 0.25))
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 10.0)
      | (df["RSI_3_4h"] > 35.0)
      | (df["RSI_3_1d"] > 35.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      | (df["ROC_9_1d"] > -40.0)
    )
    # drop in last 12 days, 15m & 1h down move, 1h still not low enough, 4h high
    & (
      (df["close"] > (df["high_max_12_1d"] * 0.25))
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_1h"] > 30.0)
      | (df["RSI_14_1h"] < 30.0)
      | (df["RSI_14_4h"] < 30.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0)
    )
    # drop in last 20 days, 15m & 1h & 1d down move, 15m still not low enough, 1h high
    & (
      (df["close"] > (df["high_max_20_1d"] * 0.05))
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_1d"] > 25.0)
      | (df["AROONU_14_15m"] < 30.0)
      | (df["AROONU_14_1h"] < 80.0)
    )
    # drop in last 20 days, 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h & 1d downtrend
    & (
      (df["close"] > (df["high_max_20_1d"] * 0.01))
      | (df["RSI_3_1h"] > 45.0)
      | (df["RSI_3_4h"] > 60.0)
      | (df["RSI_3_1d"] > 15.0)
      | (df["RSI_14_1h"] < 15.0)
      | (df["RSI_14_4h"] < 20.0)
      | (df["CMF_20_1h"] > -0.0)
      | (df["CMF_20_4h"] > -0.10)
      | (df["CMF_20_1d"] > -0.40)
      | (df["CCI_20_1h"] < -150.0)
      | (df["CCI_20_4h"] < -200.0)
      | (df["ROC_2_1d"] > -25.0)
      | (df["ROC_9_1d"] > -60.0)
    )
    # drop in last 30 days, 15m & 1h down move, 1h still high, 4h high & overbought
    & (
      (df["close"] > (df["high_max_30_1d"] * 0.10))
      | (df["RSI_3_15m"] > 10.0)
      | (df["RSI_3_1h"] > 55.0)
      | (df["AROONU_14_1h"] < 40.0)
      | (df["AROONU_14_4h"] < 85.0)
      | (df["ROC_9_4h"] < 80.0)
    )
    # drop in last 30 days, 15m down move, 15m & 1h high
    & (
      (df["close"] > (df["high_max_30_1d"] * 0.05))
      | (df["RSI_3_15m"] > 15.0)
      | (df["RSI_3_4h"] > 50.0)
      | (df["AROONU_14_15m"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 85.0)
    )
    # drop in last 30 days, 15m & 1h & 4h down move, 15m still not low enough, 1h high
    & (
      (df["close"] > (df["high_max_30_1d"] * 0.05))
      | (df["RSI_3_15m"] > 25.0)
      | (df["RSI_3_1h"] > 25.0)
      | (df["RSI_3_4h"] > 40.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] < 20.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
  )
