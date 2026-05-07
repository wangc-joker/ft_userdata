"""DEC long exit signal profit-band helper extracted from NFI."""

import numpy as np

def long_exit_dec_band_9(
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
    if 0.1 > current_profit >= 0.09:
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
        return True, f"exit_{mode_name}_d_9_1"
      elif (
        (last_candle["WILLR_14"] > -1.0)
        and (last_candle["RSI_14"] > 68.0)
        and (last_candle["CMF_20_1h"] < -0.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] < last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] < last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_9_2"
      elif (
        (last_candle["WILLR_14"] > -6.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 98.0)
        and (last_candle["CMF_20_1h"] < -0.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (
          (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0) and (last_candle["STOCHRSIk_14_14_3_3_change_pct_4h"] < -10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_3"
      elif (
        (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_14"] > 74.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] < last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] < last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_9_4"
      elif (
        (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_14"] > 72.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (last_candle["ROC_9_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_9_5"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_9_6"
      elif (
        (last_candle["RSI_14"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_9_7"
      elif (
        (last_candle["WILLR_14"] > -2.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["CMF_20_1h"] < -0.1)
        and (last_candle["CMF_20_4h"] < -0.1)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
      ):
        return True, f"exit_{mode_name}_d_9_8"
      elif (
        (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3"] > 95.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_9_9"
      elif (
        (last_candle["WILLR_14"] > -6.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
      ):
        return True, f"exit_{mode_name}_d_9_10"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["RSI_14"] < 45.0)
        and (last_candle["ROC_9_15m"] < -10.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
      ):
        return True, f"exit_{mode_name}_d_9_11"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_9_1h"] < -20.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_9_12"
      elif (last_candle["RSI_3"] > 96.0) and (last_candle["RSI_3_4h"] < 5.0) and (last_candle["ROC_9_4h"] < -25.0):
        return True, f"exit_{mode_name}_d_9_13"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 5.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_14"
      elif (last_candle["RSI_3"] > 94.0) and (last_candle["RSI_14"] > 66.0) and (last_candle["ROC_9_4h"] < -30.0):
        return True, f"exit_{mode_name}_d_9_15"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["AROONU_14_1d"] > 50.0)
        and (last_candle["change_pct_1d"] < -15.0)
      ):
        return True, f"exit_{mode_name}_d_9_16"
      elif (
        (last_candle["RSI_3"] > 96.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_17"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["RSI_14"] > 74.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["ROC_2_1d"] < -50.0)
      ):
        return True, f"exit_{mode_name}_d_9_18"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["RSI_14"] > 72.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 70.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_19"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_20"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_9_21"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_9_22"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_1d"] < 5.0)
      ):
        return True, f"exit_{mode_name}_d_9_23"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["RSI_14"] > 72.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_9_24"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_25"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_9_26"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_27"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_15m"] < 10.0)
        and (last_candle["ROC_9_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_28"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_29"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_9_30"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_31"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_32"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["ROC_2_1h"] < -10.0)
        and (last_candle["ROC_9_1h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_33"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["RSI_14_1h"] > 80.0)
        and (last_candle["ROC_9_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_34"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -6.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_9_35"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_36"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_37"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_38"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -5.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_9_39"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_40"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_9_41"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 70.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_42"
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
        return True, f"exit_{mode_name}_d_9_43"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["WILLR_14"] > -5.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_9_44"
      elif (last_candle["RSI_3"] > 94.0) and (last_candle["WILLR_14"] > -6.0) and (last_candle["RSI_3_1h"] < 10.0):
        return True, f"exit_{mode_name}_d_9_45"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_2_1d"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_9_46"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -5.0))
      ):
        return True, f"exit_{mode_name}_d_9_47"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_48"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["change_pct_1d"] < -5.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_49"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1d"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_9_50"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_51"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
      ):
        return True, f"exit_{mode_name}_d_9_52"
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
        return True, f"exit_{mode_name}_d_9_53"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["change_pct_1d"] < -10.0)
      ):
        return True, f"exit_{mode_name}_d_9_54"
      elif (
        (last_candle["RSI_3"] > 94.0)
        and (last_candle["WILLR_14"] > -14.0)
        and (last_candle["ROC_9_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_55"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
      ):
        return True, f"exit_{mode_name}_d_9_56"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 36.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_9_57"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_58"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -12.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_59"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_14_4h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_60"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_61"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
        and (last_candle["change_pct_1d"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_9_62"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_63"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_9_64"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 15.0)
      ):
        return True, f"exit_{mode_name}_d_9_65"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_66"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_9_67"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_68"
      elif (
        (last_candle["RSI_3"] > 96.0)
        and (last_candle["ROC_9_4h"] > 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_9_69"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_70"
      elif (
        (last_candle["RSI_3"] > 64.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_71"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_72"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_9_73"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_74"
      elif (
        (last_candle["RSI_3"] > 96.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_75"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["ROC_9_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_9_76"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_9_77"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_78"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_9_79"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_80"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["RSI_14_1d"], np.float64) and (last_candle["RSI_14_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_9_81"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_82"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_83"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_9_84"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_85"
      elif (
        (last_candle["RSI_3"] > 94.0)
        and (last_candle["RSI_14_4h"] > 80.0)
        and (last_candle["ROC_2_1h"] < -5.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_86"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_87"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_1h"] < -2.0)
      ):
        return True, f"exit_{mode_name}_d_9_88"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_9_89"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_9_90"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_91"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_9_92"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 50.0)
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
        return True, f"exit_{mode_name}_d_9_93"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 45.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 90.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_94"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -12.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
        and (isinstance(last_candle["AROONU_14_1d"], np.float64) and (last_candle["AROONU_14_1d"] > 75.0))
      ):
        return True, f"exit_{mode_name}_d_9_95"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_1d"] < 45.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_96"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_97"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_15m"] > 72.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["RSI_3_1d"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_98"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 65.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHk_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_9_99"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["RSI_14"] > 76.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["RSI_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_9_100"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_9_101"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_9_102"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_9_103"
      elif (
        (last_candle["RSI_3"] > 64.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_104"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_15m"] < 55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_105"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_106"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (last_candle["RSI_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_107"
      elif (
        (last_candle["RSI_3"] > 56.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_9_108"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_9_109"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_3_4h"] < 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_9_110"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
      ):
        return True, f"exit_{mode_name}_d_9_111"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["RSI_3_1d"] < 60.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_9_112"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -1.0)
        and (last_candle["RSI_3_1d"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 10.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
      ):
        return True, f"exit_{mode_name}_d_9_113"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_114"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_115"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_116"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["AROONU_14_1h"] > 80.0)
        and (last_candle["AROONU_14_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_9_117"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_118"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_119"
      elif (
        (last_candle["RSI_3"] > 54.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_9_120"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_d_9_121"
      elif (
        (last_candle["RSI_3"] > 58.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_122"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_9_123"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 80.0)
        )
      ):
        return True, f"exit_{mode_name}_d_9_124"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["RSI_3_1d"] < 40.0)
        and (last_candle["close"] < (last_candle["high_max_30_1d"] * 0.50))
      ):
        return True, f"exit_{mode_name}_d_9_125"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_126"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_127"
      elif (last_candle["RSI_3"] > 94.0) and (last_candle["RSI_3_4h"] < 30.0) and (last_candle["AROONU_14_4h"] > 85.0):
        return True, f"exit_{mode_name}_d_9_128"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_9_129"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14_1h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["CCI_20_change_pct_1h"] < -0.0)
      ):
        return True, f"exit_{mode_name}_d_9_130"
      elif (
        (last_candle["RSI_14"] < 38.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_9_131"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["AROONU_14_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_9_132"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["AROONU_14_15m"] > 75.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_9_133"

    return False, None

