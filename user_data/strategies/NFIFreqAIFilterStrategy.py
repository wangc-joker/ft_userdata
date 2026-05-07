import logging

import talib.abstract as ta
import pandas as pd

from NFIRefactorStrategy import NFIRefactorStrategy


log = logging.getLogger(__name__)


class NFIFreqAIFilterStrategy(NFIRefactorStrategy):
    """
    在纯 NFI 重构版（NFIRefactorStrategy）基础上叠加 FreqAI 入场过滤。

    AI 角色（仅过滤，不生成信号）：
        对每个 NFI 入场候选，预测未来 label_period_candles 根 K 线内的
        最大盈利幅度。若预测盈利 < 动态阈值，则跳过该入场。

    关闭 AI：
        移除 config 中的 freqai.enabled 即可回退到纯 NFI 行为。
    """

    # ---- FreqAI 特征工程入口 ----

    def feature_engineering_expand_all(self, dataframe, period, metadata):
        """
        展开特征：每对 (timeframe, indicator_period) 都会调用一次。

        放入不需要先验知识的基础技术指标。
        """
        dataframe["%-rsi"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-mfi"] = ta.MFI(dataframe, timeperiod=period)
        dataframe["%-adx"] = ta.ADX(dataframe, timeperiod=period)
        dataframe["%-cci"] = ta.CCI(dataframe, timeperiod=period)
        dataframe["%-roc"] = ta.ROC(dataframe, timeperiod=period)
        dataframe["%-willr"] = ta.WILLR(dataframe, timeperiod=period)
        dataframe["%-fastd"] = ta.STOCHRSI(dataframe, timeperiod=period)[
            "fastd"
        ] if "STOCHRSI" in dir(ta) else 50.0
        dataframe["%-ema_diff"] = (
            dataframe["close"] - ta.EMA(dataframe, timeperiod=period)
        ) / dataframe["close"].replace(0, float("nan"))
        bb = ta.BBANDS(dataframe, timeperiod=period)
        bbp = (dataframe["close"] - bb["lowerband"]) / (
            bb["upperband"] - bb["lowerband"]
        ).replace(0, float("nan"))
        dataframe["%-bb_position"] = bbp
        return dataframe

    def feature_engineering_standard(self, dataframe, metadata):
        """
        非展开特征：每个 pair/timeframe 只调用一次。

        放入已有的 NFI 风控列——让 AI 学习规则层信号和市场状态。
        """
        for col in [
            "protections_long_global",
            "protections_short_global",
            "num_empty_288",
        ]:
            if col in dataframe.columns:
                dataframe["%-" + col] = dataframe[col].fillna(0).astype(float)
        return dataframe

    # ---- FreqAI 标签定义 ----

    def set_freqai_targets(self, dataframe, metadata):
        """
        训练标签：未来 label_period_candles 根 K 线内的最大收益率。

        label = max(未来窗口最高价) / 当前收盘价 - 1

        模型学习：当前市场状态下，价格短期上冲空间有多大。
        """
        label_period = self.freqai_info.get("feature_parameters", {}).get(
            "label_period_candles", 48
        )
        future_high = dataframe["high"].rolling(window=label_period).max().shift(-label_period)
        dataframe["&-s_trade_return"] = (future_high / dataframe["close"]) - 1
        return dataframe

    # ---- 指标管线（加入 FreqAI 入口）----

    def populate_indicators(self, df, metadata: dict):
        df = super().populate_indicators(df, metadata)
        if not self.config.get("freqai", {}).get("enabled", False):
            return df
        df = self.freqai.start(df, metadata, self)
        return df

    # ---- 入场管线（叠加 AI 过滤）----

    def populate_entry_trend(self, df, metadata: dict):
        df = super().populate_entry_trend(df, metadata)
        if not self.config.get("freqai", {}).get("enabled", False):
            return df

        # 只过滤 LONG 入场（short 暂不处理）
        long_mask = df["enter_long"] == 1
        if not long_mask.any():
            return df

        # 逐根过滤有入场信号的 K 线
        for idx in df.index[long_mask]:
            if not self._freqai_entry_ok(df, idx):
                df.loc[idx, "enter_long"] = 0
                df.loc[idx, "enter_tag"] = ""
                log.debug(
                    "AI filtered: %s bar=%s pred_return=%.4f threshold=%.4f",
                    metadata.get("pair", "?"),
                    idx,
                    self._pred_at(df, idx),
                    self._ai_min_return(),
                )

        return df

    # ---- 内部过滤逻辑 ----

    def _pred_column(self) -> str:
        """FreqAI 预测列名，与 set_freqai_targets 中的标签名对应。"""
        return "&-s_trade_return"

    def _pred_at(self, df, idx) -> float:
        val = df.loc[idx, self._pred_column()]
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        try:
            val = float(val)
            if val != val:
                return None
            return val
        except (TypeError, ValueError):
            return None

    def _ai_min_return(self) -> float:
        """动态阈值：训练集均值 - 1.0 * 标准差。"""
        dk = getattr(self.freqai, "dk", None)
        if dk is None or dk.data is None:
            return 0.005  # 保守默认 0.5%
        mean = float(dk.data.get(self._pred_column() + "_mean", 0.01))
        std = float(dk.data.get(self._pred_column() + "_std", 0.02))
        return max(mean - 1.0 * std, 0.0)

    def _freqai_entry_ok(self, df, idx) -> bool:
        """
        判断 index=idx 处 NFI 产生的入场信号是否通过 AI 过滤。
        """
        do_predict = df.loc[idx, "do_predict"]
        if isinstance(do_predict, pd.Series):
            do_predict = do_predict.iloc[0]
        try:
            do_predict = int(do_predict)
        except (TypeError, ValueError):
            do_predict = 1

        if do_predict == 0:
            # 超出训练分布 → 不拦截，信任 NFI
            return True

        pred = self._pred_at(df, idx)
        if pred is None:
            # FreqAI 尚未输出预测（训练未完成）→ 不拦截
            return True

        return pred > self._ai_min_return()

    # ---- 版本 ----

    def version(self) -> str:
        return "nfi-refactor-freqai-filter-v0.1.0"
