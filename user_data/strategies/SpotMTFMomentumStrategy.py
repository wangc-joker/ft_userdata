from datetime import timedelta
from typing import Optional

import pandas as pd
from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, informative


class SpotMTFMomentumStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count = 250

    minimal_roi = {"0": 10.0}
    stoploss = -0.025

    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    @property
    def protections(self):
        return [
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 200,
                "trade_limit": 20,
                "stop_duration_candles": 48,
                "max_allowed_drawdown": 0.10,
            },
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            },
        ]

    @staticmethod
    def _crossed_above(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
        return (series_a > series_b) & (series_a.shift(1) <= series_b.shift(1))

    @staticmethod
    def _crossed_below(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
        return (series_a < series_b) & (series_a.shift(1) >= series_b.shift(1))

    @informative("4h")
    def populate_indicators_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_ratio"] = dataframe["atr"] / dataframe["close"]
        dataframe["volume_mean"] = dataframe["volume"].rolling(20).mean()
        dataframe["recent_high"] = dataframe["high"].shift(1).rolling(12).max()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        long_signal = (
            self._crossed_above(dataframe["ema_20"], dataframe["ema_50"])
            & (dataframe["close_4h"] > dataframe["ema_50_4h"])
            & (dataframe["ema_50_4h"] > dataframe["ema_50_4h"].shift(3))
            & (dataframe["close"] > dataframe["ema_200"])
            & (dataframe["ema_50"] > dataframe["ema_200"])
            & dataframe["rsi"].between(52, 65)
            & (dataframe["adx"] > 20)
            & dataframe["atr_ratio"].between(0.005, 0.04)
            & (dataframe["volume"] > dataframe["volume_mean"])
            & (dataframe["close"] > dataframe["recent_high"])
            & (dataframe["volume"] > 0)
        )

        dataframe.loc[long_signal, ["enter_long", "enter_tag"]] = (1, "mtf_momentum_long")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        exit_signal = (
            (
                self._crossed_below(dataframe["ema_20"], dataframe["ema_50"])
                | (dataframe["close_4h"] < dataframe["ema_50_4h"])
            )
            & (dataframe["volume"] > 0)
        )
        dataframe.loc[exit_signal, "exit_long"] = 1
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
        if trade.open_date_utc and current_time - trade.open_date_utc >= timedelta(hours=48):
            return "time_stop_48h"
        return None

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        closed_trades = [
            trade
            for trade in Trade.get_trades_proxy(is_open=False)
            if trade.close_date_utc and trade.close_date_utc <= current_time
        ]
        closed_trades.sort(key=lambda trade: trade.close_date_utc, reverse=True)

        kelly_fraction = 0.50
        sample = closed_trades[:20]
        if len(sample) >= 10:
            wins = [trade.close_profit for trade in sample if trade.close_profit and trade.close_profit > 0]
            losses = [abs(trade.close_profit) for trade in sample if trade.close_profit and trade.close_profit < 0]
            if wins and losses:
                win_rate = len(wins) / len(sample)
                avg_win = sum(wins) / len(wins)
                avg_loss = sum(losses) / len(losses)
                payoff = avg_win / avg_loss if avg_loss else 0.0
                edge = win_rate - ((1 - win_rate) / payoff) if payoff > 0 else 0.0
                kelly_fraction = min(0.75, max(0.25, edge * 0.5))

        last_three = sample[:3]
        loss_streak = len(last_three) == 3 and all((trade.close_profit or 0) < 0 for trade in last_three)

        risk_cap_stake = min(max_stake, proposed_stake * 4.0)
        stake = min(proposed_stake * kelly_fraction, risk_cap_stake, max_stake)

        if loss_streak:
            stake *= 0.5

        if min_stake is not None:
            stake = max(stake, min_stake)

        return min(stake, max_stake)
