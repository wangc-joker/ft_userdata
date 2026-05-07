"""DEC short exit signal profit-band helper extracted from NFI."""

import numpy as np

def short_exit_dec_band_10(
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
    if 0.12 > current_profit >= 0.1:
      if (
        (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14"] < 22.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] > last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] > last_candle["EMA_200_4h"])
        )
        and (last_candle["KST_10_15_20_30_10_10_10_15_1h"] > last_candle["KSTs_9_1h"])
        and (last_candle["KST_10_15_20_30_10_10_10_15_4h"] > last_candle["KSTs_9_4h"])
      ):
        return True, f"exit_{mode_name}_d_10_1"
      elif (
        (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14"] < 30.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] > last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] > last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_10_2"
      elif (
        (last_candle["WILLR_14"] < -96.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 2.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
        and (
          (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0) and (last_candle["STOCHRSIk_14_14_3_3_change_pct_4h"] > 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_3"
      elif (
        (last_candle["WILLR_14"] < -95.0)
        and (last_candle["RSI_14"] < 24.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] > last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] > last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_10_4"
      elif (
        (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14"] < 26.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_10_5"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 30.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_10_6"
      elif (
        (last_candle["RSI_14"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_10_7"
      elif (
        (last_candle["WILLR_14"] < -99.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 5.0)
        and (last_candle["CMF_20_1h"] > 0.1)
        and (last_candle["CMF_20_4h"] > 0.1)
        and (last_candle["change_pct_1d"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
      ):
        return True, f"exit_{mode_name}_d_10_8"
      elif (
        (last_candle["WILLR_14"] < -97.0)
        and (last_candle["RSI_3"] < 5.0)
        and (last_candle["change_pct_4h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_10_9"
      elif (
        (last_candle["WILLR_14"] < -96.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (last_candle["ROC_9_4h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
      ):
        return True, f"exit_{mode_name}_d_10_10"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["RSI_14"] > 55.0)
        and (last_candle["ROC_9_15m"] > 10.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
      ):
        return True, f"exit_{mode_name}_d_10_11"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_9_1h"] > 20.0)
        and (last_candle["ROC_9_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_12"
      elif (last_candle["RSI_3"] < 4.0) and (last_candle["RSI_3_4h"] > 95.0) and (last_candle["ROC_9_4h"] > 25.0):
        return True, f"exit_{mode_name}_d_10_13"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 95.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_10_14"
      elif (last_candle["RSI_3"] < 4.0) and (last_candle["RSI_14"] < 32.0) and (last_candle["ROC_9_4h"] > 30.0):
        return True, f"exit_{mode_name}_d_10_15"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
        and (last_candle["ROC_9_4h"] > 25.0)
        and (last_candle["AROOND_14_1d"] > 50.0)
        and (last_candle["change_pct_1d"] > 15.0)
      ):
        return True, f"exit_{mode_name}_d_10_16"
      elif (
        (last_candle["RSI_3"] < 3.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -30.0)
      ):
        return True, f"exit_{mode_name}_d_10_17"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["RSI_14"] < 24.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["ROC_2_1d"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_18"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["RSI_14"] < 26.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_19"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["AROOND_14_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_10_20"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_10_21"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["change_pct_4h"] > 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_10_22"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -95.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_1d"] > 95.0)
      ):
        return True, f"exit_{mode_name}_d_10_23"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["RSI_14"] < 26.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_10_24"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_25"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["ROC_9_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_26"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_27"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_15m"] > 90.0)
        and (last_candle["ROC_9_4h"] < -50.0)
      ):
        return True, f"exit_{mode_name}_d_10_28"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_29"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_10_30"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_10_31"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["ROC_2_4h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_32"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["ROC_2_1h"] > 10.0)
        and (last_candle["ROC_9_1h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_33"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["RSI_14_1h"] < 20.0)
        and (last_candle["ROC_9_1h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_10_34"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -95.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 25.0)
      ):
        return True, f"exit_{mode_name}_d_10_35"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["ROC_9_4h"] > 25.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_36"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] < 80.0)
        and (last_candle["RSI_3_1d"] < 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_37"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_38"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -96.0)
        and (last_candle["CMF_20_4h"] > 0.0)
        and (last_candle["RSI_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_10_39"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_40"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_10_41"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_42"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_43"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_10_44"
      elif (last_candle["RSI_3"] < 4.0) and (last_candle["WILLR_14"] < -96.0) and (last_candle["RSI_3_1h"] > 90.0):
        return True, f"exit_{mode_name}_d_10_45"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_2_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_46"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
        and (last_candle["change_pct_1d"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
      ):
        return True, f"exit_{mode_name}_d_10_47"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 58.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_48"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["change_pct_1d"] > 5.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_49"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1d"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_10_50"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_51"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_14"] < 38.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
      ):
        return True, f"exit_{mode_name}_d_10_52"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["WILLR_14"] < -75.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_53"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["ROC_9_4h"] > 10.0)
        and (last_candle["change_pct_1d"] > 10.0)
      ):
        return True, f"exit_{mode_name}_d_10_54"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["ROC_9_4h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_55"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 90.0)
      ):
        return True, f"exit_{mode_name}_d_10_56"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 66.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_10_57"
      elif (
        (last_candle["RSI_3"] < 5.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_58"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_59"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 62.0)
        and (last_candle["RSI_14_4h"] < 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_60"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -85.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_61"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
        and (last_candle["change_pct_1d"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_10_62"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_63"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_10_64"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_d_10_65"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_66"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_10_67"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["ROC_2_4h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_10_68"
      elif (
        (last_candle["RSI_3"] < 3.0)
        and (last_candle["ROC_9_4h"] < -20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["change_pct_4h"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_10_69"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["RSI_14"] > 62.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_70"
      elif (
        (last_candle["RSI_3"] < 34.0)
        and (last_candle["RSI_14"] > 58.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_71"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_10_72"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["ROC_9_4h"] > 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_10_73"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_74"
      elif (
        (last_candle["RSI_3"] < 2.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_75"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["ROC_9_1h"] < -80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_76"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_10_77"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -86.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["RSI_3_1d"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_78"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_10_79"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_10_80"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["RSI_14_1d"], np.float64) and (last_candle["RSI_14_1d"] < 50.0))
      ):
        return True, f"exit_{mode_name}_d_10_81"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 85.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_82"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_83"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_10_84"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_85"
      elif (
        (last_candle["RSI_3"] < 4.0)
        and (last_candle["RSI_14_4h"] < 20.0)
        and (last_candle["ROC_2_1h"] > 5.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_86"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["RSI_14"] > 58.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_87"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -82.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["change_pct_1h"] > 2.0)
      ):
        return True, f"exit_{mode_name}_d_10_88"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 62.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_10_89"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -75.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_10_90"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_91"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_10_92"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_3_15m"] > 50.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_10_93"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 55.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_94"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 90.0)
        and (isinstance(last_candle["AROOND_14_1d"], np.float64) and (last_candle["AROOND_14_1d"] > 75.0))
      ):
        return True, f"exit_{mode_name}_d_10_95"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_1d"] > 55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_96"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_97"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_15m"] < 26.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["RSI_3_1d"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_98"
      elif (
        (last_candle["RSI_3"] < 38.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 35.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["STOCHk_14_3_3_4h"] < 60.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_10_99"
      elif (
        (last_candle["RSI_3"] < 1.0)
        and (last_candle["RSI_14"] < 22.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["RSI_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_100"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -86.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_10_101"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_10_102"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_10_103"
      elif (
        (last_candle["RSI_3"] < 34.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_10_104"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_15m"] > 45.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -25.0)
      ):
        return True, f"exit_{mode_name}_d_10_105"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["ROC_9_4h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_10_106"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
        and (last_candle["RSI_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_107"
      elif (
        (last_candle["RSI_3"] < 42.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_108"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -94.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_10_109"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_3_4h"] > 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["ROC_9_4h"] < -25.0)
      ):
        return True, f"exit_{mode_name}_d_10_110"
      elif (
        (last_candle["RSI_3"] < 48.0)
        and (last_candle["RSI_14"] > 58.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
      ):
        return True, f"exit_{mode_name}_d_10_111"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["RSI_3_4h"] > 65.0)
        and (last_candle["RSI_3_1d"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_10_112"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_3_1d"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -10.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
      ):
        return True, f"exit_{mode_name}_d_10_113"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_114"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_115"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_116"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["AROONU_14_1h"] < 20.0)
        and (last_candle["AROONU_14_4h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_10_117"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["AROOND_14_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_10_118"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_119"
      elif (
        (last_candle["RSI_3"] < 44.0)
        and (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_10_120"
      elif (
        (last_candle["RSI_3"] < 38.0)
        and (last_candle["RSI_14"] > 56.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] < 15.0)
      ):
        return True, f"exit_{mode_name}_d_10_121"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 58.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_122"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_1d"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_10_123"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 20.0)
        )
      ):
        return True, f"exit_{mode_name}_d_10_124"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -98.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["RSI_3_1d"] > 60.0)
        and (last_candle["close"] > (last_candle["low_min_30_1d"] * 2.0))
      ):
        return True, f"exit_{mode_name}_d_10_125"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_126"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_127"
      elif (last_candle["RSI_3"] < 4.0) and (last_candle["RSI_3_4h"] > 70.0) and (last_candle["AROOND_14_4h"] > 85.0):
        return True, f"exit_{mode_name}_d_10_128"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_10_129"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["RSI_14_1h"] < 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["CCI_20_change_pct_1h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_d_10_130"
      elif (
        (last_candle["RSI_14"] > 64.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_10_131"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["RSI_3_4h"] > 65.0)
        and (last_candle["AROOND_14_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_10_132"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["AROOND_14_15m"] > 75.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_10_133"

    return False, None

