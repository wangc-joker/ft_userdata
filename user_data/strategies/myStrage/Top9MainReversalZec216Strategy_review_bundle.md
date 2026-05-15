# Top9MainReversalZec216Strategy review bundle

This is a single review document for external AI/code review. It is not intended to be executed directly.

## Backtest Snapshot

- Strategy class: `Top9RegimeMainReversal216Strategy`
- Start balance: `1000 USDT`
- max_open_trades: `2`
- Pairlist: `BTC/ETH/BNB/SOL/TRX/ADA/ZEC/XRP/DOGE`
- Timerange actually tested: `2023-05-14` to `2026-05-07 04:00`
- Protections enabled: `CooldownPeriod`, `StoplossGuard`, `MaxDrawdown`
- Total profit: `+203.69%`
- Final balance: `3036.950 USDT`
- Max account drawdown: `11.98%`
- Trades: `197`
- Winrate: `38.1%`
- Profit Factor: `2.28`

## Inheritance Chain

```text
Top9MainReversalZec216Strategy.py
  -> entrypoints.top9_reversal_216.Top9RegimeMainReversal216Strategy
  -> myStrage.Top9MainTrendStrategy.Top9RegimeMainStrategy
  -> entrypoints.top9_main.Top9RegimeMainStrategy
  -> CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy
  -> CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy
  -> CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
  -> CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy
  -> CombinedTrendCaptureMilestoneV2Top9RegimeStrategy
  -> CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy
  -> CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
  -> CombinedTrendCaptureMilestoneV2Top9Strategy
  -> CombinedTrendCaptureMilestoneV2Strategy
  -> CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy
  -> CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy
  -> CombinedTrendCaptureMilestoneV1Top8Strategy
  -> CombinedTrendCaptureMilestoneV1Strategy
  -> test.CombinedTrendCaptureNoLongTriangleStrategy
  -> test.CombinedTrendCaptureOptStrategy
  -> DoubleShunStrategy
```

## Source Files

### myStrage\Top9MainReversalZec216Strategy.py

```python
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

```

### myStrage\Top9MainReversalZec216Strategy.json

```json
{
  "strategy_name": "Top9RegimeMainReversal216Strategy",
  "params": {
    "buy": {
      "breakout_buffer": 0.009,
      "center_window": 5,
      "compression_limit": 0.006,
      "compression_window": 11,
      "daily_long_rsi": 55,
      "daily_short_rsi": 46,
      "enable_long_1d_center": true,
      "enable_long_1d_triangle": true,
      "enable_long_1h_triangle": true,
      "enable_short_1d_center": true,
      "enable_short_1d_triangle": false,
      "enable_short_1h_center": true,
      "enable_short_1h_compression": true,
      "hourly_long_rsi": 54,
      "level_proximity": 0.015,
      "level_tolerance": 0.016,
      "pullback_depth": 0.009,
      "pullback_window": 6,
      "restart_window": 4,
      "trend_ema_fast": 6,
      "trend_ema_slow": 46,
      "triangle_window": 5,
      "volume_multiplier": 1.13
    },
    "protection": {
      "cooldown_candles": 2,
      "maxdd_duration": 27,
      "maxdd_lookback": 65,
      "stop_guard_duration": 16,
      "stop_guard_lookback": 67
    },
    "sell": {
      "swing_window": 3
    },
    "roi": {
      "0": 0.1
    },
    "stoploss": {
      "stoploss": -0.02
    },
    "max_open_trades": {
      "max_open_trades": 3
    }
  }
}

```

### entrypoints\top9_reversal_216.py

```python
from pandas import DataFrame

from myStrage.Top9MainTrendStrategy import Top9RegimeMainStrategy
from shared.pair_groups import LONG_REVERSAL_PAIRS_216, SHORT_REVERSAL_PAIRS_216
from signals.reversal import apply_reversal_entry_signals, populate_reversal_indicators


class Top9RegimeMainReversal216Strategy(Top9RegimeMainStrategy):
    """
    Fixed historical 216.13% reversal version.

    This keeps the ZEC-only long breakout structure that produced the peak
    historical result, while using the broader short-reversal candidate pool.
    """

    reversal_tags = {
        "long_reversal_breakout",
        "short_reversal_breakdown",
    }

    long_reversal_pairs = LONG_REVERSAL_PAIRS_216
    short_reversal_pairs = SHORT_REVERSAL_PAIRS_216

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        return populate_reversal_indicators(dataframe, metadata["pair"])

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return apply_reversal_entry_signals(
            dataframe,
            metadata["pair"],
            self.long_reversal_pairs,
            self.short_reversal_pairs,
        )

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )
        if entry_tag == "long_reversal_breakout":
            stake *= 1.15
        elif entry_tag == "short_reversal_breakdown":
            stake *= 1.12
        return stake

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        if trade.enter_tag in self.reversal_tags and current_profit < 0.08:
            return None
        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )

```

### myStrage\Top9MainTrendStrategy.py

```python
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from entrypoints.top9_main import Top9RegimeMainStrategy as _Top9RegimeMainStrategy


class Top9RegimeMainStrategy(_Top9RegimeMainStrategy):
    pass

```

### entrypoints\top9_main.py

```python
from archive.old_versions.CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy as _Top9RegimeMainStrategy,
)


class Top9RegimeMainStrategy(_Top9RegimeMainStrategy):
    """
    Short alias for the current Top9 main strategy.

    This keeps the full parent chain intact while giving dry-run / backtesting
    a cleaner strategy name to use.
    """



```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy.py

```python
from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy,
)
from core.market_state.regime import classify_intraday_regime
from pairs.ada.trim import short_1h_center_multiplier as ada_short_multiplier
from pairs.doge.trim import short_1h_center_multiplier as doge_short_multiplier
from pairs.xrp.trim import short_1h_center_multiplier as xrp_short_multiplier


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStatePairShortsStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy
):
    """
    Keep the regime-aware hourly short sizing, then add small pair-specific trims
    for the weaker hourly short names.

    Goal:
    - preserve BTC / SOL / BNB / ZEC hourly-short upside
    - reduce noise from ADA / XRP / DOGE when the market state is not clearly bearish
    """

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if entry_tag != "short_1h_center" or not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        bull, bear, _ = classify_intraday_regime(candle)

        multiplier = 1.0
        if pair == "DOGE/USDT:USDT":
            multiplier *= doge_short_multiplier(candle, bull=bull, bear=bear)
        elif pair == "XRP/USDT:USDT":
            multiplier *= xrp_short_multiplier(candle, bull=bull, bear=bear)
        elif pair == "ADA/USDT:USDT":
            multiplier *= ada_short_multiplier(candle, bull=bull, bear=bear)

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy.py

```python
from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanHourStateStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy
):
    """
    Only retune the hourly short branch by market regime.

    The yearly breakdown showed `short_1h_center` was:
    - weak in 2022 / 2023
    - neutral in 2025
    - strong in 2024 / 2026

    So this version suppresses it harder in bull/neutral states and
    makes it more selective in bear states where it has historically
    carried more of the result.
    """

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if entry_tag != "short_1h_center" or not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        bull = (
            candle.get("close_1d", 0) > candle.get("ema_fast_1d", 0) > candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) >= 57
            and bool(candle.get("ema_slow_slope_up_1d", False))
        )
        bear = (
            candle.get("close_1d", 0) < candle.get("ema_fast_1d", 0) < candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) <= 45
            and bool(candle.get("ema_slow_slope_down_1d", False))
        )

        multiplier = 1.0
        if bear:
            multiplier *= 1.06
        elif bull:
            multiplier *= 0.86
        else:
            multiplier *= 0.90

        if pair in {"ADA/USDT:USDT", "XRP/USDT:USDT"}:
            multiplier *= 0.95

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy.py

```python
from .CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeBullLeanStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy
):
    """
    Mildly more aggressive in bull markets:
    - lift daily long continuation a bit more
    - trim hourly shorts harder when the daily regime is bullish
    """

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        bull = (
            candle.get("close_1d", 0) > candle.get("ema_fast_1d", 0) > candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) >= 57
            and bool(candle.get("ema_slow_slope_up_1d", False))
        )
        bear = (
            candle.get("close_1d", 0) < candle.get("ema_fast_1d", 0) < candle.get("ema_slow_1d", 0)
            and candle.get("rsi_1d", 50) <= 45
            and bool(candle.get("ema_slow_slope_down_1d", False))
        )

        multiplier = 1.0
        if entry_tag == "long_1d_center_compression" and bull:
            multiplier *= 1.05
        elif entry_tag == "short_1h_center" and bull:
            multiplier *= 0.88
        elif entry_tag == "short_1d_center_compression" and bear:
            multiplier *= 1.03

        stake *= multiplier
        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy.py

```python
from pandas import DataFrame

from .CombinedTrendCaptureMilestoneV2Top9RegimeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy,
)
from signals.filters import remove_range_reversion_entries


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy
):
    """
    Keep the bull/bear regime layer, but disable range-reversion entries.
    This isolates the value of the market-state logic itself.
    """

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return remove_range_reversion_entries(dataframe)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9RegimeStrategy.py

```python
from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade

from .CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy import (
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy,
)
from core.market_state.regime import classify_daily_regime, classify_intraday_regime, recent_trade_multiplier


class CombinedTrendCaptureMilestoneV2Top9RegimeStrategy(
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy
):
    """
    Internal regime base:
    - classify bull / bear / range from 1d structure
    - bias stake weights by market state
    - optionally support range mean-reversion entries in child strategies
    """

    core_bull_pairs = {"BTC/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT", "ZEC/USDT:USDT"}

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        bull, bear, _ = classify_daily_regime(dataframe)
        tags = dataframe["enter_tag"].fillna("")

        weak_bull_short = tags.eq("short_1h_center") & bull & ~dataframe["daily_momentum_short_1d"].eq(True)
        dataframe.loc[weak_bull_short, ["enter_short", "enter_tag"]] = (0, None)

        weak_bear_long = (
            tags.eq("long_1d_center_compression")
            & bear
            & ~dataframe["daily_momentum_long_1d"].eq(True)
        )
        dataframe.loc[weak_bear_long, ["enter_long", "enter_tag"]] = (0, None)

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        bull, bear, _ = classify_intraday_regime(candle)

        multiplier = 1.0
        if entry_tag == "long_1d_center_compression":
            multiplier *= 1.12 if bull else (0.86 if bear else 0.94)
            if pair in self.core_bull_pairs:
                multiplier *= 1.05
            elif pair in {"ETH/USDT:USDT", "XRP/USDT:USDT", "ADA/USDT:USDT", "TRX/USDT:USDT"}:
                multiplier *= 0.95
        elif entry_tag == "short_1d_center_compression":
            multiplier *= 1.12 if bear else (0.86 if bull else 0.95)
            if pair == "DOGE/USDT:USDT":
                multiplier *= 0.88
        elif entry_tag == "short_1h_center":
            multiplier *= 1.04 if bear else (0.76 if bull else 0.88)
            if pair == "DOGE/USDT:USDT":
                multiplier *= 0.88
            if pair == "ZEC/USDT:USDT":
                multiplier *= 0.94

        multiplier *= recent_trade_multiplier(current_time, entry_tag, pair)
        stake *= multiplier

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy.py

```python
from .CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy import (
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy,
)


class CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy(
    CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy
):
    """
    Keep the Top9 universe but trim DOGE exposure.
    DOGE boosts upside, but it also amplifies drawdown spikes.
    """

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if pair == "DOGE/USDT:USDT":
            stake *= 0.60

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy.py

```python
from .CombinedTrendCaptureMilestoneV2Top9Strategy import CombinedTrendCaptureMilestoneV2Top9Strategy


class CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy(
    CombinedTrendCaptureMilestoneV2Top9Strategy
):
    """
    Top9 experiment:
    Slightly reduce the extra stake boost on long_1d_center_compression.
    """

    stake_multipliers = {
        "long_1d_center_compression": 1.20,
        "short_1d_center_compression": 1.15,
        "short_1h_center": 0.80,
    }

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Top9Strategy.py

```python
from .CombinedTrendCaptureMilestoneV2Strategy import CombinedTrendCaptureMilestoneV2Strategy
from shared.pair_groups import TOP9_MAIN_PAIRS


class CombinedTrendCaptureMilestoneV2Top9Strategy(CombinedTrendCaptureMilestoneV2Strategy):
    allowed_pairs = TOP9_MAIN_PAIRS

```

### archive\old_versions\CombinedTrendCaptureMilestoneV2Strategy.py

```python
from .CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy import (
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy,
)


class CombinedTrendCaptureMilestoneV2Strategy(
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy
):
    """
    Frozen milestone version after stake-weighting and short-quality filtering.
    """

```

### archive\old_versions\CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy.py

```python
from pandas import DataFrame

from .CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy import (
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy,
)


class CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy(
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy
):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        short_quality = (
            self._bool_series(dataframe, "daily_momentum_short_1d")
            & self._bool_series(dataframe, "ema_slow_slope_down_1d")
            & (dataframe["close"] < dataframe["ema_fast"])
            & (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        )

        low_quality_short = dataframe.get("enter_tag", "").eq("short_1h_center") & ~short_quality
        dataframe.loc[low_quality_short, ["enter_short", "enter_tag"]] = (0, None)

        return dataframe

```

### archive\old_versions\CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy.py

```python
from .CombinedTrendCaptureMilestoneV1Top8Strategy import CombinedTrendCaptureMilestoneV1Top8Strategy


class CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy(CombinedTrendCaptureMilestoneV1Top8Strategy):
    stake_multipliers = {
        "long_1d_center_compression": 1.35,
        "short_1d_center_compression": 1.15,
        "short_1h_center": 0.80,
    }

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        multiplier = self.stake_multipliers.get(entry_tag or "", 1.0)
        weighted_stake = proposed_stake * multiplier
        if min_stake is not None:
            weighted_stake = max(weighted_stake, min_stake)
        return min(weighted_stake, max_stake)

```

### archive\old_versions\CombinedTrendCaptureMilestoneV1Top8Strategy.py

```python
from .CombinedTrendCaptureMilestoneV1Strategy import CombinedTrendCaptureMilestoneV1Strategy


class CombinedTrendCaptureMilestoneV1Top8Strategy(CombinedTrendCaptureMilestoneV1Strategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "ADA/USDT:USDT",
        "TRX/USDT:USDT",
        "LINK/USDT:USDT",
    }

```

### archive\old_versions\CombinedTrendCaptureMilestoneV1Strategy.py

```python
from test.CombinedTrendCaptureNoLongTriangleStrategy import CombinedTrendCaptureNoLongTriangleStrategy


class CombinedTrendCaptureMilestoneV1Strategy(CombinedTrendCaptureNoLongTriangleStrategy):
    """
    Frozen milestone version.
    Based on the best validated branch so far:
    CombinedTrendCaptureNoLongTriangleStrategy
    """


```

### test\CombinedTrendCaptureNoLongTriangleStrategy.py

```python
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

```

### test\CombinedTrendCaptureOptStrategy.py

```python
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

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

```

### DoubleShunStrategy.py

```python
from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import (
    DecimalParameter,
    IStrategy,
    IntParameter,
    informative,
    stoploss_from_absolute,
)

from core.indicators.structure import populate_structure_indicators


class DoubleShunStrategy(IStrategy):
    INTERFACE_VERSION = 3
    allowed_pairs = {"BTC/USDT:USDT", "BNB/USDT:USDT", "SOL/USDT:USDT"}

    can_short: bool = True
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count: int = 240

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True

    minimal_roi = {
        "0": 0.10,
    }

    stoploss = -0.02

    trend_ema_fast = IntParameter(5, 20, default=10, space="buy", optimize=True)
    trend_ema_slow = IntParameter(20, 80, default=30, space="buy", optimize=True)
    center_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    pullback_window = IntParameter(3, 8, default=4, space="buy", optimize=True)
    restart_window = IntParameter(2, 6, default=3, space="buy", optimize=True)
    triangle_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    compression_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    swing_window = IntParameter(2, 8, default=3, space="sell", optimize=True)

    pullback_depth = DecimalParameter(0.002, 0.025, default=0.010, decimals=3, space="buy", optimize=True)
    breakout_buffer = DecimalParameter(0.001, 0.012, default=0.002, decimals=3, space="buy", optimize=True)
    compression_limit = DecimalParameter(0.006, 0.040, default=0.018, decimals=3, space="buy", optimize=True)
    level_tolerance = DecimalParameter(0.002, 0.020, default=0.006, decimals=3, space="buy", optimize=True)
    level_proximity = DecimalParameter(0.002, 0.020, default=0.006, decimals=3, space="buy", optimize=True)
    volume_multiplier = DecimalParameter(1.00, 2.20, default=1.10, decimals=2, space="buy", optimize=True)

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            }
        ]

    @staticmethod
    def _bool_series(dataframe: DataFrame, column: str) -> pd.Series:
        return dataframe[column].eq(True)

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def _populate_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=int(self.trend_ema_fast.value),
            trend_ema_slow=int(self.trend_ema_slow.value),
            center_window=int(self.center_window.value),
            pullback_window=int(self.pullback_window.value),
            restart_window=int(self.restart_window.value),
            triangle_window=int(self.triangle_window.value),
            compression_window=int(self.compression_window.value),
            swing_window=int(self.swing_window.value),
            pullback_depth=float(self.pullback_depth.value),
            breakout_buffer=float(self.breakout_buffer.value),
            compression_limit=float(self.compression_limit.value),
            level_tolerance=float(self.level_tolerance.value),
            level_proximity=float(self.level_proximity.value),
            volume_multiplier=float(self.volume_multiplier.value),
        )

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.allowed_pairs:
            return dataframe

        hourly_long_context = (
            self._bool_series(dataframe, "restart_ready_long_1d")
            & self._bool_series(dataframe, "daily_momentum_long_1d")
        )
        hourly_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        triangle_long = self._bool_series(dataframe, "triangle_breakout_long")
        compression_long = self._bool_series(dataframe, "compression_breakout_long")
        center_short = self._bool_series(dataframe, "center_breakout_short")
        compression_short = self._bool_series(dataframe, "compression_breakout_short")
        triangle_long_1d = self._bool_series(dataframe, "triangle_breakout_long_1d")
        center_long_1d = self._bool_series(dataframe, "center_breakout_long_1d")
        triangle_short_1d = self._bool_series(dataframe, "triangle_breakout_short_1d")
        center_short_1d = self._bool_series(dataframe, "center_breakout_short_1d")
        daily_long_context = self._bool_series(dataframe, "restart_ready_long_1d")
        daily_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        daily_long_signal = daily_long_context & (triangle_long_1d | center_long_1d)
        daily_short_signal = daily_short_context & (triangle_short_1d | center_short_1d)
        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)
        daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)
        strong_hourly_long_triangle = (
            hourly_long_context
            & triangle_long
            & self._bool_series(dataframe, "range_tight")
            & self._bool_series(dataframe, "ema_slow_slope_up")
            & (dataframe["rsi"] > 52)
            & self._bool_series(dataframe, "breakout_above_recent_1d")
        )
        dataframe.loc[
            strong_hourly_long_triangle,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_triangle")

        dataframe.loc[
            daily_long_trigger & triangle_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_triangle")
        dataframe.loc[
            daily_long_trigger & center_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_center_compression")

        dataframe.loc[
            hourly_short_context & center_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_center")
        dataframe.loc[
            hourly_short_context & compression_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_compression")

        dataframe.loc[
            daily_short_trigger & triangle_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_triangle")
        dataframe.loc[
            daily_short_trigger & center_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_center_compression")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        if not self.dp:
            return self.stoploss

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return self.stoploss

        candle = dataframe.iloc[-1]
        tag = trade.enter_tag or ""
        scope = "1d" if "_1d_" in tag else "1h"
        suffix = "_1d" if scope == "1d" else ""

        if trade.is_short:
            structure_stop = candle.get(f"structure_stop_short{suffix}")
            capped_stop = trade.open_rate * 1.02
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = min(float(structure_stop), capped_stop)
        else:
            structure_stop = candle.get(f"structure_stop_long{suffix}")
            capped_stop = trade.open_rate * 0.98
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = max(float(structure_stop), capped_stop)

        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=trade.is_short,
            leverage=trade.leverage,
        )

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        candle = dataframe.iloc[-1]
        tag = trade.enter_tag or ""
        scope = "1d" if "_1d_" in tag else "1h"
        suffix = "_1d" if scope == "1d" else ""

        stop_long = candle.get(f"structure_stop_long{suffix}")
        stop_short = candle.get(f"structure_stop_short{suffix}")

        if trade.is_short:
            if bool(candle.get("uptrend_1d", False)):
                return "trend_flip_short"
            if scope == "1d":
                if bool(candle.get("center_up_1d", False)) and candle["close"] > candle.get("ema_fast_1d", candle["close"]):
                    return "structure_exit_short_1d"
            else:
                if bool(candle.get("center_up", False)) and candle["close"] > candle.get("ema_fast", candle["close"]):
                    return "structure_exit_short_1h"

            if pd.notna(stop_short) and candle["close"] > stop_short:
                return f"swing_exit_short_{scope}"
            return None

        if bool(candle.get("downtrend_1d", False)):
            return "trend_flip_long"
        if scope == "1d":
            if bool(candle.get("center_down_1d", False)) and candle["close"] < candle.get("ema_fast_1d", candle["close"]):
                return "structure_exit_long_1d"
        else:
            if bool(candle.get("center_down", False)) and candle["close"] < candle.get("ema_fast", candle["close"]):
                return "structure_exit_long_1h"

        if pd.notna(stop_long) and candle["close"] < stop_long:
            return f"swing_exit_long_{scope}"

        return None

```

### signals\reversal.py

```python
from pandas import DataFrame


def populate_reversal_indicators(dataframe: DataFrame, pair: str) -> DataFrame:
    typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
    candle_range = (dataframe["high"] - dataframe["low"]).clip(lower=1e-9)
    volume_mean_20 = dataframe["volume"].shift(1).rolling(20).mean()

    # Long reversal: daily selloff exhaustion -> 1h detach -> high-base breakout.
    daily_major_low_60 = dataframe["low_1d"].shift(1).rolling(60).min()
    daily_recent_pullback_low_20 = dataframe["low_1d"].shift(20).rolling(20).min()

    dataframe["reversal_daily_long_background_ok"] = (
        (dataframe["low_1d"] > daily_major_low_60 * 1.015)
        & (dataframe["low_1d"] > daily_recent_pullback_low_20 * 1.005)
        & (dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.975)
        & (dataframe["close_1d"] > dataframe["ema_fast_1d"])
        & dataframe["ema_slow_slope_up_1d"].eq(True)
        & (dataframe["rsi_1d"] > 38)
        & (dataframe["rsi_1d"] < 70)
    )

    long_launch_low_24 = dataframe["low"].shift(1).rolling(24).min()
    long_center_5 = typical_price.rolling(5).mean()
    long_center_10 = typical_price.rolling(10).mean()
    dataframe["reversal_long_regime_ok"] = (
        (dataframe["close"] > long_launch_low_24 * 1.008)
        & (long_center_5 > long_center_5.shift(2))
        & (long_center_10 > long_center_10.shift(4))
        & (dataframe["low"].shift(1).rolling(8).min() > long_launch_low_24 * 1.003)
    )

    long_ref_high_72 = dataframe["high"].shift(1).rolling(72).max()
    long_base_high_12 = dataframe["high"].shift(1).rolling(12).max()
    long_base_low_12 = dataframe["low"].shift(1).rolling(12).min()
    long_base_range_pct = (long_base_high_12 - long_base_low_12) / dataframe["close"]
    long_base_center = (long_base_high_12 + long_base_low_12) / 2.0
    long_base_center_prev = long_base_center.shift(6)
    long_base_floor = dataframe["low"].shift(1).rolling(6).min()
    long_base_floor_prev = long_base_floor.shift(6)

    dataframe["reversal_long_reaccumulation_ok"] = (
        (dataframe["close"].shift(1) >= long_ref_high_72 * 0.97)
        & (long_base_range_pct < 0.095)
        & (long_base_center > long_base_center_prev * 1.002)
        & (long_base_floor > long_base_floor_prev * 1.001)
    )

    dataframe["reversal_long_breakout_candle_ok"] = (
        (dataframe["close"] > long_ref_high_72 * 1.012)
        & (dataframe["high"] > long_ref_high_72 * 1.035)
        & (dataframe["volume"] > volume_mean_20 * 1.8)
        & (((dataframe["close"] - dataframe["open"]) / dataframe["close"]) > 0.03)
        & (((dataframe["high"] - dataframe["close"]) / candle_range) < 0.33)
        & (((dataframe["open"] - dataframe["low"]) / candle_range) < 0.20)
        & (dataframe["rsi"] < 94)
    )

    dataframe["reversal_long_risk_filter_ok"] = (
        (dataframe["rsi"] < 94)
        & (dataframe["high"].shift(1) < long_ref_high_72 * 1.02)
    )

    dataframe["reversal_long_breakout"] = (
        dataframe["reversal_daily_long_background_ok"]
        & dataframe["reversal_long_regime_ok"]
        & dataframe["reversal_long_reaccumulation_ok"]
        & dataframe["reversal_long_breakout_candle_ok"]
        & dataframe["reversal_long_risk_filter_ok"]
    )
    dataframe["reversal_long_hold_active"] = (
        dataframe["reversal_long_breakout"]
        .rolling(6, min_periods=1)
        .max()
        .shift(1)
        .fillna(False)
        .astype(bool)
    )

    # Short reversal: daily rally exhaustion -> 1h detach from the top -> low-base breakdown.
    daily_major_high_60 = dataframe["high_1d"].shift(1).rolling(60).max()
    daily_recent_rally_high_20 = dataframe["high_1d"].shift(20).rolling(20).max()

    dataframe["reversal_daily_short_background_ok"] = (
        (dataframe["high_1d"] < daily_major_high_60 * 0.985)
        & (dataframe["high_1d"] < daily_recent_rally_high_20 * 0.995)
        & (dataframe["close_1d"] <= dataframe["ema_slow_1d"] * 1.015)
        & (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        & dataframe["ema_slow_slope_down_1d"].eq(True)
        & (dataframe["rsi_1d"] > 34)
        & (dataframe["rsi_1d"] < 58)
    )

    short_launch_high_24 = dataframe["high"].shift(1).rolling(24).max()
    short_center_5 = typical_price.rolling(5).mean()
    short_center_10 = typical_price.rolling(10).mean()
    dataframe["reversal_short_regime_ok"] = (
        (dataframe["close"] < short_launch_high_24 * 0.98)
        & (short_center_5 < short_center_5.shift(3))
        & (short_center_10 < short_center_10.shift(5))
        & (dataframe["high"].shift(1).rolling(8).max() < short_launch_high_24 * 0.99)
    )

    short_ref_low_72 = dataframe["low"].shift(1).rolling(72).min()
    short_base_high_12 = dataframe["high"].shift(1).rolling(12).max()
    short_base_low_12 = dataframe["low"].shift(1).rolling(12).min()
    short_base_range_pct = (short_base_high_12 - short_base_low_12) / dataframe["close"]
    short_base_center = (short_base_high_12 + short_base_low_12) / 2.0
    short_base_center_prev = short_base_center.shift(6)
    short_base_ceiling = dataframe["high"].shift(1).rolling(6).max()
    short_base_ceiling_prev = short_base_ceiling.shift(6)

    dataframe["reversal_short_redistribution_ok"] = (
        (dataframe["close"].shift(1) <= short_ref_low_72 * 1.03)
        & (short_base_range_pct < 0.10)
        & (short_base_center < short_base_center_prev * 0.997)
        & (short_base_ceiling < short_base_ceiling_prev * 0.999)
    )

    dataframe["reversal_short_breakdown_candle_ok"] = (
        (dataframe["close"] < short_ref_low_72 * 0.992)
        & (dataframe["low"] < short_ref_low_72 * 0.97)
        & (dataframe["volume"] > volume_mean_20 * 1.8)
        & (((dataframe["open"] - dataframe["close"]) / dataframe["close"]) > 0.025)
        & (((dataframe["close"] - dataframe["low"]) / candle_range) < 0.35)
        & (((dataframe["high"] - dataframe["open"]) / candle_range) < 0.25)
        & (dataframe["rsi"] > 6)
    )

    dataframe["reversal_short_risk_filter_ok"] = (
        (dataframe["rsi"] > 6)
        & (dataframe["low"].shift(1) > short_ref_low_72 * 0.98)
    )

    dataframe["reversal_short_breakdown"] = (
        dataframe["reversal_daily_short_background_ok"]
        & dataframe["reversal_short_regime_ok"]
        & dataframe["reversal_short_redistribution_ok"]
        & dataframe["reversal_short_breakdown_candle_ok"]
        & dataframe["reversal_short_risk_filter_ok"]
    )

    if pair == "DOGE/USDT:USDT":
        dataframe["reversal_short_breakdown"] = (
            dataframe["reversal_short_breakdown"]
            & (dataframe["high_1d"] < daily_major_high_60 * 0.982)
            & (dataframe["rsi_1d"] > 40)
            & (dataframe["rsi_1d"] < 54)
            & (dataframe["close"] < short_launch_high_24 * 0.975)
            & (dataframe["high"].shift(1).rolling(8).max() < short_launch_high_24 * 0.985)
            & (dataframe["close"].shift(1) <= short_ref_low_72 * 1.02)
            & (short_base_range_pct < 0.085)
            & (short_base_center < short_base_center_prev * 0.995)
            & (short_base_ceiling < short_base_ceiling_prev * 0.998)
            & (dataframe["low"] < short_ref_low_72 * 0.965)
            & (dataframe["volume"] > volume_mean_20 * 2.0)
            & (((dataframe["open"] - dataframe["close"]) / dataframe["close"]) > 0.03)
            & (((dataframe["close"] - dataframe["low"]) / candle_range) < 0.30)
            & (((dataframe["high"] - dataframe["open"]) / candle_range) < 0.22)
        )

    dataframe["reversal_short_hold_active"] = (
        dataframe["reversal_short_breakdown"]
        .rolling(6, min_periods=1)
        .max()
        .shift(1)
        .fillna(False)
        .astype(bool)
    )

    return dataframe


def apply_reversal_entry_signals(
    dataframe: DataFrame,
    pair: str,
    long_reversal_pairs,
    short_reversal_pairs,
) -> DataFrame:
    long_mask = dataframe["reversal_long_breakout"].fillna(False)
    long_hold_mask = dataframe["reversal_long_hold_active"].fillna(False)
    short_mask = dataframe["reversal_short_breakdown"].fillna(False)
    short_hold_mask = dataframe["reversal_short_hold_active"].fillna(False)

    if pair not in long_reversal_pairs:
        long_mask = long_mask & False
        long_hold_mask = long_hold_mask & False
    if pair not in short_reversal_pairs:
        short_mask = short_mask & False
        short_hold_mask = short_hold_mask & False

    if "enter_short" in dataframe.columns:
        suppress_short = long_mask | long_hold_mask
        dataframe.loc[suppress_short, ["enter_short", "enter_tag"]] = (0, None)

    if "enter_long" in dataframe.columns:
        suppress_long = short_mask | short_hold_mask
        dataframe.loc[suppress_long, ["enter_long", "enter_tag"]] = (0, None)

    dataframe.loc[long_mask, ["enter_long", "enter_tag"]] = (1, "long_reversal_breakout")
    dataframe.loc[long_hold_mask, ["enter_long", "enter_tag"]] = (1, "long_reversal_breakout")
    if "enter_short" in dataframe.columns:
        dataframe.loc[short_mask, ["enter_short", "enter_tag"]] = (1, "short_reversal_breakdown")
        dataframe.loc[short_hold_mask, ["enter_short", "enter_tag"]] = (
            1,
            "short_reversal_breakdown",
        )

    return dataframe

```

### signals\filters.py

```python
from pandas import DataFrame


def remove_range_reversion_entries(dataframe: DataFrame) -> DataFrame:
    range_tags = dataframe["enter_tag"].fillna("").isin(
        {"long_range_1h_revert", "short_range_1h_revert"}
    )
    dataframe.loc[range_tags, ["enter_long", "enter_short", "enter_tag"]] = (0, 0, None)
    return dataframe


def remove_long_triangle_entries(dataframe: DataFrame) -> DataFrame:
    long_triangle = dataframe["enter_tag"].fillna("").eq("long_1d_triangle")
    dataframe.loc[long_triangle, ["enter_long", "enter_tag"]] = (0, None)
    return dataframe

```

### signals\long\entries.py

```python
from pandas import DataFrame


def apply_long_entry_signals(strategy, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if metadata["pair"] not in strategy.allowed_pairs:
        return dataframe

    bool_series = strategy._bool_series

    hourly_long_context = (
        bool_series(dataframe, "restart_ready_long_1d")
        & bool_series(dataframe, "daily_momentum_long_1d")
    )
    triangle_long = bool_series(dataframe, "triangle_breakout_long")
    triangle_long_1d = bool_series(dataframe, "triangle_breakout_long_1d")
    center_long_1d = bool_series(dataframe, "center_breakout_long_1d")
    daily_long_context = bool_series(dataframe, "restart_ready_long_1d")

    daily_long_signal = daily_long_context & (
        triangle_long_1d | center_long_1d
    ) & (dataframe["rsi_1d"] > int(strategy.daily_long_rsi.value))
    daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)

    strong_hourly_long_triangle = (
        hourly_long_context
        & triangle_long
        & bool_series(dataframe, "range_tight")
        & bool_series(dataframe, "ema_slow_slope_up")
        & (dataframe["rsi"] > int(strategy.hourly_long_rsi.value))
        & bool_series(dataframe, "breakout_above_recent_1d")
    )

    if bool(strategy.enable_long_1h_triangle.value):
        dataframe.loc[
            strong_hourly_long_triangle,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_triangle")

    if bool(strategy.enable_long_1d_triangle.value):
        dataframe.loc[
            daily_long_trigger & triangle_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_triangle")

    if bool(strategy.enable_long_1d_center.value):
        dataframe.loc[
            daily_long_trigger & center_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_center_compression")

    return dataframe

```

### signals\short\entries.py

```python
from pandas import DataFrame


def apply_short_entry_signals(strategy, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if metadata["pair"] not in strategy.allowed_pairs:
        return dataframe

    bool_series = strategy._bool_series

    center_short = bool_series(dataframe, "center_breakout_short")
    compression_short = bool_series(dataframe, "compression_breakout_short")
    triangle_short_1d = bool_series(dataframe, "triangle_breakout_short_1d")
    center_short_1d = bool_series(dataframe, "center_breakout_short_1d")
    daily_short_context = bool_series(dataframe, "restart_ready_short_1d")

    daily_short_signal = daily_short_context & (
        triangle_short_1d | center_short_1d
    ) & (dataframe["rsi_1d"] < int(strategy.daily_short_rsi.value))
    daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)

    if bool(strategy.enable_short_1h_center.value):
        dataframe.loc[
            daily_short_context & center_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_center")

    if bool(strategy.enable_short_1h_compression.value):
        dataframe.loc[
            daily_short_context & compression_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_compression")

    if bool(strategy.enable_short_1d_triangle.value):
        dataframe.loc[
            daily_short_trigger & triangle_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_triangle")

    if bool(strategy.enable_short_1d_center.value):
        dataframe.loc[
            daily_short_trigger & center_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_center_compression")

    return dataframe

```

### signals\exit_rules.py

```python
from typing import Optional

from freqtrade.persistence import Trade


def resolve_custom_exit(
    strategy,
    pair: str,
    trade: Trade,
    current_time,
    current_rate: float,
    current_profit: float,
    **kwargs,
) -> Optional[str]:
    if not strategy.dp:
        return None

    dataframe, _ = strategy.dp.get_analyzed_dataframe(pair, strategy.timeframe)
    if dataframe.empty:
        return None

    candle = dataframe.iloc[-1]
    tag = trade.enter_tag or ""
    scope = "1d" if "_1d_" in tag else "1h"
    suffix = "_1d" if scope == "1d" else ""

    stop_long = candle.get(f"structure_stop_long{suffix}")
    stop_short = candle.get(f"structure_stop_short{suffix}")

    if trade.is_short:
        if bool(candle.get("uptrend_1d", False)):
            return "trend_flip_short"
        if scope == "1d":
            if bool(candle.get("center_up_1d", False)) and candle["close"] > candle.get(
                "ema_fast_1d", candle["close"]
            ):
                return "structure_exit_short_1d"
        else:
            if bool(candle.get("center_up", False)) and candle["close"] > candle.get(
                "ema_fast", candle["close"]
            ):
                return "structure_exit_short_1h"

        if stop_short is not None and candle["close"] > stop_short:
            return f"swing_exit_short_{scope}"
        return None

    if bool(candle.get("downtrend_1d", False)):
        return "trend_flip_long"
    if scope == "1d":
        if bool(candle.get("center_down_1d", False)) and candle["close"] < candle.get(
            "ema_fast_1d", candle["close"]
        ):
            return "structure_exit_long_1d"
    else:
        if bool(candle.get("center_down", False)) and candle["close"] < candle.get(
            "ema_fast", candle["close"]
        ):
            return "structure_exit_long_1h"

    if stop_long is not None and candle["close"] < stop_long:
        return f"swing_exit_long_{scope}"

    return None

```

### core\market_state\regime.py

```python
from freqtrade.persistence import Trade


def classify_daily_regime(dataframe):
    bull = (
        (dataframe["close_1d"] > dataframe["ema_fast_1d"])
        & (dataframe["ema_fast_1d"] > dataframe["ema_slow_1d"])
        & (dataframe["rsi_1d"] >= 57)
        & dataframe["ema_slow_slope_up_1d"].eq(True)
    )
    bear = (
        (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        & (dataframe["ema_fast_1d"] < dataframe["ema_slow_1d"])
        & (dataframe["rsi_1d"] <= 45)
        & dataframe["ema_slow_slope_down_1d"].eq(True)
    )
    ranging = ~(bull | bear)
    return bull, bear, ranging


def classify_intraday_regime(candle):
    bull = (
        candle.get("close_1d", 0) > candle.get("ema_fast_1d", 0) > candle.get("ema_slow_1d", 0)
        and candle.get("rsi_1d", 50) >= 57
        and bool(candle.get("ema_slow_slope_up_1d", False))
    )
    bear = (
        candle.get("close_1d", 0) < candle.get("ema_fast_1d", 0) < candle.get("ema_slow_1d", 0)
        and candle.get("rsi_1d", 50) <= 45
        and bool(candle.get("ema_slow_slope_down_1d", False))
    )
    ranging = not (bull or bear)
    return bull, bear, ranging


def recent_trade_multiplier(current_time, entry_tag: str | None, pair: str) -> float:
    if not entry_tag:
        return 1.0

    closed = [
        trade
        for trade in Trade.get_trades_proxy(is_open=False)
        if trade.close_date_utc
        and trade.close_date_utc <= current_time
        and (trade.enter_tag or "") == entry_tag
    ]
    closed.sort(key=lambda trade: trade.close_date_utc, reverse=True)
    recent_tag = closed[:6]

    multiplier = 1.0
    if len(recent_tag) >= 4:
        tag_profit = sum((trade.close_profit or 0.0) for trade in recent_tag)
        tag_losses = sum(1 for trade in recent_tag if (trade.close_profit or 0.0) <= 0)
        if tag_profit < -0.04:
            multiplier *= 0.74
        elif tag_profit < -0.015 or tag_losses >= 5:
            multiplier *= 0.84
        elif tag_profit < 0:
            multiplier *= 0.92

    same_pair = [trade for trade in recent_tag if trade.pair == pair][:4]
    if len(same_pair) >= 3:
        pair_profit = sum((trade.close_profit or 0.0) for trade in same_pair)
        if pair_profit < -0.03:
            multiplier *= 0.82
        elif pair_profit < 0:
            multiplier *= 0.92

    return multiplier

```

### core\indicators\structure.py

```python
import talib.abstract as ta
from pandas import DataFrame


def populate_structure_indicators(
    dataframe: DataFrame,
    trend_ema_fast: int,
    trend_ema_slow: int,
    center_window: int,
    pullback_window: int,
    restart_window: int,
    triangle_window: int,
    compression_window: int,
    swing_window: int,
    pullback_depth: float,
    breakout_buffer: float,
    compression_limit: float,
    level_tolerance: float,
    level_proximity: float,
    volume_multiplier: float,
) -> DataFrame:
    half_window = max(2, triangle_window // 2)
    typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0

    dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=trend_ema_fast)
    dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=trend_ema_slow)
    dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
    dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
    dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
    dataframe["volume_mean"] = dataframe["volume"].rolling(max(5, triangle_window)).mean()

    dataframe["market_center"] = typical_price.rolling(center_window).mean()
    dataframe["center_up"] = dataframe["market_center"] > dataframe["market_center"].shift(2)
    dataframe["center_down"] = dataframe["market_center"] < dataframe["market_center"].shift(2)

    dataframe["uptrend"] = (
        (dataframe["close"] > dataframe["ema_slow"])
        & (dataframe["ema_fast"] > dataframe["ema_slow"])
        & dataframe["center_up"]
    )
    dataframe["downtrend"] = (
        (dataframe["close"] < dataframe["ema_slow"])
        & (dataframe["ema_fast"] < dataframe["ema_slow"])
        & dataframe["center_down"]
    )

    dataframe["recent_high"] = dataframe["high"].shift(1).rolling(triangle_window).max()
    dataframe["recent_low"] = dataframe["low"].shift(1).rolling(triangle_window).min()
    dataframe["recent_high_short"] = dataframe["high"].shift(1).rolling(half_window).max()
    dataframe["recent_low_short"] = dataframe["low"].shift(1).rolling(half_window).min()
    dataframe["prior_high_short"] = dataframe["high"].shift(half_window + 1).rolling(half_window).max()
    dataframe["prior_low_short"] = dataframe["low"].shift(half_window + 1).rolling(half_window).min()

    dataframe["rising_lows"] = dataframe["recent_low_short"] > dataframe["prior_low_short"]
    dataframe["falling_highs"] = dataframe["recent_high_short"] < dataframe["prior_high_short"]
    dataframe["flat_ceiling"] = (
        (dataframe["recent_high"] - dataframe["recent_high_short"]).abs() / dataframe["close"]
    ) < level_tolerance
    dataframe["flat_floor"] = (
        (dataframe["recent_low_short"] - dataframe["recent_low"]).abs() / dataframe["close"]
    ) < level_tolerance

    dataframe["range_width"] = (
        (
            dataframe["high"].shift(1).rolling(compression_window).max()
            - dataframe["low"].shift(1).rolling(compression_window).min()
        )
        / dataframe["close"]
    )
    dataframe["range_width_prev"] = dataframe["range_width"].shift(max(2, compression_window // 2))
    dataframe["range_tight"] = dataframe["range_width"] < compression_limit
    dataframe["range_contracting"] = dataframe["range_width"] < dataframe["range_width_prev"]
    dataframe["volume_expansion"] = dataframe["volume"] > dataframe["volume_mean"] * volume_multiplier

    dataframe["pullback_low"] = dataframe["low"].shift(1).rolling(pullback_window).min()
    dataframe["pullback_high"] = dataframe["high"].shift(1).rolling(pullback_window).max()
    dataframe["restart_high"] = dataframe["high"].shift(1).rolling(restart_window).max()
    dataframe["restart_low"] = dataframe["low"].shift(1).rolling(restart_window).min()

    dataframe["pullback_seen_long"] = dataframe["pullback_low"] <= (
        dataframe["ema_fast"] * (1 + pullback_depth)
    )
    dataframe["pullback_seen_short"] = dataframe["pullback_high"] >= (
        dataframe["ema_fast"] * (1 - pullback_depth)
    )
    dataframe["structure_intact_long"] = dataframe["pullback_low"] > (
        dataframe["ema_slow"] * (1 - pullback_depth * 2.0)
    )
    dataframe["structure_intact_short"] = dataframe["pullback_high"] < (
        dataframe["ema_slow"] * (1 + pullback_depth * 2.0)
    )

    dataframe["restart_ready_long"] = (
        dataframe["uptrend"]
        & dataframe["pullback_seen_long"]
        & dataframe["structure_intact_long"]
        & (dataframe["close"] > dataframe["ema_fast"])
        & (dataframe["rsi"] > dataframe["rsi"].shift(1))
    )
    dataframe["restart_ready_short"] = (
        dataframe["downtrend"]
        & dataframe["pullback_seen_short"]
        & dataframe["structure_intact_short"]
        & (dataframe["close"] < dataframe["ema_fast"])
        & (dataframe["rsi"] < dataframe["rsi"].shift(1))
    )

    dataframe["near_high_compression"] = (
        dataframe["close"].shift(1) >= dataframe["recent_high"] * (1 - level_proximity)
    )
    dataframe["near_low_compression"] = (
        dataframe["close"].shift(1) <= dataframe["recent_low"] * (1 + level_proximity)
    )
    dataframe["breakout_above_recent"] = (
        (dataframe["close"] > dataframe["recent_high"] * (1 + breakout_buffer))
        & (dataframe["close"].shift(1) <= dataframe["recent_high"].shift(1) * (1 + breakout_buffer))
    )
    dataframe["breakout_below_recent"] = (
        (dataframe["close"] < dataframe["recent_low"] * (1 - breakout_buffer))
        & (dataframe["close"].shift(1) >= dataframe["recent_low"].shift(1) * (1 - breakout_buffer))
    )
    dataframe["ema_slow_slope_up"] = dataframe["ema_slow"] > dataframe["ema_slow"].shift(3)
    dataframe["ema_slow_slope_down"] = dataframe["ema_slow"] < dataframe["ema_slow"].shift(3)
    dataframe["daily_momentum_long"] = (
        dataframe["uptrend"]
        & dataframe["ema_slow_slope_up"]
        & (dataframe["rsi"] > 55)
    )
    dataframe["daily_momentum_short"] = (
        dataframe["downtrend"]
        & dataframe["ema_slow_slope_down"]
        & (dataframe["rsi"] < 45)
    )

    dataframe["triangle_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["rising_lows"]
        & dataframe["flat_ceiling"]
        & dataframe["range_contracting"]
        & dataframe["breakout_above_recent"]
        & dataframe["volume_expansion"]
    )
    dataframe["triangle_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["falling_highs"]
        & dataframe["flat_floor"]
        & dataframe["range_contracting"]
        & dataframe["breakout_below_recent"]
        & dataframe["volume_expansion"]
    )

    dataframe["center_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["center_up"]
        & dataframe["range_contracting"]
        & dataframe["near_high_compression"]
        & (dataframe["market_center"] > dataframe["market_center"].shift(1))
        & dataframe["breakout_above_recent"]
        & (dataframe["close"] > dataframe["market_center"])
        & dataframe["volume_expansion"]
    )
    dataframe["center_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["center_down"]
        & dataframe["range_contracting"]
        & dataframe["near_low_compression"]
        & (dataframe["market_center"] < dataframe["market_center"].shift(1))
        & dataframe["breakout_below_recent"]
        & (dataframe["close"] < dataframe["market_center"])
        & dataframe["volume_expansion"]
    )

    dataframe["compression_breakout_long"] = (
        dataframe["restart_ready_long"]
        & dataframe["range_tight"]
        & dataframe["range_contracting"]
        & dataframe["near_high_compression"]
        & dataframe["breakout_above_recent"]
        & dataframe["volume_expansion"]
    )
    dataframe["compression_breakout_short"] = (
        dataframe["restart_ready_short"]
        & dataframe["range_tight"]
        & dataframe["range_contracting"]
        & dataframe["near_low_compression"]
        & dataframe["breakout_below_recent"]
        & dataframe["volume_expansion"]
    )

    dataframe["signal_long"] = (
        dataframe["triangle_breakout_long"]
        | dataframe["center_breakout_long"]
        | dataframe["compression_breakout_long"]
    )
    dataframe["signal_short"] = (
        dataframe["triangle_breakout_short"]
        | dataframe["center_breakout_short"]
        | dataframe["compression_breakout_short"]
    )

    dataframe["structure_stop_long"] = dataframe["low"].shift(1).rolling(swing_window).min()
    dataframe["structure_stop_short"] = dataframe["high"].shift(1).rolling(swing_window).max()

    return dataframe

```

### shared\pair_groups.py

```python
from pairs.btc.profile import PAIR as BTC_PAIR
from pairs.eth.profile import PAIR as ETH_PAIR
from pairs.zec.profile import PAIR as ZEC_PAIR

LONG_REVERSAL_PAIRS_193 = {
    BTC_PAIR,
    ETH_PAIR,
}

SHORT_REVERSAL_PAIRS_193 = {
    BTC_PAIR,
    ETH_PAIR,
    "DOGE/USDT:USDT",
    "XRP/USDT:USDT",
    ZEC_PAIR,
}

LONG_REVERSAL_PAIRS_216 = {
    ZEC_PAIR,
}

SHORT_REVERSAL_PAIRS_216 = {
    BTC_PAIR,
    "TRX/USDT:USDT",
    "ADA/USDT:USDT",
    ETH_PAIR,
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
    ZEC_PAIR,
}

TOP9_MAIN_PAIRS = {
    BTC_PAIR,
    ETH_PAIR,
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "TRX/USDT:USDT",
    "ADA/USDT:USDT",
    ZEC_PAIR,
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
}

```

### pairs\btc\profile.py

```python
PAIR = "BTC/USDT:USDT"

MAIN_ENABLED = True

REVERSAL_193_LONG_ENABLED = True
REVERSAL_193_SHORT_ENABLED = True

REVERSAL_216_LONG_ENABLED = False
REVERSAL_216_SHORT_ENABLED = True

MAIN_STAKE_MULTIPLIER = 1.0
REVERSAL_LONG_STAKE_MULTIPLIER = 1.0
REVERSAL_SHORT_STAKE_MULTIPLIER = 1.0

```

### pairs\eth\profile.py

```python
PAIR = "ETH/USDT:USDT"

MAIN_ENABLED = True

REVERSAL_193_LONG_ENABLED = True
REVERSAL_193_SHORT_ENABLED = True

REVERSAL_216_LONG_ENABLED = False
REVERSAL_216_SHORT_ENABLED = True

MAIN_STAKE_MULTIPLIER = 1.0
REVERSAL_LONG_STAKE_MULTIPLIER = 1.0
REVERSAL_SHORT_STAKE_MULTIPLIER = 1.0

```

### pairs\zec\profile.py

```python
PAIR = "ZEC/USDT:USDT"

MAIN_ENABLED = True

REVERSAL_193_LONG_ENABLED = False
REVERSAL_193_SHORT_ENABLED = True

REVERSAL_216_LONG_ENABLED = True
REVERSAL_216_SHORT_ENABLED = True

MAIN_STAKE_MULTIPLIER = 1.0
REVERSAL_LONG_STAKE_MULTIPLIER = 1.0
REVERSAL_SHORT_STAKE_MULTIPLIER = 1.0

```

### pairs\ada\trim.py

```python
def short_1h_center_multiplier(candle, bull: bool, bear: bool) -> float:
    return 0.96 if bear else 0.88 if bull else 1.0

```

### pairs\doge\trim.py

```python
def short_1h_center_multiplier(candle, bull: bool, bear: bool) -> float:
    return 0.88 if bear else 0.78 if bull else 1.0

```

### pairs\xrp\trim.py

```python
def short_1h_center_multiplier(candle, bull: bool, bear: bool) -> float:
    return 0.95 if bear else 0.86 if bull else 1.0

```
