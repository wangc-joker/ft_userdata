from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame, Series

from freqtrade.persistence import Trade
from freqtrade.strategy import (
    BooleanParameter,
    DecimalParameter,
    IStrategy,
    IntParameter,
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
    timeframe_to_minutes,
    timeframe_to_prev_date,
)


class SystemTrendBreakoutV1(IStrategy):
    """
    Medium-frequency trend-following system with breakout confirmation and risk-first trade management.

    Design goals:
    - Spot-first, long-only by default.
    - Multi-timeframe market regime filter using 15m / 1h / 4h.
    - Clear vectorized indicators for backtest / hyperopt / lookahead / recursive checks.
    - Minimal heavy work in callbacks to keep live execution efficient.
    """

    INTERFACE_VERSION = 3

    timeframe = "15m"
    informative_timeframe_1h = "1h"
    informative_timeframe_4h = "4h"

    can_short = False
    process_only_new_candles = True
    startup_candle_count = 2400

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    use_custom_stoploss = True

    stoploss = -0.18
    trailing_stop = False

    minimal_roi = {
        "0": 0.10,
        "240": 0.05,
        "720": 0.02,
        "1440": 0.0,
    }

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "emergency_exit": "market",
        "force_entry": "market",
        "force_exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": False,
        "stoploss_on_exchange_interval": 60,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    max_open_trades = 4

    breakout_lookback = IntParameter(20, 96, default=48, space="buy", optimize=True)
    breakout_buffer = DecimalParameter(0.000, 0.006, default=0.001, decimals=3, space="buy", optimize=True)
    rsi_lower = IntParameter(48, 58, default=52, space="buy", optimize=True)
    rsi_upper = IntParameter(62, 75, default=68, space="buy", optimize=True)
    adx_threshold = IntParameter(18, 28, default=22, space="buy", optimize=True)
    atr_ratio_min = DecimalParameter(0.002, 0.012, default=0.004, decimals=3, space="buy", optimize=True)
    atr_ratio_max = DecimalParameter(0.015, 0.080, default=0.040, decimals=3, space="buy", optimize=True)
    volume_window = IntParameter(12, 48, default=24, space="buy", optimize=False)
    volume_factor = DecimalParameter(1.0, 2.5, default=1.2, decimals=2, space="buy", optimize=True)
    ema_slope_window = IntParameter(6, 48, default=24, space="buy", optimize=True)
    chase_atr_limit = DecimalParameter(0.4, 2.0, default=1.0, decimals=2, space="buy", optimize=True)
    bb_extension_limit = DecimalParameter(0.001, 0.03, default=0.01, decimals=3, space="buy", optimize=True)
    pullback_tolerance = DecimalParameter(0.002, 0.02, default=0.008, decimals=3, space="buy", optimize=True)
    pullback_structure_window = IntParameter(6, 24, default=12, space="buy", optimize=False)
    breakout_memory = IntParameter(4, 24, default=12, space="buy", optimize=False)
    enable_pullback_module = BooleanParameter(default=True, space="buy", optimize=True)

    risk_per_trade = DecimalParameter(0.002, 0.010, default=0.005, decimals=3, space="stake", optimize=False)
    min_position_size_pct = DecimalParameter(0.01, 0.10, default=0.02, decimals=3, space="stake", optimize=False)
    max_position_size_pct = DecimalParameter(0.05, 0.35, default=0.20, decimals=3, space="stake", optimize=False)
    max_pair_exposure_pct = DecimalParameter(0.05, 0.35, default=0.20, decimals=3, space="stake", optimize=False)
    initial_atr_stop_mult = DecimalParameter(1.5, 4.0, default=2.4, decimals=2, space="stoploss", optimize=True)
    breakeven_r_multiple = DecimalParameter(0.8, 1.8, default=1.0, decimals=2, space="stoploss", optimize=True)
    profit_lock_r_multiple = DecimalParameter(1.2, 3.0, default=1.8, decimals=2, space="stoploss", optimize=True)
    atr_trail_mult = DecimalParameter(1.0, 3.5, default=1.8, decimals=2, space="stoploss", optimize=True)
    swing_window = IntParameter(6, 30, default=12, space="stoploss", optimize=False)

    momentum_exit_rsi = IntParameter(38, 55, default=45, space="sell", optimize=True)
    timeout_bars = IntParameter(24, 192, default=96, space="sell", optimize=True)
    timeout_min_profit = DecimalParameter(-0.01, 0.03, default=0.005, decimals=3, space="sell", optimize=True)
    volatility_exit_enabled = BooleanParameter(default=True, space="sell", optimize=True)
    volatility_exit_wick_ratio = DecimalParameter(0.35, 0.75, default=0.50, decimals=2, space="sell", optimize=True)
    volatility_exit_volume_mult = DecimalParameter(1.5, 4.0, default=2.2, decimals=2, space="sell", optimize=True)

    cooldown_candles = IntParameter(2, 16, default=4, space="protection", optimize=True)
    stoploss_guard_lookback = IntParameter(24, 144, default=72, space="protection", optimize=True)
    stoploss_guard_trade_limit = IntParameter(2, 8, default=4, space="protection", optimize=True)
    stoploss_guard_duration = IntParameter(4, 48, default=12, space="protection", optimize=True)
    max_drawdown_lookback = IntParameter(48, 288, default=144, space="protection", optimize=True)
    max_drawdown_trade_limit = IntParameter(6, 30, default=12, space="protection", optimize=True)
    max_drawdown_stop = IntParameter(12, 96, default=24, space="protection", optimize=True)
    max_drawdown_allowed = DecimalParameter(0.08, 0.30, default=0.16, decimals=2, space="protection", optimize=True)
    low_profit_lookback = IntParameter(24, 192, default=72, space="protection", optimize=True)
    low_profit_trade_limit = IntParameter(2, 12, default=4, space="protection", optimize=True)
    low_profit_stop = IntParameter(4, 48, default=12, space="protection", optimize=True)
    low_profit_required = DecimalParameter(-0.02, 0.03, default=0.0, decimals=3, space="protection", optimize=True)

    @property
    def protections(self) -> list[dict[str, Any]]:
        """
        Return strategy-local protections.
        """
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": int(self.cooldown_candles.value),
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": int(self.stoploss_guard_lookback.value),
                "trade_limit": int(self.stoploss_guard_trade_limit.value),
                "stop_duration_candles": int(self.stoploss_guard_duration.value),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.max_drawdown_lookback.value),
                "trade_limit": int(self.max_drawdown_trade_limit.value),
                "stop_duration_candles": int(self.max_drawdown_stop.value),
                "max_allowed_drawdown": float(self.max_drawdown_allowed.value),
            },
            {
                "method": "LowProfitPairs",
                "lookback_period_candles": int(self.low_profit_lookback.value),
                "trade_limit": int(self.low_profit_trade_limit.value),
                "stop_duration_candles": int(self.low_profit_stop.value),
                "required_profit": float(self.low_profit_required.value),
            },
        ]

    def informative_pairs(self) -> list[tuple[str, str]]:
        """
        Provide 1h and 4h informative pairs for every pair in the current whitelist.
        """
        if not self.dp:
            return []

        pairs = self.dp.current_whitelist()
        informative: list[tuple[str, str]] = []
        for pair in pairs:
            informative.append((pair, self.informative_timeframe_1h))
            informative.append((pair, self.informative_timeframe_4h))
        return informative

    def _safe_series(self, series: Series, fill_value: float = 0.0) -> Series:
        """
        Normalize NaN / inf values for indicator columns.
        """
        return series.replace([np.inf, -np.inf], np.nan).fillna(fill_value)

    def _add_main_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        Calculate all 15m indicators used by entry, exit, and risk logic.
        """
        dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_ratio"] = self._safe_series(dataframe["atr"] / dataframe["close"])

        bbands = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_upper"] = bbands["upperband"]
        dataframe["bb_middle"] = bbands["middleband"]
        dataframe["bb_lower"] = bbands["lowerband"]

        volume_window = int(self.volume_window.value)
        dataframe["volume_mean"] = dataframe["volume"].rolling(volume_window, min_periods=volume_window).mean()
        dataframe["volume_ratio"] = self._safe_series(dataframe["volume"] / dataframe["volume_mean"])

        lookback = int(self.breakout_lookback.value)
        dataframe["donchian_high"] = dataframe["high"].shift(1).rolling(lookback, min_periods=lookback).max()
        dataframe["donchian_low"] = dataframe["low"].shift(1).rolling(lookback, min_periods=lookback).min()
        dataframe["donchian_mid"] = (dataframe["donchian_high"] + dataframe["donchian_low"]) / 2.0

        structure_window = int(self.pullback_structure_window.value)
        dataframe["structure_low"] = dataframe["low"].shift(1).rolling(
            structure_window, min_periods=structure_window
        ).min()
        dataframe["swing_low"] = dataframe["low"].shift(1).rolling(
            int(self.swing_window.value), min_periods=int(self.swing_window.value)
        ).min()

        slope_window = int(self.ema_slope_window.value)
        dataframe["ema200_slope_15m"] = dataframe["ema_200"] - dataframe["ema_200"].shift(slope_window)
        dataframe["distance_over_ema20"] = self._safe_series((dataframe["close"] - dataframe["ema_20"]) / dataframe["close"])
        dataframe["distance_to_bb_upper"] = self._safe_series((dataframe["bb_upper"] - dataframe["close"]) / dataframe["close"])

        breakout_buffer = float(self.breakout_buffer.value)
        dataframe["breakout_trigger"] = (
            (dataframe["close"] > dataframe["donchian_high"] * (1.0 + breakout_buffer))
            & (dataframe["close"].shift(1) <= dataframe["donchian_high"].shift(1) * (1.0 + breakout_buffer))
        ).astype(int)
        dataframe["recent_breakout"] = (
            dataframe["breakout_trigger"]
            .shift(1)
            .rolling(int(self.breakout_memory.value), min_periods=1)
            .max()
            .fillna(0)
            .astype(int)
        )

        dataframe["upper_wick_ratio"] = self._safe_series(
            (dataframe["high"] - dataframe[["open", "close"]].max(axis=1))
            / (dataframe["high"] - dataframe["low"]).replace(0, np.nan)
        )
        dataframe["is_green"] = (dataframe["close"] > dataframe["open"]).astype(int)
        dataframe["trend_stack"] = (
            (dataframe["ema_20"] > dataframe["ema_50"]) & (dataframe["ema_50"] > dataframe["ema_200"])
        ).astype(int)

        return dataframe

    def _add_informative_indicators(self, dataframe: DataFrame, pair: str) -> DataFrame:
        """
        Merge and derive indicators from 1h and 4h informative dataframes.
        """
        if not self.dp:
            return dataframe

        informative_1h = self.dp.get_pair_dataframe(pair=pair, timeframe=self.informative_timeframe_1h)
        informative_1h["adx"] = ta.ADX(informative_1h, timeperiod=14)
        informative_1h["ema_50"] = ta.EMA(informative_1h, timeperiod=50)
        informative_1h["ema_200"] = ta.EMA(informative_1h, timeperiod=200)

        informative_4h = self.dp.get_pair_dataframe(pair=pair, timeframe=self.informative_timeframe_4h)
        informative_4h["ema_200"] = ta.EMA(informative_4h, timeperiod=200)
        informative_4h["atr"] = ta.ATR(informative_4h, timeperiod=14)
        informative_4h["atr_ratio"] = self._safe_series(informative_4h["atr"] / informative_4h["close"])
        informative_4h["ema200_slope"] = informative_4h["ema_200"] - informative_4h["ema_200"].shift(
            int(self.ema_slope_window.value)
        )

        dataframe = merge_informative_pair(
            dataframe,
            informative_1h,
            self.timeframe,
            self.informative_timeframe_1h,
            ffill=True,
        )
        dataframe = merge_informative_pair(
            dataframe,
            informative_4h,
            self.timeframe,
            self.informative_timeframe_4h,
            ffill=True,
        )

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Build all indicators and debug columns.

        Debug columns are intentionally kept in the dataframe so exported signals
        can be analyzed after backtesting.
        """
        dataframe = self._add_main_indicators(dataframe)
        dataframe = self._add_informative_indicators(dataframe, metadata["pair"])

        slope_window = int(self.ema_slope_window.value)
        dataframe["regime_4h_bull"] = (
            (dataframe["close_4h"] > dataframe["ema_200_4h"])
            & (dataframe["ema_200_4h"] > dataframe["ema_200_4h"].shift(slope_window))
        ).astype(int)
        dataframe["trend_strength_1h"] = (dataframe["adx_1h"] > int(self.adx_threshold.value)).astype(int)
        dataframe["volatility_ok"] = (
            (dataframe["atr_ratio"] >= float(self.atr_ratio_min.value))
            & (dataframe["atr_ratio"] <= float(self.atr_ratio_max.value))
        ).astype(int)
        dataframe["volume_ok"] = (
            dataframe["volume"] > dataframe["volume_mean"] * float(self.volume_factor.value)
        ).astype(int)
        dataframe["market_regime_ok"] = (
            (dataframe["regime_4h_bull"] == 1)
            & (dataframe["trend_strength_1h"] == 1)
            & (dataframe["volatility_ok"] == 1)
            & (dataframe["volume_ok"] == 1)
        ).astype(int)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Create vectorized long entry signals for breakout and pullback modules.
        """
        dataframe["enter_long"] = 0
        dataframe["enter_tag"] = None

        regime_ok = dataframe["market_regime_ok"] == 1
        trend_stack = dataframe["trend_stack"] == 1
        rsi_ok = dataframe["rsi"].between(int(self.rsi_lower.value), int(self.rsi_upper.value))
        not_too_extended = (
            (dataframe["distance_over_ema20"] <= dataframe["atr_ratio"] * float(self.chase_atr_limit.value))
            & (dataframe["distance_to_bb_upper"] >= -float(self.bb_extension_limit.value))
        )

        breakout_entry = (
            regime_ok
            & trend_stack
            & rsi_ok
            & not_too_extended
            & (dataframe["breakout_trigger"] == 1)
        )

        tolerance = float(self.pullback_tolerance.value)
        near_pullback_zone = (
            self._safe_series((dataframe["close"] - dataframe["ema_20"]).abs() / dataframe["close"]) <= tolerance
        ) | (
            self._safe_series((dataframe["close"] - dataframe["donchian_mid"]).abs() / dataframe["close"]) <= tolerance
        )

        pullback_reclaim = (
            (dataframe["close"] > dataframe["ema_20"])
            & (dataframe["close"] > dataframe["open"])
            & (dataframe["volume"] > dataframe["volume_mean"] * float(self.volume_factor.value))
            & (dataframe["close"] > dataframe["close"].shift(1))
        )

        structure_intact = dataframe["low"] > dataframe["structure_low"] * (1.0 - tolerance)

        pullback_entry = (
            regime_ok
            & trend_stack
            & (dataframe["recent_breakout"] == 1)
            & near_pullback_zone
            & structure_intact
            & pullback_reclaim
        )

        if not bool(self.enable_pullback_module.value):
            pullback_entry = pd.Series(False, index=dataframe.index)

        dataframe.loc[breakout_entry, "enter_long"] = 1
        dataframe.loc[breakout_entry, "enter_tag"] = "breakout"

        pullback_only = pullback_entry & ~breakout_entry
        dataframe.loc[pullback_only, "enter_long"] = 1
        dataframe.loc[pullback_only, "enter_tag"] = "pullback"

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Keep vectorized exits light and reserve stateful logic for custom_exit.
        """
        dataframe["exit_long"] = 0
        dataframe["exit_tag"] = None

        base_exit = (dataframe["close"] < dataframe["ema_50"]) & (dataframe["rsi"] < int(self.momentum_exit_rsi.value))
        dataframe.loc[base_exit, "exit_long"] = 1
        dataframe.loc[base_exit, "exit_tag"] = "signal_trend_fail"

        return dataframe

    def _get_analyzed_candle(self, pair: str, current_time: datetime) -> Series | None:
        """
        Fetch the latest analyzed candle aligned to the current trade callback time.
        """
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        candle_time = timeframe_to_prev_date(self.timeframe, current_time)
        candle_df = dataframe.loc[dataframe["date"] == candle_time]
        if candle_df.empty:
            return dataframe.iloc[-1]
        return candle_df.iloc[-1]

    def _get_trade_open_candle(self, pair: str, trade: Trade) -> Series | None:
        """
        Fetch the candle corresponding to the trade open time for stable per-trade references.
        """
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        trade_date = timeframe_to_prev_date(self.timeframe, trade.open_date_utc)
        candle_df = dataframe.loc[dataframe["date"] == trade_date]
        if candle_df.empty:
            earlier = dataframe.loc[dataframe["date"] <= trade_date]
            if earlier.empty:
                return None
            return earlier.iloc[-1]
        return candle_df.iloc[-1]

    def _stake_balance(self) -> float:
        """
        Return current total stake-currency equity with safe fallbacks.
        """
        stake_currency = self.config.get("stake_currency", "USDT")

        try:
            if self.wallets:
                total = float(self.wallets.get_total(stake_currency))
                if total > 0:
                    return total
        except Exception:
            pass

        dry_run_wallet = self.config.get("dry_run_wallet", 10000)
        if isinstance(dry_run_wallet, dict):
            total = float(dry_run_wallet.get(stake_currency, 10000))
            if total > 0:
                return total
        try:
            return float(dry_run_wallet)
        except Exception:
            return 10000.0

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs: Any,
    ) -> float:
        """
        Size positions from risk budget and ATR-based initial stop distance.
        """
        if side != "long":
            return 0.0

        candle = self._get_analyzed_candle(pair, current_time)
        if candle is None:
            return proposed_stake

        atr = float(candle.get("atr", 0.0))
        if atr <= 0 or current_rate <= 0:
            return proposed_stake

        equity = self._stake_balance()
        risk_budget = equity * float(self.risk_per_trade.value)
        stop_distance_ratio = (atr * float(self.initial_atr_stop_mult.value)) / current_rate

        if stop_distance_ratio <= 0:
            return proposed_stake

        raw_stake = risk_budget / stop_distance_ratio
        exposure_cap = equity * float(self.max_pair_exposure_pct.value)
        min_cap = equity * float(self.min_position_size_pct.value)
        max_cap = equity * float(self.max_position_size_pct.value)

        stake = min(raw_stake, exposure_cap, max_cap, max_stake)
        stake = max(stake, min_cap)

        if min_stake is not None:
            stake = max(stake, float(min_stake))

        stake = min(stake, max_stake)

        if not np.isfinite(stake) or stake <= 0:
            return proposed_stake

        return float(stake)

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs: Any,
    ) -> float | None:
        """
        Manage stoploss in layers with ATR and swing-low logic.
        """
        candle = self._get_analyzed_candle(pair, current_time)
        open_candle = self._get_trade_open_candle(pair, trade)
        if candle is None or open_candle is None or current_rate <= 0:
            return None

        entry_atr = float(open_candle.get("atr", 0.0))
        live_atr = float(candle.get("atr", 0.0))
        swing_low = float(candle.get("swing_low", np.nan))
        if entry_atr <= 0:
            return None

        initial_abs_stop = trade.open_rate - entry_atr * float(self.initial_atr_stop_mult.value)
        initial_risk = max(trade.open_rate - initial_abs_stop, trade.open_rate * 0.002)
        one_r_profit = initial_risk / trade.open_rate

        if after_fill:
            return stoploss_from_absolute(
                initial_abs_stop,
                current_rate=current_rate,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )

        if current_profit < float(self.breakeven_r_multiple.value) * one_r_profit:
            return stoploss_from_absolute(
                initial_abs_stop,
                current_rate=current_rate,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )

        breakeven_buffer = max(entry_atr * 0.15, trade.open_rate * 0.001)
        breakeven_stop = trade.open_rate + breakeven_buffer
        desired_stop = breakeven_stop

        if current_profit >= float(self.profit_lock_r_multiple.value) * one_r_profit and live_atr > 0:
            atr_trail_stop = current_rate - live_atr * float(self.atr_trail_mult.value)
            desired_stop = max(desired_stop, atr_trail_stop)

        if np.isfinite(swing_low) and swing_low > 0:
            desired_stop = max(desired_stop, swing_low - live_atr * 0.25)

        desired_stop = min(desired_stop, current_rate * 0.995)

        if desired_stop <= 0:
            return None

        if desired_stop <= trade.open_rate and current_profit > 0:
            return stoploss_from_open(
                0.0,
                current_profit=current_profit,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )

        return stoploss_from_absolute(
            desired_stop,
            current_rate=current_rate,
            is_short=trade.is_short,
            leverage=trade.leverage,
        )

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs: Any,
    ) -> str | None:
        """
        Use state-aware exits for momentum decay, time stop, and optional volatility climax.
        """
        candle = self._get_analyzed_candle(pair, current_time)
        if candle is None:
            return None

        timeframe_minutes = timeframe_to_minutes(self.timeframe)
        bars_held = max(int((current_time - trade.open_date_utc).total_seconds() // 60 // timeframe_minutes), 0)

        rsi = float(candle.get("rsi", np.nan))
        close_price = float(candle.get("close", current_rate))
        ema20 = float(candle.get("ema_20", np.nan))
        volume_ratio = float(candle.get("volume_ratio", 0.0))
        upper_wick_ratio = float(candle.get("upper_wick_ratio", 0.0))

        if np.isfinite(rsi) and np.isfinite(ema20):
            if rsi < int(self.momentum_exit_rsi.value) and close_price < ema20 and current_profit > -0.01:
                return "momentum_exit"

        if bars_held >= int(self.timeout_bars.value) and current_profit < float(self.timeout_min_profit.value):
            return "timeout_exit"

        if bool(self.volatility_exit_enabled.value):
            if (
                current_profit > 0.01
                and upper_wick_ratio >= float(self.volatility_exit_wick_ratio.value)
                and volume_ratio >= float(self.volatility_exit_volume_mult.value)
                and close_price < float(candle.get("high", current_rate))
            ):
                return "volatility_exit"

        regime_4h_bull = int(candle.get("regime_4h_bull", 1))
        if regime_4h_bull == 0 and current_profit > 0:
            return "regime_exit"

        return None
