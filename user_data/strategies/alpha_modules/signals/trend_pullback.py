import talib.abstract as ta
from pandas import DataFrame

from alpha_modules.signal_base import SignalModule


class TrendPullbackSignal(SignalModule):
    """Buys controlled pullbacks inside an existing uptrend."""

    name = "trend_pullback"
    version = "0.1.0"
    entry_tag = "alpha_trend_pullback_v1"
    long_signal_column = "signal_trend_pullback_long"
    short_signal_column = "signal_trend_pullback_short"
    score_column = "signal_trend_pullback_score"
    priority = 100
    min_score = 0

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["tp_rsi_3"] = ta.RSI(dataframe, timeperiod=3)
        dataframe["tp_rsi_fast"] = ta.RSI(dataframe, timeperiod=7)
        dataframe["tp_pullback_depth"] = (dataframe["ema_20"] - dataframe["close"]) / dataframe["close"]
        dataframe["tp_volume_pressure"] = dataframe["volume"] / dataframe["volume_mean_30"]
        return dataframe

    def generate_entry(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe[self.short_signal_column] = 0
        dataframe[self.long_signal_column] = (
            (dataframe["close"] > dataframe["ema_50"])
            & (dataframe["close"] < dataframe["ema_20"])
            & (dataframe["tp_pullback_depth"] > 0.002)
            & (dataframe["tp_pullback_depth"] < 0.035)
            & (dataframe["rsi_14"] > 38)
            & (dataframe["rsi_14"] < 58)
            & (dataframe["tp_rsi_fast"] < 45)
            & (dataframe["tp_volume_pressure"] > 0.65)
        ).astype(int)
        dataframe[self.score_column] = (
            20
            + ((dataframe["tp_pullback_depth"] > 0.006) & (dataframe["tp_pullback_depth"] < 0.022)).astype(int) * 20
            + ((dataframe["rsi_14"] > 42) & (dataframe["rsi_14"] < 54)).astype(int) * 15
            + (dataframe["tp_rsi_fast"] < 38).astype(int) * 10
            + (dataframe["pair_rsi_14_15m"] > 45).astype(int) * 10
            + (dataframe["pair_close_15m"] > dataframe["pair_ema_50_15m"]).astype(int) * 10
            + (dataframe["tp_volume_pressure"] > 1.0).astype(int) * 15
            + (dataframe["alpha_trend_quality_score"] >= 5).astype(int) * 10
            + (dataframe["alpha_trend_quality_score"] >= 6).astype(int) * 10
        )
        return dataframe

    def explain(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "idea": "Enter long when a coin remains in an uptrend but pulls back toward EMA20 without breaking EMA50.",
            "market": "Best suited for liquid coins in bullish or constructive regimes.",
            "risk": "Can fail during fast trend reversals; shared risk filters should block high-volatility breaks.",
        }
