from pandas import DataFrame


class MarketRegime:
    """Classifies the current pair trend using simple, explainable features."""

    def add_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["alpha_regime_bull"] = (
            (dataframe["close"] > dataframe["ema_200"])
            & (dataframe["ema_50"] > dataframe["ema_200"])
        ).astype(int)

        dataframe["alpha_regime_bear"] = (
            (dataframe["close"] < dataframe["ema_200"])
            & (dataframe["ema_50"] < dataframe["ema_200"])
        ).astype(int)

        dataframe["alpha_regime_trend_ok"] = (
            (dataframe["ema_20"] > dataframe["ema_50"])
            & (dataframe["close"] > dataframe["ema_50"])
        ).astype(int)

        dataframe["alpha_regime_downtrend_ok"] = (
            (dataframe["ema_20"] < dataframe["ema_50"])
            & (dataframe["close"] < dataframe["ema_50"])
        ).astype(int)

        dataframe["alpha_regime_volatility"] = (
            dataframe["atr_14"] / dataframe["close"]
        )

        return dataframe

    def add_market_context(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        btc_ok = dataframe.get("btc_regime_ok_1h")

        if btc_ok is None:
            dataframe["btc_regime_ok_1h"] = 1
        if "btc_regime_ok_4h" not in dataframe.columns:
            dataframe["btc_regime_ok_4h"] = dataframe["btc_regime_ok_1h"]

        dataframe["btc_regime_ok_1h"] = dataframe["btc_regime_ok_1h"].fillna(0)
        dataframe["btc_regime_ok_4h"] = dataframe["btc_regime_ok_4h"].fillna(0)

        if "btc_bear_regime_1h" not in dataframe.columns:
            dataframe["btc_bear_regime_1h"] = 0
        if "btc_bear_regime_4h" not in dataframe.columns:
            dataframe["btc_bear_regime_4h"] = dataframe["btc_bear_regime_1h"]

        dataframe["btc_bear_regime_1h"] = dataframe["btc_bear_regime_1h"].fillna(0)
        dataframe["btc_bear_regime_4h"] = dataframe["btc_bear_regime_4h"].fillna(0)

        dataframe["alpha_market_ok"] = (
            (dataframe["btc_regime_ok_1h"] == 1)
            & (dataframe["btc_regime_ok_4h"] == 1)
        ).astype(int)

        dataframe["alpha_market_bias"] = 0
        dataframe.loc[
            (dataframe["btc_regime_ok_1h"] == 1)
            & (dataframe["btc_regime_ok_4h"] == 1),
            "alpha_market_bias",
        ] = 1
        dataframe.loc[
            (dataframe["btc_bear_regime_1h"] == 1)
            & (dataframe["btc_bear_regime_4h"] == 1),
            "alpha_market_bias",
        ] = -1

        dataframe["alpha_btc_panic"] = (
            (dataframe.get("btc_roc_3_1h", 0) < -0.035)
            | (dataframe.get("btc_roc_12_1h", 0) < -0.08)
            | (dataframe.get("btc_roc_3_4h", 0) < -0.06)
        ).astype(int)

        dataframe["alpha_btc_stress"] = (
            (dataframe["alpha_btc_panic"] == 1)
            | (dataframe["btc_regime_ok_1h"] == 0)
            | (dataframe["btc_regime_ok_4h"] == 0)
        ).astype(int)

        dataframe["alpha_long_market_weight"] = 0.65
        dataframe.loc[dataframe["alpha_market_bias"] == 1, "alpha_long_market_weight"] = 1.0
        dataframe.loc[dataframe["alpha_market_bias"] == -1, "alpha_long_market_weight"] = 0.35

        dataframe["alpha_short_market_weight"] = 0.65
        dataframe.loc[dataframe["alpha_market_bias"] == -1, "alpha_short_market_weight"] = 1.0
        dataframe.loc[dataframe["alpha_market_bias"] == 1, "alpha_short_market_weight"] = 0.35

        return dataframe
