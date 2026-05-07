"""DEC long exit signal profit-band helper extracted from NFI."""

import numpy as np

def long_exit_dec_band_4(
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
    if 0.05 > current_profit >= 0.04:
      if (
        (last_candle["WILLR_14"] > -1.0)
        and (last_candle["RSI_14"] > 78.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] < last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] < last_candle["EMA_200_4h"])
        )
        and (last_candle["KST_10_15_20_30_10_10_10_15_1h"] < last_candle["KSTs_9_1h"])
        and (last_candle["KST_10_15_20_30_10_10_10_15_4h"] < last_candle["KSTs_9_4h"])
      ):
        return True, f"exit_{mode_name}_d_4_1"
      elif (
        (last_candle["WILLR_14"] > -1.0)
        and (last_candle["RSI_14"] > 62.0)
        and (last_candle["CMF_20_1h"] < -0.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] < last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] < last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_4_2"
      elif (
        (last_candle["WILLR_14"] > -20.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["CMF_20_1h"] < -0.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (
          (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0) and (last_candle["STOCHRSIk_14_14_3_3_change_pct_4h"] < -10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_3"
      elif (
        (last_candle["WILLR_14"] > -30.0)
        and (last_candle["RSI_14"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] < last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] < last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_4_4"
      elif (
        (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_14"] > 66.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (last_candle["ROC_9_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_4_5"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_4_6"
      elif (
        (last_candle["RSI_14"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_4_7"
      elif (
        (last_candle["WILLR_14"] > -8.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["CMF_20_1h"] < -0.1)
        and (last_candle["CMF_20_4h"] < -0.1)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
      ):
        return True, f"exit_{mode_name}_d_4_8"
      elif (
        (last_candle["WILLR_14"] > -7.0)
        and (last_candle["RSI_3"] > 95.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_4_9"
      elif (
        (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
      ):
        return True, f"exit_{mode_name}_d_4_10"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] < 45.0)
        and (last_candle["ROC_9_15m"] < -10.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
      ):
        return True, f"exit_{mode_name}_d_4_11"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_9_1h"] < -20.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_4_12"
      elif (last_candle["RSI_3"] > 80.0) and (last_candle["RSI_3_4h"] < 5.0) and (last_candle["ROC_9_4h"] < -25.0):
        return True, f"exit_{mode_name}_d_4_13"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 5.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_14"
      elif (last_candle["RSI_3"] > 88.0) and (last_candle["RSI_14"] > 60.0) and (last_candle["ROC_9_4h"] < -30.0):
        return True, f"exit_{mode_name}_d_4_15"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["AROONU_14_1d"] > 50.0)
        and (last_candle["change_pct_1d"] < -15.0)
      ):
        return True, f"exit_{mode_name}_d_4_16"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -30.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_17"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["ROC_2_1d"] < -50.0)
      ):
        return True, f"exit_{mode_name}_d_4_18"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_14"] > 66.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 70.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_19"
      elif (
        (last_candle["RSI_3"] > 44.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_20"
      elif (
        (last_candle["RSI_3"] > 55.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_4_21"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_4_22"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_1d"] < 5.0)
      ):
        return True, f"exit_{mode_name}_d_4_23"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_14"] > 66.0)
        and (last_candle["WILLR_14"] > -30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_4_24"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_25"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_4_26"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_27"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_15m"] < 10.0)
        and (last_candle["ROC_9_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_28"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_29"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_4_30"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_31"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_32"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["ROC_2_1h"] < -10.0)
        and (last_candle["ROC_9_1h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_33"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["RSI_14_1h"] > 80.0)
        and (last_candle["ROC_9_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_34"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -9.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_4_35"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -30.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_36"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_37"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -30.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_38"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_4_39"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -30.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_40"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_4_41"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["WILLR_14"] > -40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 70.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_42"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_43"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_4_44"
      elif (last_candle["RSI_3"] > 88.0) and (last_candle["WILLR_14"] > -12.0) and (last_candle["RSI_3_1h"] < 10.0):
        return True, f"exit_{mode_name}_d_4_45"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_2_1d"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_4_46"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -5.0))
      ):
        return True, f"exit_{mode_name}_d_4_47"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_48"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["change_pct_1d"] < -5.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_49"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1d"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_4_50"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_51"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
      ):
        return True, f"exit_{mode_name}_d_4_52"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_53"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["change_pct_1d"] < -10.0)
      ):
        return True, f"exit_{mode_name}_d_4_54"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["ROC_9_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_55"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
      ):
        return True, f"exit_{mode_name}_d_4_56"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 42.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_4_57"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_58"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -18.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_59"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_14_4h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_60"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_61"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
        and (last_candle["change_pct_1d"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_4_62"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_63"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_4_64"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 15.0)
      ):
        return True, f"exit_{mode_name}_d_4_65"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_66"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_4_67"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_68"
      elif (
        (last_candle["RSI_3"] > 93.0)
        and (last_candle["ROC_9_4h"] > 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_4_69"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_70"
      elif (
        (last_candle["RSI_3"] > 58.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_71"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_72"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_4_73"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_74"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_75"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["ROC_9_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_4_76"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_4_77"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -22.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_78"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_4_79"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_80"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["RSI_14_1d"], np.float64) and (last_candle["RSI_14_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_4_81"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_82"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_83"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_4_84"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -14.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_85"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["RSI_14_4h"] > 80.0)
        and (last_candle["ROC_2_1h"] < -5.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_86"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_87"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -26.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_1h"] < -2.0)
      ):
        return True, f"exit_{mode_name}_d_4_88"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_4_89"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_4_90"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_91"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_4_92"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["RSI_3_15m"] < 50.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_4_93"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 45.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_94"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["WILLR_14"] > -18.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
        and (isinstance(last_candle["AROONU_14_1d"], np.float64) and (last_candle["AROONU_14_1d"] > 75.0))
      ):
        return True, f"exit_{mode_name}_d_4_95"
      elif (
        (last_candle["RSI_3"] > 56.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_1d"] < 45.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_96"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_97"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_3_15m"] > 66.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["RSI_3_1d"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_98"
      elif (
        (last_candle["RSI_3"] > 54.0)
        and (last_candle["RSI_14"] < 58.0)
        and (last_candle["RSI_3_1h"] < 65.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHk_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_4_99"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["RSI_14"] > 70.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["RSI_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_4_100"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["WILLR_14"] > -22.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_4_101"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_4_102"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 62.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_4_103"
      elif (
        (last_candle["RSI_3"] > 58.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_104"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_15m"] < 55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_105"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_106"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (last_candle["RSI_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_107"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_4_108"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -14.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_4_109"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_3_4h"] < 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_4_110"
      elif (
        (last_candle["RSI_3"] > 44.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
      ):
        return True, f"exit_{mode_name}_d_4_111"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["WILLR_14"] > -40.0)
        and (last_candle["RSI_14"] < 58.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["RSI_3_1d"] < 60.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_4_112"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1d"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 10.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
      ):
        return True, f"exit_{mode_name}_d_4_113"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_114"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_115"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_116"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["AROONU_14_1h"] > 80.0)
        and (last_candle["AROONU_14_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_4_117"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_118"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_119"
      elif (
        (last_candle["RSI_3"] > 48.0)
        and (last_candle["RSI_14"] < 54.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_4_120"
      elif (
        (last_candle["RSI_3"] > 54.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_d_4_121"
      elif (
        (last_candle["RSI_3"] > 52.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_122"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_4_123"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 80.0)
        )
      ):
        return True, f"exit_{mode_name}_d_4_124"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["RSI_3_1d"] < 40.0)
        and (last_candle["close"] < (last_candle["high_max_30_1d"] * 0.50))
      ):
        return True, f"exit_{mode_name}_d_4_125"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_126"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_127"
      elif (last_candle["RSI_3"] > 88.0) and (last_candle["RSI_3_4h"] < 30.0) and (last_candle["AROONU_14_4h"] > 85.0):
        return True, f"exit_{mode_name}_d_4_128"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_4_129"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14_1h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["CCI_20_change_pct_1h"] < -0.0)
      ):
        return True, f"exit_{mode_name}_d_4_130"
      elif (
        (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_4_131"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["AROONU_14_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_4_132"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["AROONU_14_15m"] > 75.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_4_133"

    return False, None

