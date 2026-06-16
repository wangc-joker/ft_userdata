from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class DualTrendCompressionRestartLongBase(DualTrendCompressionRestartShortV1Strategy):
    """
    Long-side experimental base for the dual-trend compression restart idea.

    The short strategies are left untouched. This class reuses shared indicator
    helpers, stake sizing, protections, and then implements long-only entries.
    """

    can_short = False
    minimal_roi = {"0": 0.08}

    enable_long_pullback_restart = True
    enable_long_compression_breakout = True

    high_zone_buffer = 0.965
    long_close_position_min = 0.60
    require_btc_trend_up_for_longs = False

    trade_pair_allowlist = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ADA/USDT:USDT",
        "LINK/USDT:USDT",
        "NEAR/USDT:USDT",
        "SUI/USDT:USDT",
        "TRX/USDT:USDT",
        "ZEC/USDT:USDT",
        "TAO/USDT:USDT",
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        cw = self.compression_window
        hw = self.compression_half_window
        pw = self.pretrend_window

        dataframe["breakout_long"] = dataframe["close"] > dataframe["compression_high"] * (1 + self.breakout_buffer)
        dataframe["low_min_first_half"] = dataframe["low"].shift(hw + 1).rolling(hw).min()
        dataframe["low_min_last_half"] = dataframe["low"].shift(1).rolling(hw).min()
        dataframe["center_up"] = (
            (dataframe["low_min_last_half"] > dataframe["low_min_first_half"])
            & (dataframe["close_mean_last_half"] > dataframe["close_mean_first_half"])
        )

        dataframe["pretrend_up"] = dataframe["return_24h"] > dataframe["pretrend_threshold"]
        dataframe["recent_high_24"] = dataframe["high"].shift(1).rolling(pw).max()
        dataframe["pullback_low_12"] = dataframe["low"].shift(1).rolling(cw).min()
        dataframe["pullback_depth_long"] = (dataframe["recent_high_24"] - dataframe["pullback_low_12"]) / dataframe[
            "recent_high_24"
        ]
        dataframe["pullback_seen_long"] = dataframe["pullback_depth_long"].between(
            self.pullback_min_depth,
            self.pullback_max_depth,
        )
        dataframe["near_high_zone"] = dataframe["compression_low"] >= dataframe["recent_high_24"] * self.high_zone_buffer

        candle_range = dataframe["high"] - dataframe["low"]
        dataframe["candle_quality_long"] = (
            (candle_range > 0)
            & (dataframe["body_pct_of_range"] >= self.candle_body_min)
            & (dataframe["close_position"] >= self.long_close_position_min)
        )

        dataframe["long_compression_stop"] = dataframe["compression_low"] - self.stop_atr_buffer * dataframe["atr_ref"]
        dataframe["long_pullback_stop"] = dataframe["pullback_low_12"] - self.stop_atr_buffer * dataframe["atr_ref"]
        dataframe["long_compression_risk_pct"] = (dataframe["close"] - dataframe["long_compression_stop"]) / dataframe[
            "close"
        ]
        dataframe["long_pullback_risk_pct"] = (dataframe["close"] - dataframe["long_pullback_stop"]) / dataframe["close"]
        dataframe["long_compression_risk_pct_ok"] = dataframe["long_compression_risk_pct"].between(
            self.min_stop_distance,
            self.max_stop_distance,
        )
        dataframe["long_pullback_risk_pct_ok"] = dataframe["long_pullback_risk_pct"].between(
            self.min_stop_distance,
            self.max_stop_distance,
        )

        dataframe["btc_filter_long_ok"] = True
        if self.use_btc_filter and metadata["pair"] != "BTC/USDT:USDT":
            btc_up = dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
            btc_down = dataframe.get("btc_trend_down_4h", pd.Series(False, index=dataframe.index)).fillna(False)
            dataframe["btc_filter_long_ok"] = btc_up if self.require_btc_trend_up_for_longs else ~btc_down
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        trend_up = dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
        ema50_4h = dataframe.get("ema50_4h", pd.Series(np.nan, index=dataframe.index))
        btc_filter = dataframe.get("btc_filter_long_ok", pd.Series(True, index=dataframe.index)).fillna(True)
        pullback_intact_long = dataframe["pullback_low_12"] >= ema50_4h * 0.99
        base_filter = (
            trend_up
            & dataframe["compression_ok"]
            & dataframe["center_up"]
            & dataframe["breakout_long"]
            & dataframe["vol_ok"]
            & dataframe["candle_quality_long"]
            & btc_filter
            & (dataframe["volume"] > 0)
        )

        long_pullback_restart = (
            self.enable_long_pullback_restart
            & base_filter
            & dataframe["pullback_seen_long"]
            & pullback_intact_long
            & dataframe["long_pullback_risk_pct_ok"]
        )
        long_compression_breakout = (
            self.enable_long_compression_breakout
            & base_filter
            & dataframe["pretrend_up"]
            & dataframe["near_high_zone"]
            & dataframe["long_compression_risk_pct_ok"]
        )

        dataframe.loc[long_pullback_restart, ["enter_long", "enter_tag"]] = (1, "long_pullback_restart")
        dataframe.loc[long_pullback_restart, "enter_initial_stop"] = dataframe.loc[
            long_pullback_restart,
            "long_pullback_stop",
        ]
        dataframe.loc[long_pullback_restart, "enter_risk_pct"] = dataframe.loc[
            long_pullback_restart,
            "long_pullback_risk_pct",
        ]

        dataframe.loc[long_compression_breakout, ["enter_long", "enter_tag"]] = (1, "long_compression_breakout")
        dataframe.loc[long_compression_breakout, "enter_initial_stop"] = dataframe.loc[
            long_compression_breakout,
            "long_compression_stop",
        ]
        dataframe.loc[long_compression_breakout, "enter_risk_pct"] = dataframe.loc[
            long_compression_breakout,
            "long_compression_risk_pct",
        ]
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        candle = self._entry_candle(pair, trade)
        if candle is None:
            return self.stoploss
        tag = trade.enter_tag or ""
        stop_col = "long_compression_stop" if tag == "long_compression_breakout" else "long_pullback_stop"
        initial_stop = float(candle.get(stop_col, np.nan))
        capped_stop = trade.open_rate * (1 - self.max_stop_distance)
        stop_price = capped_stop if not np.isfinite(initial_stop) else max(initial_stop, capped_stop)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=False,
            leverage=trade.leverage,
        )

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        candle = self._current_candle(pair)
        if candle is None:
            return None

        age = current_time - trade.open_date_utc
        if age > timedelta(hours=72) and current_profit < 0:
            return "stale_loss_72h"
        if age > timedelta(hours=120) and current_profit < 0.01:
            return "stale_flat_120h"
        if age > timedelta(hours=240) and current_profit < 0.03:
            return "stale_low_profit_240h"

        if bool(candle.get("trend_down_4h", False)) and current_profit < 0.03:
            return "trend_flip_long"
        return None


class DualTrendCompressionRestartLongMirrorCandidate(DualTrendCompressionRestartLongBase):
    """
    Candidate A: mirror the original long logic across the full 13-pair universe.
    """


class DualTrendCompressionRestartLongPullbackCandidate(DualTrendCompressionRestartLongBase):
    """
    Candidate B: only use the long pullback restart signal.
    """

    enable_long_compression_breakout = False


class DualTrendCompressionRestartLongSelectiveCandidate(DualTrendCompressionRestartLongBase):
    """
    Candidate C: keep only pairs that showed some long-side promise in audit.
    """

    enable_long_compression_breakout = False
    require_btc_trend_up_for_longs = True
    minimal_roi = {"0": 0.06}
    trade_pair_allowlist = {
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
    }


class DualTrendCompressionRestartLongQualityCandidate(DualTrendCompressionRestartLongSelectiveCandidate):
    """
    Candidate D: selective pullback entries plus stronger candle and extension filters.
    """

    long_close_position_min = 0.70
    max_entry_atr_pct = 0.055
    max_return_24h = 0.14
    min_return_24h = -0.03
    max_pullback_depth_v2 = 0.06

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        if "enter_long" not in dataframe:
            return dataframe

        entry = dataframe["enter_long"] == 1
        if not entry.any():
            return dataframe

        keep = (
            (dataframe["atr_pct"] <= self.max_entry_atr_pct)
            & dataframe["return_24h"].between(self.min_return_24h, self.max_return_24h)
            & (dataframe["pullback_depth_long"] <= self.max_pullback_depth_v2)
            & (dataframe["close"] > dataframe["ema50_4h"])
        )
        clear = entry & ~keep
        dataframe.loc[clear, ["enter_long", "enter_tag"]] = (0, None)
        dataframe.loc[clear, ["enter_initial_stop", "enter_risk_pct"]] = np.nan
        return dataframe


class DualTrendCompressionRestartLongQualityRoi5Candidate(DualTrendCompressionRestartLongQualityCandidate):
    """
    Candidate E: quality long entries with a faster 5% ROI target.
    """

    minimal_roi = {"0": 0.05}


class DualTrendCompressionRestartLongNoEthCandidate(DualTrendCompressionRestartLongQualityCandidate):
    """
    Candidate F: remove ETH after pair-level tests showed it drags both recent
    and full-sample long results.
    """

    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
    }


class DualTrendCompressionRestartLongNoEthRoi5Candidate(DualTrendCompressionRestartLongNoEthCandidate):
    """
    Candidate G: no-ETH long set with a faster 5% profit target.
    """

    minimal_roi = {"0": 0.05}


class DualTrendCompressionRestartLongTightNoEthRoi5Candidate(DualTrendCompressionRestartLongNoEthRoi5Candidate):
    """
    Candidate H: no-ETH set with tighter extension and volatility gates.
    """

    long_close_position_min = 0.72
    max_entry_atr_pct = 0.05
    max_return_24h = 0.12
    min_return_24h = -0.02
    max_pullback_depth_v2 = 0.05


class DualTrendCompressionRestartLongBnbOnlyRoi5Candidate(DualTrendCompressionRestartLongQualityRoi5Candidate):
    """
    Candidate I: isolate the strongest long-side contributor.
    """

    trade_pair_allowlist = {
        "BNB/USDT:USDT",
    }
