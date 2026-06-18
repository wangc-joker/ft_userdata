from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.strategy import informative

from DualTrendCombinedLongDailyCenterShortV1Strategy import (
    DualTrendCombinedLongDailyCenterShortV1Strategy,
)


class _DualTrendCombinedGlobalFilterBase(DualTrendCombinedLongDailyCenterShortV1Strategy):
    """
    Global validation variants for the combined strategy.

    Goal:
    - do not special-case individual pairs
    - improve entry quality with market-wide filters
    - reduce low-quality long 1d breakouts and weak short pullbacks
    """

    use_short_daily_center_filter = False
    short_filter_mode = "strict_all"
    use_long_strong_confirm = False
    use_long_btc_trend_filter = False
    long_filter_mode = "none"
    use_short_pullback_shape_filter = False
    short_pullback_max_width_pct = 0.035
    use_long_center_streak_filter = False
    long_center_streak_min = 3

    long_daily_rsi = 58

    @staticmethod
    def _add_legacy_center(dataframe: DataFrame, suffix: str = "") -> DataFrame:
        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
        center = typical_price.rolling(5).mean()
        dataframe[f"legacy_market_center{suffix}"] = center
        dataframe[f"legacy_center_up{suffix}"] = center > center.shift(3)
        dataframe[f"legacy_center_down{suffix}"] = center < center.shift(3)
        return dataframe

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators_1d(dataframe, metadata)
        return self._add_legacy_center(dataframe)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        return self._add_legacy_center(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)

        if self.use_short_daily_center_filter and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            close_above_center = dataframe["close"] > market_center_1d

            if self.short_filter_mode == "strict_all":
                allow_short = center_down_1d & close_below_center
                reject_short = short_entry & ~allow_short
            elif self.short_filter_mode == "strict_breakdown_only":
                allow_short = center_down_1d & close_below_center
                reject_short = short_entry & enter_tag.eq("short_compression_breakdown") & ~allow_short
            elif self.short_filter_mode == "reject_clear_uptrend_all":
                reject_short = short_entry & center_up_1d & close_above_center
            elif self.short_filter_mode == "reject_clear_uptrend_breakdown_only":
                reject_short = (
                    short_entry
                    & enter_tag.eq("short_compression_breakdown")
                    & center_up_1d
                    & close_above_center
                )
            else:
                reject_short = pd.Series(False, index=dataframe.index)

            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        if self.use_long_strong_confirm and long_entry.any():
            allow_long = (
                dataframe.get("daily_momentum_long_1d", pd.Series(False, index=dataframe.index)).fillna(False)
                & dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
                & dataframe.get("center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            )
            if self.use_long_btc_trend_filter and metadata["pair"] != "BTC/USDT:USDT":
                allow_long &= dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)

            reject_long = long_entry & ~allow_long
            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.long_filter_mode != "none" and long_entry.any():
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            close_above_center = dataframe["close"] > market_center_1d

            if self.long_filter_mode == "reject_clear_downtrend":
                reject_long = long_entry & center_down_1d & close_below_center
            elif self.long_filter_mode == "require_4h_trend_up":
                allow_long = dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
                reject_long = long_entry & ~allow_long
            elif self.long_filter_mode == "require_legacy_center_up":
                reject_long = long_entry & ~(center_up_1d & close_above_center)
            else:
                reject_long = pd.Series(False, index=dataframe.index)

            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_short_pullback_shape_filter and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            tight_enough = dataframe.get(
                "compression_width_pct",
                pd.Series(np.nan, index=dataframe.index),
            ) <= self.short_pullback_max_width_pct
            shape_ok = center_down_1d & close_below_center & tight_enough.fillna(False)
            reject_short = short_entry & enter_tag.eq("short_pullback_restart") & ~shape_ok
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_long_center_streak_filter and long_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            range_contracting_1d = dataframe.get("range_contracting_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            streak = pd.Series(0, index=dataframe.index, dtype="int64")
            for i in range(1, self.long_center_streak_min + 1):
                streak += center_up_1d.shift(i - 1).fillna(False).astype("int64")
            streak_ok = streak >= self.long_center_streak_min
            confirm_long = range_contracting_1d & streak_ok
            reject_long = long_entry & enter_tag.eq("long_1d_center_compression") & ~confirm_long
            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        return dataframe


class DualTrendCombinedGlobalV2Strategy(_DualTrendCombinedGlobalFilterBase):
    """
    Current combined candidate:
    - keep validated Long daily center RSI at 58
    - reject shorts only when 1d legacy center is clearly up and price is above it
    """

    use_short_daily_center_filter = True
    short_filter_mode = "reject_clear_uptrend_all"
    long_daily_rsi = 58


class DualTrendCombinedShortPullbackShapeV1Strategy(DualTrendCombinedGlobalV2Strategy):
    """
    Validation branch:
    - keep the current main strategy
    - further tighten short_pullback_restart with 1d center alignment and narrower compression
    """

    use_short_pullback_shape_filter = True
    short_pullback_max_width_pct = 0.035


class DualTrendCombinedLongCenterStreakV1Strategy(DualTrendCombinedGlobalV2Strategy):
    """
    Validation branch:
    - keep the current main strategy
    - require long_1d_center_compression to have contracting range and 3-bar center-up streak
    """

    use_long_center_streak_filter = True
    long_center_streak_min = 3


class DualTrendCombinedShapeFocusedV1Strategy(DualTrendCombinedGlobalV2Strategy):
    """
    Validation branch:
    - combine the short pullback shape filter and long center streak filter
    """

    use_short_pullback_shape_filter = True
    short_pullback_max_width_pct = 0.035
    use_long_center_streak_filter = True
    long_center_streak_min = 3
