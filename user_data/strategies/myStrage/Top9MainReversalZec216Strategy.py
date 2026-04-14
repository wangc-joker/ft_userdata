from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from entrypoints.top9_reversal_216 import (
    Top9RegimeMainReversal216Strategy as _Top9RegimeMainReversal216Strategy,
)


class Top9RegimeMainReversal216Strategy(_Top9RegimeMainReversal216Strategy):
    pass
