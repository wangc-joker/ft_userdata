from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import informative

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class _DualTrendShortV1LegacyFilterBase(DualTrendCompressionRestartShortV1Strategy):
    """
    Validation-only variants that borrow old Top9 center/early-fail ideas.

    The two original Short V1 entry shapes remain unchanged. Subclasses only
    veto entries after the base signal is created, or add an early failure exit.
    """

    use_legacy_market_center_filter = False
    use_legacy_daily_center_filter = False
    use_legacy_early_fail_exit = False

    legacy_center_window = 5
    legacy_center_slope_shift = 3
    legacy_early_fail_hours = 12
    legacy_early_fail_max_profit = 0.005

    @staticmethod
    def _add_legacy_center(dataframe: DataFrame, suffix: str = "") -> DataFrame:
        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
        center = typical_price.rolling(_DualTrendShortV1LegacyFilterBase.legacy_center_window).mean()
        dataframe[f"legacy_market_center{suffix}"] = center
        dataframe[f"legacy_center_up{suffix}"] = center > center.shift(
            _DualTrendShortV1LegacyFilterBase.legacy_center_slope_shift
        )
        dataframe[f"legacy_center_down{suffix}"] = center < center.shift(
            _DualTrendShortV1LegacyFilterBase.legacy_center_slope_shift
        )
        dataframe[f"legacy_ema_fast{suffix}"] = dataframe["close"].ewm(span=20, adjust=False, min_periods=20).mean()
        dataframe[f"legacy_ema_slow{suffix}"] = dataframe["close"].ewm(span=50, adjust=False, min_periods=50).mean()
        return dataframe

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._add_legacy_center(dataframe.copy())

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        return self._add_legacy_center(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if not entry.any():
            return dataframe

        allow = pd.Series(True, index=dataframe.index)
        if self.use_legacy_market_center_filter:
            allow &= dataframe["legacy_center_down"].fillna(False)
            allow &= dataframe["close"] < dataframe["legacy_market_center"]
        if self.use_legacy_daily_center_filter:
            daily_center_down = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index))
            daily_market_center = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            allow &= daily_center_down.fillna(False)
            allow &= dataframe["close"] < daily_market_center

        rejected = entry & ~allow
        dataframe.loc[rejected, "enter_short"] = 0
        dataframe.loc[rejected, "enter_tag"] = None
        dataframe.loc[rejected, "enter_initial_stop"] = np.nan
        dataframe.loc[rejected, "enter_risk_pct"] = np.nan
        return dataframe

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        base_exit = super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )
        if base_exit or not self.use_legacy_early_fail_exit or not trade.is_short:
            return base_exit

        candle = self._current_candle(pair)
        if candle is None:
            return None

        age = current_time - trade.open_date_utc
        if age > timedelta(hours=self.legacy_early_fail_hours):
            return None
        if current_profit > self.legacy_early_fail_max_profit:
            return None

        center_up = bool(candle.get("legacy_center_up", False))
        center = float(candle.get("legacy_market_center", np.nan))
        ema_fast = float(candle.get("legacy_ema_fast", np.nan))
        close = float(candle.get("close", np.nan))
        if np.isfinite(close) and np.isfinite(center) and np.isfinite(ema_fast):
            if center_up and close > min(center, ema_fast):
                return "legacy_early_fail_short"
        return None


class DualTrendShortV1MarketCenterFilterStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_market_center_filter = True


class DualTrendShortV1DailyCenterFilterStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_daily_center_filter = True


class DualTrendShortV1MarketDailyCenterFilterStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_market_center_filter = True
    use_legacy_daily_center_filter = True


class DualTrendShortV1EarlyFailExitStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_early_fail_exit = True


class DualTrendShortV1DailyCenterEarlyFailStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_daily_center_filter = True
    use_legacy_early_fail_exit = True


class DualTrendShortV1EarlyFailLossOnly6hStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_early_fail_exit = True
    legacy_early_fail_hours = 6
    legacy_early_fail_max_profit = 0.0


class DualTrendShortV1DailyCenterEarlyFailLossOnly6hStrategy(_DualTrendShortV1LegacyFilterBase):
    use_legacy_daily_center_filter = True
    use_legacy_early_fail_exit = True
    legacy_early_fail_hours = 6
    legacy_early_fail_max_profit = 0.0
