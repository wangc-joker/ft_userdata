from freqtrade.strategy import informative
from pandas import DataFrame

from CombinedTrendCaptureMilestoneV2Top8ZecScaledBase import (
    CombinedTrendCaptureMilestoneV2Top8ZecScaledBase,
)


class CombinedTrendCaptureMilestoneV2Top8Zec15m6hStrategy(
    CombinedTrendCaptureMilestoneV2Top8ZecScaledBase
):
    timeframe = "15m"
    startup_candle_count = 960
    higher_timeframe = "6h"
    higher_suffix = "_6h"
    base_tag = "15m"
    higher_tag = "6h"

    stake_multipliers = {
        "long_6h_center_compression": 1.35,
        "short_6h_center_compression": 1.15,
        "short_15m_center": 0.80,
    }

    @informative("6h")
    def populate_indicators_6h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)
