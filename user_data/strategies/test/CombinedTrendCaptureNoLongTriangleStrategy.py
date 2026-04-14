from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pandas import DataFrame

from test.CombinedTrendCaptureOptStrategy import CombinedTrendCaptureOptStrategy
from signals.filters import remove_long_triangle_entries


class CombinedTrendCaptureNoLongTriangleStrategy(CombinedTrendCaptureOptStrategy):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return remove_long_triangle_entries(dataframe)
