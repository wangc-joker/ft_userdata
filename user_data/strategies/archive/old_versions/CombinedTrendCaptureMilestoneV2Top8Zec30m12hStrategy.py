from freqtrade.strategy import informative
from pandas import DataFrame

from CombinedTrendCaptureMilestoneV2Top8ZecScaledBase import (
    CombinedTrendCaptureMilestoneV2Top8ZecScaledBase,
)


class CombinedTrendCaptureMilestoneV2Top8Zec30m12hStrategy(
    CombinedTrendCaptureMilestoneV2Top8ZecScaledBase
):
    timeframe = "30m"
    startup_candle_count = 480
    higher_timeframe = "12h"
    higher_suffix = "_12h"
    base_tag = "30m"
    higher_tag = "12h"

    stake_multipliers = {
        "long_12h_center_compression": 1.35,
        "short_12h_center_compression": 1.15,
        "short_30m_center": 0.80,
    }

    @informative("12h")
    def populate_indicators_12h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)
