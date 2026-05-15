import json
from datetime import timedelta
from pathlib import Path

from NostalgiaForInfinityX7 import NostalgiaForInfinityX7


def _safe_ratio(value, fallback=0.0):
    try:
        if value != value:
            return fallback
        return float(value)
    except (TypeError, ValueError):
        return fallback


class NFIRiskDurationDynamicRiskBudgetVolatilityCap12TightRebuyScaleRecoveryCutGentleStrategy(
    NostalgiaForInfinityX7
):
    """
    Production candidate: NFI original wrapper with risk-duration controls.

    This wrapper inherits the original NostalgiaForInfinityX7 directly.
    Updating upstream NFI only requires replacing NostalgiaForInfinityX7.py,
    while this file keeps the RecoveryCutGentle risk overlay:
    - smaller tag-120 initial/add exposure,
    - dynamic tag-120 risk budget based on account growth and pair volatility,
    - stabilized confirmation before adding to falling tag-120 trades,
    - volatility scaling for non-tag-120 positive position adjustments,
    - gentle stale tag-120 release rules.
    """

    # Soft release / deep-loss protection inherited from the best experiment chain.
    risk_flash_crash_stop = -0.38
    risk_aged_loss_stop = -0.22
    risk_aged_loss_days = 4
    risk_grind_deep_loss_stop = -0.18
    risk_grind_deep_loss_days = 10
    risk_grind_timeout_days = 60
    risk_grind_timeout_profit_ceiling = 0.025
    risk_max_hold_days = 90
    risk_max_hold_profit_ceiling = 0.01

    # Tag-120 stake and budget controls.
    risk_grind_stake_scale = 0.65
    risk_grind_adjustment_scale = 0.65
    risk_grind_initial_budget_ratio = 0.22
    risk_grind_profit_budget_ratio = 0.012

    # Age-aware tag-120 add/exit controls.
    risk_grind_freeze_add_days = 14
    risk_grind_freeze_add_profit = -0.06
    risk_grind_time_cut_days = 28
    risk_grind_time_cut_profit = -0.04
    risk_grind_stale_cut_days = 45
    risk_grind_stale_cut_profit = 0.015

    # Stabilized-add confirmation for tag-120 trades.
    risk_grind_stabilized_profit = -0.01
    risk_grind_recent_crash_roc_4h = -8.0
    risk_grind_recent_crash_roc_24h = -15.0
    risk_grind_stable_roc_1h = -2.0
    risk_grind_stable_bounce_from_1h_low = 1.2
    risk_grind_stable_close_vs_15m = 0.0

    # Volatility-aware tag-120 budget controls.
    risk_vol_budget_min_scale = 0.45
    risk_vol_daily_soft = 12.0
    risk_vol_daily_hard = 30.0
    risk_vol_range_soft = 22.0
    risk_vol_range_hard = 50.0
    risk_vol_drop_soft = 6.0
    risk_vol_drop_hard = 18.0
    risk_vol_volume_soft = 2.0
    risk_vol_volume_hard = 5.0

    # Non-tag-120 rebuy scaling.
    risk_rebuy_scale_min = 0.60
    risk_rebuy_pressure_start = 0.55

    # Gentle stale-grind release controls.
    risk_recovery_weak_days = 24
    risk_recovery_weak_profit = -0.03
    risk_recovery_stale_days = 40
    risk_recovery_stale_profit = 0.02
    risk_recovery_hot_loss_days = 10
    risk_recovery_hot_loss_profit = -0.16
    risk_recovery_hot_pressure = 0.85

    # Volume-tier capital safety belt.  This caps order size, but keeps the NFI
    # signal / grind / rebuy decision engine intact.
    volume_tier_file = "config/pair_volume_tiers.json"
    volume_tier_first_cap_enabled = True
    volume_tier_adjustment_cap_enabled = True
    # 10,000,000 USDT 24h volume -> max 1,000 USDT first order.
    # Larger markets scale linearly, so this is a liquidity ceiling rather than
    # an account-size ceiling.
    volume_first_cap_per_10m = 1000.0
    volume_first_cap_base_volume = 10_000_000.0
    volume_absolute_first_cap = None
    volume_bracket_first_caps = [
        (1_000_000_000.0, 3000.0),
        (100_000_000.0, 2000.0),
        (50_000_000.0, 1000.0),
        (0.0, 500.0),
    ]
    volume_tier_params = {
        "L5": {
            "max_adds": 2,
            "total_first_mult": 3.0,
            "add_first_mult": 1.0,
        },
        "L4": {
            "max_adds": 2,
            "total_first_mult": 3.0,
            "add_first_mult": 1.0,
        },
        "L3": {
            "max_adds": 2,
            "total_first_mult": 3.0,
            "add_first_mult": 1.0,
        },
        "L2": {
            "max_adds": 1,
            "total_first_mult": 2.0,
            "add_first_mult": 1.0,
        },
        "L1": {
            "max_adds": 0,
            "total_first_mult": 1.0,
            "add_first_mult": 0.0,
        },
    }

    def version(self) -> str:
        return "nfi-original-wrapper-recovery-cut-gentle-volume-tier-cap-0.5.0"

    def bot_start(self, **kwargs):
        try:
            super().bot_start(**kwargs)
        except AttributeError:
            pass
        self.load_volume_tiers()

    def _volume_tier_path_candidates(self):
        configured = Path(str(self.volume_tier_file))
        candidates = [configured]

        user_data_dir = self.config.get("user_data_dir") if hasattr(self, "config") else None
        if user_data_dir:
            user_data_dir = Path(str(user_data_dir))
            candidates.extend(
                [
                    user_data_dir / configured,
                    user_data_dir / "config" / "pair_volume_tiers.json",
                ]
            )

        cwd = Path.cwd()
        candidates.extend(
            [
                cwd / configured,
                cwd / "user_data" / configured,
                cwd / "user_data" / "config" / "pair_volume_tiers.json",
                Path("/freqtrade/user_data/config/pair_volume_tiers.json"),
            ]
        )

        seen = set()
        unique = []
        for path in candidates:
            key = str(path)
            if key not in seen:
                unique.append(path)
                seen.add(key)
        return unique

    def load_volume_tiers(self):
        self.pair_to_volume_tier = {}
        self.pair_to_volume = {}

        for path in self._volume_tier_path_candidates():
            try:
                if not path.exists():
                    continue
                with path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                break
            except Exception:
                data = None
        else:
            data = None

        if not data:
            return

        for tier, obj in data.get("tiers", {}).items():
            for pair in obj.get("pairs", []):
                self.pair_to_volume_tier[str(pair)] = tier

        for pair, volume in data.get("volumes", {}).items():
            self.pair_to_volume[str(pair)] = _safe_ratio(volume, 0.0)

    def _pair_keys(self, pair: str):
        pair = str(pair)
        keys = [pair]
        if ":USDT" in pair:
            keys.append(pair.replace(":USDT", ""))
        if "/" in pair:
            keys.append(pair.replace("/", "").replace(":USDT", ""))
        return keys

    def get_pair_tier(self, pair: str) -> str:
        if not hasattr(self, "pair_to_volume_tier"):
            self.load_volume_tiers()

        for key in self._pair_keys(pair):
            tier = self.pair_to_volume_tier.get(key)
            if tier:
                return tier
        return "L0"

    def get_pair_24h_volume(self, pair: str):
        if not hasattr(self, "pair_to_volume"):
            self.load_volume_tiers()

        for key in self._pair_keys(pair):
            if key in self.pair_to_volume:
                return self.pair_to_volume[key]
        return None

    def _tier_config(self, pair: str):
        return self.volume_tier_params.get(self.get_pair_tier(pair))

    def _configured_max_adds(self) -> int:
        value = self.config.get("max_entry_position_adjustment", 0)
        try:
            return max(int(value or 0), 0)
        except (TypeError, ValueError):
            return 0

    def _volume_cap_capital(self, fallback: float) -> float:
        wallets = getattr(self, "wallets", None)
        if wallets is not None:
            try:
                value = _safe_ratio(wallets.get_total_stake_amount(), 0.0)
                if value > 0:
                    return value
            except Exception:
                pass
        equity = self._current_wallet_equity()
        return equity if equity > 0 else fallback

    def _volume_custom_config(self) -> dict:
        config = getattr(self, "config", {}) or {}
        value = config.get("nfi_volume_tier", {})
        return value if isinstance(value, dict) else {}

    def _volume_absolute_first_cap(self):
        custom = self._volume_custom_config()
        value = custom.get("absolute_first_cap", self.volume_absolute_first_cap)
        if value is None:
            return None
        value = _safe_ratio(value, 0.0)
        return value if value > 0 else None

    def _volume_bracket_first_cap(self, pair: str):
        custom = self._volume_custom_config()
        if custom.get("use_volume_bracket_first_cap", True) is False:
            return None

        volume = self.get_pair_24h_volume(pair)
        if volume is None:
            return None

        brackets = custom.get("volume_bracket_first_caps", self.volume_bracket_first_caps)
        for min_volume, cap in brackets:
            if volume >= _safe_ratio(min_volume, 0.0):
                cap = _safe_ratio(cap, 0.0)
                return cap if cap > 0 else None
        return None

    def _volume_first_order_cap(self, pair: str):
        volume = self.get_pair_24h_volume(pair)
        if not volume:
            return None
        base_volume = max(_safe_ratio(self.volume_first_cap_base_volume, 0.0), 1.0)
        base_cap = _safe_ratio(self.volume_first_cap_per_10m, 0.0)
        return volume / base_volume * base_cap

    def _volume_first_cap(self, pair: str, stake: float, proposed_stake: float, min_stake, max_stake):
        if not self.volume_tier_first_cap_enabled:
            return stake

        tier_cfg = self._tier_config(pair)
        if tier_cfg is None:
            return 0.0

        max_stake = proposed_stake if max_stake is None else max_stake
        capital = self._volume_cap_capital(max_stake or proposed_stake)
        slots = max(int(self.config.get("max_open_trades", 1) or 1), 1)

        # First entry uses an equal account split, then liquidity caps it only
        # when the pair is too small for that order size.
        budget_first_cap = capital / slots
        volume_first_cap = self._volume_first_order_cap(pair)
        caps = [stake, budget_first_cap, max_stake]
        if volume_first_cap is not None:
            caps.append(volume_first_cap)
        absolute_first_cap = self._volume_absolute_first_cap()
        if absolute_first_cap is not None:
            caps.append(absolute_first_cap)
        bracket_first_cap = self._volume_bracket_first_cap(pair)
        if bracket_first_cap is not None:
            caps.append(bracket_first_cap)

        capped = min(caps)
        if min_stake is not None and capped < min_stake:
            return 0.0
        return capped

    def _first_entry_stake(self, trade) -> float:
        try:
            entries = trade.select_filled_orders(trade.entry_side)
            if entries:
                return _safe_ratio(entries[0].cost, 0.0)
        except Exception:
            pass

        entries_count = max(int(getattr(trade, "nr_of_successful_entries", 1) or 1), 1)
        stake = _safe_ratio(getattr(trade, "stake_amount", 0.0), 0.0)
        return stake / entries_count

    def _replace_adjustment_amount(self, adjustment, amount: float):
        if isinstance(adjustment, tuple):
            return (amount, *adjustment[1:])
        return amount

    def _cap_adjustment_to_volume_tier(self, trade, adjustment, min_stake, max_stake):
        if not self.volume_tier_adjustment_cap_enabled or adjustment is None:
            return adjustment

        amount = self._adjustment_amount(adjustment)
        if amount <= 0:
            return adjustment

        tier_cfg = self._tier_config(trade.pair)
        if tier_cfg is None:
            return None

        max_adds = int(tier_cfg["max_adds"])
        already_added = max(int(getattr(trade, "nr_of_successful_entries", 1) or 1) - 1, 0)
        if already_added >= max_adds:
            return None

        max_stake = amount if max_stake is None else max_stake
        first_entry_stake = self._first_entry_stake(trade)
        if first_entry_stake <= 0:
            first_entry_stake = _safe_ratio(getattr(trade, "stake_amount", 0.0), 0.0)

        volume_first_cap = self._volume_first_order_cap(trade.pair)
        volume_total_cap = volume_first_cap * (1 + max_adds) if volume_first_cap is not None else None
        first_total_cap = first_entry_stake * tier_cfg["total_first_mult"]
        pair_total_caps = [first_total_cap]
        if volume_total_cap is not None:
            pair_total_caps.append(volume_total_cap)
        pair_total_cap = min(pair_total_caps)

        current_stake = _safe_ratio(getattr(trade, "stake_amount", 0.0), 0.0)
        remaining_budget = pair_total_cap - current_stake
        if remaining_budget <= 0:
            return None

        single_add_cap = first_entry_stake * tier_cfg["add_first_mult"]
        capped = min(amount, remaining_budget, single_add_cap, max_stake)
        if min_stake is not None and capped < min_stake:
            return None
        return self._replace_adjustment_amount(adjustment, capped)

    def populate_indicators(self, df, metadata: dict):
        df = super().populate_indicators(df, metadata)

        df["risk_stable_roc_1h"] = (df["close"] / df["close"].shift(12) - 1.0) * 100.0
        df["risk_stable_roc_4h"] = (df["close"] / df["close"].shift(48) - 1.0) * 100.0
        df["risk_stable_roc_24h"] = (df["close"] / df["close"].shift(288) - 1.0) * 100.0
        df["risk_stable_low_1h"] = df["close"].rolling(12, min_periods=3).min()
        df["risk_stable_bounce_1h"] = (df["close"] / df["risk_stable_low_1h"] - 1.0) * 100.0
        df["risk_stable_close_vs_15m"] = (df["close"] / df["close"].shift(3) - 1.0) * 100.0

        df["risk_vol_return_5m"] = df["close"].pct_change()
        df["risk_vol_realized_24h"] = (
            df["risk_vol_return_5m"].rolling(288, min_periods=72).std()
            * (288 ** 0.5)
            * 100.0
        )
        df["risk_vol_high_24h"] = df["high"].rolling(288, min_periods=72).max()
        df["risk_vol_low_24h"] = df["low"].rolling(288, min_periods=72).min()
        df["risk_vol_range_24h"] = (df["risk_vol_high_24h"] / df["risk_vol_low_24h"] - 1.0) * 100.0
        df["risk_vol_drop_24h"] = (df["close"] / df["close"].shift(288) - 1.0) * 100.0
        df["risk_vol_volume_mean_24h"] = df["volume"].rolling(288, min_periods=72).mean()
        df["risk_vol_volume_ratio_24h"] = df["volume"] / df["risk_vol_volume_mean_24h"]
        return df

    def _entry_tags(self, entry_tag) -> set[str]:
        return set(str(entry_tag or "").split())

    def _is_grind120(self, entry_tag) -> bool:
        return "120" in self._entry_tags(entry_tag)

    def _trade_age(self, trade, current_time):
        open_time = getattr(trade, "open_date_utc", None) or getattr(trade, "open_date", None)
        if open_time is None:
            return timedelta(0)
        if getattr(open_time, "tzinfo", None) is not None and getattr(current_time, "tzinfo", None) is None:
            open_time = open_time.replace(tzinfo=None)
        elif getattr(open_time, "tzinfo", None) is None and getattr(current_time, "tzinfo", None) is not None:
            current_time = current_time.replace(tzinfo=None)
        return current_time - open_time

    def _initial_wallet(self) -> float:
        wallet = _safe_ratio(self.config.get("dry_run_wallet"), 0.0)
        if wallet <= 0:
            wallet = _safe_ratio(self.config.get("available_capital"), 0.0)
        return wallet

    def _current_wallet_equity(self) -> float:
        wallets = getattr(self, "wallets", None)
        stake_currency = self.config.get("stake_currency")
        if wallets is not None and stake_currency:
            for method_name in ("get_total", "get_total_stake_amount"):
                method = getattr(wallets, method_name, None)
                if method is None:
                    continue
                try:
                    value = method(stake_currency) if method_name == "get_total" else method()
                    value = _safe_ratio(value, 0.0)
                    if value > 0:
                        return value
                except Exception:
                    pass

        return self._initial_wallet()

    def _pressure_from_high_value(self, value: float, soft: float, hard: float) -> float:
        value = _safe_ratio(value, 0.0)
        if value <= soft:
            return 0.0
        if value >= hard:
            return 1.0
        return (value - soft) / (hard - soft)

    def _pressure_from_drop(self, value: float) -> float:
        decline = max(-_safe_ratio(value, 0.0), 0.0)
        if decline <= self.risk_vol_drop_soft:
            return 0.0
        if decline >= self.risk_vol_drop_hard:
            return 1.0
        return (decline - self.risk_vol_drop_soft) / (
            self.risk_vol_drop_hard - self.risk_vol_drop_soft
        )

    def _volatility_budget_scale(self, pair: str) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return 1.0

        candle = dataframe.iloc[-1]
        pressure = max(
            self._pressure_from_high_value(
                candle.get("risk_vol_realized_24h"),
                self.risk_vol_daily_soft,
                self.risk_vol_daily_hard,
            ),
            self._pressure_from_high_value(
                candle.get("risk_vol_range_24h"),
                self.risk_vol_range_soft,
                self.risk_vol_range_hard,
            ),
            self._pressure_from_high_value(
                candle.get("risk_vol_volume_ratio_24h"),
                self.risk_vol_volume_soft,
                self.risk_vol_volume_hard,
            ),
            self._pressure_from_drop(candle.get("risk_vol_drop_24h")),
        )

        pressure = max(0.0, min(pressure, 1.0))
        return 1.0 - ((1.0 - self.risk_vol_budget_min_scale) * pressure)

    def _volatility_pressure(self, pair: str) -> float:
        budget_scale = self._volatility_budget_scale(pair)
        denominator = max(1.0 - self.risk_vol_budget_min_scale, 0.000001)
        pressure = (1.0 - budget_scale) / denominator
        return max(0.0, min(pressure, 1.0))

    def _available_trade_budget(self, trade) -> float:
        initial_wallet = self._initial_wallet()
        current_equity = self._current_wallet_equity()
        if initial_wallet <= 0 and current_equity <= 0:
            return 0.0

        initial_budget = initial_wallet * self.risk_grind_initial_budget_ratio
        equity_growth = max(current_equity - initial_wallet, 0.0)
        growth_budget = equity_growth * self.risk_grind_profit_budget_ratio
        max_exposure = initial_budget + growth_budget
        max_exposure *= self._volatility_budget_scale(getattr(trade, "pair", ""))

        current_exposure = _safe_ratio(getattr(trade, "stake_amount", 0.0), 0.0)
        return max(max_exposure - current_exposure, 0.0)

    def _adjustment_amount(self, adjustment) -> float:
        if adjustment is None:
            return 0.0
        if isinstance(adjustment, tuple):
            return _safe_ratio(adjustment[0], 0.0)
        return _safe_ratio(adjustment, 0.0)

    def _scale_positive_adjustment_by_value(self, adjustment, scale: float):
        if adjustment is None or scale >= 0.999:
            return adjustment

        if isinstance(adjustment, tuple):
            amount = adjustment[0]
            if amount is not None and amount > 0:
                return (amount * scale, *adjustment[1:])
            return adjustment

        if adjustment > 0:
            return adjustment * scale
        return adjustment

    def _cap_adjustment_to_budget(self, trade, adjustment):
        if adjustment is None:
            return None

        budget = self._available_trade_budget(trade)
        if budget <= 0:
            amount = adjustment[0] if isinstance(adjustment, tuple) else adjustment
            if amount is not None and amount > 0:
                return None
            return adjustment

        if isinstance(adjustment, tuple):
            amount = adjustment[0]
            if amount is not None and amount > 0:
                return (min(amount, budget), *adjustment[1:])
            return adjustment

        if adjustment > 0:
            return min(adjustment, budget)
        return adjustment

    def _rebuy_volatility_scale(self, pair: str) -> float:
        pressure = self._volatility_pressure(pair)
        if pressure <= self.risk_rebuy_pressure_start:
            return 1.0

        active_pressure = (pressure - self.risk_rebuy_pressure_start) / (
            1.0 - self.risk_rebuy_pressure_start
        )
        active_pressure = max(0.0, min(active_pressure, 1.0))
        return 1.0 - ((1.0 - self.risk_rebuy_scale_min) * active_pressure)

    def _pair_recovery_state(self, pair: str) -> tuple[bool, bool]:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return False, True

        current_candle = dataframe.iloc[-1]
        roc_1h = _safe_ratio(current_candle.get("risk_stable_roc_1h"), 0.0)
        roc_4h = _safe_ratio(current_candle.get("risk_stable_roc_4h"), 0.0)
        roc_24h = _safe_ratio(current_candle.get("risk_stable_roc_24h"), 0.0)
        bounce_1h = _safe_ratio(current_candle.get("risk_stable_bounce_1h"), 0.0)
        close_vs_15m = _safe_ratio(current_candle.get("risk_stable_close_vs_15m"), 0.0)

        recent_crash = (
            roc_4h <= self.risk_grind_recent_crash_roc_4h
            or roc_24h <= self.risk_grind_recent_crash_roc_24h
        )
        stabilized = (
            roc_1h >= self.risk_grind_stable_roc_1h
            and bounce_1h >= self.risk_grind_stable_bounce_from_1h_low
            and close_vs_15m >= self.risk_grind_stable_close_vs_15m
        )
        return recent_crash, stabilized

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake,
        max_stake: float,
        leverage: float,
        entry_tag,
        side: str,
        **kwargs,
    ) -> float:
        try:
            stake = super().custom_stake_amount(
                pair,
                current_time,
                current_rate,
                proposed_stake,
                min_stake,
                max_stake,
                leverage,
                entry_tag,
                side,
                **kwargs,
            )
        except AttributeError:
            stake = proposed_stake

        if stake is None:
            stake = proposed_stake

        if side == "long" and self._is_grind120(entry_tag):
            min_allowed = min_stake if min_stake is not None else 0.0
            stake = max(stake * self.risk_grind_stake_scale, min_allowed)

        return self._volume_first_cap(pair, stake, proposed_stake, min_stake, max_stake)

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag,
        side: str,
        **kwargs,
    ) -> bool:
        if self.get_pair_tier(pair) == "L0":
            return False

        return super().confirm_trade_entry(
            pair,
            order_type,
            amount,
            rate,
            time_in_force,
            current_time,
            entry_tag,
            side,
            **kwargs,
        )

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        tags = self._entry_tags(getattr(trade, "enter_tag", None))
        is_grind120 = "120" in tags
        age = self._trade_age(trade, current_time)

        if is_grind120:
            pressure = self._volatility_pressure(pair)

            if age >= timedelta(days=self.risk_recovery_hot_loss_days):
                if (
                    current_profit <= self.risk_recovery_hot_loss_profit
                    and pressure >= self.risk_recovery_hot_pressure
                ):
                    return "risk_grind_hot_loss_release"

            if age >= timedelta(days=self.risk_recovery_weak_days):
                if current_profit <= self.risk_recovery_weak_profit:
                    return "risk_grind_weak_recovery_release"

            if age >= timedelta(days=self.risk_recovery_stale_days):
                if current_profit <= self.risk_recovery_stale_profit:
                    return "risk_grind_stale_recovery_release"

            if age >= timedelta(days=self.risk_grind_time_cut_days):
                if current_profit <= self.risk_grind_time_cut_profit:
                    return "risk_grind_time_cut"

            if age >= timedelta(days=self.risk_grind_stale_cut_days):
                if current_profit <= self.risk_grind_stale_cut_profit:
                    return "risk_grind_stale_cut"

            if age >= timedelta(days=self.risk_grind_deep_loss_days):
                if current_profit <= self.risk_grind_deep_loss_stop:
                    return "risk_grind_deep_loss"

        if current_profit <= self.risk_flash_crash_stop:
            return "risk_flash_crash_stop"

        if age >= timedelta(days=self.risk_aged_loss_days) and current_profit <= self.risk_aged_loss_stop:
            return "risk_aged_loss_stop"

        if is_grind120 and age >= timedelta(days=self.risk_grind_timeout_days):
            if current_profit <= self.risk_grind_timeout_profit_ceiling:
                return "risk_grind_soft_timeout"

        if age >= timedelta(days=self.risk_max_hold_days):
            if current_profit <= self.risk_max_hold_profit_ceiling:
                return "risk_soft_max_hold"

        return super().custom_exit(
            pair,
            trade,
            current_time,
            current_rate,
            current_profit,
            **kwargs,
        )

    def adjust_trade_position(
        self,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake,
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ):
        is_grind120 = self._is_grind120(getattr(trade, "enter_tag", None))

        if is_grind120:
            age = self._trade_age(trade, current_time)
            if age >= timedelta(days=self.risk_grind_freeze_add_days):
                if current_profit <= self.risk_grind_freeze_add_profit:
                    return None

        adjustment = super().adjust_trade_position(
            trade,
            current_time,
            current_rate,
            current_profit,
            min_stake,
            max_stake,
            current_entry_rate,
            current_exit_rate,
            current_entry_profit,
            current_exit_profit,
            **kwargs,
        )

        if is_grind120:
            adjustment = self._scale_positive_adjustment_by_value(
                adjustment,
                self.risk_grind_adjustment_scale,
            )
            adjustment = self._cap_adjustment_to_budget(trade, adjustment)
            if self._adjustment_amount(adjustment) <= 0:
                return adjustment
            if current_profit > self.risk_grind_stabilized_profit:
                return self._cap_adjustment_to_volume_tier(trade, adjustment, min_stake, max_stake)

            recent_crash, stabilized = self._pair_recovery_state(trade.pair)
            if recent_crash and not stabilized:
                return None
            return self._cap_adjustment_to_volume_tier(trade, adjustment, min_stake, max_stake)

        if self._adjustment_amount(adjustment) <= 0:
            return adjustment

        scale = self._rebuy_volatility_scale(trade.pair)
        adjustment = self._scale_positive_adjustment_by_value(adjustment, scale)
        return self._cap_adjustment_to_volume_tier(trade, adjustment, min_stake, max_stake)
