import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path("user_data/analysis/pyramid_second_add_2026-07-13")
OUTPUT_DIR = Path("user_data/analysis/pyramid_second_add_guard_2026-07-14")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "3y": "backtest-result-2026-07-13_04-46-06.zip",
    "5y": "backtest-result-2026-07-13_07-35-27.zip",
}

BASELINE = "DualTrendPyramidCloseFloor07V1Strategy"
WINNER = "DualTrendPyramidSecondAdd15V1Strategy"


def load_result(zip_name: str) -> dict:
    with zipfile.ZipFile(BASE_DIR / zip_name) as zf:
        json_name = next(
            name for name in zf.namelist() if name.endswith(".json") and "_config" not in name
        )
        return json.loads(zf.read(json_name))


def trade_key(trade: dict) -> tuple:
    return (
        trade["pair"],
        trade["open_date"],
        trade.get("enter_tag", ""),
        bool(trade.get("is_short", False)),
    )


def ts_to_iso(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat()


def short_profit(open_rate: float, current_rate: float) -> float:
    if open_rate <= 0:
        return 0.0
    return open_rate / current_rate - 1.0


def main() -> None:
    rows: list[dict] = []

    for sample, filename in FILES.items():
        data = load_result(filename)
        baseline = data["strategy"][BASELINE]
        winner = data["strategy"][WINNER]
        baseline_trades = {trade_key(trade): trade for trade in baseline["trades"]}

        for trade in winner["trades"]:
            entries = [order for order in trade.get("orders", []) if order.get("ft_is_entry")]
            if len(entries) < 3:
                continue

            base_trade = baseline_trades.get(trade_key(trade))
            if base_trade is None:
                continue

            first_add = entries[1]
            second_add = entries[2]
            open_rate = float(trade["open_rate"])
            first_rate = float(first_add.get("safe_price", 0.0) or 0.0)
            second_rate = float(second_add.get("safe_price", 0.0) or 0.0)
            first_ts = int(first_add["order_filled_timestamp"])
            second_ts = int(second_add["order_filled_timestamp"])

            delta_abs = float(trade["profit_abs"]) - float(base_trade["profit_abs"])
            rows.append(
                {
                    "sample": sample,
                    "pair": trade["pair"],
                    "open_date": trade["open_date"],
                    "second_add_time": ts_to_iso(second_ts),
                    "hours_after_open": round((second_ts - int(trade["open_timestamp"])) / 3600000, 2),
                    "hours_after_first_add": round((second_ts - first_ts) / 3600000, 2),
                    "open_rate": open_rate,
                    "first_add_rate": first_rate,
                    "second_add_rate": second_rate,
                    "profit_at_first_add": round(short_profit(open_rate, first_rate), 5),
                    "profit_at_second_add": round(short_profit(open_rate, second_rate), 5),
                    "extra_drop_after_first_add": round(short_profit(first_rate, second_rate), 5),
                    "final_profit_ratio": round(float(trade["profit_ratio"]), 5),
                    "baseline_profit_abs": round(float(base_trade["profit_abs"]), 5),
                    "winner_profit_abs": round(float(trade["profit_abs"]), 5),
                    "delta_abs": round(delta_abs, 5),
                    "delta_direction": "improved" if delta_abs > 1e-9 else "worsened" if delta_abs < -1e-9 else "same",
                    "exit_reason": trade.get("exit_reason", ""),
                    "baseline_exit_reason": base_trade.get("exit_reason", ""),
                    "trade_duration_min": trade.get("trade_duration"),
                }
            )

    fields = [
        "sample",
        "pair",
        "open_date",
        "second_add_time",
        "hours_after_open",
        "hours_after_first_add",
        "open_rate",
        "first_add_rate",
        "second_add_rate",
        "profit_at_first_add",
        "profit_at_second_add",
        "extra_drop_after_first_add",
        "final_profit_ratio",
        "baseline_profit_abs",
        "winner_profit_abs",
        "delta_abs",
        "delta_direction",
        "exit_reason",
        "baseline_exit_reason",
        "trade_duration_min",
    ]

    out_csv = OUTPUT_DIR / "second_add15_bad_add_diagnosis.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    by_sample: dict[str, list[dict]] = {}
    for row in rows:
        by_sample.setdefault(row["sample"], []).append(row)

    summary_rows = []
    for sample, sample_rows in by_sample.items():
        improved = [r for r in sample_rows if r["delta_direction"] == "improved"]
        worsened = [r for r in sample_rows if r["delta_direction"] == "worsened"]
        summary_rows.append(
            {
                "sample": sample,
                "second_add_trades": len(sample_rows),
                "improved_count": len(improved),
                "worsened_count": len(worsened),
                "total_delta_abs": round(sum(float(r["delta_abs"]) for r in sample_rows), 5),
                "improved_delta_abs": round(sum(float(r["delta_abs"]) for r in improved), 5),
                "worsened_delta_abs": round(sum(float(r["delta_abs"]) for r in worsened), 5),
                "avg_profit_at_second_add": round(
                    sum(float(r["profit_at_second_add"]) for r in sample_rows) / max(1, len(sample_rows)), 5
                ),
                "avg_hours_after_first_add": round(
                    sum(float(r["hours_after_first_add"]) for r in sample_rows) / max(1, len(sample_rows)), 2
                ),
            }
        )

    summary_csv = OUTPUT_DIR / "second_add15_bad_add_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)


if __name__ == "__main__":
    main()
