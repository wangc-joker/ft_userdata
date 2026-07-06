#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"
STARTING_BALANCE = 1000.0


@dataclass(frozen=True)
class ModelSpec:
    name: str
    label: str
    steps: tuple[tuple[float, float], ...]
    partials: tuple[tuple[float, float, float], ...] = ()
    ladder: tuple[float, float, float, int, float, float, float] | None = None


MODELS = (
    ModelSpec("baseline", "Baseline no profit lock", ()),
    ModelSpec("breakeven_only", "Profit >=2% lock +0.1%", ((0.02, 0.001),)),
    ModelSpec("loose", "2% BE, 6% lock 2%, 10% lock 4%", ((0.10, 0.04), (0.06, 0.02), (0.02, 0.001))),
    ModelSpec("medium", "2% BE, 4/6/8% lock 1.5/3/4.5%", ((0.08, 0.045), (0.06, 0.03), (0.04, 0.015), (0.02, 0.001))),
    ModelSpec("tight", "2% BE, 4/6/8% lock 2/3.5/5%", ((0.08, 0.05), (0.06, 0.035), (0.04, 0.02), (0.02, 0.001))),
    ModelSpec("partial_ladder_a", "2% BE, every +10% sell 50% remaining, lock 5% +0.5%/step max 8%", ((0.02, 0.001),), ladder=(0.10, 0.10, 0.50, 6, 0.05, 0.005, 0.08)),
    ModelSpec("partial_ladder_b", "2% BE, every +8% sell 50% remaining, lock 4% +0.5%/step max 7.5%", ((0.02, 0.001),), ladder=(0.08, 0.08, 0.50, 6, 0.04, 0.005, 0.075)),
    ModelSpec("partial_ladder_c", "2% BE, every +12% sell 50% remaining, lock 5.5% +0.6%/step max 9.5%", ((0.02, 0.001),), ladder=(0.12, 0.12, 0.50, 6, 0.055, 0.006, 0.095)),
)

SAMPLES = {
    "3y": ANALYSIS_DIR / "positive13_trades_max3_3y.csv",
    "1y": ANALYSIS_DIR / "positive13_trades_max3_1y.csv",
}


def pair_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def load_ohlcv(pair: str) -> pd.DataFrame:
    path = DATA_DIR / f"{pair_stem(pair)}-1h-futures.feather"
    frame = pd.read_feather(path)
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    return frame.sort_values("date").reset_index(drop=True)


def direction_profit(entry: float, price: float, is_short: bool) -> float:
    return (entry - price) / entry if is_short else (price - entry) / entry


def stop_price(entry: float, locked_profit: float, is_short: bool) -> float:
    return entry * (1.0 - locked_profit) if is_short else entry * (1.0 + locked_profit)


def locked_profit_for(best_profit: float, steps: tuple[tuple[float, float], ...]) -> float | None:
    for trigger_profit, locked_profit in steps:
        if best_profit >= trigger_profit:
            return locked_profit
    return None


def trail_gap_for(best_profit: float, partials: tuple[tuple[float, float, float], ...]) -> float | None:
    for trigger_profit, _fraction, trail_gap in partials:
        if best_profit >= trigger_profit:
            return trail_gap
    return None


def ladder_lock_for(best_profit: float, model: ModelSpec) -> float | None:
    if model.ladder is None:
        return None
    start, step, _fraction, max_steps, first_lock, lock_step, lock_max = model.ladder
    if best_profit < start:
        return None
    steps = int((best_profit - start) // step) + 1
    steps = max(1, min(steps, max_steps))
    return min(first_lock + (steps - 1) * lock_step, lock_max)


def simulate_trade(trade: pd.Series, candles: pd.DataFrame, model: ModelSpec) -> dict:
    baseline_profit_ratio = float(trade["profit_ratio"])
    baseline_profit_abs = float(trade["profit_abs"])
    stake = float(trade["stake_amount"])
    entry = float(trade["open_rate"])
    is_short = str(trade["is_short"]).lower() == "true"
    opened = pd.Timestamp(trade["open_date"])
    closed = pd.Timestamp(trade["close_date"])
    if opened.tzinfo is None:
        opened = opened.tz_localize("UTC")
    else:
        opened = opened.tz_convert("UTC")
    if closed.tzinfo is None:
        closed = closed.tz_localize("UTC")
    else:
        closed = closed.tz_convert("UTC")

    if not model.steps and not model.partials and model.ladder is None:
        return {
            "profit_ratio": baseline_profit_ratio,
            "profit_abs": baseline_profit_abs,
            "exit_reason_model": "baseline_exit",
            "model_exit_date": closed,
            "activated": False,
            "locked_profit": None,
            "partial_exits": 0,
            "baseline_profit_ratio": baseline_profit_ratio,
            "baseline_profit_abs": baseline_profit_abs,
        }

    window = candles[(candles["date"] >= opened) & (candles["date"] <= closed)]
    best_profit = 0.0
    active_locked_profit: float | None = None
    remaining_stake = stake
    realized_abs = 0.0
    partial_done: set[float] = set()
    partial_exits = 0
    ladder_done_steps = 0

    for _, candle in window.iterrows():
        if active_locked_profit is None:
            close_profit = direction_profit(entry, float(candle["close"]), is_short)
            best_profit = max(best_profit, close_profit)
            next_locked = locked_profit_for(best_profit, model.steps)
            if next_locked is not None:
                active_locked_profit = max(active_locked_profit or 0.0, next_locked)
            if model.partials:
                gap = trail_gap_for(best_profit, model.partials)
                if gap is not None:
                    active_locked_profit = max(active_locked_profit or 0.0, best_profit - gap)
                for trigger_profit, fraction, trail_gap in sorted(model.partials):
                    if trigger_profit in partial_done or close_profit < trigger_profit:
                        continue
                    sell_stake = remaining_stake * fraction
                    realized_abs += sell_stake * close_profit
                    remaining_stake -= sell_stake
                    partial_done.add(trigger_profit)
                    partial_exits += 1
                    active_locked_profit = max(active_locked_profit or 0.0, close_profit - trail_gap)
            if model.ladder is not None:
                start, step, fraction, max_steps, _first_lock, _lock_step, _lock_max = model.ladder
                while ladder_done_steps < max_steps:
                    trigger_profit = start + ladder_done_steps * step
                    if close_profit < trigger_profit:
                        break
                    sell_stake = remaining_stake * fraction
                    realized_abs += sell_stake * close_profit
                    remaining_stake -= sell_stake
                    ladder_done_steps += 1
                    partial_exits += 1
                ladder_lock = ladder_lock_for(best_profit, model)
                if ladder_lock is not None:
                    active_locked_profit = max(active_locked_profit or 0.0, ladder_lock)
            continue

        current_stop = stop_price(entry, active_locked_profit, is_short)
        hit = float(candle["high"]) >= current_stop if is_short else float(candle["low"]) <= current_stop
        if hit:
            profit_ratio = active_locked_profit
            profit_abs = realized_abs + remaining_stake * profit_ratio
            return {
                "profit_ratio": profit_abs / stake if stake else profit_ratio,
                "profit_abs": profit_abs,
                "exit_reason_model": "profit_lock_stop",
                "model_exit_date": candle["date"],
                "activated": True,
                "locked_profit": active_locked_profit,
                "partial_exits": partial_exits,
                "baseline_profit_ratio": baseline_profit_ratio,
                "baseline_profit_abs": baseline_profit_abs,
            }

        close_profit = direction_profit(entry, float(candle["close"]), is_short)
        best_profit = max(best_profit, close_profit)
        next_locked = locked_profit_for(best_profit, model.steps)
        if next_locked is not None:
            active_locked_profit = max(active_locked_profit or 0.0, next_locked)
        if model.partials:
            gap = trail_gap_for(best_profit, model.partials)
            if gap is not None:
                active_locked_profit = max(active_locked_profit or 0.0, best_profit - gap)
            for trigger_profit, fraction, trail_gap in sorted(model.partials):
                if trigger_profit in partial_done or close_profit < trigger_profit:
                    continue
                sell_stake = remaining_stake * fraction
                realized_abs += sell_stake * close_profit
                remaining_stake -= sell_stake
                partial_done.add(trigger_profit)
                partial_exits += 1
                active_locked_profit = max(active_locked_profit or 0.0, close_profit - trail_gap)
        if model.ladder is not None:
            start, step, fraction, max_steps, _first_lock, _lock_step, _lock_max = model.ladder
            while ladder_done_steps < max_steps:
                trigger_profit = start + ladder_done_steps * step
                if close_profit < trigger_profit:
                    break
                sell_stake = remaining_stake * fraction
                realized_abs += sell_stake * close_profit
                remaining_stake -= sell_stake
                ladder_done_steps += 1
                partial_exits += 1
            ladder_lock = ladder_lock_for(best_profit, model)
            if ladder_lock is not None:
                active_locked_profit = max(active_locked_profit or 0.0, ladder_lock)

    profit_abs = realized_abs + remaining_stake * baseline_profit_ratio
    return {
        "profit_ratio": profit_abs / stake if stake else baseline_profit_ratio,
        "profit_abs": profit_abs,
        "exit_reason_model": "baseline_exit_after_lock",
        "model_exit_date": closed,
        "activated": active_locked_profit is not None,
        "locked_profit": active_locked_profit,
        "partial_exits": partial_exits,
        "baseline_profit_ratio": baseline_profit_ratio,
        "baseline_profit_abs": baseline_profit_abs,
    }


def max_drawdown_pct(rows: pd.DataFrame) -> float:
    ordered = rows.sort_values("model_exit_date")
    equity = STARTING_BALANCE + ordered["profit_abs"].cumsum()
    peak = equity.cummax()
    dd = (peak - equity) / peak
    return float(dd.max() * 100.0) if len(dd) else 0.0


def summarize(rows: pd.DataFrame) -> dict:
    wins = rows[rows["profit_abs"] > 0]
    losses = rows[rows["profit_abs"] < 0]
    gross_profit = float(wins["profit_abs"].sum())
    gross_loss = float(-losses["profit_abs"].sum())
    return {
        "trades": int(len(rows)),
        "total_profit_abs": float(rows["profit_abs"].sum()),
        "total_profit_pct": float(rows["profit_abs"].sum() / STARTING_BALANCE * 100.0),
        "profit_factor": gross_profit / gross_loss if gross_loss else 0.0,
        "winrate": float(len(wins) / len(rows) * 100.0) if len(rows) else 0.0,
        "max_drawdown_pct": max_drawdown_pct(rows),
        "avg_profit_pct": float(rows["profit_ratio"].mean() * 100.0) if len(rows) else 0.0,
        "locked_exits": int((rows["exit_reason_model"] == "profit_lock_stop").sum()),
        "activated": int(rows["activated"].sum()),
        "partial_exits": int(rows["partial_exits"].sum()),
        "hurt_trades": int((rows["profit_abs"] < rows["baseline_profit_abs"]).sum()),
        "saved_trades": int((rows["profit_abs"] > rows["baseline_profit_abs"]).sum()),
    }


def run_sample(sample: str, csv_path: Path) -> tuple[list[dict], pd.DataFrame]:
    trades = pd.read_csv(csv_path)
    candles_by_pair = {pair: load_ohlcv(pair) for pair in trades["pair"].unique()}
    detail_rows = []
    summary_rows = []

    for model in MODELS:
        for _, trade in trades.iterrows():
            result = simulate_trade(trade, candles_by_pair[str(trade["pair"])], model)
            detail_rows.append(
                {
                    "sample": sample,
                    "model": model.name,
                    "model_label": model.label,
                    "pair": trade["pair"],
                    "side": trade["side"],
                    "entry_tag": trade["entry_tag"],
                    "open_date": trade["open_date"],
                    **result,
                }
            )

        model_rows = pd.DataFrame([row for row in detail_rows if row["sample"] == sample and row["model"] == model.name])
        summary = summarize(model_rows)
        summary_rows.append({"sample": sample, "model": model.name, "model_label": model.label, **summary})

    return summary_rows, pd.DataFrame(detail_rows)


def write_report(summary: pd.DataFrame, details: pd.DataFrame) -> None:
    lines = [
        "# Positive13 Profit Lock Validation",
        "",
        "- Strategy baseline: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Entry sample: fixed Positive13 max_open_trades=3 baseline trades",
        "- Method: offline exit counterfactual using 1H OHLCV inside each original trade window",
        "- Scope: compares profit-lock exits only; entries, stakes, pair pool, ROI, and structural exits stay fixed",
        "",
        "## Summary",
        "",
        "| Sample | Model | Trades | Profit | PF | MaxDD | Winrate | Lock exits | Partial exits | Activated | Saved | Hurt |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['sample']} | {row['model']} | {int(row['trades'])} | "
            f"{row['total_profit_pct']:.2f}% / {row['total_profit_abs']:.2f} | "
            f"{row['profit_factor']:.2f} | {row['max_drawdown_pct']:.2f}% | {row['winrate']:.2f}% | "
            f"{int(row['locked_exits'])} | {int(row['partial_exits'])} | {int(row['activated'])} | "
            f"{int(row['saved_trades'])} | {int(row['hurt_trades'])} |"
        )

    lines.extend(["", "## Interpretation", ""])
    for sample in summary["sample"].unique():
        sample_rows = summary[summary["sample"] == sample].copy()
        baseline = sample_rows[sample_rows["model"] == "baseline"].iloc[0]
        best = sample_rows.sort_values(["profit_factor", "total_profit_abs"], ascending=False).iloc[0]
        lines.append(
            f"- {sample}: baseline profit {baseline['total_profit_pct']:.2f}%, PF {baseline['profit_factor']:.2f}, "
            f"MaxDD {baseline['max_drawdown_pct']:.2f}%. Best PF model is `{best['model']}` "
            f"with profit {best['total_profit_pct']:.2f}%, PF {best['profit_factor']:.2f}, "
            f"MaxDD {best['max_drawdown_pct']:.2f}%."
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is not a full Freqtrade rerun because Docker could not load Binance futures markets during this pass.",
            "- The test is still useful for this question because it isolates exit behavior on the same baseline trades.",
            "- Intrabar ordering is approximated from 1H OHLCV, so any final candidate should still receive a Docker backtest when exchange access is available.",
        ]
    )
    (REPORTS_DIR / "positive13_profit_lock_validation.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    all_summary = []
    all_details = []
    for sample, csv_path in SAMPLES.items():
        summary_rows, details = run_sample(sample, csv_path)
        all_summary.extend(summary_rows)
        all_details.append(details)

    summary = pd.DataFrame(all_summary)
    details = pd.concat(all_details, ignore_index=True)
    summary.to_csv(ANALYSIS_DIR / "positive13_profit_lock_validation_summary.csv", index=False)
    details.to_csv(ANALYSIS_DIR / "positive13_profit_lock_validation_trades.csv", index=False)
    write_report(summary, details)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
