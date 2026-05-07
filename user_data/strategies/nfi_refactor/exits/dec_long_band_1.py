"""DEC long exit signal profit-band helper extracted from NFI."""

import numpy as np

def long_exit_dec_band_1(
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
    if 0.02 > current_profit >= 0.01:
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
        return True, f"exit_{mode_name}_d_1_1"
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
        return True, f"exit_{mode_name}_d_1_2"
      elif (
        (last_candle["WILLR_14"] > -8.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 99.0)
        and (last_candle["CMF_20_1h"] < -0.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (
          (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0) and (last_candle["STOCHRSIk_14_14_3_3_change_pct_4h"] < -10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_1_3"
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
        return True, f"exit_{mode_name}_d_1_4"
      elif (
        (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_14"] > 72.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (last_candle["ROC_9_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_1_5"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_1_6"
      elif (
        (last_candle["RSI_14"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_1_7"
      elif (
        (last_candle["WILLR_14"] > -2.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] > 95.0)
        and (last_candle["CMF_20_1h"] < -0.1)
        and (last_candle["CMF_20_4h"] < -0.1)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
      ):
        return True, f"exit_{mode_name}_d_1_8"
      elif (
        (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3"] > 95.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_1_9"
      elif (
        (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
      ):
        return True, f"exit_{mode_name}_d_1_10"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] < 45.0)
        and (last_candle["ROC_9_15m"] < -10.0)
        and (last_candle["ROC_9_1h"] < -10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
      ):
        return True, f"exit_{mode_name}_d_1_11"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_9_1h"] < -20.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_1_12"
      elif (last_candle["RSI_3"] > 80.0) and (last_candle["RSI_3_4h"] < 5.0) and (last_candle["ROC_9_4h"] < -25.0):
        return True, f"exit_{mode_name}_d_1_13"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 5.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_14"
      elif (last_candle["RSI_3"] > 95.0) and (last_candle["RSI_14"] > 75.0) and (last_candle["ROC_9_4h"] < -30.0):
        return True, f"exit_{mode_name}_d_1_15"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["AROONU_14_1d"] > 50.0)
        and (last_candle["change_pct_1d"] < -15.0)
      ):
        return True, f"exit_{mode_name}_d_1_16"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_17"
      elif (
        (last_candle["RSI_3"] > 75.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["ROC_2_1d"] < -50.0)
      ):
        return True, f"exit_{mode_name}_d_1_18"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["RSI_14"] > 72.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 70.0)
        )
      ):
        return True, f"exit_{mode_name}_d_1_19"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_20"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_1_21"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["change_pct_4h"] < -5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_1_22"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_1d"] < 5.0)
      ):
        return True, f"exit_{mode_name}_d_1_23"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["RSI_14"] > 75.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_1_24"
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
        return True, f"exit_{mode_name}_d_1_25"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_1_26"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_27"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_15m"] < 10.0)
        and (last_candle["ROC_9_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_28"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_29"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_1_30"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_31"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_32"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["ROC_2_1h"] < -10.0)
        and (last_candle["ROC_9_1h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_33"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["RSI_14_1h"] > 80.0)
        and (last_candle["ROC_9_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_34"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -6.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_1_35"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["ROC_9_4h"] < -25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_36"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_37"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -15.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_38"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -5.0)
        and (last_candle["CMF_20_4h"] < -0.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_1_39"
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
        return True, f"exit_{mode_name}_d_1_40"
      elif (
        (last_candle["RSI_3"] > 95.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_1_41"
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
        return True, f"exit_{mode_name}_d_1_42"
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
        return True, f"exit_{mode_name}_d_1_43"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["WILLR_14"] > -5.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_1_44"
      elif (last_candle["RSI_3"] > 94.0) and (last_candle["WILLR_14"] > -6.0) and (last_candle["RSI_3_1h"] < 10.0):
        return True, f"exit_{mode_name}_d_1_45"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["ROC_2_1d"] < -20.0)
      ):
        return True, f"exit_{mode_name}_d_1_46"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (last_candle["change_pct_1d"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -5.0))
      ):
        return True, f"exit_{mode_name}_d_1_47"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_48"
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
        return True, f"exit_{mode_name}_d_1_49"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1d"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_1_50"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_51"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
      ):
        return True, f"exit_{mode_name}_d_1_52"
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
        return True, f"exit_{mode_name}_d_1_53"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["ROC_9_4h"] < -10.0)
        and (last_candle["change_pct_1d"] < -10.0)
      ):
        return True, f"exit_{mode_name}_d_1_54"
      elif (
        (last_candle["RSI_3"] > 94.0)
        and (last_candle["WILLR_14"] > -14.0)
        and (last_candle["ROC_9_4h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_55"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
      ):
        return True, f"exit_{mode_name}_d_1_56"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 36.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_1_57"
      elif (
        (last_candle["RSI_3"] > 70.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_58"
      elif (
        (last_candle["RSI_3"] > 85.0)
        and (last_candle["WILLR_14"] > -12.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_59"
      elif (
        (last_candle["RSI_3"] > 65.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_14_4h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_60"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_4h"] < 10.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_61"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
        and (last_candle["change_pct_1d"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_1_62"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_63"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_1_64"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 15.0)
      ):
        return True, f"exit_{mode_name}_d_1_65"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_66"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_1_67"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["ROC_2_4h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_68"
      elif (
        (last_candle["RSI_3"] > 96.0)
        and (last_candle["ROC_9_4h"] > 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_4h"] < -5.0)
      ):
        return True, f"exit_{mode_name}_d_1_69"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_70"
      elif (
        (last_candle["RSI_3"] > 64.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_71"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 42.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["AROONU_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_72"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 15.0)
        and (last_candle["ROC_9_4h"] < -20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_1_73"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (last_candle["RSI_3_1d"] < 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_74"
      elif (
        (last_candle["RSI_3"] > 96.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_1_75"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["ROC_9_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_1_76"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_1_77"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (last_candle["RSI_3_1d"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_78"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_1_79"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_80"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_1h"] < 25.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["RSI_14_1d"], np.float64) and (last_candle["RSI_14_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_1_81"
      elif (
        (last_candle["RSI_3"] > 82.0)
        and (last_candle["WILLR_14"] > -10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 15.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_82"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_83"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_1_84"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 30.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_85"
      elif (
        (last_candle["RSI_3"] > 94.0)
        and (last_candle["RSI_14_4h"] > 80.0)
        and (last_candle["ROC_2_1h"] < -5.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_86"
      elif (
        (last_candle["RSI_3"] > 66.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_87"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["change_pct_1h"] < -2.0)
      ):
        return True, f"exit_{mode_name}_d_1_88"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_1_89"
      elif (
        (last_candle["RSI_3"] > 92.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_1_90"
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
        return True, f"exit_{mode_name}_d_1_91"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 25.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_1_92"
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
        return True, f"exit_{mode_name}_d_1_93"
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
        return True, f"exit_{mode_name}_d_1_94"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -12.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 10.0)
        and (isinstance(last_candle["AROONU_14_1d"], np.float64) and (last_candle["AROONU_14_1d"] > 75.0))
      ):
        return True, f"exit_{mode_name}_d_1_95"
      elif (
        (last_candle["RSI_3"] > 62.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 45.0)
        and (last_candle["RSI_3_1d"] < 45.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_96"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_97"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_15m"] > 72.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["RSI_3_1d"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_98"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 65.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
        and (last_candle["STOCHk_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_1_99"
      elif (
        (last_candle["RSI_3"] > 98.0)
        and (last_candle["RSI_14"] > 76.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["RSI_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_1_100"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -16.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 40.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_1_101"
      elif (
        (last_candle["RSI_3"] > 68.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_1_102"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 56.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_1_103"
      elif (
        (last_candle["RSI_3"] > 64.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_104"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_15m"] < 55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_105"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["ROC_9_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_106"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 70.0)
        and (last_candle["RSI_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_107"
      elif (
        (last_candle["RSI_3"] > 56.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_1_108"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["WILLR_14"] > -8.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 50.0))
      ):
        return True, f"exit_{mode_name}_d_1_109"
      elif (
        (last_candle["RSI_3"] > 72.0)
        and (last_candle["RSI_3_4h"] < 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (last_candle["ROC_9_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_1_110"
      elif (
        (last_candle["RSI_3"] > 50.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 70.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
      ):
        return True, f"exit_{mode_name}_d_1_111"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["WILLR_14"] > -25.0)
        and (last_candle["RSI_14"] < 52.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["RSI_3_1d"] < 60.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_1_112"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["WILLR_14"] > -2.0)
        and (last_candle["RSI_3_1d"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] > 10.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
      ):
        return True, f"exit_{mode_name}_d_1_113"
      elif (
        (last_candle["RSI_3"] > 84.0)
        and (last_candle["RSI_14"] < 50.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_114"
      elif (
        (last_candle["RSI_3"] > 78.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_115"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_116"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["AROONU_14_1h"] > 80.0)
        and (last_candle["AROONU_14_4h"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_1_117"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["AROONU_14_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_118"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["WILLR_14"] > -20.0)
        and (last_candle["RSI_3_1h"] < 60.0)
        and (last_candle["RSI_3_4h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_119"
      elif (
        (last_candle["RSI_3"] > 54.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["RSI_3_1h"] < 40.0)
        and (last_candle["AROONU_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_1_120"
      elif (
        (last_candle["RSI_3"] > 60.0)
        and (last_candle["RSI_14"] < 46.0)
        and (last_candle["RSI_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_d_1_121"
      elif (
        (last_candle["RSI_3"] > 58.0)
        and (last_candle["RSI_14"] < 44.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_122"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_1d"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_1_123"
      elif (
        (last_candle["RSI_3"] > 88.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] > 80.0)
        )
      ):
        return True, f"exit_{mode_name}_d_1_124"
      elif (
        (last_candle["RSI_3"] > 76.0)
        and (last_candle["WILLR_14"] > -4.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["RSI_3_1d"] < 40.0)
        and (last_candle["close"] < (last_candle["high_max_30_1d"] * 0.50))
      ):
        return True, f"exit_{mode_name}_d_1_125"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 15.0)
        and (last_candle["RSI_3_4h"] < 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_126"
      elif (
        (last_candle["RSI_3"] > 90.0)
        and (last_candle["RSI_3_1h"] < 10.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["RSI_3_1d"] < 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_127"
      elif (last_candle["RSI_3"] > 94.0) and (last_candle["RSI_3_4h"] < 30.0) and (last_candle["AROONU_14_4h"] > 85.0):
        return True, f"exit_{mode_name}_d_1_128"
      elif (
        (last_candle["RSI_3"] > 86.0)
        and (last_candle["RSI_3_4h"] < 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 80.0))
      ):
        return True, f"exit_{mode_name}_d_1_129"
      elif (
        (last_candle["RSI_3"] > 74.0)
        and (last_candle["RSI_14_1h"] > 65.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 80.0)
        and (last_candle["CCI_20_change_pct_1h"] < -0.0)
      ):
        return True, f"exit_{mode_name}_d_1_130"
      elif (
        (last_candle["RSI_14"] < 38.0)
        and (last_candle["RSI_3_1h"] < 20.0)
        and (last_candle["RSI_3_4h"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_1_131"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["RSI_3_1h"] < 35.0)
        and (last_candle["RSI_3_4h"] < 35.0)
        and (last_candle["AROONU_14_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_1_132"
      elif (
        (last_candle["RSI_3"] > 80.0)
        and (last_candle["AROONU_14_15m"] > 75.0)
        and (last_candle["AROONU_14_1h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_1_133"

    return False, None

