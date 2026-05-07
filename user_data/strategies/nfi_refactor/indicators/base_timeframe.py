"""Base timeframe indicator builder extracted from NostalgiaForInfinityX7.

The original function also contains the backtest age filter and live-data
availability protection. We keep that behavior together during parity refactor
and split it into protection modules only after regression checks are stable.
"""

import logging
import time

import numpy as np
import pandas as pd
import pandas_ta as pta
import talib.abstract as ta
from pandas import DataFrame

log = logging.getLogger(__name__)
def base_tf_5m_indicators(strategy, metadata: dict, df: DataFrame) -> DataFrame:
  tik = time.perf_counter()

  # Indicators
  # base_tf_5m_indicators_pandas_ta = pta.Strategy(
  #   name="base_tf_5m_indicators_pandas_ta",
  #   ta=[
  #     # RSI
  #     {"kind": "rsi", "length": 3},
  #     {"kind": "rsi", "length": 4},
  #     {"kind": "rsi", "length": 14},
  #     {"kind": "rsi", "length": 20},
  #     # EMA
  #     {"kind": "ema", "length": 3},
  #     {"kind": "ema", "length": 9},
  #     {"kind": "ema", "length": 12},
  #     {"kind": "ema", "length": 16},
  #     {"kind": "ema", "length": 20},
  #     {"kind": "ema", "length": 26},
  #     {"kind": "ema", "length": 50},
  #     {"kind": "ema", "length": 100},
  #     {"kind": "ema", "length": 200},
  #     # SMA
  #     {"kind": "sma", "length": 16},
  #     {"kind": "sma", "length": 30},
  #     {"kind": "sma", "length": 75},
  #     {"kind": "sma", "length": 200},
  #     # BB 20 - STD2
  #     {"kind": "bbands", "length": 20},
  #     # BB 40 - STD2
  #     {"kind": "bbands", "length": 40},
  #     # Williams %R
  #     {"kind": "willr", "length": 14},
  #     {"kind": "willr", "length": 480},
  #     # CTI
  #     {"kind": "cti", "length": 20},
  #     # MFI
  #     {"kind": "mfi"},
  #     # CMF
  #     {"kind": "cmf"},
  #     # CCI
  #     {"kind": "cci", "length": 20},
  #     # Hull Moving Average
  #     {"kind": "hma", "length": 55},
  #     {"kind": "hma", "length": 70},
  #     # ZL MA
  #     # {"kind": "zlma", "length": 50, "mamode":"linreg"},
  #     # Heiken Ashi
  #     # {"kind": "ha"},
  #     # STOCHRSI
  #     {"kind": "stochrsi"},
  #     # KST
  #     {"kind": "kst"},
  #     # ROC
  #     {"kind": "roc"},
  #     # AROON
  #     {"kind": "aroon"},
  #     # UO
  #     {"kind": "uo"},
  #     # AO
  #     {"kind": "ao"},
  #     # OBV
  #     {"kind": "obv"},
  #   ],
  # )
  # df.ta.study(base_tf_5m_indicators_pandas_ta, cores=strategy.num_cores_indicators_calc)
  # RSI
  df["RSI_3"] = pta.rsi(df["close"], length=3)
  df["RSI_4"] = pta.rsi(df["close"], length=4)
  df["RSI_14"] = pta.rsi(df["close"], length=14)
  df["RSI_20"] = pta.rsi(df["close"], length=20)
  df["RSI_3_change_pct"] = df["RSI_3"].pct_change() * 100.0
  df["RSI_14_change_pct"] = df["RSI_14"].pct_change() * 100.0
  # EMA
  df["EMA_3"] = pta.ema(df["close"], length=3)
  df["EMA_9"] = pta.ema(df["close"], length=9)
  df["EMA_12"] = pta.ema(df["close"], length=12)
  df["EMA_16"] = pta.ema(df["close"], length=16)
  df["EMA_20"] = pta.ema(df["close"], length=20)
  df["EMA_26"] = pta.ema(df["close"], length=26)
  df["EMA_50"] = pta.ema(df["close"], length=50)
  df["EMA_100"] = pta.ema(df["close"], length=100, fillna=0.0)
  df["EMA_200"] = pta.ema(df["close"], length=200, fillna=0.0)
  # SMA
  df["SMA_9"] = pta.sma(df["close"], length=9)
  df["SMA_16"] = pta.sma(df["close"], length=16)
  df["SMA_21"] = pta.sma(df["close"], length=21)
  df["SMA_30"] = pta.sma(df["close"], length=30)
  df["SMA_200"] = pta.sma(df["close"], length=200)
  # BB 20 - STD2
  bbands_20_2 = pta.bbands(df["close"], length=20)
  df["BBL_20_2.0"] = bbands_20_2["BBL_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  df["BBM_20_2.0"] = bbands_20_2["BBM_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  df["BBU_20_2.0"] = bbands_20_2["BBU_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  df["BBB_20_2.0"] = bbands_20_2["BBB_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  df["BBP_20_2.0"] = bbands_20_2["BBP_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  # BB 40 - STD2
  upper, middle, lower = ta.BBANDS(df["close"], timeperiod=40, nbdevup=2.0, nbdevdn=2.0, matype=0)
  df["BBL_40_2.0"] = lower
  df["BBM_40_2.0"] = middle
  df["BBU_40_2.0"] = upper
  df["BBB_40_2.0"] = (upper - lower) / middle * 100.0  # Bandwidth
  df["BBP_40_2.0"] = (df["close"] - lower) / (upper - lower)  # %B
  df["BBD_40_2.0"] = (df["BBM_40_2.0"] - df["BBL_40_2.0"]).abs()  # delta
  df["BBT_40_2.0"] = (df["close"] - df["BBL_40_2.0"]).abs()  # tail
  # MFI
  df["MFI_14"] = pta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14)
  # CMF
  df["CMF_20"] = pta.cmf(df["high"], df["low"], df["close"], df["volume"], length=20)
  # Williams %R
  df["WILLR_14"] = pta.willr(df["high"], df["low"], df["close"], length=14)
  df["WILLR_480"] = pta.willr(df["high"], df["low"], df["close"], length=480)
  # AROON
  aroon_14 = pta.aroon(df["high"], df["low"], length=14)
  df["AROONU_14"] = aroon_14["AROONU_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  df["AROOND_14"] = aroon_14["AROOND_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  # Stochastic RSI
  stochrsi = pta.stochrsi(df["close"])
  df["STOCHRSIk_14_14_3_3"] = stochrsi["STOCHRSIk_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  df["STOCHRSId_14_14_3_3"] = stochrsi["STOCHRSId_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  # KST
  kst = pta.kst(df["close"])
  df["KST_10_15_20_30_10_10_10_15"] = kst["KST_10_15_20_30_10_10_10_15"] if isinstance(kst, pd.DataFrame) else np.nan
  df["KSTs_9"] = kst["KSTs_9"] if isinstance(kst, pd.DataFrame) else np.nan
  # OBV
  df["OBV"] = pta.obv(df["close"], df["volume"])
  df["OBV_change_pct"] = df["OBV"].pct_change() * 100.0
  # ROC
  df["ROC_2"] = pta.roc(df["close"], length=2)
  df["ROC_9"] = pta.roc(df["close"], length=9)
  # Candle change
  df["change_pct"] = (df["close"] - df["open"]) / df["open"] * 100.0
  # Close delta
  df["close_delta"] = (df["close"] - df["close"].shift()).abs()
  # Close max
  df["close_max_6"] = df["close"].rolling(6).max()
  df["close_max_12"] = df["close"].rolling(12).max()
  df["close_max_48"] = df["close"].rolling(48).max()
  # Close min
  df["close_min_6"] = df["close"].rolling(6).min()
  df["close_min_12"] = df["close"].rolling(12).min()
  df["close_min_48"] = df["close"].rolling(48).min()
  # Number of empty candles
  df["num_empty_288"] = (df["volume"] <= 0).rolling(window=288, min_periods=288).sum()

  # -----------------------------------------------------------------------------------------

  # Global protections
  # -----------------------------------------------------------------------------------------
  if not strategy.config["runmode"].value in ("live", "dry_run"):
    # Backtest age filter
    df["bt_agefilter_ok"] = False
    df.loc[df.index > (12 * 24 * strategy.bt_min_age_days), "bt_agefilter_ok"] = True
  else:
    # Exchange downtime protection
    df["live_data_ok"] = df["volume"].rolling(window=72, min_periods=72).min() > 0

  # Performance logging
  # -----------------------------------------------------------------------------------------
  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] base_tf_5m_indicators took: {tok - tik:0.4f} seconds.")

  return df

# Coin Pair Indicator Switch Case
