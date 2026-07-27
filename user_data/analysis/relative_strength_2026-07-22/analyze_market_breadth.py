#!/usr/bin/env python3
"""Screen archived long trades with a frozen Positive13 4h market-breadth rule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from analyze_relative_strength import (
    DEFAULT_ARCHIVE,
    DEFAULT_DATA_DIR,
    DEFAULT_OUTPUT_DIR,
    load_trades,
    markdown_table,
    summarize,
)


DEFAULT_CONFIG = (
    "/freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path(DEFAULT_ARCHIVE))
    parser.add_argument("--config", type=Path, default=Path(DEFAULT_CONFIG))
    parser.add_argument("--data-dir", type=Path, default=Path(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", type=Path, default=Path(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def candle_path(data_dir: Path, pair: str) -> Path:
    base, quote_settle = pair.split("/")
    quote, settle = quote_settle.split(":")
    return data_dir / f"{base}_{quote}_{settle}-4h-futures.feather"


def load_pair_trend(data_dir: Path, pair: str) -> pd.DataFrame:
    candles = pd.read_feather(candle_path(data_dir, pair), columns=["date", "close"])
    candles["date"] = pd.to_datetime(candles["date"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    candles = candles.sort_values("date").drop_duplicates("date", keep="last")
    ema50 = candles["close"].ewm(span=50, adjust=False, min_periods=50).mean()
    ema200 = candles["close"].ewm(span=200, adjust=False, min_periods=200).mean()
    available = ema200.notna()
    trend_up = (
        candles["close"].gt(ema50)
        & ema50.gt(ema200)
        & ema50.gt(ema50.shift(3))
    )

    symbol = pair.split("/")[0]
    return pd.DataFrame(
        {
            # A 4h candle stamped 04:00 is usable only after it closes at 08:00.
            "market_state_date": candles["date"] + pd.Timedelta(hours=4),
            f"{symbol}_available": available,
            f"{symbol}_trend_up": trend_up,
        }
    )


def build_breadth(data_dir: Path, pairs: list[str]) -> pd.DataFrame:
    breadth: pd.DataFrame | None = None
    trend_columns: list[str] = []
    availability_columns: list[str] = []

    for pair in pairs:
        pair_trend = load_pair_trend(data_dir, pair)
        symbol = pair.split("/")[0]
        trend_columns.append(f"{symbol}_trend_up")
        availability_columns.append(f"{symbol}_available")
        breadth = (
            pair_trend
            if breadth is None
            else breadth.merge(pair_trend, on="market_state_date", how="outer")
        )

    assert breadth is not None
    breadth = breadth.sort_values("market_state_date")
    breadth[trend_columns] = (
        breadth[trend_columns].astype("boolean").fillna(False).astype(bool)
    )
    breadth[availability_columns] = (
        breadth[availability_columns].astype("boolean").fillna(False).astype(bool)
    )
    breadth["breadth_up_count"] = breadth[trend_columns].sum(axis=1)
    breadth["breadth_available_count"] = breadth[availability_columns].sum(axis=1)
    breadth["breadth_ratio_fixed13"] = breadth["breadth_up_count"] / len(pairs)
    breadth["breadth_rule_pass"] = breadth["breadth_up_count"].ge(7)
    return breadth[
        [
            "market_state_date",
            "breadth_up_count",
            "breadth_available_count",
            "breadth_ratio_fixed13",
            "breadth_rule_pass",
        ]
    ]


def attach_breadth(trades: pd.DataFrame, breadth: pd.DataFrame) -> pd.DataFrame:
    enriched = pd.merge_asof(
        trades.sort_values("open_date"),
        breadth.sort_values("market_state_date"),
        left_on="open_date",
        right_on="market_state_date",
        direction="backward",
        allow_exact_matches=False,
    )
    enriched["breadth_rule_pass"] = enriched["breadth_rule_pass"].astype("boolean")
    enriched["breadth_state"] = enriched["breadth_rule_pass"].map(
        {True: "pass", False: "reject"}
    )
    return enriched


def write_outputs(enriched: pd.DataFrame, output_dir: Path, pair_count: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_dir / "market_breadth_trade_features.csv", index=False)

    overall = summarize(enriched, ["breadth_state"])
    by_tag = summarize(enriched, ["enter_tag", "breadth_state"])
    by_year = summarize(enriched, ["entry_year", "breadth_state"])
    micro_columns = [
        "pair",
        "open_date",
        "profit_abs",
        "profit_ratio",
        "market_state_date",
        "breadth_up_count",
        "breadth_available_count",
        "breadth_state",
    ]
    micro = enriched.loc[
        enriched["enter_tag"].eq("long_pullback_restart_1h_body"), micro_columns
    ].copy()

    availability = enriched["breadth_rule_pass"].notna().mean()
    report = f"""# Positive13 4H Market-Breadth Diagnostic

## Frozen rule

- Universe: the {pair_count} pairs in the standard Positive13/max3 config.
- Per-pair uptrend: `close > EMA50 > EMA200` and EMA50 above its value three 4h bars earlier, matching the existing strategy definition.
- Pass: at least 7 of 13 configured pairs are in that uptrend state.
- Timing: latest 4h candle whose close is strictly before the archived trade `open_date`.
- Feature availability: {availability:.2%} ({enriched['breadth_rule_pass'].notna().sum()}/{len(enriched)}).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall longs

{markdown_table(overall)}

## By entry tag

{markdown_table(by_tag)}

## By entry year

{markdown_table(by_year)}

## LongMicro trades

{markdown_table(micro)}
"""
    (output_dir / "market_breadth_diagnostic.md").write_text(report, encoding="utf-8")
    print(report)


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    pairs = config["exchange"]["pair_whitelist"]
    trades = load_trades(args.archive)
    breadth = build_breadth(args.data_dir, pairs)
    enriched = attach_breadth(trades, breadth)
    write_outputs(enriched, args.output_dir, len(pairs))


if __name__ == "__main__":
    main()
