"""Pair informative indicator builders extracted from NostalgiaForInfinityX7.

This first extraction intentionally keeps the original calculations almost
verbatim. After parity is stable, duplicated indicator blocks can be cleaned up
behind tests without changing strategy behavior.
"""

import logging
import time

import numpy as np
import pandas as pd
import pandas_ta as pta
from pandas import DataFrame

log = logging.getLogger(__name__)
def informative_1d_indicators(strategy, metadata: dict, info_timeframe) -> DataFrame:
  tik = time.perf_counter()
  assert strategy.dp, "DataProvider is required for multiple timeframes."
  # Get the informative pair
  informative_1d = strategy.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

  # Indicators
  # -----------------------------------------------------------------------------------------
  # informative_1d_indicators_pandas_ta = pta.Strategy(
  #   name="informative_1d_indicators_pandas_ta",
  #   ta=[
  #     # RSI
  #     {"kind": "rsi", "length": 3},
  #     {"kind": "rsi", "length": 14},
  #     # {"kind": "rsi", "length": 20},
  #     # EMA
  #     # {"kind": "ema", "length": 12},
  #     # {"kind": "ema", "length": 16},
  #     # {"kind": "ema", "length": 20},
  #     # {"kind": "ema", "length": 26},
  #     # {"kind": "ema", "length": 50},
  #     # {"kind": "ema", "length": 100},
  #     # {"kind": "ema", "length": 200},
  #     # SMA
  #     # {"kind": "sma", "length": 16},
  #     # MFI
  #     {"kind": "mfi"},
  #     # CMF
  #     {"kind": "cmf"},
  #     # Williams %R
  #     {"kind": "willr", "length": 14},
  #     # STOCHRSI
  #     {"kind": "stochrsi"},
  #     # KST
  #     {"kind": "kst"},
  #     # ROC
  #     {"kind": "roc"},
  #     # AROON
  #     {"kind": "aroon"},
  #   ],
  # )
  # informative_1d.ta.study(informative_1d_indicators_pandas_ta, cores=strategy.num_cores_indicators_calc)
  # RSI
  informative_1d["RSI_3"] = pta.rsi(informative_1d["close"], length=3)
  informative_1d["RSI_14"] = pta.rsi(informative_1d["close"], length=14)
  informative_1d["RSI_3_change_pct"] = informative_1d["RSI_3"].pct_change() * 100.0
  informative_1d["RSI_14_change_pct"] = informative_1d["RSI_14"].pct_change() * 100.0
  informative_1d["RSI_3_diff"] = informative_1d["RSI_3"].diff()
  informative_1d["RSI_14_diff"] = informative_1d["RSI_14"].diff()
  # BB 20 - STD2
  bbands_20_2 = pta.bbands(informative_1d["close"], length=20)
  informative_1d["BBL_20_2.0"] = bbands_20_2["BBL_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1d["BBM_20_2.0"] = bbands_20_2["BBM_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1d["BBU_20_2.0"] = bbands_20_2["BBU_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1d["BBB_20_2.0"] = bbands_20_2["BBB_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1d["BBP_20_2.0"] = bbands_20_2["BBP_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  # MFI
  informative_1d["MFI_14"] = pta.mfi(
    informative_1d["high"], informative_1d["low"], informative_1d["close"], informative_1d["volume"], length=14
  )
  # CMF
  informative_1d["CMF_20"] = pta.cmf(
    informative_1d["high"], informative_1d["low"], informative_1d["close"], informative_1d["volume"], length=20
  )
  # Williams %R
  informative_1d["WILLR_14"] = pta.willr(
    informative_1d["high"], informative_1d["low"], informative_1d["close"], length=14
  )
  # AROON
  aroon_14 = pta.aroon(informative_1d["high"], informative_1d["low"], length=14)
  informative_1d["AROONU_14"] = aroon_14["AROONU_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  informative_1d["AROOND_14"] = aroon_14["AROOND_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  # Stochastic
  try:
    stochrsi = pta.stoch(informative_1d["high"], informative_1d["low"], informative_1d["close"])
    informative_1d["STOCHk_14_3_3"] = stochrsi["STOCHk_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
    informative_1d["STOCHd_14_3_3"] = stochrsi["STOCHd_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  except AttributeError:
    informative_1d["STOCHk_14_3_3"] = np.nan
    informative_1d["STOCHd_14_3_3"] = np.nan
  # Stochastic RSI
  stochrsi = pta.stochrsi(informative_1d["close"])
  informative_1d["STOCHRSIk_14_14_3_3"] = (
    stochrsi["STOCHRSIk_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  informative_1d["STOCHRSId_14_14_3_3"] = (
    stochrsi["STOCHRSId_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  # ROC
  informative_1d["ROC_2"] = pta.roc(informative_1d["close"], length=2)
  informative_1d["ROC_9"] = pta.roc(informative_1d["close"], length=9)
  # Candle change
  informative_1d["change_pct"] = (informative_1d["close"] - informative_1d["open"]) / informative_1d["open"] * 100.0
  # Wicks
  informative_1d["top_wick_pct"] = (
    (informative_1d["high"] - np.maximum(informative_1d["open"], informative_1d["close"]))
    / np.maximum(informative_1d["open"], informative_1d["close"])
    * 100.0
  )
  informative_1d["bot_wick_pct"] = abs(
    (informative_1d["low"] - np.minimum(informative_1d["open"], informative_1d["close"]))
    / np.minimum(informative_1d["open"], informative_1d["close"])
    * 100.0
  )
  # Max highs
  informative_1d["high_max_6"] = informative_1d["high"].rolling(6).max()
  informative_1d["high_max_12"] = informative_1d["high"].rolling(12).max()
  informative_1d["high_max_20"] = informative_1d["high"].rolling(20).max()
  informative_1d["high_max_30"] = informative_1d["high"].rolling(30).max()
  # Max lows
  informative_1d["low_min_6"] = informative_1d["low"].rolling(6).min()
  informative_1d["low_min_12"] = informative_1d["low"].rolling(12).min()
  informative_1d["low_min_20"] = informative_1d["low"].rolling(20).min()
  informative_1d["low_min_30"] = informative_1d["low"].rolling(30).min()

  # Performance logging
  # -----------------------------------------------------------------------------------------
  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] informative_1d_indicators took: {tok - tik:0.4f} seconds.")

  return informative_1d

# Informative 4h Timeframe Indicators
# ---------------------------------------------------------------------------------------------
def informative_4h_indicators(strategy, metadata: dict, info_timeframe) -> DataFrame:
  tik = time.perf_counter()
  assert strategy.dp, "DataProvider is required for multiple timeframes."
  # Get the informative pair
  informative_4h = strategy.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

  # Indicators
  # -----------------------------------------------------------------------------------------
  # informative_4h_indicators_pandas_ta = pta.Strategy(
  #   name="informative_4h_indicators_pandas_ta",
  #   ta=[
  #     # RSI
  #     {"kind": "rsi", "length": 3},
  #     {"kind": "rsi", "length": 14},
  #     # {"kind": "rsi", "length": 20},
  #     # EMA
  #     {"kind": "ema", "length": 12},
  #     # {"kind": "ema", "length": 16},
  #     # {"kind": "ema", "length": 20},
  #     {"kind": "ema", "length": 26},
  #     # {"kind": "ema", "length": 50},
  #     # {"kind": "ema", "length": 100},
  #     {"kind": "ema", "length": 200},
  #     # SMA
  #     # {"kind": "sma", "length": 16},
  #     # BB 20 - STD2
  #     {"kind": "bbands", "length": 20},
  #     # MFI
  #     {"kind": "mfi"},
  #     # CMF
  #     {"kind": "cmf"},
  #     # Williams %R
  #     {"kind": "willr", "length": 14},
  #     # CTI
  #     {"kind": "cti", "length": 20},
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
  #   ],
  # )
  # informative_4h.ta.study(informative_4h_indicators_pandas_ta, cores=strategy.num_cores_indicators_calc)
  # RSI
  informative_4h["RSI_3"] = pta.rsi(informative_4h["close"], length=3)
  informative_4h["RSI_14"] = pta.rsi(informative_4h["close"], length=14)
  informative_4h["RSI_3_change_pct"] = informative_4h["RSI_3"].pct_change() * 100.0
  informative_4h["RSI_14_change_pct"] = informative_4h["RSI_14"].pct_change() * 100.0
  informative_4h["RSI_3_diff"] = informative_4h["RSI_3"].diff()
  informative_4h["RSI_14_diff"] = informative_4h["RSI_14"].diff()
  # EMA
  informative_4h["EMA_12"] = pta.ema(informative_4h["close"], length=12)
  informative_4h["EMA_200"] = pta.ema(informative_4h["close"], length=200, fillna=0.0)
  # BB 20 - STD2
  bbands_20_2 = pta.bbands(informative_4h["close"], length=20)
  informative_4h["BBL_20_2.0"] = bbands_20_2["BBL_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_4h["BBM_20_2.0"] = bbands_20_2["BBM_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_4h["BBU_20_2.0"] = bbands_20_2["BBU_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_4h["BBB_20_2.0"] = bbands_20_2["BBB_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_4h["BBP_20_2.0"] = bbands_20_2["BBP_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  # MFI
  informative_4h["MFI_14"] = pta.mfi(
    informative_4h["high"], informative_4h["low"], informative_4h["close"], informative_4h["volume"], length=14
  )
  # CMF
  informative_4h["CMF_20"] = pta.cmf(
    informative_4h["high"], informative_4h["low"], informative_4h["close"], informative_4h["volume"], length=20
  )
  # Williams %R
  informative_4h["WILLR_14"] = pta.willr(
    informative_4h["high"], informative_4h["low"], informative_4h["close"], length=14
  )
  # AROON
  aroon_14 = pta.aroon(informative_4h["high"], informative_4h["low"], length=14)
  informative_4h["AROONU_14"] = aroon_14["AROONU_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  informative_4h["AROOND_14"] = aroon_14["AROOND_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  # Stochastic
  try:
    stochrsi = pta.stoch(informative_4h["high"], informative_4h["low"], informative_4h["close"])
    informative_4h["STOCHk_14_3_3"] = stochrsi["STOCHk_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
    informative_4h["STOCHd_14_3_3"] = stochrsi["STOCHd_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  except AttributeError:
    informative_4h["STOCHk_14_3_3"] = np.nan
    informative_4h["STOCHd_14_3_3"] = np.nan
  # Stochastic RSI
  stochrsi = pta.stochrsi(informative_4h["close"])
  informative_4h["STOCHRSIk_14_14_3_3"] = (
    stochrsi["STOCHRSIk_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  informative_4h["STOCHRSId_14_14_3_3"] = (
    stochrsi["STOCHRSId_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  informative_4h["STOCHRSIk_14_14_3_3_change_pct"] = (informative_4h["STOCHRSIk_14_14_3_3"].pct_change()) * 100.0
  # KST
  kst = pta.kst(informative_4h["close"])
  informative_4h["KST_10_15_20_30_10_10_10_15"] = (
    kst["KST_10_15_20_30_10_10_10_15"] if isinstance(kst, pd.DataFrame) else np.nan
  )
  informative_4h["KSTs_9"] = kst["KSTs_9"] if isinstance(kst, pd.DataFrame) else np.nan
  # UO
  informative_4h["UO_7_14_28"] = pta.uo(informative_4h["high"], informative_4h["low"], informative_4h["close"])
  # OBV
  informative_4h["OBV"] = pta.obv(informative_4h["close"], informative_4h["volume"])
  informative_4h["OBV_change_pct"] = (informative_4h["OBV"].pct_change()) * 100.0
  # ROC
  informative_4h["ROC_2"] = pta.roc(informative_4h["close"], length=2)
  informative_4h["ROC_9"] = pta.roc(informative_4h["close"], length=9)
  # CCI
  informative_4h["CCI_20"] = pta.cci(
    informative_4h["high"], informative_4h["low"], informative_4h["close"], length=20
  )
  informative_4h["CCI_20"] = (
    (informative_4h["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
  )
  informative_4h["CCI_20_change_pct"] = (informative_4h["CCI_20"].pct_change()) * 100.0

  # Candle change
  informative_4h["change_pct"] = (informative_4h["close"] - informative_4h["open"]) / informative_4h["open"] * 100.0
  informative_4h["change_pct_min_3"] = informative_4h["change_pct"].rolling(3).min()
  informative_4h["change_pct_min_6"] = informative_4h["change_pct"].rolling(6).min()
  informative_4h["change_pct_max_3"] = informative_4h["change_pct"].rolling(3).max()
  informative_4h["change_pct_max_6"] = informative_4h["change_pct"].rolling(6).max()
  # Candle change
  informative_4h["change_pct"] = (informative_4h["close"] - informative_4h["open"]) / informative_4h["open"] * 100.0
  # Wicks
  informative_4h["top_wick_pct"] = (
    (informative_4h["high"] - np.maximum(informative_4h["open"], informative_4h["close"]))
    / np.maximum(informative_4h["open"], informative_4h["close"])
    * 100.0
  )
  informative_4h["bot_wick_pct"] = abs(
    (informative_4h["low"] - np.minimum(informative_4h["open"], informative_4h["close"]))
    / np.minimum(informative_4h["open"], informative_4h["close"])
    * 100.0
  )
  # Max highs
  informative_4h["high_max_6"] = informative_4h["high"].rolling(6).max()
  informative_4h["high_max_12"] = informative_4h["high"].rolling(12).max()
  informative_4h["high_max_24"] = informative_4h["high"].rolling(24).max()
  # Min lows
  informative_4h["low_min_6"] = informative_4h["low"].rolling(6).min()
  informative_4h["low_min_12"] = informative_4h["low"].rolling(12).min()
  informative_4h["low_min_24"] = informative_4h["low"].rolling(24).min()

  # Performance logging
  # -----------------------------------------------------------------------------------------
  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] informative_1d_indicators took: {tok - tik:0.4f} seconds.")

  return informative_4h

# Informative 1h Timeframe Indicators
# ---------------------------------------------------------------------------------------------
def informative_1h_indicators(strategy, metadata: dict, info_timeframe) -> DataFrame:
  tik = time.perf_counter()
  assert strategy.dp, "DataProvider is required for multiple timeframes."
  # Get the informative pair
  informative_1h = strategy.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

  # Indicators
  # -----------------------------------------------------------------------------------------
  # informative_1h_indicators_pandas_ta = pta.Strategy(
  #   name="informative_1h_indicators_pandas_ta",
  #   ta=[
  #     # RSI
  #     {"kind": "rsi", "length": 3},
  #     {"kind": "rsi", "length": 14},
  #     # {"kind": "rsi", "length": 20},
  #     # EMA
  #     {"kind": "ema", "length": 12},
  #     # {"kind": "ema", "length": 16},
  #     {"kind": "ema", "length": 20},
  #     {"kind": "ema", "length": 26},
  #     # {"kind": "ema", "length": 50},
  #     # {"kind": "ema", "length": 100},
  #     {"kind": "ema", "length": 200},
  #     # SMA
  #     # {"kind": "sma", "length": 16},
  #     # BB 20 - STD2
  #     {"kind": "bbands", "length": 20},
  #     # MFI
  #     {"kind": "mfi"},
  #     # CMF
  #     {"kind": "cmf"},
  #     # Williams %R
  #     {"kind": "willr", "length": 14},
  #     # CTI
  #     {"kind": "cti", "length": 20},
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
  #   ],
  # )
  # informative_1h.ta.study(informative_1h_indicators_pandas_ta, cores=strategy.num_cores_indicators_calc)
  # RSI
  informative_1h["RSI_3"] = pta.rsi(informative_1h["close"], length=3)
  informative_1h["RSI_14"] = pta.rsi(informative_1h["close"], length=14)
  informative_1h["RSI_3_change_pct"] = informative_1h["RSI_3"].pct_change() * 100.0
  informative_1h["RSI_14_change_pct"] = informative_1h["RSI_14"].pct_change() * 100.0
  informative_1h["RSI_3_diff"] = informative_1h["RSI_3"].diff()
  informative_1h["RSI_14_diff"] = informative_1h["RSI_14"].diff()
  # EMA
  informative_1h["EMA_12"] = pta.ema(informative_1h["close"], length=12)
  informative_1h["EMA_200"] = pta.ema(informative_1h["close"], length=200, fillna=0.0)
  # SMA
  informative_1h["SMA_16"] = pta.sma(informative_1h["close"], length=16)
  # BB 20 - STD2
  bbands_20_2 = pta.bbands(informative_1h["close"], length=20)
  informative_1h["BBL_20_2.0"] = bbands_20_2["BBL_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1h["BBM_20_2.0"] = bbands_20_2["BBM_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1h["BBU_20_2.0"] = bbands_20_2["BBU_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1h["BBB_20_2.0"] = bbands_20_2["BBB_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  informative_1h["BBP_20_2.0"] = bbands_20_2["BBP_20_2.0"] if isinstance(bbands_20_2, pd.DataFrame) else np.nan
  # MFI
  informative_1h["MFI_14"] = pta.mfi(
    informative_1h["high"], informative_1h["low"], informative_1h["close"], informative_1h["volume"], length=14
  )
  # CMF
  informative_1h["CMF_20"] = pta.cmf(
    informative_1h["high"], informative_1h["low"], informative_1h["close"], informative_1h["volume"], length=20
  )
  # Williams %R
  informative_1h["WILLR_14"] = pta.willr(
    informative_1h["high"], informative_1h["low"], informative_1h["close"], length=14
  )
  informative_1h["WILLR_84"] = pta.willr(
    informative_1h["high"], informative_1h["low"], informative_1h["close"], length=84
  )
  # AROON
  aroon_14 = pta.aroon(informative_1h["high"], informative_1h["low"], length=14)
  informative_1h["AROONU_14"] = aroon_14["AROONU_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  informative_1h["AROOND_14"] = aroon_14["AROOND_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  # Stochastic
  stochrsi = pta.stoch(informative_1h["high"], informative_1h["low"], informative_1h["close"])
  informative_1h["STOCHk_14_3_3"] = stochrsi["STOCHk_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  informative_1h["STOCHd_14_3_3"] = stochrsi["STOCHd_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  # Stochastic RSI
  stochrsi = pta.stochrsi(informative_1h["close"])
  informative_1h["STOCHRSIk_14_14_3_3"] = (
    stochrsi["STOCHRSIk_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  informative_1h["STOCHRSId_14_14_3_3"] = (
    stochrsi["STOCHRSId_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  # KST
  kst = pta.kst(informative_1h["close"])
  informative_1h["KST_10_15_20_30_10_10_10_15"] = (
    kst["KST_10_15_20_30_10_10_10_15"] if isinstance(kst, pd.DataFrame) else np.nan
  )
  informative_1h["KSTs_9"] = kst["KSTs_9"] if isinstance(kst, pd.DataFrame) else np.nan
  # UO
  informative_1h["UO_7_14_28"] = pta.uo(informative_1h["high"], informative_1h["low"], informative_1h["close"])
  informative_1h["UO_7_14_28"] = (
    (informative_1h["UO_7_14_28"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))
  )
  informative_1h["UO_7_14_28_change_pct"] = informative_1h["UO_7_14_28"].pct_change() * 100.0
  # OBV
  informative_1h["OBV"] = pta.obv(informative_1h["close"], informative_1h["volume"])
  informative_1h["OBV_change_pct"] = informative_1h["OBV"].pct_change() * 100.0
  # ROC
  informative_1h["ROC_2"] = pta.roc(informative_1h["close"], length=2)
  informative_1h["ROC_9"] = pta.roc(informative_1h["close"], length=9)
  # CCI
  informative_1h["CCI_20"] = pta.cci(
    informative_1h["high"], informative_1h["low"], informative_1h["close"], length=20
  )
  informative_1h["CCI_20"] = (
    (informative_1h["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
  )
  informative_1h["CCI_20_change_pct"] = informative_1h["CCI_20"].pct_change() * 100.0
  # Candle change
  informative_1h["change_pct"] = (informative_1h["close"] - informative_1h["open"]) / informative_1h["open"] * 100.0
  # Wicks
  informative_1h["top_wick_pct"] = (
    (informative_1h["high"] - np.maximum(informative_1h["open"], informative_1h["close"]))
    / np.maximum(informative_1h["open"], informative_1h["close"])
    * 100.0
  )
  informative_1h["bot_wick_pct"] = abs(
    (informative_1h["low"] - np.minimum(informative_1h["open"], informative_1h["close"]))
    / np.minimum(informative_1h["open"], informative_1h["close"])
    * 100.0
  )
  # Max highs
  informative_1h["high_max_6"] = informative_1h["high"].rolling(6).max()
  informative_1h["high_max_12"] = informative_1h["high"].rolling(12).max()
  informative_1h["high_max_24"] = informative_1h["high"].rolling(24).max()
  # Min lows
  informative_1h["low_min_6"] = informative_1h["low"].rolling(6).min()
  informative_1h["low_min_12"] = informative_1h["low"].rolling(12).min()
  informative_1h["low_min_24"] = informative_1h["low"].rolling(24).min()

  # Performance logging
  # -----------------------------------------------------------------------------------------
  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] informative_1h_indicators took: {tok - tik:0.4f} seconds.")

  return informative_1h

# Informative 15m Timeframe Indicators
# ---------------------------------------------------------------------------------------------
def informative_15m_indicators(strategy, metadata: dict, info_timeframe) -> DataFrame:
  tik = time.perf_counter()
  assert strategy.dp, "DataProvider is required for multiple timeframes."

  # Get the informative pair
  informative_15m = strategy.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

  # Indicators
  # -----------------------------------------------------------------------------------------
  # informative_15m_indicators_pandas_ta = pta.Strategy(
  #   name="informative_15m_indicators_pandas_ta",
  #   ta=[
  #     # RSI
  #     {"kind": "rsi", "length": 3},
  #     {"kind": "rsi", "length": 14},
  #     # {"kind": "rsi", "length": 20},
  #     # EMA
  #     {"kind": "ema", "length": 12},
  #     # {"kind": "ema", "length": 16},
  #     # {"kind": "ema", "length": 20},
  #     # {"kind": "ema", "length": 26},
  #     # {"kind": "ema", "length": 50},
  #     # {"kind": "ema", "length": 100},
  #     # {"kind": "ema", "length": 200},
  #     # SMA
  #     # {"kind": "sma", "length": 16},
  #     # BB 20 - STD2
  #     {"kind": "bbands", "length": 20},
  #     # Williams %R
  #     {"kind": "willr", "length": 14},
  #     # CTI
  #     {"kind": "cti", "length": 20},
  #     # STOCHRSI
  #     {"kind": "stochrsi"},
  #     # ROC
  #     {"kind": "roc"},
  #     # AROON
  #     {"kind": "aroon"},
  #     # UO
  #     {"kind": "uo"},
  #     # AO
  #     {"kind": "ao"},
  #   ],
  # )
  # informative_15m.ta.study(informative_15m_indicators_pandas_ta, cores=strategy.num_cores_indicators_calc)
  # RSI
  informative_15m["RSI_3"] = pta.rsi(informative_15m["close"], length=3)
  informative_15m["RSI_14"] = pta.rsi(informative_15m["close"], length=14)
  informative_15m["RSI_3_change_pct"] = informative_15m["RSI_3"].pct_change() * 100.0
  informative_15m["RSI_14_change_pct"] = informative_15m["RSI_14"].pct_change() * 100.0
  # EMA
  informative_15m["EMA_12"] = pta.ema(informative_15m["close"], length=12)
  informative_15m["EMA_20"] = pta.ema(informative_15m["close"], length=20)
  informative_15m["EMA_26"] = pta.ema(informative_15m["close"], length=26)
  # MFI
  informative_15m["MFI_14"] = pta.mfi(
    informative_15m["high"], informative_15m["low"], informative_15m["close"], informative_15m["volume"], length=14
  )
  # CMF
  informative_15m["CMF_20"] = pta.cmf(
    informative_15m["high"], informative_15m["low"], informative_15m["close"], informative_15m["volume"], length=20
  )
  # Williams %R
  informative_15m["WILLR_14"] = pta.willr(
    informative_15m["high"], informative_15m["low"], informative_15m["close"], length=14
  )
  # AROON
  aroon_14 = pta.aroon(informative_15m["high"], informative_15m["low"], length=14)
  informative_15m["AROONU_14"] = aroon_14["AROONU_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  informative_15m["AROOND_14"] = aroon_14["AROOND_14"] if isinstance(aroon_14, pd.DataFrame) else np.nan
  # Stochastic
  stochrsi = pta.stoch(informative_15m["high"], informative_15m["low"], informative_15m["close"])
  informative_15m["STOCHk_14_3_3"] = stochrsi["STOCHk_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  informative_15m["STOCHd_14_3_3"] = stochrsi["STOCHd_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  # Stochastic RSI
  stochrsi = pta.stochrsi(informative_15m["close"])
  informative_15m["STOCHRSIk_14_14_3_3"] = (
    stochrsi["STOCHRSIk_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  informative_15m["STOCHRSId_14_14_3_3"] = (
    stochrsi["STOCHRSId_14_14_3_3"] if isinstance(stochrsi, pd.DataFrame) else np.nan
  )
  # UO
  informative_15m["UO_7_14_28"] = pta.uo(informative_15m["high"], informative_15m["low"], informative_15m["close"])
  informative_15m["UO_7_14_28_change_pct"] = informative_15m["UO_7_14_28"].pct_change() * 100.0
  # OBV
  informative_15m["OBV"] = pta.obv(informative_15m["close"], informative_15m["volume"])
  informative_15m["OBV_change_pct"] = informative_15m["OBV"].pct_change() * 100.0
  # ROC
  informative_15m["ROC_9"] = pta.roc(informative_15m["close"], length=9)
  # CCI
  informative_15m["CCI_20"] = pta.cci(
    informative_15m["high"], informative_15m["low"], informative_15m["close"], length=20
  )
  informative_15m["CCI_20"] = (
    (informative_15m["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
  )
  informative_15m["CCI_20_change_pct"] = informative_15m["CCI_20"].pct_change() * 100.0
  # Candle change
  informative_15m["change_pct"] = (
    (informative_15m["close"] - informative_15m["open"]) / informative_15m["open"] * 100.0
  )

  # Performance logging
  # -----------------------------------------------------------------------------------------
  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] informative_15m_indicators took: {tok - tik:0.4f} seconds.")

  return informative_15m

# Coin Pair Base Timeframe Indicators
# ---------------------------------------------------------------------------------------------
def base_tf_5m_indicators(self, metadata: dict, df: DataFrame) -> DataFrame:
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
# ---------------------------------------------------------------------------------------------
def info_switcher(strategy, metadata: dict, info_timeframe) -> DataFrame:
  if info_timeframe == "1d":
    return strategy.informative_1d_indicators(metadata, info_timeframe)
  elif info_timeframe == "4h":
    return strategy.informative_4h_indicators(metadata, info_timeframe)
  elif info_timeframe == "1h":
    return strategy.informative_1h_indicators(metadata, info_timeframe)
  elif info_timeframe == "15m":
    return strategy.informative_15m_indicators(metadata, info_timeframe)
  else:
    raise RuntimeError(f"{info_timeframe} not supported as informative timeframe for BTC pair.")

