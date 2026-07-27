#!/usr/bin/env python3
"""Compare the current max3 archive with max4 and 3-short/1-long experiments."""

from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path

import pandas as pd


MAX3_STRATEGY = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"
MAX4_STRATEGY = MAX3_STRATEGY
SIDE_SLOTS_STRATEGY = "DualTrendPyramidSecondAdd20LongMicroSideSlots3S1LV1Strategy"
DEFAULT_MAX3 = Path(
    "/freqtrade/user_data/analysis/long_micro_validation_2026-07-20/"
    "corrected_positive13_five_year-2026-07-20_05-54-29.zip"
)
DEFAULT_MAX4 = Path(
    "/freqtrade/user_data/analysis/side_slots_3s1l_2026-07-22/five_year/"
    "backtest-result-2026-07-22_03-15-49.zip"
)
DEFAULT_OUTPUT = Path(
    "/freqtrade/user_data/analysis/side_slots_3s1l_2026-07-22"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max3", type=Path, default=DEFAULT_MAX3)
    parser.add_argument("--max4", type=Path, default=DEFAULT_MAX4)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_result(archive: Path, strategy_name: str) -> tuple[dict, pd.DataFrame]:
    with zipfile.ZipFile(archive) as bundle:
        result_name = next(
            name
            for name in bundle.namelist()
            if name.endswith(".json") and not name.endswith("_config.json")
        )
        strategy = json.loads(bundle.read(result_name))["strategy"][strategy_name]

    trades = pd.DataFrame(strategy["trades"])
    trades["open_date"] = pd.to_datetime(trades["open_date"], utc=True)
    trades["close_date"] = pd.to_datetime(trades["close_date"], utc=True)
    trades["side"] = trades["is_short"].map({True: "short", False: "long"})
    trades["entry_year"] = trades["open_date"].dt.year
    return strategy, trades


def profit_factor(values: pd.Series) -> float:
    gross_profit = values.loc[values > 0].sum()
    gross_loss = -values.loc[values < 0].sum()
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else math.nan
    return gross_profit / gross_loss


def metrics_row(label: str, strategy: dict) -> dict:
    return {
        "run": label,
        "max_open": strategy["max_open_trades"],
        "trades": strategy["total_trades"],
        "longs": strategy["trade_count_long"],
        "shorts": strategy["trade_count_short"],
        "profit_pct": strategy["profit_total"] * 100,
        "profit_abs": strategy["profit_total_abs"],
        "profit_factor": strategy["profit_factor"],
        "maxdd_account_pct": strategy["max_drawdown_account"] * 100,
        "long_profit_abs": strategy["profit_total_long_abs"],
        "short_profit_abs": strategy["profit_total_short_abs"],
    }


def summarize_tags(label: str, trades: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (side, tag), group in trades.groupby(["side", "enter_tag"], observed=True):
        rows.append(
            {
                "run": label,
                "side": side,
                "enter_tag": tag,
                "trades": len(group),
                "wins": int(group["profit_abs"].gt(0).sum()),
                "profit_abs": group["profit_abs"].sum(),
                "profit_factor": profit_factor(group["profit_abs"]),
            }
        )
    return pd.DataFrame(rows)


def summarize_years(label: str, strategy: dict) -> pd.DataFrame:
    rows = []
    for year in strategy["periodic_breakdown"]["year"]:
        rows.append(
            {
                "run": label,
                "year": pd.to_datetime(year["date"], dayfirst=True).year,
                "trades": year["trades"],
                "profit_abs": year["profit_abs"],
                "profit_factor": year["profit_factor"],
            }
        )
    return pd.DataFrame(rows)


KEY_COLUMNS = ["pair", "side", "enter_tag", "open_date"]


def add_duplicate_index(trades: pd.DataFrame) -> pd.DataFrame:
    keyed = trades.copy()
    keyed["key_duplicate"] = keyed.groupby(KEY_COLUMNS, dropna=False).cumcount()
    return keyed


def trade_differences(
    base: pd.DataFrame,
    candidate: pd.DataFrame,
    comparison: str,
) -> pd.DataFrame:
    base_keyed = add_duplicate_index(base)
    candidate_keyed = add_duplicate_index(candidate)
    keys = KEY_COLUMNS + ["key_duplicate"]

    candidate_check = candidate_keyed.merge(
        base_keyed[keys],
        on=keys,
        how="left",
        indicator=True,
    )
    extras = candidate_check.loc[candidate_check["_merge"].eq("left_only")].copy()
    extras["difference"] = "candidate_only"

    base_check = base_keyed.merge(
        candidate_keyed[keys],
        on=keys,
        how="left",
        indicator=True,
    )
    missing = base_check.loc[base_check["_merge"].eq("left_only")].copy()
    missing["difference"] = "base_only"

    output_columns = [
        "pair",
        "side",
        "enter_tag",
        "open_date",
        "close_date",
        "profit_abs",
        "profit_ratio",
        "exit_reason",
        "difference",
    ]
    result = pd.concat([extras[output_columns], missing[output_columns]], ignore_index=True)
    result.insert(0, "comparison", comparison)
    return result.sort_values(["difference", "open_date", "pair"])


def summarize_differences(differences: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (comparison, difference, side), group in differences.groupby(
        ["comparison", "difference", "side"], observed=True
    ):
        rows.append(
            {
                "comparison": comparison,
                "difference": difference,
                "side": side,
                "trades": len(group),
                "profit_abs_attributed": group["profit_abs"].sum(),
                "profit_factor": profit_factor(group["profit_abs"]),
            }
        )
    return pd.DataFrame(rows)


def fmt(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if isinstance(value, float):
        if math.isinf(value):
            return "inf"
        return f"{value:.3f}"
    return str(value)


def markdown_table(frame: pd.DataFrame) -> str:
    headers = [str(column) for column in frame.columns]
    rows = [headers, ["---"] * len(headers)]
    rows.extend([[fmt(value) for value in row] for row in frame.itertuples(index=False)])
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def main() -> None:
    args = parse_args()
    max3_strategy, max3_trades = load_result(args.max3, MAX3_STRATEGY)
    max4_strategy, max4_trades = load_result(args.max4, MAX4_STRATEGY)
    slots_strategy, slots_trades = load_result(args.max4, SIDE_SLOTS_STRATEGY)

    runs = {
        "max3_current": (max3_strategy, max3_trades),
        "max4_unrestricted": (max4_strategy, max4_trades),
        "max4_3short_1long": (slots_strategy, slots_trades),
    }
    metrics = pd.DataFrame(
        [metrics_row(label, strategy) for label, (strategy, _) in runs.items()]
    )
    tags = pd.concat(
        [summarize_tags(label, trades) for label, (_, trades) in runs.items()],
        ignore_index=True,
    )
    years = pd.concat(
        [summarize_years(label, strategy) for label, (strategy, _) in runs.items()],
        ignore_index=True,
    )

    differences = pd.concat(
        [
            trade_differences(max3_trades, max4_trades, "max4_unrestricted_vs_max3"),
            trade_differences(max3_trades, slots_trades, "max4_3short_1long_vs_max3"),
        ],
        ignore_index=True,
    )
    difference_summary = summarize_differences(differences)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "run_metrics.csv", index=False)
    tags.to_csv(args.output_dir / "tag_metrics.csv", index=False)
    years.to_csv(args.output_dir / "year_metrics.csv", index=False)
    differences.to_csv(args.output_dir / "trade_differences.csv", index=False)

    report = f"""# Side-Slot Audit

## Full-run metrics

{markdown_table(metrics)}

## Entry tags

{markdown_table(tags)}

## Calendar years

{markdown_table(years)}

## Executed-trade set differences

Trade identity uses `pair + side + enter_tag + exact open_date`. Attributed profit is the
archived profit of the run containing that trade and is not a counterfactual portfolio delta.

{markdown_table(difference_summary)}
"""
    (args.output_dir / "audit.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
