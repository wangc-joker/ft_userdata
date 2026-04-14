from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from entrypoints.top9_reversal_216_nolong_aggressive import (
    Top9RegimeMainReversal216NoLongAggressiveStrategy as _Top9RegimeMainReversal216NoLongAggressiveStrategy,
)


class Top9RegimeMainReversal216NoLongAggressiveStrategy(
    _Top9RegimeMainReversal216NoLongAggressiveStrategy
):
    pass
