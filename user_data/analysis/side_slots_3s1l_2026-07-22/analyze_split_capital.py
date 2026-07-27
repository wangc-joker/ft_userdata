#!/usr/bin/env python3
"""Reconstruct an 80% short / 20% long portfolio from isolated engines."""

from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path

import pandas as pd

from freqtrade.data.metrics import calculate_max_drawdown


SHORT_STRATEGY = "DualTrendPyramidSecondAdd20LongMicroShortOnlyV1Strategy"
LONG_STRATEGY = "DualTrendPyramidSecondAdd20LongMicroLongOnlyV1Strategy"
CURRENT_STRATEGY = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"
DEFAULT_SPLIT = Path(
    "/freqtrade/user_data/analysis/side_slots_3s1l_2026-07-22/split_capital/"
    "backtest-result-2026-07-22_03-33-28.zip"
)
DEFAULT_CURRENT = Path(
    "/freqtrade/user_data/analysis/long_micro_validation_2026-07-20/"
    "corrected_positive13_five_year-2026-07-20_05-54-29.zip"
)
DEFAULT_OUTPUT = Path(
    "/freqtrade/user_data/analysis/side_slots_3s1l_2026-07-22"
)
SHORT_WEIGHT = 0.80
LONG_WEIGHT = 0.20
STARTING_BALANCE = 1000.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-archive", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--current-archive", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_strategy(archive: Path, strategy_name: str) -> tuple[dict, pd.DataFrame]:
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
    return strategy, trades


def profit_factor(values: pd.Series) -> float:
    gross_profit = values.loc[values > 0].sum()
    gross_loss = -values.loc[values < 0].sum()
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else math.nan
    return gross_profit / gross_loss


def engine_row(label: str, strategy: dict) -> dict:
    return {
        "portfolio": label,
        "trades": strategy["total_trades"],
        "profit_pct": strategy["profit_total"] * 100,
        "profit_abs": strategy["profit_total_abs"],
        "profit_factor": strategy["profit_factor"],
        "maxdd_account_pct": strategy["max_drawdown_account"] * 100,
    }


def weighted_portfolio(short_trades: pd.DataFrame, long_trades: pd.DataFrame) -> pd.DataFrame:
    short_scaled = short_trades[["close_date", "profit_abs"]].copy()
    short_scaled["profit_abs"] *= SHORT_WEIGHT
    short_scaled["engine"] = "short"
    long_scaled = long_trades[["close_date", "profit_abs"]].copy()
    long_scaled["profit_abs"] *= LONG_WEIGHT
    long_scaled["engine"] = "long"
    return pd.concat([short_scaled, long_scaled], ignore_index=True).sort_values("close_date")


def portfolio_row(portfolio: pd.DataFrame, days: int) -> tuple[dict, object]:
    profit_abs = portfolio["profit_abs"].sum()
    final_balance = STARTING_BALANCE + profit_abs
    drawdown = calculate_max_drawdown(
        portfolio,
        starting_balance=STARTING_BALANCE,
        relative=False,
    )
    cagr = (final_balance / STARTING_BALANCE) ** (365.0 / days) - 1.0
    return (
        {
            "portfolio": "split_80short_20long",
            "trades": len(portfolio),
            "profit_pct": profit_abs / STARTING_BALANCE * 100,
            "profit_abs": profit_abs,
            "profit_factor": profit_factor(portfolio["profit_abs"]),
            "maxdd_account_pct": drawdown.relative_account_drawdown * 100,
            "cagr_pct": cagr * 100,
        },
        drawdown,
    )


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
    short_strategy, short_trades = load_strategy(args.split_archive, SHORT_STRATEGY)
    long_strategy, long_trades = load_strategy(args.split_archive, LONG_STRATEGY)
    current_strategy, _ = load_strategy(args.current_archive, CURRENT_STRATEGY)

    portfolio = weighted_portfolio(short_trades, long_trades)
    split_row, drawdown = portfolio_row(portfolio, current_strategy["backtest_days"])
    rows = [
        engine_row("current_shared_max3", current_strategy),
        engine_row("short_only_100pct", short_strategy),
        engine_row("long_only_100pct", long_strategy),
        split_row,
    ]
    metrics = pd.DataFrame(rows)

    portfolio["year"] = portfolio["close_date"].dt.year
    annual = portfolio.groupby(["year", "engine"], observed=True)["profit_abs"].sum().unstack(
        fill_value=0.0
    )
    annual["combined_profit_abs"] = annual.sum(axis=1)
    annual = annual.reset_index()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    portfolio.to_csv(args.output_dir / "split_80short_20long_events.csv", index=False)
    metrics.to_csv(args.output_dir / "split_capital_metrics.csv", index=False)
    annual.to_csv(args.output_dir / "split_capital_annual.csv", index=False)

    report = f"""# Split-Capital Audit

## Metrics

{markdown_table(metrics)}

## 80/20 annual realized profit

{markdown_table(annual)}

## Drawdown interval

- High: {drawdown.high_date} at {STARTING_BALANCE + drawdown.high_value:.3f} USDT.
- Low: {drawdown.low_date} at {STARTING_BALANCE + drawdown.low_value:.3f} USDT.
- Absolute drawdown: {drawdown.drawdown_abs:.3f} USDT.
- Account drawdown: {drawdown.relative_account_drawdown:.3%}.

The reconstruction scales standalone 1000-USDT engine PnL by fixed 80/20 weights. Existing
minimum long stake remains above the exchange minimum after 20% scaling, so the linear scaling
does not create a minimum-order discontinuity in the observed sample.
"""
    (args.output_dir / "split_capital_audit.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
