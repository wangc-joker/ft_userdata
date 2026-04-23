# NostalgiaForInfinityX7 函数索引

这个文件是自动提取的函数/类索引，方便你阅读主文档时快速定位源码位置。

| 行号 | 定义 |
| ---: | --- |
| 68 | `class NostalgiaForInfinityX7(IStrategy):` |
| 71 | `def version(self) -> str:` |
| 880 | `def __init__(self, config: dict) -> None:` |
| 1000 | `def plot_config(self):` |
| 1019 | `def get_ticker_indicator(self):` |
| 1024 | `def mark_profit_target(` |
| 1044 | `def exit_profit_target(` |
| 1707 | `def calc_total_profit(` |
| 1761 | `def custom_exit(` |
| 2345 | `def custom_stake_amount(` |
| 2498 | `def order_filled(self, pair: str, trade: Trade, order: Order, current_time: datetime, **kwargs) -> None:` |
| 2511 | `def adjust_trade_position(` |
| 2814 | `def notification_msg(` |
| 2947 | `def informative_pairs(self):` |
| 2984 | `def informative_1d_indicators(self, metadata: dict, info_timeframe) -> DataFrame:` |
| 3108 | `def informative_4h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:` |
| 3268 | `def informative_1h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:` |
| 3425 | `def informative_15m_indicators(self, metadata: dict, info_timeframe) -> DataFrame:` |
| 3537 | `def base_tf_5m_indicators(self, metadata: dict, df: DataFrame) -> DataFrame:` |
| 3703 | `def info_switcher(self, metadata: dict, info_timeframe) -> DataFrame:` |
| 3717 | `def btc_info_1d_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3755 | `def btc_info_4h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3773 | `def btc_info_1h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3791 | `def btc_info_15m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3809 | `def btc_info_5m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3827 | `def btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:` |
| 3843 | `def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:` |
| 11465 | `def confirm_trade_entry(` |
| 11551 | `def _handle_grind_mode(self, pair: str, config: dict, current_time: datetime) -> bool:` |
| 11565 | `def _handle_top_coins_mode(self, pair: str, config: dict, current_time: datetime) -> bool:` |
| 11572 | `def _handle_scalp_mode(self, pair: str, config: dict, current_time: datetime) -> bool:` |
| 11581 | `def confirm_trade_exit(` |
| 11624 | `def bot_loop_start(self, current_time: datetime, **kwargs) -> None:` |
| 11635 | `def leverage(` |
| 11655 | `def correct_min_stake(self, min_stake: float) -> float:` |
| 11662 | `def is_backtest_mode(self) -> bool:` |
| 11666 | `def is_system_v3(self, trade: Trade) -> bool:` |
| 11670 | `def is_system_v3_1(self, trade: Trade) -> bool:` |
| 11674 | `def is_system_v3_2(self, trade: Trade) -> bool:` |
| 11678 | `def has_valid_entry_conditions(self, trade: Trade, exit_rate: float, last_candle, previous_candle) -> bool:` |
| 11692 | `def update_signals_from_config(self, config):` |
| 11707 | `def _set_profit_target(` |
| 11720 | `def _remove_profit_target(self, pair: str):` |
| 11727 | `def get_hold_trades_config_file(self):` |
| 11754 | `def load_hold_trades_config(self):` |
| 11766 | `def _should_hold_trade(self, trade: "Trade", rate: float, sell_reason: str) -> bool:` |
| 11859 | `def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:` |
| 11889 | `def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:` |
| 25177 | `def long_exit_normal(` |
| 25436 | `def long_exit_pump(` |
| 25687 | `def long_exit_quick(` |
| 25977 | `def long_exit_rebuy(` |
| 26254 | `def long_exit_high_profit(` |
| 26484 | `def long_exit_rapid(` |
| 26815 | `def long_exit_grind(` |
| 26846 | `def long_exit_btc(` |
| 26877 | `def long_exit_top_coins(` |
| 27134 | `def long_exit_scalp(` |
| 27412 | `def long_exit_signals(` |
| 27509 | `def long_exit_main(` |
| 27612 | `def long_exit_williams_r(` |
| 29299 | `def long_exit_dec(` |
| 43115 | `def long_exit_stoploss(` |
| 43253 | `def long_grind_adjust_trade_position_v2(` |
| 45291 | `def long_buyback_entry_v2(` |
| 45382 | `def long_grind_entry_v2(` |
| 45631 | `def long_buyback_exit_v2(` |
| 45646 | `def long_grind_exit_v2(` |
| 45663 | `def long_grind_adjust_trade_position_v3(` |
| 47282 | `def long_grind_entry_v3(` |
| 47531 | `def long_buyback_entry_v3(` |
| 47547 | `def long_rebuy_entry_v3(` |
| 47564 | `def long_grind_adjust_trade_position(` |
| 49675 | `def long_grind_entry(` |
| 49768 | `def long_adjust_trade_position_no_derisk(` |
| 51235 | `def long_rebuy_adjust_trade_position(` |
| 51422 | `def long_rebuy_adjust_trade_position_v3(` |
| 51597 | `def short_exit_normal(` |
| 51856 | `def short_exit_pump(` |
| 52107 | `def short_exit_quick(` |
| 52397 | `def short_exit_rebuy(` |
| 52674 | `def short_exit_high_profit(` |
| 52904 | `def short_exit_rapid(` |
| 53235 | `def short_exit_grind(` |
| 53266 | `def short_exit_top_coins(` |
| 53523 | `def short_exit_scalp(` |
| 53801 | `def short_exit_signals(` |
| 53898 | `def short_exit_main(` |
| 54001 | `def short_exit_williams_r(` |
| 55688 | `def short_exit_dec(` |
| 69504 | `def short_exit_stoploss(` |
| 69643 | `def short_grind_adjust_trade_position_v2(` |
| 71663 | `def short_buyback_entry_v2(` |
| 71754 | `def short_grind_entry_v2(` |
| 72003 | `def short_buyback_exit_v2(` |
| 72018 | `def short_grind_exit_v2(` |
| 72035 | `def short_grind_adjust_trade_position_v3(` |
| 73389 | `def short_grind_entry_v3(` |
| 73638 | `def short_rebuy_entry_v3(` |
| 73657 | `def short_grind_adjust_trade_position(` |
| 75706 | `def short_grind_entry(` |
| 75799 | `def short_adjust_trade_position_no_derisk(` |
| 77266 | `def short_rebuy_adjust_trade_position(` |
| 77443 | `def short_rebuy_adjust_trade_position_v3(` |
| 77596 | `def is_support(row_data) -> bool:` |
| 77609 | `def is_resistance(row_data) -> bool:` |
| 77622 | `def ewo(df, ema1_length=5, ema2_length=35):` |
| 77631 | `def pivot_points(df: DataFrame, mode="fibonacci") -> Series:` |
| 77668 | `def heikin_ashi(df, smooth_inputs=False, smooth_outputs=False, length=10):` |
| 77704 | `def range_percent_change(self, df: DataFrame, method, length: int) -> float:` |
| 77722 | `def top_percent_change(self, df: DataFrame, length: int) -> float:` |
| 77742 | `class Cache:` |
| 77743 | `def __init__(self, path):` |
| 77754 | `def rapidjson_load_kwargs():` |
| 77758 | `def rapidjson_dump_kwargs():` |
| 77761 | `def load(self):` |
| 77765 | `def save(self):` |
| 77769 | `def process_loaded_data(self, data):` |
| 77772 | `def _load(self):` |
| 77784 | `def _save(self):` |
| 77791 | `class HoldsCache(Cache):` |
| 77793 | `def rapidjson_load_kwargs():` |
| 77801 | `def rapidjson_dump_kwargs():` |
| 77807 | `def save(self):` |
| 77810 | `def process_loaded_data(self, data):` |
| 77921 | `def _object_hook(data):` |
