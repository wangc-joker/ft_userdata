from pandas import DataFrame


class RiskManager:
    """Centralized filters shared by all entry signals."""

    max_atr_ratio = 0.08
    min_trend_quality_score = 5

    def add_filters(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["alpha_liquidity_ok"] = (
            dataframe["volume"] > (dataframe["volume_mean_30"] * 0.5)
        ).astype(int)

        dataframe["alpha_volatility_ok"] = (
            dataframe["alpha_regime_volatility"] < self.max_atr_ratio
        ).astype(int)

        dataframe["alpha_pair_drop_1h"] = dataframe["close"] / dataframe["close"].shift(12) - 1
        dataframe["alpha_pair_drop_4h"] = dataframe["close"] / dataframe["close"].shift(48) - 1
        dataframe["alpha_pair_panic_guard"] = (
            (dataframe["alpha_pair_drop_1h"] > -0.06)
            & (dataframe["alpha_pair_drop_4h"] > -0.14)
        ).astype(int)

        dataframe["alpha_red_volume_spike_guard"] = (
            ~(
                (dataframe["close"] < dataframe["open"])
                & (dataframe["volume"] > dataframe["volume_mean_30"] * 2.5)
                & (dataframe["close"] < dataframe["close"].shift(1) * 0.985)
            )
        ).astype(int)

        if "pair_context_ok_1h" not in dataframe.columns:
            dataframe["pair_context_ok_1h"] = 1

        dataframe["alpha_ema50_slope"] = (
            dataframe["ema_50"] - dataframe["ema_50"].shift(12)
        ) / dataframe["ema_50"].shift(12)

        dataframe["alpha_price_extension"] = (
            dataframe["close"] - dataframe["ema_200"]
        ) / dataframe["ema_200"]

        dataframe["alpha_trend_quality_score"] = (
            (dataframe["alpha_ema50_slope"] > 0.001).astype(int)
            + (dataframe["alpha_price_extension"] > 0.01).astype(int)
            + (dataframe["alpha_price_extension"] < 0.18).astype(int)
            + (dataframe["rsi_14"] > 42).astype(int)
            + (dataframe["rsi_14"] < 64).astype(int)
            + (dataframe["volume"] > dataframe["volume_mean_30"]).astype(int)
            + (dataframe["alpha_regime_volatility"] < 0.045).astype(int)
        )

        dataframe["alpha_trend_quality_ok"] = (
            dataframe["alpha_trend_quality_score"] >= self.min_trend_quality_score
        ).astype(int)

        dataframe["alpha_short_quality_score"] = (
            (dataframe["alpha_ema50_slope"] < -0.001).astype(int)
            + (dataframe["alpha_price_extension"] < -0.01).astype(int)
            + (dataframe["alpha_price_extension"] > -0.18).astype(int)
            + (dataframe["rsi_14"] > 36).astype(int)
            + (dataframe["rsi_14"] < 58).astype(int)
            + (dataframe["volume"] > dataframe["volume_mean_30"]).astype(int)
            + (dataframe["alpha_regime_volatility"] < 0.045).astype(int)
        )

        dataframe["alpha_long_required_quality"] = 6
        dataframe.loc[dataframe["alpha_market_bias"] == 1, "alpha_long_required_quality"] = 5
        dataframe.loc[dataframe["alpha_market_bias"] == -1, "alpha_long_required_quality"] = 7

        dataframe["alpha_short_required_quality"] = 6
        dataframe.loc[dataframe["alpha_market_bias"] == -1, "alpha_short_required_quality"] = 5
        dataframe.loc[dataframe["alpha_market_bias"] == 1, "alpha_short_required_quality"] = 7

        dataframe["alpha_trend_quality_ok"] = (
            dataframe["alpha_trend_quality_score"] >= dataframe["alpha_long_required_quality"]
        ).astype(int)

        dataframe["alpha_short_quality_ok"] = (
            dataframe["alpha_short_quality_score"] >= dataframe["alpha_short_required_quality"]
        ).astype(int)

        dataframe["alpha_allow_long"] = (
            (dataframe["alpha_regime_bull"] == 1)
            & (dataframe["alpha_regime_trend_ok"] == 1)
            & (dataframe["alpha_market_bias"] == 1)
            & (dataframe["alpha_btc_stress"] == 0)
            & (dataframe["alpha_liquidity_ok"] == 1)
            & (dataframe["alpha_volatility_ok"] == 1)
            & (dataframe["alpha_pair_panic_guard"] == 1)
            & (dataframe["alpha_red_volume_spike_guard"] == 1)
            & (dataframe["pair_context_ok_1h"] == 1)
            & (dataframe["alpha_trend_quality_ok"] == 1)
        ).astype(int)

        dataframe["alpha_allow_short"] = (
            (dataframe["alpha_regime_bear"] == 1)
            & (dataframe["alpha_regime_downtrend_ok"] == 1)
            & (dataframe["alpha_market_bias"] == -1)
            & (dataframe["alpha_liquidity_ok"] == 1)
            & (dataframe["alpha_volatility_ok"] == 1)
            & (dataframe["alpha_short_quality_ok"] == 1)
        ).astype(int)

        return dataframe
