from pandas import DataFrame

from freqtrade.strategy import BooleanParameter, IntParameter

from DoubleShunStrategy import DoubleShunStrategy
from signals.exit_rules import resolve_custom_exit
from signals.long.entries import apply_long_entry_signals
from signals.short.entries import apply_short_entry_signals


class CombinedTrendCaptureOptStrategy(DoubleShunStrategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
    }

    enable_long_1h_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_long_1d_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_long_1d_center = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1h_center = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1h_compression = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1d_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1d_center = BooleanParameter(default=True, space="buy", optimize=True)

    hourly_long_rsi = IntParameter(48, 62, default=52, space="buy", optimize=True)
    daily_long_rsi = IntParameter(50, 65, default=55, space="buy", optimize=True)
    daily_short_rsi = IntParameter(35, 50, default=45, space="buy", optimize=True)

    cooldown_candles = IntParameter(2, 8, default=4, space="protection", optimize=True)
    stop_guard_lookback = IntParameter(24, 72, default=48, space="protection", optimize=True)
    stop_guard_duration = IntParameter(6, 18, default=12, space="protection", optimize=True)
    maxdd_lookback = IntParameter(48, 144, default=96, space="protection", optimize=True)
    maxdd_duration = IntParameter(12, 36, default=24, space="protection", optimize=True)

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": int(self.cooldown_candles.value),
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": int(self.stop_guard_lookback.value),
                "trade_limit": 2,
                "stop_duration_candles": int(self.stop_guard_duration.value),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.maxdd_lookback.value),
                "trade_limit": 10,
                "stop_duration_candles": int(self.maxdd_duration.value),
                "max_allowed_drawdown": 0.10,
            },
        ]

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = apply_long_entry_signals(self, dataframe, metadata)
        dataframe = apply_short_entry_signals(self, dataframe, metadata)
        return dataframe

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        return resolve_custom_exit(
            self,
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )
