import csv
from pathlib import Path


INPUT = Path("user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_candle_features.csv")
OUTPUT = Path("user_data/analysis/pyramid_second_add_guard_2026-07-14/second_add15_guard_threshold_scan.csv")


def to_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return float("nan")


def main() -> None:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    scans = []
    rules = []
    numeric_columns = [
        "profit_at_second_add",
        "hours_after_first_add",
        "extra_drop_after_first_add",
        "close_position_1h",
        "body_ratio_1h",
        "range_pct_1h",
        "ret_1h",
        "ret_3h",
        "ret_6h",
        "ret_12h",
        "ret_24h",
        "dist_ema20_1h",
        "dist_ema50_1h",
        "ema20_slope_3_1h",
        "ema50_slope_3_1h",
        "atr_pct_1h",
        "vol_ratio_24_1h",
        "lower_wick_ratio_1h",
        "upper_wick_ratio_1h",
        "ret_4h_1",
        "ret_4h_3",
        "dist_ema20_4h",
        "dist_ema50_4h",
        "ema20_slope_3_4h",
        "ema50_slope_3_4h",
        "atr_pct_4h",
    ]

    for column in numeric_columns:
        values = sorted({to_float(row[column]) for row in rows if row[column] != ""})
        values = [value for value in values if value == value]
        if len(values) < 3:
            continue
        candidates = values[1:-1]
        for threshold in candidates:
            for op in ("<", ">", "<=", ">="):
                if op == "<":
                    removed = [row for row in rows if to_float(row[column]) < threshold]
                elif op == ">":
                    removed = [row for row in rows if to_float(row[column]) > threshold]
                elif op == "<=":
                    removed = [row for row in rows if to_float(row[column]) <= threshold]
                else:
                    removed = [row for row in rows if to_float(row[column]) >= threshold]
                kept = [row for row in rows if row not in removed]
                if len(removed) == 0 or len(kept) == 0:
                    continue
                removed_delta = sum(to_float(row["delta_abs"]) for row in removed)
                kept_delta = sum(to_float(row["delta_abs"]) for row in kept)
                removed_improved = sum(1 for row in removed if row["delta_direction"] == "improved")
                removed_worsened = sum(1 for row in removed if row["delta_direction"] == "worsened")
                scans.append(
                    {
                        "column": column,
                        "op": op,
                        "threshold": round(threshold, 6),
                        "removed_count": len(removed),
                        "removed_improved": removed_improved,
                        "removed_worsened": removed_worsened,
                        "removed_delta_abs": round(removed_delta, 5),
                        "kept_count": len(kept),
                        "kept_delta_abs": round(kept_delta, 5),
                        "estimated_gain_if_removed": round(-removed_delta, 5),
                    }
                )

    scans.sort(key=lambda row: (float(row["estimated_gain_if_removed"]), int(row["removed_worsened"]), -int(row["removed_improved"])), reverse=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = [
            "column",
            "op",
            "threshold",
            "removed_count",
            "removed_improved",
            "removed_worsened",
            "removed_delta_abs",
            "kept_count",
            "kept_delta_abs",
            "estimated_gain_if_removed",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scans)


if __name__ == "__main__":
    main()
