"""Trade profit calculations shared by exits and position management."""


def calc_total_profit(strategy, trade, filled_entries, filled_exits, exit_rate: float) -> tuple:
    """
    Calculate open-trade profit using NFI's original fee and partial-fill rules.

    Returns:
        total profit in stake, profit ratio by total stake, profit ratio by
        current remaining stake, and profit ratio by first entry stake.
    """
    fee_open_rate = trade.fee_open if strategy.custom_fee_open_rate is None else strategy.custom_fee_open_rate
    fee_close_rate = trade.fee_close if strategy.custom_fee_close_rate is None else strategy.custom_fee_close_rate

    total_amount = 0.0
    total_stake = 0.0
    total_profit = 0.0
    current_stake = 0.0
    for entry_order in filled_entries:
        if trade.is_short:
            entry_stake = entry_order.safe_filled * entry_order.safe_price * (1 - fee_open_rate)
            total_amount += entry_order.safe_filled
            total_stake += entry_stake
            total_profit += entry_stake
        else:
            entry_stake = entry_order.safe_filled * entry_order.safe_price * (1 + fee_open_rate)
            total_amount += entry_order.safe_filled
            total_stake += entry_stake
            total_profit -= entry_stake
    for exit_order in filled_exits:
        if trade.is_short:
            exit_stake = exit_order.safe_filled * exit_order.safe_price * (1 + fee_close_rate)
            total_amount -= exit_order.safe_filled
            total_profit -= exit_stake
        else:
            exit_stake = exit_order.safe_filled * exit_order.safe_price * (1 - fee_close_rate)
            total_amount -= exit_order.safe_filled
            total_profit += exit_stake
    if trade.is_short:
        current_stake = total_amount * exit_rate * (1 + fee_close_rate)
        total_profit -= current_stake
    else:
        current_stake = total_amount * exit_rate * (1 - fee_close_rate)
        total_profit += current_stake
    if strategy.is_futures_mode:
        total_profit += trade.funding_fees
    total_profit_ratio = total_profit / total_stake
    current_profit_ratio = total_profit / current_stake
    init_profit_ratio = total_profit / filled_entries[0].cost
    return total_profit, total_profit_ratio, current_profit_ratio, init_profit_ratio
