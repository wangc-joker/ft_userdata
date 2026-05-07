"""Top-level strategy defaults extracted from NostalgiaForInfinityX7.

This module is documentation-like code for the refactor stage. The parity
adapter still inherits the original strategy directly, so these constants do
not change trading behavior yet.
"""

STOPLOSS = -0.99

TIMEFRAME = "5m"
INFO_TIMEFRAMES = ["15m", "1h", "4h", "1d"]
BTC_INFO_TIMEFRAMES = ["5m", "15m", "1h", "4h", "1d"]
STARTUP_CANDLE_COUNT = 800

HAS_BACKTEST_AGE_FILTER = False
BACKTEST_MIN_AGE_DAYS = 3
HAS_DOWNTIME_PROTECTION = False
HOLD_SUPPORT_ENABLED = True

PROCESS_ONLY_NEW_CANDLES = True
USE_EXIT_SIGNAL = True
EXIT_PROFIT_ONLY = False
IGNORE_ROI_IF_ENTRY_SIGNAL = True

IS_FUTURES_MODE = False
FUTURES_MODE_LEVERAGE = 3.0
FUTURES_MODE_LEVERAGE_REBUY_MODE = 3.0
FUTURES_MODE_LEVERAGE_GRIND_MODE = 3.0

PROFIT_MAX_THRESHOLDS = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.05, 0.05]
MAX_SLIPPAGE = 0.01
