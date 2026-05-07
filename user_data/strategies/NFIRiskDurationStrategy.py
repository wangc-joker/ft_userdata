from datetime import timedelta

from NFIRefactorStrategy import NFIRefactorStrategy


def _safe_ratio(value, fallback=0.0):
    try:
        if value != value:
            return fallback
        return float(value)
    except (TypeError, ValueError):
        return fallback


class NFIRiskDurationDynamicRiskBudgetVolatilityCap12TightRebuyScaleRecoveryCutGentleStrategy(
    NFIRefactorStrategy
):
    """
    Production candidate: NFI refactor with risk-duration controls.

    This is the retained strategy after the optimization experiments.  It keeps
    the NFI entry logic and grind engine, but adds these risk controls:
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

    def version(self) -> str:
        return "nfi-risk-duration-dynamic-risk-budget-volatility-cap-12-tight-rebuy-scale-recovery-cut-gentle-0.1.0"

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
        if side == "long" and self._is_grind120(entry_tag):
            min_allowed = min_stake if min_stake is not None else 0.0
            return max(stake * self.risk_grind_stake_scale, min_allowed)
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
                return adjustment

            recent_crash, stabilized = self._pair_recovery_state(trade.pair)
            if recent_crash and not stabilized:
                return None
            return adjustment

        if self._adjustment_amount(adjustment) <= 0:
            return adjustment

        scale = self._rebuy_volatility_scale(trade.pair)
        return self._scale_positive_adjustment_by_value(adjustment, scale)
