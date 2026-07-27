from __future__ import annotations

import argparse
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "user_data" / "data" / "binance" / "futures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure DualTrend collision occupancy cost and same-candle ranking options"
    )
    parser.add_argument("--constrained-zip", required=True)
    parser.add_argument("--collision-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--max-open-trades", type=int, default=3)
    return parser.parse_args()


def safe_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def strategy_archive(path: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        result_names = [
            name
            for name in archive.namelist()
            if name.endswith(".json") and not name.endswith("_config.json")
        ]
        config_names = [name for name in archive.namelist() if name.endswith("_config.json")]
        if len(result_names) != 1 or len(config_names) != 1:
            raise ValueError(f"Unable to identify result/config JSON in {path}")
        result = json.loads(archive.read(result_names[0]))
        config = json.loads(archive.read(config_names[0]))
    strategy_name = next(iter(result["strategy"]))
    return strategy_name, result["strategy"][strategy_name], config


def trades_frame(payload: dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(payload.get("trades", []))
    if frame.empty:
        return frame
    for column in ("open_date", "close_date"):
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="coerce")
    frame["trade_key"] = [f"trade_{index}" for index in range(len(frame))]
    return frame.sort_values(["open_date", "pair"]).reset_index(drop=True)


def collision_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    for column in ("signal_date", "counterfactual_open_date", "counterfactual_close_date"):
        if column in frame:
            frame[column] = pd.to_datetime(frame[column], utc=True, errors="coerce")
    return frame[frame["match_status"].eq("matched_counterfactual_entry")].copy()


def occupants_at(trades: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
    return trades[
        (trades["open_date"] <= timestamp)
        & (trades["close_date"].isna() | (trades["close_date"] > timestamp))
    ]


def pair_filename(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_") + "-5m-futures.feather"


class CandleMarks:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.frames: dict[str, pd.Series] = {}

    def price(self, pair: str, timestamp: pd.Timestamp) -> float | None:
        if pair not in self.frames:
            path = self.data_dir / pair_filename(pair)
            if not path.exists():
                self.frames[pair] = pd.Series(dtype=float)
            else:
                frame = pd.read_feather(path)
                date_column = "date" if "date" in frame.columns else frame.columns[0]
                dates = pd.to_datetime(frame[date_column], utc=True, errors="coerce")
                self.frames[pair] = pd.Series(
                    pd.to_numeric(frame["open"], errors="coerce").to_numpy(), index=dates
                )
        series = self.frames[pair]
        if timestamp not in series.index:
            return None
        value = series.loc[timestamp]
        if isinstance(value, pd.Series):
            value = value.iloc[-1]
        return safe_number(value)


def order_timestamp(order: dict[str, Any]) -> pd.Timestamp | None:
    raw = order.get("order_filled_timestamp")
    if raw is not None:
        return pd.to_datetime(raw, unit="ms", utc=True, errors="coerce")
    raw = order.get("order_date") or order.get("order_filled_date")
    if raw:
        return pd.to_datetime(raw, utc=True, errors="coerce")
    return None


def order_cash(order: dict[str, Any], is_short: bool, fee_open: float, fee_close: float) -> float | None:
    amount = safe_number(order.get("amount"))
    price = safe_number(order.get("safe_price")) or safe_number(order.get("price"))
    if amount is None or price is None:
        return None
    is_entry = bool(order.get("ft_is_entry"))
    notional = amount * price
    if is_short:
        return notional * (1.0 - fee_open) if is_entry else -notional * (1.0 + fee_close)
    return -notional * (1.0 + fee_open) if is_entry else notional * (1.0 - fee_close)


def remaining_trade_value(trade: pd.Series, timestamp: pd.Timestamp, mark: float | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mark_price": mark,
        "mark_basis": "collision_5m_open",
        "current_amount": None,
        "current_notional": None,
        "future_order_count": 0,
        "current_mark_return": None,
        "hold_minus_close_abs": None,
        "hold_minus_close_ratio": None,
        "valuation_status": "missing_mark",
    }
    if mark is None:
        return result

    orders = list(trade.get("orders") or [])
    if not orders:
        result["valuation_status"] = "missing_orders"
        return result

    fee_open = safe_number(trade.get("fee_open")) or 0.0
    fee_close = safe_number(trade.get("fee_close")) or 0.0
    is_short = bool(trade.get("is_short"))
    current_amount = 0.0
    past_cash = 0.0
    past_entry_notional = 0.0
    future_cash = 0.0
    future_order_count = 0
    missing_future_cash = False

    for order in orders:
        filled_at = order_timestamp(order)
        amount = safe_number(order.get("amount"))
        if filled_at is None or pd.isna(filled_at) or amount is None:
            continue
        if filled_at <= timestamp:
            current_amount += amount if bool(order.get("ft_is_entry")) else -amount
            cash = order_cash(order, is_short, fee_open, fee_close)
            if cash is not None:
                past_cash += cash
            if bool(order.get("ft_is_entry")):
                price = safe_number(order.get("safe_price")) or safe_number(order.get("price"))
                if price is not None:
                    past_entry_notional += amount * price
            continue
        cash = order_cash(order, is_short, fee_open, fee_close)
        future_order_count += 1
        if cash is None:
            missing_future_cash = True
        else:
            future_cash += cash

    if current_amount <= 1e-12:
        result["valuation_status"] = "no_open_amount_at_collision"
        return result
    if missing_future_cash:
        result["valuation_status"] = "incomplete_future_orders"
        return result

    current_notional = current_amount * mark
    immediate_close_cash = (
        -current_notional * (1.0 + fee_close)
        if is_short
        else current_notional * (1.0 - fee_close)
    )
    hold_minus_close_abs = future_cash - immediate_close_cash
    current_mark_return = (
        (past_cash + immediate_close_cash) / past_entry_notional
        if past_entry_notional > 0
        else None
    )
    result.update(
        {
            "current_amount": current_amount,
            "current_notional": current_notional,
            "future_order_count": future_order_count,
            "current_mark_return": current_mark_return,
            "hold_minus_close_abs": hold_minus_close_abs,
            "hold_minus_close_ratio": hold_minus_close_abs / current_notional,
            "valuation_status": "valued_without_funding",
        }
    )
    return result


def occupant_cost_rows(
    collisions: pd.DataFrame, trades: pd.DataFrame, marks: CandleMarks
) -> tuple[pd.DataFrame, pd.DataFrame]:
    occupant_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    for _, collision in collisions.iterrows():
        timestamp = collision["signal_date"]
        candidate_return = safe_number(collision.get("counterfactual_profit_ratio"))
        occupants = occupants_at(trades, timestamp)
        event_values: list[float] = []
        older_values: list[float] = []
        for _, trade in occupants.iterrows():
            same_candle = trade["open_date"] == timestamp
            valuation = remaining_trade_value(
                trade, timestamp, marks.price(str(trade["pair"]), timestamp)
            )
            remaining = safe_number(valuation.get("hold_minus_close_ratio"))
            if remaining is not None:
                event_values.append(remaining)
                if not same_candle:
                    older_values.append(remaining)
            occupant_rows.append(
                {
                    "signal_date": timestamp,
                    "candidate_pair": collision["pair"],
                    "candidate_side": collision["side"],
                    "candidate_tag": collision["entry_tag"],
                    "candidate_counterfactual_return": candidate_return,
                    "occupant_pair": trade["pair"],
                    "occupant_side": "short" if bool(trade.get("is_short")) else "long",
                    "occupant_tag": trade.get("enter_tag"),
                    "occupant_open_date": trade["open_date"],
                    "occupant_close_date": trade["close_date"],
                    "occupant_age_hours": (
                        timestamp - trade["open_date"]
                    ).total_seconds()
                    / 3600.0,
                    "occupant_total_return": safe_number(trade.get("profit_ratio")),
                    "occupant_same_candle": same_candle,
                    **valuation,
                    "candidate_minus_remaining": (
                        candidate_return - remaining
                        if candidate_return is not None and remaining is not None
                        else None
                    ),
                }
            )
        weakest = min(event_values) if event_values else None
        weakest_older = min(older_values) if older_values else None
        event_rows.append(
            {
                "signal_date": timestamp,
                "candidate_pair": collision["pair"],
                "candidate_side": collision["side"],
                "candidate_tag": collision["entry_tag"],
                "candidate_counterfactual_return": candidate_return,
                "occupant_count": len(occupants),
                "same_candle_occupants": int((occupants["open_date"] == timestamp).sum()),
                "older_occupants": int((occupants["open_date"] < timestamp).sum()),
                "valued_occupants": len(event_values),
                "weakest_occupant_remaining": weakest,
                "mean_occupant_remaining": (
                    sum(event_values) / len(event_values) if event_values else None
                ),
                "weakest_older_remaining": weakest_older,
                "candidate_minus_weakest": (
                    candidate_return - weakest
                    if candidate_return is not None and weakest is not None
                    else None
                ),
                "candidate_minus_weakest_older": (
                    candidate_return - weakest_older
                    if candidate_return is not None and weakest_older is not None
                    else None
                ),
            }
        )
    return pd.DataFrame(occupant_rows), pd.DataFrame(event_rows)


def short_tag_rank(tag: str) -> int:
    if tag == "short_pullback_restart":
        return 0
    if tag == "short_compression_breakdown":
        return 1
    return 2


def outcome_record(
    source: str, pair: str, side: str, tag: str, outcome: Any, pair_order: dict[str, int]
) -> dict[str, Any]:
    return {
        "source": source,
        "pair": pair,
        "side": side,
        "tag": tag,
        "outcome": safe_number(outcome),
        "pair_order": pair_order.get(pair, 1_000_000),
    }


def admission_ranking_rows(
    collisions: pd.DataFrame, trades: pd.DataFrame, pair_whitelist: list[str]
) -> pd.DataFrame:
    pair_order = {pair: index for index, pair in enumerate(pair_whitelist)}
    rows: list[dict[str, Any]] = []
    for timestamp, rejected in collisions.groupby("signal_date", sort=True):
        occupants = occupants_at(trades, timestamp)
        actual = occupants[occupants["open_date"].eq(timestamp)]
        candidates: list[dict[str, Any]] = []
        for _, trade in actual.iterrows():
            candidates.append(
                outcome_record(
                    "actual",
                    str(trade["pair"]),
                    "short" if bool(trade.get("is_short")) else "long",
                    str(trade.get("enter_tag") or ""),
                    trade.get("profit_ratio"),
                    pair_order,
                )
            )
        for _, candidate in rejected.iterrows():
            candidates.append(
                outcome_record(
                    "rejected",
                    str(candidate["pair"]),
                    str(candidate["side"]),
                    str(candidate["entry_tag"]),
                    candidate.get("counterfactual_profit_ratio"),
                    pair_order,
                )
            )

        slots = len(actual)
        actual_selected = [item for item in candidates if item["source"] == "actual"]
        all_short = bool(candidates) and all(item["side"] == "short" for item in candidates)
        complete_outcomes = all(item["outcome"] is not None for item in candidates)
        policy_selected: list[dict[str, Any]] = []
        oracle_selected: list[dict[str, Any]] = []
        if slots and all_short and complete_outcomes:
            policy_selected = sorted(
                candidates, key=lambda item: (short_tag_rank(item["tag"]), item["pair_order"])
            )[:slots]
        if slots and complete_outcomes:
            oracle_selected = sorted(candidates, key=lambda item: item["outcome"], reverse=True)[:slots]

        actual_sum = sum(item["outcome"] for item in actual_selected if item["outcome"] is not None)
        policy_sum = (
            sum(item["outcome"] for item in policy_selected) if policy_selected else None
        )
        oracle_sum = (
            sum(item["outcome"] for item in oracle_selected) if oracle_selected else None
        )
        actual_pairs = {item["pair"] for item in actual_selected}
        policy_pairs = {item["pair"] for item in policy_selected}
        rows.append(
            {
                "signal_date": timestamp,
                "year": timestamp.year,
                "older_occupants": int((occupants["open_date"] < timestamp).sum()),
                "same_candle_slots": slots,
                "candidate_count": len(candidates),
                "rejected_count": len(rejected),
                "all_short_candidates": all_short,
                "admission_addressable": bool(slots and len(rejected)),
                "policy_evaluable": bool(policy_selected),
                "actual_pairs": "|".join(item["pair"] for item in actual_selected),
                "actual_tags": "|".join(item["tag"] for item in actual_selected),
                "rejected_pairs": "|".join(str(value) for value in rejected["pair"]),
                "rejected_tags": "|".join(str(value) for value in rejected["entry_tag"]),
                "policy_pairs": "|".join(item["pair"] for item in policy_selected),
                "policy_tags": "|".join(item["tag"] for item in policy_selected),
                "actual_sum_return": actual_sum,
                "pullback_first_sum_return": policy_sum,
                "pullback_first_delta": (
                    policy_sum - actual_sum if policy_sum is not None else None
                ),
                "policy_changed_selection": bool(policy_selected and actual_pairs != policy_pairs),
                "oracle_sum_return": oracle_sum,
                "oracle_delta": oracle_sum - actual_sum if oracle_sum is not None else None,
            }
        )
    return pd.DataFrame(rows)


def preemption_rows(
    collisions: pd.DataFrame,
    trades: pd.DataFrame,
    marks: CandleMarks,
    pair_whitelist: list[str],
) -> pd.DataFrame:
    pair_order = {pair: index for index, pair in enumerate(pair_whitelist)}
    rows: list[dict[str, Any]] = []
    for timestamp, rejected in collisions.groupby("signal_date", sort=True):
        occupants = occupants_at(trades, timestamp)
        if occupants.empty or occupants["open_date"].eq(timestamp).any():
            continue

        candidates = [
            outcome_record(
                "rejected",
                str(candidate["pair"]),
                str(candidate["side"]),
                str(candidate["entry_tag"]),
                candidate.get("counterfactual_profit_ratio"),
                pair_order,
            )
            for _, candidate in rejected.iterrows()
        ]
        all_short = bool(candidates) and all(item["side"] == "short" for item in candidates)
        candidate_complete = all(item["outcome"] is not None for item in candidates)
        selected_candidate = (
            sorted(
                candidates, key=lambda item: (short_tag_rank(item["tag"]), item["pair_order"])
            )[0]
            if all_short and candidate_complete
            else None
        )

        victims: list[dict[str, Any]] = []
        for _, trade in occupants.iterrows():
            valuation = remaining_trade_value(
                trade, timestamp, marks.price(str(trade["pair"]), timestamp)
            )
            victims.append(
                {
                    "pair": str(trade["pair"]),
                    "tag": str(trade.get("enter_tag") or ""),
                    "open_date": trade["open_date"],
                    "age_hours": (timestamp - trade["open_date"]).total_seconds() / 3600.0,
                    "current_mark_return": safe_number(valuation.get("current_mark_return")),
                    "remaining_return": safe_number(valuation.get("hold_minus_close_ratio")),
                    "pair_order": pair_order.get(str(trade["pair"]), 1_000_000),
                }
            )
        victims_complete = all(
            item["current_mark_return"] is not None and item["remaining_return"] is not None
            for item in victims
        )
        worst_mark = (
            min(victims, key=lambda item: (item["current_mark_return"], item["pair_order"]))
            if victims_complete
            else None
        )
        oldest = (
            min(victims, key=lambda item: (item["open_date"], item["pair_order"]))
            if victims_complete
            else None
        )
        oracle_victim = (
            min(victims, key=lambda item: item["remaining_return"])
            if victims_complete
            else None
        )
        oracle_candidate = (
            max(candidates, key=lambda item: item["outcome"])
            if candidate_complete
            else None
        )
        evaluable = selected_candidate is not None and victims_complete
        candidate_return = selected_candidate["outcome"] if selected_candidate else None
        rows.append(
            {
                "signal_date": timestamp,
                "year": timestamp.year,
                "candidate_count": len(candidates),
                "all_short_candidates": all_short,
                "preemption_evaluable": evaluable,
                "selected_candidate_pair": selected_candidate["pair"] if selected_candidate else None,
                "selected_candidate_tag": selected_candidate["tag"] if selected_candidate else None,
                "selected_candidate_return": candidate_return,
                "worst_mark_victim_pair": worst_mark["pair"] if worst_mark else None,
                "worst_mark_victim_tag": worst_mark["tag"] if worst_mark else None,
                "worst_mark_victim_current_return": (
                    worst_mark["current_mark_return"] if worst_mark else None
                ),
                "worst_mark_victim_remaining": worst_mark["remaining_return"] if worst_mark else None,
                "worst_mark_delta": (
                    candidate_return - worst_mark["remaining_return"]
                    if evaluable and worst_mark
                    else None
                ),
                "oldest_victim_pair": oldest["pair"] if oldest else None,
                "oldest_victim_tag": oldest["tag"] if oldest else None,
                "oldest_victim_age_hours": oldest["age_hours"] if oldest else None,
                "oldest_victim_remaining": oldest["remaining_return"] if oldest else None,
                "oldest_delta": (
                    candidate_return - oldest["remaining_return"]
                    if evaluable and oldest
                    else None
                ),
                "oracle_candidate_pair": oracle_candidate["pair"] if oracle_candidate else None,
                "oracle_victim_pair": oracle_victim["pair"] if oracle_victim else None,
                "oracle_delta": (
                    oracle_candidate["outcome"] - oracle_victim["remaining_return"]
                    if oracle_candidate and oracle_victim
                    else None
                ),
            }
        )
    return pd.DataFrame(rows)


def fmt_pct(value: Any) -> str:
    number = safe_number(value)
    return "n/a" if number is None else f"{number * 100:+.2f}%"


def markdown_report(
    strategy_name: str,
    payload: dict[str, Any],
    collisions: pd.DataFrame,
    occupant_costs: pd.DataFrame,
    events: pd.DataFrame,
    ranking: pd.DataFrame,
    preemption: pd.DataFrame,
) -> str:
    addressable = ranking[ranking["admission_addressable"]]
    policy = ranking[ranking["policy_evaluable"]]
    changed = policy[policy["policy_changed_selection"]]
    older_only = ranking[ranking["same_candle_slots"].eq(0)]
    valued = events[events["valued_occupants"].gt(0)]
    comparable_older = events[events["weakest_older_remaining"].notna()]
    candidate_better = int(valued["candidate_minus_weakest"].gt(0).sum())
    candidate_better_older = int(
        comparable_older["candidate_minus_weakest_older"].gt(0).sum()
    )
    policy_delta = pd.to_numeric(policy["pullback_first_delta"], errors="coerce").sum()
    oracle_delta = pd.to_numeric(addressable["oracle_delta"], errors="coerce").sum()
    preemption_evaluable = preemption[preemption["preemption_evaluable"]]
    worst_mark_delta = pd.to_numeric(
        preemption_evaluable["worst_mark_delta"], errors="coerce"
    )
    oldest_delta = pd.to_numeric(preemption_evaluable["oldest_delta"], errors="coerce")
    worst_mark_without_best = (
        worst_mark_delta.sum() - worst_mark_delta.max() if not worst_mark_delta.empty else None
    )

    lines = [
        "# DualTrend Collision Opportunity Cost",
        "",
        f"> Generated {datetime.now(timezone.utc).isoformat()} from the constrained archive and exact matched collision episodes.",
        "",
        "## Scope",
        "",
        f"- Strategy: `{strategy_name}`",
        f"- Backtest range: `{payload.get('backtest_start')} -> {payload.get('backtest_end')}`",
        f"- Constrained trades: `{len(payload.get('trades', []))}`",
        f"- Matched rejected episodes: `{len(collisions)}` across `{len(ranking)}` collision timestamps",
        f"- Admission-addressable timestamps: `{len(addressable)}`",
        f"- Older-occupants-only timestamps: `{len(older_only)}`",
        "",
        "A timestamp is admission-addressable only when at least one constrained trade opened on the same candle. Older-only collisions cannot be fixed by tag ordering; they require an explicit preemption or early-exit rule.",
        "",
        "## Same-candle Ranking",
        "",
        "The tested local rule applies only to all-short candidate pools: `short_pullback_restart` before `short_compression_breakdown`, then the archived whitelist order. Mixed long/short pools are excluded because no cross-direction priority was prespecified.",
        "",
        f"- Evaluable all-short timestamps: `{len(policy)}`",
        f"- Timestamps whose selected pairs would change: `{len(changed)}`",
        f"- Sum of local selected-trade return deltas: `{fmt_pct(policy_delta)}`",
        f"- Oracle upper-bound delta across addressable timestamps: `{fmt_pct(oracle_delta)}`",
        "",
        "| Year | Evaluable | Changed | Pullback-first delta |",
        "|---:|---:|---:|---:|",
    ]
    for year, group in policy.groupby("year", sort=True):
        lines.append(
            f"| {year} | {len(group)} | {int(group['policy_changed_selection'].sum())} | {fmt_pct(group['pullback_first_delta'].sum())} |"
        )
    lines.extend(
        [
            "",
            "These deltas are one-step static comparisons of known trade outcomes. Replacing a trade changes later occupancy, stake sizing, protections, and possibly future signals, so the sum is not a portfolio-return estimate.",
            "",
            "## Occupant Remaining Value",
            "",
            f"- Occupant valuations completed: `{int(occupant_costs['valuation_status'].eq('valued_without_funding').sum())} / {len(occupant_costs)}`",
            f"- Rejected candidate beat the hindsight-weakest occupant by realized remaining value: `{candidate_better} / {len(valued)}` valued episodes",
            f"- Rejected candidate beat the hindsight-weakest older occupant: `{candidate_better_older} / {len(comparable_older)}` comparable episodes",
            "",
            "Remaining value is the fee-adjusted cash-flow difference between holding the actual trade through its recorded future entries/exits and closing it at the collision 5m candle open, normalized by current notional. Funding is not reconstructed. This is a diagnostic ranking signal, not a replacement backtest.",
            "",
            "## Older-position Preemption",
            "",
            "Each older-only timestamp permits at most one static replacement. The candidate is selected with the same pullback-first short rule; mixed-direction timestamps are excluded. Victims are chosen only from information visible at the collision: either the worst marked return or the oldest open time.",
            "",
            f"- Evaluable older-only timestamps: `{len(preemption_evaluable)}`",
            f"- Worst-current-return victim: `{int(worst_mark_delta.gt(0).sum())} / {len(worst_mark_delta)}` positive local deltas, sum `{fmt_pct(worst_mark_delta.sum())}`",
            f"- Worst-current-return median delta: `{fmt_pct(worst_mark_delta.median())}`; sum after removing the single best event: `{fmt_pct(worst_mark_without_best)}`",
            f"- Oldest-position victim: `{int(oldest_delta.gt(0).sum())} / {len(oldest_delta)}` positive local deltas, sum `{fmt_pct(oldest_delta.sum())}`",
            "",
            "| Year | Evaluable | Worst-mark positive | Worst-mark delta | Oldest delta |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for year, group in preemption_evaluable.groupby("year", sort=True):
        lines.append(
            f"| {year} | {len(group)} | {int(group['worst_mark_delta'].gt(0).sum())} | {fmt_pct(group['worst_mark_delta'].sum())} | {fmt_pct(group['oldest_delta'].sum())} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Do not change live admission or preempt existing positions from this analysis alone. A ranking rule is promotable only if its gains are reasonably distributed across years and it survives a full stateful backtest that propagates replacement effects.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    constrained_path = Path(args.constrained_zip).resolve()
    collision_path = Path(args.collision_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    strategy_name, payload, config = strategy_archive(constrained_path)
    trades = trades_frame(payload)
    collisions = collision_frame(collision_path)
    marks = CandleMarks(Path(args.data_dir).resolve())
    occupant_costs, events = occupant_cost_rows(collisions, trades, marks)
    ranking = admission_ranking_rows(
        collisions, trades, list(config.get("exchange", {}).get("pair_whitelist", []))
    )
    preemption = preemption_rows(
        collisions,
        trades,
        marks,
        list(config.get("exchange", {}).get("pair_whitelist", [])),
    )

    occupant_costs.to_csv(output_dir / "collision_occupant_opportunity_cost.csv", index=False)
    events.to_csv(output_dir / "collision_event_opportunity_cost.csv", index=False)
    ranking.to_csv(output_dir / "collision_admission_ranking.csv", index=False)
    preemption.to_csv(output_dir / "collision_preemption_screen.csv", index=False)
    report = markdown_report(
        strategy_name, payload, collisions, occupant_costs, events, ranking, preemption
    )
    (output_dir / "collision_opportunity_cost.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
