from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from entrypoints.top9_main import Top9RegimeMainStrategy as _Top9RegimeMainStrategy


class Top9RegimeMainStrategy(_Top9RegimeMainStrategy):
    pass
