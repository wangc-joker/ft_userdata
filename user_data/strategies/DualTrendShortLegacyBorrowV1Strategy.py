from __future__ import annotations

from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, informative, stoploss_from_absolute

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy
from core.indicators.structure import populate_structure_indicators
from signals.reversal import populate_reversal_indicators


class _DualTrendShortLegacyStructureBase(IStrategy):
    """
    Validation base for old DoubleShun short structure tags.

    This file is intentionally isolated from the current Short V1 production
    candidate. It lets us test borrowed ideas before deciding what to migrate.
    """

    INTERFACE_VERSION = 3

    can_short = True
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count = 240

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True
    position_adjustment_enable = False

    minimal_roi = {"0": 0.10}
    stoploss = -0.02

    trend_ema_fast = 6
    trend_ema_slow = 46
    center_window = 5
    pullback_window = 6
    restart_window = 4
    triangle_window = 5
    compression_window = 11
    swing_window = 3

    pullback_depth = 0.009
    breakout_buffer = 0.009
    compression_limit = 0.006
    level_tolerance = 0.016
    level_proximity = 0.015
    volume_multiplier = 1.13
    daily_short_rsi = 46

    allowed_pairs: set[str] | None = None
    entry_tag_name = "legacy_short"
    use_daily_scope = False

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            }
        ]

    @staticmethod
    def _bool_series(dataframe: DataFrame, column: str) -> pd.Series:
        if column not in dataframe:
            return pd.Series(False, index=dataframe.index)
        return dataframe[column].eq(True)

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def _populate_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.trend_ema_fast,
            trend_ema_slow=self.trend_ema_slow,
            center_window=self.center_window,
            pullback_window=self.pullback_window,
            restart_window=self.restart_window,
            triangle_window=self.triangle_window,
            compression_window=self.compression_window,
            swing_window=self.swing_window,
            pullback_depth=self.pullback_depth,
            breakout_buffer=self.breakout_buffer,
            compression_limit=self.compression_limit,
            level_tolerance=self.level_tolerance,
            level_proximity=self.level_proximity,
            volume_multiplier=self.volume_multiplier,
        )

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def _entry_mask(self, dataframe: DataFrame) -> pd.Series:
        raise NotImplementedError

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_short"] = 0
        dataframe["enter_tag"] = None

        if self.allowed_pairs is not None and metadata["pair"] not in self.allowed_pairs:
            return dataframe

        entry = self._entry_mask(dataframe)
        dataframe.loc[entry, ["enter_short", "enter_tag"]] = (1, self.entry_tag_name)
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_short"] = 0
        return dataframe

    def _current_candle(self, pair: str) -> Optional[pd.Series]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        return dataframe.iloc[-1]

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
        candle = self._current_candle(pair)
        if candle is None:
            return self.stoploss

        suffix = "_1d" if self.use_daily_scope else ""
        structure_stop = candle.get(f"structure_stop_short{suffix}")
        stop_price = trade.open_rate * 1.02
        if pd.notna(structure_stop):
            stop_price = min(float(structure_stop), stop_price)

        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
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

        suffix = "_1d" if self.use_daily_scope else ""
        scope = "1d" if self.use_daily_scope else "1h"

        if bool(candle.get(f"uptrend{suffix}", False)):
            return f"trend_flip_short_{scope}"
        if bool(candle.get(f"center_up{suffix}", False)) and candle["close"] > candle.get(
            f"ema_fast{suffix}",
            candle["close"],
        ):
            return f"structure_exit_short_{scope}"
        structure_stop = candle.get(f"structure_stop_short{suffix}")
        if pd.notna(structure_stop) and candle["close"] > structure_stop:
            return f"swing_exit_short_{scope}"
        return None


class DualTrendShortDailyCenterV1Strategy(_DualTrendShortLegacyStructureBase):
    entry_tag_name = "short_1d_center_compression"
    use_daily_scope = True

    def _entry_mask(self, dataframe: DataFrame) -> pd.Series:
        daily_short_signal = (
            self._bool_series(dataframe, "restart_ready_short_1d")
            & self._bool_series(dataframe, "center_breakout_short_1d")
            & (dataframe["rsi_1d"] < self.daily_short_rsi)
        )
        return daily_short_signal & ~daily_short_signal.shift(1).eq(True)


class DualTrendShortDailyCenterFilteredV1Strategy(DualTrendShortDailyCenterV1Strategy):
    """
    Independent daily-center candidate with the first bad/zero contributors
    removed from the 13-pair universe.
    """

    allowed_pairs = {
        "BTC/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "ADA/USDT:USDT",
        "LINK/USDT:USDT",
        "NEAR/USDT:USDT",
        "SUI/USDT:USDT",
        "TAO/USDT:USDT",
    }


class DualTrendShortHourlyCenterV1Strategy(_DualTrendShortLegacyStructureBase):
    entry_tag_name = "short_1h_center"
    use_daily_scope = False

    def _entry_mask(self, dataframe: DataFrame) -> pd.Series:
        return self._bool_series(dataframe, "restart_ready_short_1d") & self._bool_series(
            dataframe,
            "center_breakout_short",
        )


class DualTrendShortReversalBreakdownV1Strategy(IStrategy):
    """
    Validation strategy for old short_reversal_breakdown.
    """

    INTERFACE_VERSION = 3

    can_short = True
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count = 240

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True
    position_adjustment_enable = False

    minimal_roi = {"0": 0.10}
    stoploss = -0.03

    trend_ema_fast = 6
    trend_ema_slow = 46
    center_window = 5
    pullback_window = 6
    restart_window = 4
    triangle_window = 5
    compression_window = 11
    swing_window = 3

    pullback_depth = 0.009
    breakout_buffer = 0.009
    compression_limit = 0.006
    level_tolerance = 0.016
    level_proximity = 0.015
    volume_multiplier = 1.13

    allowed_pairs: set[str] | None = None
    old_reversal_pairs = {
        "ZEC/USDT:USDT",
        "ADA/USDT:USDT",
        "XRP/USDT:USDT",
    }

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            }
        ]

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.trend_ema_fast,
            trend_ema_slow=self.trend_ema_slow,
            center_window=self.center_window,
            pullback_window=self.pullback_window,
            restart_window=self.restart_window,
            triangle_window=self.triangle_window,
            compression_window=self.compression_window,
            swing_window=self.swing_window,
            pullback_depth=self.pullback_depth,
            breakout_buffer=self.breakout_buffer,
            compression_limit=self.compression_limit,
            level_tolerance=self.level_tolerance,
            level_proximity=self.level_proximity,
            volume_multiplier=self.volume_multiplier,
        )

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.trend_ema_fast,
            trend_ema_slow=self.trend_ema_slow,
            center_window=self.center_window,
            pullback_window=self.pullback_window,
            restart_window=self.restart_window,
            triangle_window=self.triangle_window,
            compression_window=self.compression_window,
            swing_window=self.swing_window,
            pullback_depth=self.pullback_depth,
            breakout_buffer=self.breakout_buffer,
            compression_limit=self.compression_limit,
            level_tolerance=self.level_tolerance,
            level_proximity=self.level_proximity,
            volume_multiplier=self.volume_multiplier,
        )
        return populate_reversal_indicators(dataframe, metadata["pair"])

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_short"] = 0
        dataframe["enter_tag"] = None

        if self.allowed_pairs is not None and metadata["pair"] not in self.allowed_pairs:
            return dataframe

        entry = dataframe["reversal_short_breakdown"].fillna(False)
        hold = dataframe["reversal_short_hold_active"].fillna(False)
        dataframe.loc[entry | hold, ["enter_short", "enter_tag"]] = (1, "short_reversal_breakdown")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_short"] = 0
        return dataframe

    def _current_candle(self, pair: str) -> Optional[pd.Series]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        return dataframe.iloc[-1]

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
        candle = self._current_candle(pair)
        if candle is None:
            return self.stoploss
        structure_stop = candle.get("structure_stop_short")
        stop_price = trade.open_rate * 1.03
        if pd.notna(structure_stop):
            stop_price = min(float(structure_stop), stop_price)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
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
        if bool(candle.get("uptrend_1d", False)) and current_profit < 0.08:
            return "trend_flip_short_reversal"
        if bool(candle.get("center_up", False)) and candle["close"] > candle.get("ema_fast", candle["close"]):
            return "structure_exit_short_reversal"
        return None


class DualTrendShortReversalBreakdownOldPairsV1Strategy(DualTrendShortReversalBreakdownV1Strategy):
    allowed_pairs = {
        "ZEC/USDT:USDT",
        "ADA/USDT:USDT",
        "XRP/USDT:USDT",
    }


class DualTrendShortReversalBreakdownPositivePairsV1Strategy(DualTrendShortReversalBreakdownV1Strategy):
    allowed_pairs = {
        "XRP/USDT:USDT",
        "ZEC/USDT:USDT",
        "ADA/USDT:USDT",
        "NEAR/USDT:USDT",
    }


class _ShortV1BorrowBase(DualTrendCompressionRestartShortV1Strategy):
    """
    Migration-test base: keep current Short V1 intact, then optionally add old
    short tags as extra entries. This is a validation layer, not the main V1.
    """

    trend_ema_fast = 6
    trend_ema_slow = 46
    center_window = 5
    old_pullback_window = 6
    old_restart_window = 4
    old_triangle_window = 5
    old_compression_window = 11
    old_swing_window = 3

    old_pullback_depth = 0.009
    old_breakout_buffer = 0.009
    old_compression_limit = 0.006
    old_level_tolerance = 0.016
    old_level_proximity = 0.015
    old_volume_multiplier = 1.13
    daily_short_rsi = 46

    enable_borrow_daily_center = False
    enable_borrow_reversal = False
    borrow_reversal_pairs: set[str] | None = None

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_old_structure_indicators(dataframe)

    def _populate_old_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.trend_ema_fast,
            trend_ema_slow=self.trend_ema_slow,
            center_window=self.center_window,
            pullback_window=self.old_pullback_window,
            restart_window=self.old_restart_window,
            triangle_window=self.old_triangle_window,
            compression_window=self.old_compression_window,
            swing_window=self.old_swing_window,
            pullback_depth=self.old_pullback_depth,
            breakout_buffer=self.old_breakout_buffer,
            compression_limit=self.old_compression_limit,
            level_tolerance=self.old_level_tolerance,
            level_proximity=self.old_level_proximity,
            volume_multiplier=self.old_volume_multiplier,
        )

    @staticmethod
    def _bool_series(dataframe: DataFrame, column: str) -> pd.Series:
        if column not in dataframe:
            return pd.Series(False, index=dataframe.index)
        return dataframe[column].eq(True)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        dataframe = self._populate_old_structure_indicators(dataframe)
        if self.enable_borrow_reversal:
            dataframe = populate_reversal_indicators(dataframe, metadata["pair"])
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        empty_slot = dataframe.get("enter_short", 0) != 1

        if self.enable_borrow_daily_center:
            daily_short_signal = (
                self._bool_series(dataframe, "restart_ready_short_1d")
                & self._bool_series(dataframe, "center_breakout_short_1d")
                & (dataframe["rsi_1d"] < self.daily_short_rsi)
            )
            daily_center = daily_short_signal & ~daily_short_signal.shift(1).eq(True)
            daily_center &= empty_slot
            dataframe.loc[daily_center, ["enter_short", "enter_tag"]] = (
                1,
                "borrow_short_1d_center",
            )
            daily_stop = dataframe["structure_stop_short_1d"]
            daily_risk = (daily_stop - dataframe["close"]) / dataframe["close"]
            dataframe.loc[daily_center, "enter_initial_stop"] = daily_stop.loc[daily_center].astype("float32")
            dataframe.loc[daily_center, "enter_risk_pct"] = daily_risk.loc[daily_center].astype("float32")

        if self.enable_borrow_reversal:
            empty_slot = dataframe.get("enter_short", 0) != 1
            reversal = (
                dataframe["reversal_short_breakdown"].fillna(False)
                | dataframe["reversal_short_hold_active"].fillna(False)
            )
            if self.borrow_reversal_pairs is not None and metadata["pair"] not in self.borrow_reversal_pairs:
                reversal &= False
            reversal &= empty_slot
            dataframe.loc[reversal, ["enter_short", "enter_tag"]] = (
                1,
                "borrow_short_reversal",
            )
            reversal_stop = dataframe["structure_stop_short"].combine(
                dataframe["close"] * 1.03,
                min,
            )
            reversal_risk = (reversal_stop - dataframe["close"]) / dataframe["close"]
            dataframe.loc[reversal, "enter_initial_stop"] = reversal_stop.loc[reversal].astype("float32")
            dataframe.loc[reversal, "enter_risk_pct"] = reversal_risk.loc[reversal].astype("float32")

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
        tag = trade.enter_tag or ""
        if tag not in {"borrow_short_1d_center", "borrow_short_reversal"}:
            return super().custom_stoploss(
                pair,
                trade,
                current_time,
                current_rate,
                current_profit,
                after_fill,
                **kwargs,
            )

        candle = self._current_candle(pair)
        if candle is None:
            return self.stoploss

        suffix = "_1d" if tag == "borrow_short_1d_center" else ""
        cap = self.max_stop_distance if tag == "borrow_short_1d_center" else 0.03
        structure_stop = candle.get(f"structure_stop_short{suffix}")
        stop_price = trade.open_rate * (1 + cap)
        if pd.notna(structure_stop):
            stop_price = min(float(structure_stop), stop_price)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
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
        tag = trade.enter_tag or ""
        if tag not in {"borrow_short_1d_center", "borrow_short_reversal"}:
            return super().custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs)

        candle = self._current_candle(pair)
        if candle is None:
            return None

        suffix = "_1d" if tag == "borrow_short_1d_center" else ""
        scope = "1d" if tag == "borrow_short_1d_center" else "reversal"
        if bool(candle.get(f"uptrend{suffix}", False)) and current_profit < 0.08:
            return f"borrow_trend_flip_short_{scope}"
        if bool(candle.get(f"center_up{suffix}", False)) and candle["close"] > candle.get(
            f"ema_fast{suffix}",
            candle["close"],
        ):
            return f"borrow_structure_exit_short_{scope}"

        base_exit = super().custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs)
        return base_exit


class DualTrendShortV1PlusDailyCenterV1Strategy(_ShortV1BorrowBase):
    enable_borrow_daily_center = True


class DualTrendShortV1PlusReversalV1Strategy(_ShortV1BorrowBase):
    enable_borrow_reversal = True


class DualTrendShortV1PlusReversalPositivePairsV1Strategy(_ShortV1BorrowBase):
    enable_borrow_reversal = True
    borrow_reversal_pairs = {
        "XRP/USDT:USDT",
        "ZEC/USDT:USDT",
        "ADA/USDT:USDT",
        "NEAR/USDT:USDT",
    }


class DualTrendShortV1PlusDailyCenterReversalV1Strategy(_ShortV1BorrowBase):
    enable_borrow_daily_center = True
    enable_borrow_reversal = True
