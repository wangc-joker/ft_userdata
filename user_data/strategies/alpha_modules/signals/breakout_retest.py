import talib.abstract as ta
from pandas import DataFrame

from alpha_modules.signal_base import SignalModule


class BreakoutRetestSignal(SignalModule):
    """Buys the first controlled retest after a high-volume breakout."""

    name = "breakout_retest"
    version = "0.1.0"
    entry_tag = "alpha_breakout_retest_v1"
    long_signal_column = "signal_breakout_retest_long"
    score_column = "signal_breakout_retest_score"
    priority = 80
    min_score = 0

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["br_rsi_fast"] = ta.RSI(dataframe, timeperiod=7)
        dataframe["br_prior_high_72"] = dataframe["high"].shift(1).rolling(72).max()
        dataframe["br_volume_pressure"] = dataframe["volume"] / dataframe["volume_mean_30"]
        dataframe["br_breakout_candle"] = (
            (dataframe["close"] > dataframe["br_prior_high_72"] * 1.003)
            & (dataframe["br_volume_pressure"] > 1.2)
            & (dataframe["rsi_14"] > 52)
            & (dataframe["rsi_14"] < 72)
        ).astype(int)
        dataframe["br_recent_breakout"] = dataframe["br_breakout_candle"].shift(1).rolling(18).max().fillna(0)
        dataframe["br_retest_depth"] = (dataframe["ema_20"] - dataframe["low"]) / dataframe["ema_20"]
        return dataframe

    def generate_entry(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe[self.long_signal_column] = (
            (dataframe["br_recent_breakout"] == 1)
            & (dataframe["close"] > dataframe["ema_20"])
            & (dataframe["low"] <= dataframe["ema_20"] * 1.01)
            & (dataframe["close"] > dataframe["ema_50"])
            & (dataframe["rsi_14"] > 48)
            & (dataframe["rsi_14"] < 68)
            & (dataframe["br_rsi_fast"] > 42)
            & (dataframe["br_volume_pressure"] > 0.7)
            & (dataframe["br_retest_depth"] < 0.025)
        ).astype(int)
        dataframe[self.score_column] = (
            20
            + (dataframe["br_volume_pressure"] > 1.0).astype(int) * 15
            + (dataframe["br_volume_pressure"] > 1.5).astype(int) * 10
            + ((dataframe["rsi_14"] > 52) & (dataframe["rsi_14"] < 64)).astype(int) * 15
            + (dataframe["br_retest_depth"] < 0.012).astype(int) * 15
            + (dataframe["alpha_trend_quality_score"] >= 5).astype(int) * 10
            + (dataframe["alpha_trend_quality_score"] >= 6).astype(int) * 15
        )
        return dataframe

    def explain(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "idea": "Enter long after a liquid coin breaks a recent range on volume, then retests EMA20 without losing EMA50.",
            "market": "Best suited for constructive BTC regimes where momentum coins rotate strongly.",
            "risk": "Can buy late if the breakout is exhausted; shared market and trend filters should block weak regimes.",
        }
