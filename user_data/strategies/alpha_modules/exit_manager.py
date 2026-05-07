from datetime import datetime
from typing import Optional

from freqtrade.persistence import Trade
from pandas import DataFrame


class ExitManager:
    """Shared exit logic for the first Alpha strategy version."""

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["alpha_exit_trend_break"] = (
            (dataframe["close"] < dataframe["ema_50"])
            & (dataframe["rsi_14"] < 45)
        ).astype(int)
        dataframe["alpha_exit_short_trend_break"] = (
            (dataframe["close"] > dataframe["ema_50"])
            & (dataframe["rsi_14"] > 55)
        ).astype(int)
        return dataframe

    def vector_long_exit_mask(self, dataframe: DataFrame):
        return (
            (dataframe["alpha_exit_trend_break"] == 1)
            | (dataframe["rsi_14"] > 76)
        )

    def vector_short_exit_mask(self, dataframe: DataFrame):
        return (
            (dataframe["alpha_exit_short_trend_break"] == 1)
            | (dataframe["rsi_14"] < 24)
        )

    def vector_exit_mask(self, dataframe: DataFrame):
        return self.vector_long_exit_mask(dataframe)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        state_store,
    ) -> Optional[str]:
        held_minutes = (current_time.replace(tzinfo=None) - trade.open_date_utc.replace(tzinfo=None)).total_seconds() / 60

        if current_profit >= 0.08:
            state_store.set_pair_state(pair, "profit_seen", current_profit)
            return "alpha_profit_take_8"

        if current_profit >= 0.035 and held_minutes >= 360:
            return "alpha_time_profit_take"

        if current_profit <= -0.04 and held_minutes >= 720:
            return "alpha_time_stop"

        return None
