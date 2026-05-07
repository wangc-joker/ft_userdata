import talib.abstract as ta
from pandas import DataFrame

from alpha_modules.signal_base import SignalModule


class DowntrendBounceShortSignal(SignalModule):
    """Shorts weak bounces inside an established downtrend."""

    name = "downtrend_bounce_short"
    version = "0.1.0"
    entry_tag = "alpha_downtrend_bounce_short_v1"
    long_signal_column = "signal_downtrend_bounce_long"
    short_signal_column = "signal_downtrend_bounce_short"
    score_column = "signal_downtrend_bounce_short_score"
    priority = 100
    min_score = 60

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["db_rsi_fast"] = ta.RSI(dataframe, timeperiod=7)
        dataframe["db_bounce_height"] = (dataframe["close"] - dataframe["ema_20"]) / dataframe["close"]
        dataframe["db_volume_pressure"] = dataframe["volume"] / dataframe["volume_mean_30"]
        return dataframe

    def generate_entry(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe[self.long_signal_column] = 0
        dataframe[self.short_signal_column] = (
            (dataframe["close"] < dataframe["ema_50"])
            & (dataframe["close"] > dataframe["ema_20"])
            & (dataframe["db_bounce_height"] > 0.002)
            & (dataframe["db_bounce_height"] < 0.035)
            & (dataframe["rsi_14"] > 42)
            & (dataframe["rsi_14"] < 62)
            & (dataframe["db_rsi_fast"] > 55)
            & (dataframe["db_volume_pressure"] > 0.65)
        ).astype(int)
        dataframe[self.score_column] = (
            20
            + ((dataframe["db_bounce_height"] > 0.006) & (dataframe["db_bounce_height"] < 0.022)).astype(int) * 20
            + ((dataframe["rsi_14"] > 46) & (dataframe["rsi_14"] < 58)).astype(int) * 15
            + (dataframe["db_rsi_fast"] > 62).astype(int) * 10
            + (dataframe["db_volume_pressure"] > 1.0).astype(int) * 15
            + (dataframe["alpha_short_quality_score"] >= 5).astype(int) * 10
            + (dataframe["alpha_short_quality_score"] >= 6).astype(int) * 10
        )
        return dataframe

    def explain(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "idea": "Enter short when a coin remains in a downtrend but bounces toward EMA20 without reclaiming EMA50.",
            "market": "Best suited for bearish BTC regimes where weak rallies often fade.",
            "risk": "Can be squeezed during sharp relief rallies; market-bias quality gates must stay strict.",
        }
