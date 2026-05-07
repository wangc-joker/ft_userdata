"""Williams-R short exit signal library extracted from NFI."""

import numpy as np

def short_exit_williams_r(
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
    if 0.01 > current_profit >= 0.001:
      if (last_candle["WILLR_480"] < -99.9) and (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 25.0):
        return True, f"exit_{mode_name}_w_0_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 16.0):
        return True, f"exit_{mode_name}_w_0_2"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] > 60.0):
        return True, f"exit_{mode_name}_w_0_3"
      elif (
        (last_candle["WILLR_14"] <= -99.0)
        and (last_candle["RSI_14"] < 20.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_0_4"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_0_5"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_0_6"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_0_7"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_0_8"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_0_9"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -84.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_0_10"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_w_0_11"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_0_12"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_0_13"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_0_14"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_0_15"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_0_16"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_0_17"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_0_18"
    elif 0.02 > current_profit >= 0.01:
      if last_candle["WILLR_480"] < -99.8:
        return True, f"exit_{mode_name}_w_1_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 22.0):
        return True, f"exit_{mode_name}_w_1_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 54.0):
        return True, f"exit_{mode_name}_w_1_3"
      elif (
        (last_candle["WILLR_14"] <= -98.0)
        and (last_candle["RSI_14"] < 22.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_1_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_1_5"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_1_6"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_1_7"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_1_8"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_1_9"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -82.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_1_10"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_1_11"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_1_12"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_1_13"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_1_14"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_1_15"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_1_16"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_1_17"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_1_18"
    elif 0.03 > current_profit >= 0.02:
      if last_candle["WILLR_480"] < -99.7:
        return True, f"exit_{mode_name}_w_2_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 23.0):
        return True, f"exit_{mode_name}_w_2_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 52.0):
        return True, f"exit_{mode_name}_w_2_3"
      elif (
        (last_candle["WILLR_14"] <= -95.0)
        and (last_candle["RSI_14"] < 25.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_2_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_2_5"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_2_6"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_2_7"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_2_8"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_2_9"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_2_10"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_2_11"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_2_12"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_2_13"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_2_14"
      elif (
        (last_candle["RSI_3"] < 52.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_2_15"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_2_16"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_2_17"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_2_18"
    elif 0.04 > current_profit >= 0.03:
      if last_candle["WILLR_480"] < -99.6:
        return True, f"exit_{mode_name}_w_3_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 24.0):
        return True, f"exit_{mode_name}_w_3_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 50.0):
        return True, f"exit_{mode_name}_w_3_3"
      elif (
        (last_candle["WILLR_14"] <= -95.0)
        and (last_candle["RSI_14"] < 25.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_3_4"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_3_5"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_3_6"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_3_7"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_3_8"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_3_9"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -78.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_3_10"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_3_11"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_3_12"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_3_13"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_3_14"
      elif (
        (last_candle["RSI_3"] < 54.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_3_15"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_3_16"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_3_17"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_3_18"
    elif 0.05 > current_profit >= 0.04:
      if last_candle["WILLR_480"] < -99.5:
        return True, f"exit_{mode_name}_w_4_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 25.0):
        return True, f"exit_{mode_name}_w_4_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 48.0):
        return True, f"exit_{mode_name}_w_4_3"
      elif (
        (last_candle["WILLR_14"] <= -95.0)
        and (last_candle["RSI_14"] < 25.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_4_4"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_4_5"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_4_6"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_4_7"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_4_8"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_4_9"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -76.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_4_10"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_4_11"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_4_12"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_4_13"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_4_14"
      elif (
        (last_candle["RSI_3"] < 56.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_4_15"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_4_16"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_4_17"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_4_18"
    elif 0.06 > current_profit >= 0.05:
      if last_candle["WILLR_480"] < -99.4:
        return True, f"exit_{mode_name}_w_5_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 26.0):
        return True, f"exit_{mode_name}_w_5_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 46.0):
        return True, f"exit_{mode_name}_w_5_3"
      elif (
        (last_candle["WILLR_14"] <= -90.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_5_4"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -86.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_5_5"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_5_6"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_5_7"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_5_8"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_5_9"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -74.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_5_10"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_5_11"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_5_12"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_5_13"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_5_14"
      elif (
        (last_candle["RSI_3"] < 58.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 42.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_5_15"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_5_16"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -86.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_5_17"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_5_18"
    elif 0.07 > current_profit >= 0.06:
      if last_candle["WILLR_480"] < -99.3:
        return True, f"exit_{mode_name}_w_6_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 25.0):
        return True, f"exit_{mode_name}_w_6_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 48.0):
        return True, f"exit_{mode_name}_w_6_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_6_4"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_6_5"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_6_6"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_6_7"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_6_8"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_6_9"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -76.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_6_10"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_6_11"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_6_12"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_6_13"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_6_14"
      elif (
        (last_candle["RSI_3"] < 56.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_6_15"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_6_16"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_6_17"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_6_18"
    elif 0.08 > current_profit >= 0.07:
      if last_candle["WILLR_480"] < -99.2:
        return True, f"exit_{mode_name}_w_7_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 24.0):
        return True, f"exit_{mode_name}_w_7_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 50.0):
        return True, f"exit_{mode_name}_w_7_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_7_4"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_7_5"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_7_6"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_7_7"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_7_8"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_7_9"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -78.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_7_10"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_7_11"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_7_12"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_7_13"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_7_14"
      elif (
        (last_candle["RSI_3"] < 54.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_7_15"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_7_16"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_7_17"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_7_18"
    elif 0.09 > current_profit >= 0.08:
      if last_candle["WILLR_480"] < -99.1:
        return True, f"exit_{mode_name}_w_8_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 23.0):
        return True, f"exit_{mode_name}_w_8_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 52.0):
        return True, f"exit_{mode_name}_w_8_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_8_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_8_5"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_8_6"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_8_7"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_8_8"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_8_9"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_8_10"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_8_11"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_8_12"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_8_13"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_8_14"
      elif (
        (last_candle["RSI_3"] < 52.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_8_15"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_8_16"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_8_17"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_8_18"
    elif 0.1 > current_profit >= 0.09:
      if last_candle["WILLR_480"] < -99.0:
        return True, f"exit_{mode_name}_w_9_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 22.0):
        return True, f"exit_{mode_name}_w_9_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 54.0):
        return True, f"exit_{mode_name}_w_9_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_9_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_9_5"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_9_6"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_9_7"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_9_8"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_9_9"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -82.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_9_10"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_9_11"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_9_12"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_9_13"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_9_14"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_9_15"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_9_16"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_9_17"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_9_18"
    elif 0.12 > current_profit >= 0.1:
      if last_candle["WILLR_480"] < -98.9:
        return True, f"exit_{mode_name}_w_10_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 21.0):
        return True, f"exit_{mode_name}_w_10_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 56.0):
        return True, f"exit_{mode_name}_w_10_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_10_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_10_5"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_10_6"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_10_7"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_10_8"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_10_9"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -84.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_10_10"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_10_11"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_10_12"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_10_13"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_10_14"
      elif (
        (last_candle["RSI_3"] < 48.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_10_15"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_10_16"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_10_17"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_10_18"
    elif 0.2 > current_profit >= 0.12:
      if last_candle["WILLR_480"] < -99.6:
        return True, f"exit_{mode_name}_w_11_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 20.0):
        return True, f"exit_{mode_name}_w_11_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 58.0):
        return True, f"exit_{mode_name}_w_11_3"
      elif (
        (last_candle["WILLR_14"] <= -85.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_11_4"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_11_5"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_11_6"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_11_7"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_11_8"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_11_9"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["WILLR_14"] < -86.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_11_10"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_11_11"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_11_12"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_11_13"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_11_14"
      elif (
        (last_candle["RSI_3"] < 46.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_11_15"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_11_16"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_11_17"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_11_18"
    elif current_profit >= 0.2:
      if last_candle["WILLR_480"] < -99.8:
        return True, f"exit_{mode_name}_w_12_1"
      elif (last_candle["WILLR_14"] <= -99.0) and (last_candle["RSI_14"] < 19.0):
        return True, f"exit_{mode_name}_w_12_2"
      elif (last_candle["WILLR_14"] <= -98.0) and (last_candle["RSI_14"] > 60.0):
        return True, f"exit_{mode_name}_w_12_3"
      elif (
        (last_candle["WILLR_14"] <= -99.0)
        and (last_candle["RSI_14"] < 20.0)
        and (last_candle["ROC_9_1h"] > 0.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_w_12_4"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_12_5"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_w_12_6"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14_4h"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_w_12_7"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_w_12_8"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_w_12_9"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["CCI_20_change_pct_4h"] > 0.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_w_12_10"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_w_12_11"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_w_12_12"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_w_12_13"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_w_12_14"
      elif (
        (last_candle["RSI_3"] < 44.0)
        and (last_candle["WILLR_480"] < -75.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -100.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -100.0))
      ):
        return True, f"exit_{mode_name}_w_12_15"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_w_12_16"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_w_12_17"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (last_candle["bot_wick_pct_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_w_12_18"

    #  Here ends exit signal conditions for short_exit_williams_r

    return False, None
