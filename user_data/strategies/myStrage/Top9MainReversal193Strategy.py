from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from entrypoints.top9_reversal_193 import (
    Top9RegimeMainReversalStrategy as _Top9RegimeMainReversalStrategy,
)


class Top9RegimeMainReversalStrategy(_Top9RegimeMainReversalStrategy):
    pass
