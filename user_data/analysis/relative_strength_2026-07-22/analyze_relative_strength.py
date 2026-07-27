#!/usr/bin/env python3
"""Attach pre-entry PAIR/BTC relative-strength features to archived long trades."""

from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path

import pandas as pd


DEFAULT_ARCHIVE = (
    "/freqtrade/user_data/analysis/long_micro_validation_2026-07-20/"
    "corrected_positive13_five_year-2026-07-20_05-54-29.zip"
)
DEFAULT_DATA_DIR = "/freqtrade/user_data/data/binance/futures"
DEFAULT_OUTPUT_DIR = "/freqtrade/user_data/analysis/relative_strength_2026-07-22"
STRATEGY = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"
BTC_PAIR = "BTC/USDT:USDT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path(DEFAULT_ARCHIVE))
    parser.add_argument("--data-dir", type=Path, default=Path(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", type=Path, default=Path(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def load_trades(archive: Path) -> pd.DataFrame:
    with zipfile.ZipFile(archive) as bundle:
        result_name = next(
            name
            for name in bundle.namelist()
            if name.endswith(".json") and not name.endswith("_config.json")
        )
        result = json.loads(bundle.read(result_name))

    trades = pd.DataFrame(result["strategy"][STRATEGY]["trades"])
    trades = trades.loc[~trades["is_short"]].copy()
    trades["open_date"] = pd.to_datetime(trades["open_date"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    trades["close_date"] = pd.to_datetime(trades["close_date"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    trades["entry_year"] = trades["open_date"].dt.year
    return trades


def candle_path(data_dir: Path, pair: str) -> Path:
    base, quote_settle = pair.split("/")
    quote, settle = quote_settle.split(":")
    return data_dir / f"{base}_{quote}_{settle}-1h-futures.feather"


def load_close(data_dir: Path, pair: str, close_name: str) -> pd.DataFrame:
    candles = pd.read_feather(candle_path(data_dir, pair), columns=["date", "close"])
    candles["date"] = pd.to_datetime(candles["date"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    candles = candles.rename(columns={"close": close_name})
    return candles.sort_values("date").drop_duplicates("date", keep="last")


def build_pair_features(
    data_dir: Path, pair: str, btc_close: pd.DataFrame
) -> pd.DataFrame:
    pair_close = load_close(data_dir, pair, "pair_close")
    aligned = pair_close.merge(btc_close, on="date", how="inner", validate="one_to_one")
    aligned["rs_ratio"] = aligned["pair_close"] / aligned["btc_close"]
    aligned["rs_ema24"] = aligned["rs_ratio"].ewm(
        span=24, adjust=False, min_periods=72
    ).mean()
    aligned["rs_ema72"] = aligned["rs_ratio"].ewm(
        span=72, adjust=False, min_periods=72
    ).mean()
    aligned["rs_slope_6h"] = aligned["rs_ema24"] / aligned["rs_ema24"].shift(6) - 1.0
    aligned["rs_rule_pass"] = (
        aligned["rs_ema24"].gt(aligned["rs_ema72"])
        & aligned["rs_slope_6h"].gt(0.0)
    )
    return aligned


def attach_features(
    trades: pd.DataFrame, data_dir: Path
) -> pd.DataFrame:
    btc_close = load_close(data_dir, BTC_PAIR, "btc_close")
    frames: list[pd.DataFrame] = []

    for pair, pair_trades in trades.groupby("pair", sort=True):
        current = pair_trades.sort_values("open_date").copy()
        if pair == BTC_PAIR:
            current["signal_date"] = current["open_date"] - pd.Timedelta(hours=1)
            current["rs_ratio"] = 1.0
            current["rs_ema24"] = 1.0
            current["rs_ema72"] = 1.0
            current["rs_slope_6h"] = 0.0
            current["rs_rule_pass"] = True
            current["rs_rule_scope"] = "btc_passthrough"
            frames.append(current)
            continue

        features = build_pair_features(data_dir, pair, btc_close)
        feature_columns = [
            "date",
            "rs_ratio",
            "rs_ema24",
            "rs_ema72",
            "rs_slope_6h",
            "rs_rule_pass",
        ]
        current = pd.merge_asof(
            current,
            features[feature_columns],
            left_on="open_date",
            right_on="date",
            direction="backward",
            allow_exact_matches=False,
        ).rename(columns={"date": "signal_date"})
        current["rs_rule_scope"] = "non_btc_filter"
        frames.append(current)

    enriched = pd.concat(frames, ignore_index=True).sort_values("open_date")
    enriched["rs_rule_pass"] = enriched["rs_rule_pass"].astype("boolean")
    return enriched


def profit_factor(values: pd.Series) -> float:
    gross_profit = values.loc[values > 0].sum()
    gross_loss = -values.loc[values < 0].sum()
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else math.nan
    return gross_profit / gross_loss


def summarize(frame: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    rows = []
    for keys, group in frame.groupby(group_columns, dropna=False, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_columns, keys))
        row.update(
            trades=len(group),
            wins=int(group["profit_abs"].gt(0).sum()),
            win_rate=group["profit_abs"].gt(0).mean(),
            profit_abs=group["profit_abs"].sum(),
            profit_abs_mean=group["profit_abs"].mean(),
            profit_ratio_sum=group["profit_ratio"].sum(),
            profit_factor=profit_factor(group["profit_abs"]),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def fmt_number(value: float, decimals: int = 3) -> str:
    if pd.isna(value):
        return "n/a"
    if math.isinf(value):
        return "inf"
    return f"{value:.{decimals}f}"


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(fmt_number)
    headers = [str(column) for column in display.columns]
    rows = [headers, ["---"] * len(headers)]
    rows.extend([[str(value) for value in row] for row in display.itertuples(index=False)])
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def write_outputs(enriched: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "trade_features.csv"
    enriched.to_csv(csv_path, index=False)

    non_btc = enriched.loc[enriched["rs_rule_scope"].eq("non_btc_filter")].copy()
    availability = non_btc["rs_rule_pass"].notna().mean()
    non_btc["rs_state"] = non_btc["rs_rule_pass"].map({True: "pass", False: "reject"})

    overall = summarize(non_btc, ["rs_state"])
    by_tag = summarize(non_btc, ["enter_tag", "rs_state"])
    by_year = summarize(non_btc, ["entry_year", "rs_state"])

    btc = enriched.loc[enriched["rs_rule_scope"].eq("btc_passthrough")].copy()
    btc["rs_state"] = "btc_passthrough"
    btc_by_tag = summarize(btc, ["enter_tag", "rs_state"])

    micro_columns = [
        "pair",
        "open_date",
        "profit_abs",
        "profit_ratio",
        "rs_ema24",
        "rs_ema72",
        "rs_slope_6h",
        "rs_state",
    ]
    all_states = pd.concat([non_btc, btc], ignore_index=True)
    micro = all_states.loc[
        all_states["enter_tag"].eq("long_pullback_restart_1h_body"), micro_columns
    ].copy()

    report = f"""# PAIR/BTC Relative-Strength Diagnostic

## Frozen rule

- Scope: existing non-BTC long entries from the corrected five-year LongMicro archive.
- Signal candle: latest completed 1h candle strictly before `open_date`.
- Pass: `EMA24(PAIR/BTC) > EMA72(PAIR/BTC)` and `EMA24` is above its value six hours earlier.
- BTC entries pass through unchanged and are excluded from the pass/reject attribution below.
- Feature availability: {availability:.2%} ({non_btc['rs_rule_pass'].notna().sum()}/{len(non_btc)}).

The profit sums below attribute archived trades in isolation. They are a screening diagnostic,
not a replacement for a portfolio backtest with stake sizing and max-open-trade contention.

## Overall non-BTC longs

{markdown_table(overall)}

## By entry tag

{markdown_table(by_tag)}

## By entry year

{markdown_table(by_year)}

## BTC passthrough

{markdown_table(btc_by_tag)}

## LongMicro trades

{markdown_table(micro)}
"""
    (output_dir / "diagnostic.md").write_text(report, encoding="utf-8")

    print(report)


def main() -> None:
    args = parse_args()
    trades = load_trades(args.archive)
    enriched = attach_features(trades, args.data_dir)
    write_outputs(enriched, args.output_dir)


if __name__ == "__main__":
    main()
