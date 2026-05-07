"""DEC short exit signal profit-band helper extracted from NFI."""

import numpy as np

def short_exit_dec_band_5(
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
    if 0.06 > current_profit >= 0.05:
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
        return True, f"exit_{mode_name}_d_5_1"
      elif (
        (last_candle["WILLR_14"] < -99.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] > last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] > last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_5_2"
      elif (
        (last_candle["WILLR_14"] < -80.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 5.0)
        and (last_candle["CMF_20_1h"] > 0.0)
        and (last_candle["CMF_20_4h"] > 0.0)
        and (
          (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0) and (last_candle["STOCHRSIk_14_14_3_3_change_pct_4h"] > 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_3"
      elif (
        (last_candle["WILLR_14"] < -70.0)
        and (last_candle["RSI_14"] < 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
        and (
          isinstance(last_candle["EMA_200_1h"], np.float64) and (last_candle["EMA_12_1h"] > last_candle["EMA_200_1h"])
        )
        and (
          isinstance(last_candle["EMA_200_4h"], np.float64) and (last_candle["EMA_12_4h"] > last_candle["EMA_200_4h"])
        )
      ):
        return True, f"exit_{mode_name}_d_5_4"
      elif (
        (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_14"] < 36.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (last_candle["ROC_9_4h"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_5_5"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 30.0)
        and (last_candle["RSI_14"] > 60.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_5_6"
      elif (
        (last_candle["RSI_14"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 40.0))
      ):
        return True, f"exit_{mode_name}_d_5_7"
      elif (
        (last_candle["WILLR_14"] < -90.0)
        and (last_candle["STOCHRSIk_14_14_3_3"] < 5.0)
        and (last_candle["CMF_20_1h"] > 0.1)
        and (last_candle["CMF_20_4h"] > 0.1)
        and (last_candle["change_pct_1d"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -15.0))
      ):
        return True, f"exit_{mode_name}_d_5_8"
      elif (
        (last_candle["WILLR_14"] < -92.0)
        and (last_candle["RSI_3"] < 5.0)
        and (last_candle["change_pct_4h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_5_9"
      elif (
        (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (last_candle["ROC_9_4h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
      ):
        return True, f"exit_{mode_name}_d_5_10"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["RSI_14"] > 55.0)
        and (last_candle["ROC_9_15m"] > 10.0)
        and (last_candle["ROC_9_1h"] > 10.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 20.0))
      ):
        return True, f"exit_{mode_name}_d_5_11"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_9_1h"] > 20.0)
        and (last_candle["ROC_9_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_12"
      elif (last_candle["RSI_3"] < 20.0) and (last_candle["RSI_3_4h"] > 95.0) and (last_candle["ROC_9_4h"] > 25.0):
        return True, f"exit_{mode_name}_d_5_13"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_4h"] > 95.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_5_14"
      elif (last_candle["RSI_3"] < 14.0) and (last_candle["RSI_14"] > 58.0) and (last_candle["ROC_9_4h"] > 30.0):
        return True, f"exit_{mode_name}_d_5_15"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
        and (last_candle["ROC_9_4h"] > 25.0)
        and (last_candle["AROOND_14_1d"] > 50.0)
        and (last_candle["change_pct_1d"] > 15.0)
      ):
        return True, f"exit_{mode_name}_d_5_16"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -65.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -30.0)
      ):
        return True, f"exit_{mode_name}_d_5_17"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["RSI_14"] < 40.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["ROC_2_1d"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_18"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["RSI_14"] < 36.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_19"
      elif (
        (last_candle["RSI_3"] < 58.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["AROOND_14_1h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_5_20"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_5_21"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["change_pct_4h"] > 5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_5_22"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["WILLR_14"] < -70.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_1d"] > 95.0)
      ):
        return True, f"exit_{mode_name}_d_5_23"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["RSI_14"] < 36.0)
        and (last_candle["WILLR_14"] < -65.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_5_24"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_9_4h"] > 15.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_25"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["ROC_9_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_26"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_27"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_15m"] > 90.0)
        and (last_candle["ROC_9_4h"] < -50.0)
      ):
        return True, f"exit_{mode_name}_d_5_28"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_29"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_5_30"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_5_31"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["ROC_2_4h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_32"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["ROC_2_1h"] > 10.0)
        and (last_candle["ROC_9_1h"] < -30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_33"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["RSI_14_1h"] < 20.0)
        and (last_candle["ROC_9_1h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_5_34"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 25.0)
      ):
        return True, f"exit_{mode_name}_d_5_35"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["WILLR_14"] < -65.0)
        and (last_candle["ROC_9_4h"] > 25.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_36"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] < 80.0)
        and (last_candle["RSI_3_1d"] < 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_37"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["WILLR_14"] < -65.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_38"
      elif (
        (last_candle["RSI_3"] < 9.0)
        and (last_candle["WILLR_14"] < -91.0)
        and (last_candle["CMF_20_4h"] > 0.0)
        and (last_candle["RSI_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_5_39"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["WILLR_14"] < -65.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_40"
      elif (
        (last_candle["RSI_3"] < 25.0)
        and (last_candle["WILLR_14"] < -70.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_5_41"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["WILLR_14"] < -55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 30.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_42"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_43"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["WILLR_14"] < -75.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 25.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
      ):
        return True, f"exit_{mode_name}_d_5_44"
      elif (last_candle["RSI_3"] < 14.0) and (last_candle["WILLR_14"] < -86.0) and (last_candle["RSI_3_1h"] > 90.0):
        return True, f"exit_{mode_name}_d_5_45"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["ROC_2_1d"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_46"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
        and (last_candle["change_pct_1d"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 5.0))
      ):
        return True, f"exit_{mode_name}_d_5_47"
      elif (
        (last_candle["RSI_3"] < 55.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_48"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["change_pct_1d"] > 5.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_49"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_1d"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 10.0)
      ):
        return True, f"exit_{mode_name}_d_5_50"
      elif (
        (last_candle["RSI_3"] < 42.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_51"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["RSI_14"] < 48.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
      ):
        return True, f"exit_{mode_name}_d_5_52"
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
        return True, f"exit_{mode_name}_d_5_53"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["ROC_9_4h"] > 10.0)
        and (last_candle["change_pct_1d"] > 10.0)
      ):
        return True, f"exit_{mode_name}_d_5_54"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["WILLR_14"] < -78.0)
        and (last_candle["ROC_9_4h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -10.0))
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_55"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 90.0)
      ):
        return True, f"exit_{mode_name}_d_5_56"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 56.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 30.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 30.0)
      ):
        return True, f"exit_{mode_name}_d_5_57"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_58"
      elif (
        (last_candle["RSI_3"] < 15.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 15.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_59"
      elif (
        (last_candle["RSI_3"] < 35.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_14_4h"] < 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_60"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["WILLR_14"] < -75.0)
        and (last_candle["RSI_3_4h"] > 90.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_61"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
        and (last_candle["change_pct_1d"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_5_62"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_63"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_5_64"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 85.0)
      ):
        return True, f"exit_{mode_name}_d_5_65"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_66"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_5_67"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["ROC_2_4h"] > 30.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_5_68"
      elif (
        (last_candle["RSI_3"] < 8.0)
        and (last_candle["ROC_9_4h"] < -20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["change_pct_4h"] > 5.0)
      ):
        return True, f"exit_{mode_name}_d_5_69"
      elif (
        (last_candle["RSI_3"] < 42.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_70"
      elif (
        (last_candle["RSI_3"] < 44.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_71"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 50.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["AROOND_14_4h"] > 25.0)
      ):
        return True, f"exit_{mode_name}_d_5_72"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 85.0)
        and (last_candle["ROC_9_4h"] > 20.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_5_73"
      elif (
        (last_candle["RSI_3"] < 6.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["RSI_3_1d"] > 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_74"
      elif (
        (last_candle["RSI_3"] < 12.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_75"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 42.0)
        and (last_candle["ROC_9_1h"] < -80.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_76"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_5_77"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -76.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (last_candle["RSI_3_1d"] > 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_78"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 90.0)
      ):
        return True, f"exit_{mode_name}_d_5_79"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 75.0)
      ):
        return True, f"exit_{mode_name}_d_5_80"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["WILLR_14"] < -82.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["RSI_14_1d"], np.float64) and (last_candle["RSI_14_1d"] < 50.0))
      ):
        return True, f"exit_{mode_name}_d_5_81"
      elif (
        (last_candle["RSI_3"] < 26.0)
        and (last_candle["WILLR_14"] < -82.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 85.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_82"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_83"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 80.0)
      ):
        return True, f"exit_{mode_name}_d_5_84"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -84.0)
        and (last_candle["RSI_3_1h"] > 70.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_85"
      elif (
        (last_candle["RSI_3"] < 14.0)
        and (last_candle["RSI_14_4h"] < 20.0)
        and (last_candle["ROC_2_1h"] > 5.0)
        and (last_candle["ROC_9_1h"] < -5.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_86"
      elif (
        (last_candle["RSI_3"] < 42.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_87"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -72.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["change_pct_1h"] > 2.0)
      ):
        return True, f"exit_{mode_name}_d_5_88"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 52.0)
        and (last_candle["ROC_9_1h"] > 5.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_5_89"
      elif (
        (last_candle["RSI_3"] < 16.0)
        and (last_candle["WILLR_14"] < -75.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_5_90"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 50.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_91"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 75.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 25.0))
      ):
        return True, f"exit_{mode_name}_d_5_92"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 42.0)
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
        return True, f"exit_{mode_name}_d_5_93"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["RSI_14"] > 42.0)
        and (last_candle["RSI_3_1h"] > 75.0)
        and (last_candle["RSI_3_4h"] > 55.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 10.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_94"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 90.0)
        and (isinstance(last_candle["AROOND_14_1d"], np.float64) and (last_candle["AROOND_14_1d"] > 75.0))
      ):
        return True, f"exit_{mode_name}_d_5_95"
      elif (
        (last_candle["RSI_3"] < 46.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 55.0)
        and (last_candle["RSI_3_1d"] > 55.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_96"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_97"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_15m"] < 36.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["RSI_3_1d"] < 20.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_98"
      elif (
        (last_candle["RSI_3"] < 48.0)
        and (last_candle["RSI_14"] > 40.0)
        and (last_candle["RSI_3_1h"] > 35.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["AROOND_14_4h"] > 50.0)
        and (last_candle["STOCHk_14_3_3_4h"] < 60.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_5_99"
      elif (
        (last_candle["RSI_3"] < 10.0)
        and (last_candle["RSI_14"] < 32.0)
        and (last_candle["RSI_3_15m"] < 30.0)
        and (last_candle["RSI_3_4h"] > 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_100"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["WILLR_14"] < -76.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 60.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_5_101"
      elif (
        (last_candle["RSI_3"] < 40.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] > 70.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -40.0))
      ):
        return True, f"exit_{mode_name}_d_5_102"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 36.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_5_103"
      elif (
        (last_candle["RSI_3"] < 44.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_5_104"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_15m"] > 45.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 10.0)
        and (last_candle["ROC_9_4h"] < -25.0)
      ):
        return True, f"exit_{mode_name}_d_5_105"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["ROC_9_4h"] < -40.0)
      ):
        return True, f"exit_{mode_name}_d_5_106"
      elif (
        (last_candle["RSI_3"] < 34.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 30.0)
        and (last_candle["RSI_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_107"
      elif (
        (last_candle["RSI_3"] < 52.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_108"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["WILLR_14"] < -84.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_3_4h"] > 80.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -50.0))
      ):
        return True, f"exit_{mode_name}_d_5_109"
      elif (
        (last_candle["RSI_3"] < 36.0)
        and (last_candle["RSI_3_4h"] > 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (last_candle["ROC_9_4h"] < -25.0)
      ):
        return True, f"exit_{mode_name}_d_5_110"
      elif (
        (last_candle["RSI_3"] < 58.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] < 30.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -20.0))
      ):
        return True, f"exit_{mode_name}_d_5_111"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["WILLR_14"] < -55.0)
        and (last_candle["RSI_14"] > 40.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["RSI_3_4h"] > 65.0)
        and (last_candle["RSI_3_1d"] > 40.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -30.0))
      ):
        return True, f"exit_{mode_name}_d_5_112"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["WILLR_14"] < -90.0)
        and (last_candle["RSI_3_1d"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
        and (isinstance(last_candle["ROC_9_4h"], np.float64) and (last_candle["ROC_9_4h"] < -10.0))
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] > 10.0))
      ):
        return True, f"exit_{mode_name}_d_5_113"
      elif (
        (last_candle["RSI_3"] < 24.0)
        and (last_candle["RSI_14"] > 42.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_114"
      elif (
        (last_candle["RSI_3"] < 30.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_15m"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_115"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["AROONU_14_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_116"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["AROONU_14_1h"] < 20.0)
        and (last_candle["AROONU_14_4h"] < 20.0)
      ):
        return True, f"exit_{mode_name}_d_5_117"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["AROOND_14_4h"] > 40.0)
      ):
        return True, f"exit_{mode_name}_d_5_118"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["WILLR_14"] < -80.0)
        and (last_candle["RSI_3_1h"] > 40.0)
        and (last_candle["RSI_3_4h"] > 40.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_119"
      elif (
        (last_candle["RSI_3"] < 54.0)
        and (last_candle["RSI_14"] > 44.0)
        and (last_candle["RSI_3_1h"] > 60.0)
        and (last_candle["AROOND_14_4h"] > 75.0)
      ):
        return True, f"exit_{mode_name}_d_5_120"
      elif (
        (last_candle["RSI_3"] < 48.0)
        and (last_candle["RSI_14"] > 46.0)
        and (last_candle["RSI_3_1h"] > 50.0)
        and (last_candle["RSI_14_4h"] < 15.0)
      ):
        return True, f"exit_{mode_name}_d_5_121"
      elif (
        (last_candle["RSI_3"] < 50.0)
        and (last_candle["RSI_14"] > 48.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_122"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_1d"] > 70.0)
      ):
        return True, f"exit_{mode_name}_d_5_123"
      elif (
        (last_candle["RSI_3"] < 20.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (
          isinstance(last_candle["STOCHRSIk_14_14_3_3_1d"], np.float64)
          and (last_candle["STOCHRSIk_14_14_3_3_1d"] < 20.0)
        )
      ):
        return True, f"exit_{mode_name}_d_5_124"
      elif (
        (last_candle["RSI_3"] < 32.0)
        and (last_candle["WILLR_14"] < -88.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["RSI_3_1d"] > 60.0)
        and (last_candle["close"] > (last_candle["low_min_30_1d"] * 2.0))
      ):
        return True, f"exit_{mode_name}_d_5_125"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_1h"] > 85.0)
        and (last_candle["RSI_3_4h"] > 60.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_126"
      elif (
        (last_candle["RSI_3"] < 18.0)
        and (last_candle["RSI_3_1h"] > 90.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["RSI_3_1d"] > 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_127"
      elif (last_candle["RSI_3"] < 14.0) and (last_candle["RSI_3_4h"] > 70.0) and (last_candle["AROOND_14_4h"] > 85.0):
        return True, f"exit_{mode_name}_d_5_128"
      elif (
        (last_candle["RSI_3"] < 22.0)
        and (last_candle["RSI_3_4h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -80.0))
      ):
        return True, f"exit_{mode_name}_d_5_129"
      elif (
        (last_candle["RSI_3"] < 34.0)
        and (last_candle["RSI_14_1h"] < 35.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 20.0)
        and (last_candle["CCI_20_change_pct_1h"] > 0.0)
      ):
        return True, f"exit_{mode_name}_d_5_130"
      elif (
        (last_candle["RSI_14"] > 54.0)
        and (last_candle["RSI_3_1h"] > 80.0)
        and (last_candle["RSI_3_4h"] > 70.0)
        and (last_candle["STOCHRSIk_14_14_3_3_4h"] < 50.0)
      ):
        return True, f"exit_{mode_name}_d_5_131"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["RSI_3_1h"] > 65.0)
        and (last_candle["RSI_3_4h"] > 65.0)
        and (last_candle["AROOND_14_1h"] > 50.0)
        and (last_candle["STOCHRSIk_14_14_3_3_1h"] < 60.0)
      ):
        return True, f"exit_{mode_name}_d_5_132"
      elif (
        (last_candle["RSI_3"] < 28.0)
        and (last_candle["AROOND_14_15m"] > 75.0)
        and (last_candle["AROOND_14_1h"] > 75.0)
        and (isinstance(last_candle["ROC_9_1d"], np.float64) and (last_candle["ROC_9_1d"] < -25.0))
      ):
        return True, f"exit_{mode_name}_d_5_133"

    return False, None

