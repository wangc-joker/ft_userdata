from datetime import datetime

from freqtrade.persistence import Order, Trade


def order_filled(strategy, pair: str, trade: Trade, order: Order, current_time: datetime, **kwargs) -> None:
    # Only the first filled entry initializes the trade-level strategy version marker.
    if trade.nr_of_successful_entries == 1:
        if strategy.system_name_use == strategy.system_v3_2_name:
            trade.set_custom_data(key="system_version", value=strategy.system_v3_2_name)
        elif strategy.system_name_use == strategy.system_v3_1_name:
            trade.set_custom_data(key="system_version", value=strategy.system_v3_1_name)
        elif strategy.system_name_use == strategy.system_v3_name:
            trade.set_custom_data(key="system_version", value=strategy.system_v3_name)
    return None
