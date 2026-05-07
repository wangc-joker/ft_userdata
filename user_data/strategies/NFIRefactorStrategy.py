from NostalgiaForInfinityX7 import NostalgiaForInfinityX7
from nfi_refactor.entries import confirm_entry
from nfi_refactor.entries import trend as entry_trend
from nfi_refactor.exits import confirm_exit
from nfi_refactor.exits import custom_exit as custom_exit_module
from nfi_refactor.exits import dec as exit_dec
from nfi_refactor.exits import main as exit_main
from nfi_refactor.exits import mode_advanced as exit_mode_advanced
from nfi_refactor.exits import mode_scalp as exit_mode_scalp
from nfi_refactor.exits import mode_simple as exit_mode_simple
from nfi_refactor.exits import mode_top_coins as exit_mode_top_coins
from nfi_refactor.exits import profit_target as profit_target_module
from nfi_refactor.exits import signals as exit_signals
from nfi_refactor.exits import stoploss as exit_stoploss
from nfi_refactor.exits import trend as exit_trend
from nfi_refactor.exits import williams as exit_williams
from nfi_refactor.indicators import base_timeframe
from nfi_refactor.indicators import pipeline
from nfi_refactor.indicators.btc_informative import btc_info_indicators, btc_info_switcher
from nfi_refactor.indicators import pair_informative
from nfi_refactor.market_context.informative_pairs import build_informative_pairs
from nfi_refactor.position import adjustment as adjustment_module
from nfi_refactor.position import adjustment_helpers
from nfi_refactor.position import leverage as leverage_module
from nfi_refactor.position import order_events
from nfi_refactor.position import profit as profit_module
from nfi_refactor.position import rebuy_adjustment
from nfi_refactor.position import stake as stake_module
from nfi_refactor.state import hold_trades
from nfi_refactor.state import initialization
from nfi_refactor.state import runtime as runtime_state


class NFIRefactorStrategy(NostalgiaForInfinityX7):
    """
    Parity adapter for the NFI modular refactor.

    This first version intentionally inherits the original strategy behavior.
    We will move logic into modules step by step, with backtest parity checks
    after each extraction.
    """

    def __init__(self, config: dict) -> None:
        initialization.initialize_strategy(self, config)

    def version(self) -> str:
        return "nfi-refactor-parity-adapter-upstream-v17.4.43-0.2.0"

    def informative_pairs(self):
        return build_informative_pairs(
            pairs=self.dp.current_whitelist(),
            config=self.config,
            info_timeframes=self.info_timeframes,
            btc_info_timeframes=self.btc_info_timeframes,
        )

    def btc_info_1d_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_indicators(self, btc_info_pair, btc_info_timeframe, metadata)

    def btc_info_4h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_indicators(self, btc_info_pair, btc_info_timeframe, metadata)

    def btc_info_1h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_indicators(self, btc_info_pair, btc_info_timeframe, metadata)

    def btc_info_15m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_indicators(self, btc_info_pair, btc_info_timeframe, metadata)

    def btc_info_5m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_indicators(self, btc_info_pair, btc_info_timeframe, metadata)

    def btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata: dict):
        return btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata)

    def informative_1d_indicators(self, metadata: dict, info_timeframe):
        return pair_informative.informative_1d_indicators(self, metadata, info_timeframe)

    def informative_4h_indicators(self, metadata: dict, info_timeframe):
        return pair_informative.informative_4h_indicators(self, metadata, info_timeframe)

    def informative_1h_indicators(self, metadata: dict, info_timeframe):
        return pair_informative.informative_1h_indicators(self, metadata, info_timeframe)

    def informative_15m_indicators(self, metadata: dict, info_timeframe):
        return pair_informative.informative_15m_indicators(self, metadata, info_timeframe)

    def info_switcher(self, metadata: dict, info_timeframe):
        return pair_informative.info_switcher(self, metadata, info_timeframe)

    def base_tf_5m_indicators(self, metadata: dict, df):
        return base_timeframe.base_tf_5m_indicators(self, metadata, df)

    def populate_indicators(self, df, metadata: dict):
        return pipeline.populate_indicators(self, df, metadata)

    def populate_entry_trend(self, df, metadata: dict):
        # Upstream X7 v17.4.15 -> v17.4.43 changed many entry protections.
        # Delegate this surface to the parent until those changes are re-split.
        return super().populate_entry_trend(df, metadata)

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
        return confirm_entry.confirm_trade_entry(
            self,
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

    def _handle_grind_mode(self, pair: str, config: dict, current_time) -> bool:
        return confirm_entry.handle_grind_mode(pair, config, current_time)

    def _handle_top_coins_mode(self, pair: str, config: dict, current_time) -> bool:
        return confirm_entry.handle_top_coins_mode(pair, config, current_time)

    def _handle_scalp_mode(self, pair: str, config: dict, current_time) -> bool:
        return confirm_entry.handle_scalp_mode(self, pair, config, current_time)

    def confirm_trade_exit(
        self,
        pair: str,
        trade,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        exit_reason: str,
        current_time,
        **kwargs,
    ) -> bool:
        return confirm_exit.confirm_trade_exit(
            self,
            pair,
            trade,
            order_type,
            amount,
            rate,
            time_in_force,
            exit_reason,
            current_time,
            **kwargs,
        )

    def leverage(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag,
        side: str,
        **kwargs,
    ) -> float:
        return leverage_module.leverage(
            self,
            pair,
            current_time,
            current_rate,
            proposed_leverage,
            max_leverage,
            entry_tag,
            side,
            **kwargs,
        )

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
        return stake_module.custom_stake_amount(
            self,
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

    def correct_min_stake(self, min_stake: float) -> float:
        return stake_module.correct_min_stake(self, min_stake)

    def get_ticker_indicator(self):
        return runtime_state.get_ticker_indicator(self)

    def is_backtest_mode(self) -> bool:
        return runtime_state.is_backtest_mode(self)

    def is_system_v3(self, trade) -> bool:
        return runtime_state.is_system_v3(self, trade)

    def is_system_v3_1(self, trade) -> bool:
        return runtime_state.is_system_v3_1(self, trade)

    def is_system_v3_2(self, trade) -> bool:
        return runtime_state.is_system_v3_2(self, trade)

    def has_valid_entry_conditions(self, trade, exit_rate: float, last_candle, previous_candle) -> bool:
        return runtime_state.has_valid_entry_conditions(
            self, trade, exit_rate, last_candle, previous_candle
        )

    def update_signals_from_config(self, config):
        return runtime_state.update_signals_from_config(self, config)

    def _set_profit_target(
        self, pair: str, sell_reason: str, rate: float, current_profit: float, current_time
    ):
        return runtime_state.set_profit_target(
            self, pair, sell_reason, rate, current_profit, current_time
        )

    def _remove_profit_target(self, pair: str):
        return runtime_state.remove_profit_target(self, pair)

    def mark_profit_target(
        self,
        mode_name: str,
        pair: str,
        sell: bool,
        signal_name: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        last_candle,
        previous_candle_1,
    ) -> tuple:
        return profit_target_module.mark_profit_target(
            self,
            mode_name,
            pair,
            sell,
            signal_name,
            trade,
            current_time,
            current_rate,
            current_profit,
            last_candle,
            previous_candle_1,
        )

    def exit_profit_target(
        self,
        mode_name: str,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        profit_stake: float,
        profit_ratio: float,
        profit_current_stake_ratio: float,
        profit_init_ratio: float,
        last_candle,
        previous_candle_1,
        previous_rate,
        previous_profit,
        previous_sell_reason,
        previous_time_profit_reached,
        enter_tags,
    ) -> tuple:
        return profit_target_module.exit_profit_target(
            self,
            mode_name,
            pair,
            trade,
            current_time,
            current_rate,
            profit_stake,
            profit_ratio,
            profit_current_stake_ratio,
            profit_init_ratio,
            last_candle,
            previous_candle_1,
            previous_rate,
            previous_profit,
            previous_sell_reason,
            previous_time_profit_reached,
            enter_tags,
        )

    def calc_total_profit(self, trade, filled_entries, filled_exits, exit_rate: float) -> tuple:
        return profit_module.calc_total_profit(
            self, trade, filled_entries, filled_exits, exit_rate
        )

    def get_hold_trades_config_file(self):
        return hold_trades.get_hold_trades_config_file(self)

    def load_hold_trades_config(self):
        return hold_trades.load_hold_trades_config(self)

    def _should_hold_trade(self, trade, rate: float, sell_reason: str) -> bool:
        return hold_trades.should_hold_trade(self, trade, rate, sell_reason)

    def bot_loop_start(self, current_time, **kwargs) -> None:
        return initialization.bot_loop_start(self, current_time, **kwargs)

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        return custom_exit_module.custom_exit(
            self,
            pair,
            trade,
            current_time,
            current_rate,
            current_profit,
            **kwargs,
        )

    def populate_exit_trend(self, df, metadata: dict):
        return exit_trend.populate_exit_trend(self, df, metadata)

    def long_exit_grind(self, *args, **kwargs):
        return exit_mode_simple.long_exit_grind(self, *args, **kwargs)

    def long_exit_btc(self, *args, **kwargs):
        return exit_mode_simple.long_exit_btc(self, *args, **kwargs)

    def short_exit_grind(self, *args, **kwargs):
        return exit_mode_simple.short_exit_grind(self, *args, **kwargs)

    def long_exit_signals(self, *args, **kwargs):
        return exit_signals.long_exit_signals(self, *args, **kwargs)

    def short_exit_signals(self, *args, **kwargs):
        return exit_signals.short_exit_signals(self, *args, **kwargs)

    def long_exit_main(self, *args, **kwargs):
        return exit_main.long_exit_main(self, *args, **kwargs)

    def short_exit_main(self, *args, **kwargs):
        return exit_main.short_exit_main(self, *args, **kwargs)

    def long_exit_stoploss(self, *args, **kwargs):
        return exit_stoploss.long_exit_stoploss(self, *args, **kwargs)

    def short_exit_stoploss(self, *args, **kwargs):
        return exit_stoploss.short_exit_stoploss(self, *args, **kwargs)

    def long_exit_top_coins(self, *args, **kwargs):
        return exit_mode_top_coins.long_exit_top_coins(self, *args, **kwargs)

    def short_exit_top_coins(self, *args, **kwargs):
        return exit_mode_top_coins.short_exit_top_coins(self, *args, **kwargs)

    def long_exit_scalp(self, *args, **kwargs):
        return exit_mode_scalp.long_exit_scalp(self, *args, **kwargs)

    def short_exit_scalp(self, *args, **kwargs):
        return exit_mode_scalp.short_exit_scalp(self, *args, **kwargs)

    def long_exit_williams_r(self, *args, **kwargs):
        return exit_williams.long_exit_williams_r(self, *args, **kwargs)

    def short_exit_williams_r(self, *args, **kwargs):
        return exit_williams.short_exit_williams_r(self, *args, **kwargs)

    def long_exit_dec(self, *args, **kwargs):
        return exit_dec.long_exit_dec(self, *args, **kwargs)

    def short_exit_dec(self, *args, **kwargs):
        return exit_dec.short_exit_dec(self, *args, **kwargs)

    def long_exit_high_profit(self, *args, **kwargs):
        return exit_mode_advanced.long_exit_high_profit(self, *args, **kwargs)

    def short_exit_high_profit(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_high_profit(self, *args, **kwargs)

    def long_exit_normal(self, *args, **kwargs):
        return exit_mode_advanced.long_exit_normal(self, *args, **kwargs)

    def short_exit_normal(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_normal(self, *args, **kwargs)

    def long_exit_pump(self, *args, **kwargs):
        return exit_mode_advanced.long_exit_pump(self, *args, **kwargs)

    def short_exit_pump(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_pump(self, *args, **kwargs)

    def long_exit_quick(self, *args, **kwargs):
        return exit_mode_advanced.long_exit_quick(self, *args, **kwargs)

    def short_exit_quick(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_quick(self, *args, **kwargs)

    def long_exit_rapid(self, *args, **kwargs):
        return exit_mode_advanced.long_exit_rapid(self, *args, **kwargs)

    def short_exit_rapid(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_rapid(self, *args, **kwargs)

    def long_exit_rebuy(self, *args, **kwargs):
        return super().long_exit_rebuy(*args, **kwargs)

    def short_exit_rebuy(self, *args, **kwargs):
        return exit_mode_advanced.short_exit_rebuy(self, *args, **kwargs)

    def order_filled(self, pair: str, trade, order, current_time, **kwargs) -> None:
        return order_events.order_filled(self, pair, trade, order, current_time, **kwargs)

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
        # Upstream changed v3 rebuy/grind de-risk routing; keep parity first.
        return super().adjust_trade_position(
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

    def long_rebuy_adjust_trade_position(self, *args, **kwargs):
        return rebuy_adjustment.long_rebuy_adjust_trade_position(self, *args, **kwargs)

    def long_rebuy_adjust_trade_position_v3(self, *args, **kwargs):
        return super().long_rebuy_adjust_trade_position_v3(*args, **kwargs)

    def short_rebuy_adjust_trade_position(self, *args, **kwargs):
        return rebuy_adjustment.short_rebuy_adjust_trade_position(self, *args, **kwargs)

    def short_rebuy_adjust_trade_position_v3(self, *args, **kwargs):
        return super().short_rebuy_adjust_trade_position_v3(*args, **kwargs)

    def long_buyback_entry_v2(self, *args, **kwargs):
        return adjustment_helpers.long_buyback_entry_v2(self, *args, **kwargs)

    def long_grind_entry_v2(self, *args, **kwargs):
        return adjustment_helpers.long_grind_entry_v2(self, *args, **kwargs)

    def long_buyback_exit_v2(self, *args, **kwargs):
        return adjustment_helpers.long_buyback_exit_v2(self, *args, **kwargs)

    def long_grind_exit_v2(self, *args, **kwargs):
        return adjustment_helpers.long_grind_exit_v2(self, *args, **kwargs)

    def long_grind_entry_v3(self, *args, **kwargs):
        return super().long_grind_entry_v3(*args, **kwargs)

    def long_buyback_entry_v3(self, *args, **kwargs):
        return adjustment_helpers.long_buyback_entry_v3(self, *args, **kwargs)

    def long_rebuy_entry_v3(self, *args, **kwargs):
        return adjustment_helpers.long_rebuy_entry_v3(self, *args, **kwargs)

    def long_grind_entry(self, *args, **kwargs):
        return adjustment_helpers.long_grind_entry(self, *args, **kwargs)

    def short_buyback_entry_v2(self, *args, **kwargs):
        return adjustment_helpers.short_buyback_entry_v2(self, *args, **kwargs)

    def short_grind_entry_v2(self, *args, **kwargs):
        return adjustment_helpers.short_grind_entry_v2(self, *args, **kwargs)

    def short_buyback_exit_v2(self, *args, **kwargs):
        return adjustment_helpers.short_buyback_exit_v2(self, *args, **kwargs)

    def short_grind_exit_v2(self, *args, **kwargs):
        return adjustment_helpers.short_grind_exit_v2(self, *args, **kwargs)

    def short_grind_entry_v3(self, *args, **kwargs):
        return super().short_grind_entry_v3(*args, **kwargs)

    def short_rebuy_entry_v3(self, *args, **kwargs):
        return adjustment_helpers.short_rebuy_entry_v3(self, *args, **kwargs)

    def short_grind_entry(self, *args, **kwargs):
        return adjustment_helpers.short_grind_entry(self, *args, **kwargs)
