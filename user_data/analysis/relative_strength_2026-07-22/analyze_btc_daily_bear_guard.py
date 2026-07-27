#!/usr/bin/env python3
"""Screen archived long trades with a frozen BTC daily bear-regime guard."""

from __future__ import annotations

import argparse
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


BTC_DAILY_FILE = "BTC_USDT_USDT-1d-futures.feather"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path(DEFAULT_ARCHIVE))
    parser.add_argument("--data-dir", type=Path, default=Path(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", type=Path, default=Path(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def build_btc_regime(data_dir: Path) -> pd.DataFrame:
    candles = pd.read_feather(
        data_dir / BTC_DAILY_FILE,
        columns=["date", "close"],
    )
    candles["date"] = pd.to_datetime(candles["date"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    candles = candles.sort_values("date").drop_duplicates("date", keep="last")
    ema50 = candles["close"].ewm(span=50, adjust=False, min_periods=50).mean()
    ema200 = candles["close"].ewm(span=200, adjust=False, min_periods=200).mean()
    available = ema200.notna()
    bear = (
        candles["close"].lt(ema50)
        & ema50.lt(ema200)
        & ema50.lt(ema50.shift(3))
    )
    return pd.DataFrame(
        {
            # A daily candle stamped at midnight is usable after the next midnight.
            "btc_regime_date": candles["date"] + pd.Timedelta(days=1),
            "btc_daily_close": candles["close"],
            "btc_daily_ema50": ema50,
            "btc_daily_ema200": ema200,
            "btc_daily_bear": bear.where(available),
        }
    )


def attach_regime(trades: pd.DataFrame, regime: pd.DataFrame) -> pd.DataFrame:
    enriched = pd.merge_asof(
        trades.sort_values("open_date"),
        regime.sort_values("btc_regime_date"),
        left_on="open_date",
        right_on="btc_regime_date",
        direction="backward",
        allow_exact_matches=False,
    )
    enriched["btc_daily_bear"] = enriched["btc_daily_bear"].astype("boolean")
    enriched["btc_bear_guard_pass"] = ~enriched["btc_daily_bear"]
    enriched["btc_bear_guard_state"] = enriched["btc_bear_guard_pass"].map(
        {True: "pass", False: "reject"}
    )
    return enriched


def write_outputs(enriched: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_dir / "btc_daily_bear_trade_features.csv", index=False)

    overall = summarize(enriched, ["btc_bear_guard_state"])
    by_tag = summarize(enriched, ["enter_tag", "btc_bear_guard_state"])
    by_year = summarize(enriched, ["entry_year", "btc_bear_guard_state"])
    rejected = enriched.loc[
        enriched["btc_bear_guard_state"].eq("reject"),
        [
            "pair",
            "open_date",
            "enter_tag",
            "profit_abs",
            "profit_ratio",
            "btc_regime_date",
            "btc_daily_close",
            "btc_daily_ema50",
            "btc_daily_ema200",
        ],
    ].copy()

    availability = enriched["btc_daily_bear"].notna().mean()
    report = f"""# BTC Daily Bear-Regime Guard Diagnostic

## Frozen rule

- Pass all existing long entries except during a confirmed BTC daily bear regime.
- Bear regime: `BTC close < EMA50 < EMA200` and EMA50 below its value three daily bars earlier.
- Timing: latest daily candle whose close is strictly before the archived trade `open_date`.
- Feature availability: {availability:.2%} ({enriched['btc_daily_bear'].notna().sum()}/{len(enriched)}).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall longs

{markdown_table(overall)}

## By entry tag

{markdown_table(by_tag)}

## By entry year

{markdown_table(by_year)}

## Rejected trades

{markdown_table(rejected)}
"""
    (output_dir / "btc_daily_bear_guard_diagnostic.md").write_text(
        report,
        encoding="utf-8",
    )
    print(report)


def main() -> None:
    args = parse_args()
    trades = load_trades(args.archive)
    regime = build_btc_regime(args.data_dir)
    enriched = attach_regime(trades, regime)
    write_outputs(enriched, args.output_dir)


if __name__ == "__main__":
    main()
