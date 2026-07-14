import csv
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


BASE_DIR = Path("/freqtrade/user_data/analysis/pyramid_second_add_2026-07-13")
OUTPUT_DIR = Path("/freqtrade/user_data/analysis/pyramid_second_add_guard_2026-07-14")
DATA_DIR = Path("/freqtrade/user_data/data/binance/futures")
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


def pair_file(pair: str, timeframe: str) -> Path:
    symbol = pair.replace("/", "_").replace(":", "_")
    return DATA_DIR / f"{symbol}-{timeframe}-futures.feather"


def load_pair_df(pair: str, timeframe: str) -> pd.DataFrame:
    df = pd.read_feather(pair_file(pair, timeframe))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    candle_range = (df["high"] - df["low"]).replace(0, pd.NA)
    df["close_position"] = (df["close"] - df["low"]) / candle_range
    df["body_ratio"] = (df["close"] - df["open"]).abs() / candle_range
    df["range_pct"] = (df["high"] - df["low"]) / df["close"].replace(0, pd.NA)
    df["ret_1h"] = df["close"].pct_change(1)
    df["ret_3h"] = df["close"].pct_change(3)
    df["ret_6h"] = df["close"].pct_change(6)
    df["ret_12h"] = df["close"].pct_change(12)
    df["ret_24h"] = df["close"].pct_change(24)
    df["ema20"] = df["close"].ewm(span=20, adjust=False, min_periods=20).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False, min_periods=50).mean()
    df["ema20_slope_3"] = df["ema20"].pct_change(3)
    df["ema50_slope_3"] = df["ema50"].pct_change(3)
    df["dist_ema20"] = df["close"] / df["ema20"] - 1.0
    df["dist_ema50"] = df["close"] / df["ema50"] - 1.0
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["close"].shift(1)).abs()
    tr3 = (df["low"] - df["close"].shift(1)).abs()
    df["atr14"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14, min_periods=14).mean()
    df["atr_pct"] = df["atr14"] / df["close"].replace(0, pd.NA)
    df["vol_ratio_24"] = df["volume"] / df["volume"].rolling(24, min_periods=12).mean()
    df["lower_wick_ratio"] = (df[["open", "close"]].min(axis=1) - df["low"]) / candle_range
    df["upper_wick_ratio"] = (df["high"] - df[["open", "close"]].max(axis=1)) / candle_range
    return df


def latest_row_before(df: pd.DataFrame, timestamp_ms: int) -> pd.Series | None:
    ts = pd.Timestamp(datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc))
    idx = df["date"].searchsorted(ts, side="right") - 1
    if idx < 0:
        return None
    return df.iloc[int(idx)]


def safe_float(value) -> float:
    try:
        result = float(value)
    except Exception:
        return math.nan
    return result if math.isfinite(result) else math.nan


def short_profit(open_rate: float, current_rate: float) -> float:
    return open_rate / current_rate - 1.0 if open_rate > 0 and current_rate > 0 else math.nan


def main() -> None:
    pair_cache_1h: dict[str, pd.DataFrame] = {}
    pair_cache_4h: dict[str, pd.DataFrame] = {}
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

            pair = trade["pair"]
            if pair not in pair_cache_1h:
                pair_cache_1h[pair] = add_features(load_pair_df(pair, "1h"))
                pair_cache_4h[pair] = add_features(load_pair_df(pair, "4h"))

            first_add = entries[1]
            second_add = entries[2]
            second_ts = int(second_add["order_filled_timestamp"])
            row_1h = latest_row_before(pair_cache_1h[pair], second_ts)
            row_4h = latest_row_before(pair_cache_4h[pair], second_ts)
            if row_1h is None or row_4h is None:
                continue

            open_rate = safe_float(trade["open_rate"])
            first_rate = safe_float(first_add.get("safe_price"))
            second_rate = safe_float(second_add.get("safe_price"))
            delta_abs = safe_float(trade["profit_abs"]) - safe_float(base_trade["profit_abs"])

            rows.append(
                {
                    "sample": sample,
                    "pair": pair,
                    "open_date": trade["open_date"],
                    "second_add_time": datetime.fromtimestamp(second_ts / 1000, tz=timezone.utc).isoformat(),
                    "signal_1h_date": row_1h["date"].isoformat(),
                    "signal_4h_date": row_4h["date"].isoformat(),
                    "hours_after_open": round((second_ts - int(trade["open_timestamp"])) / 3600000, 2),
                    "hours_after_first_add": round((second_ts - int(first_add["order_filled_timestamp"])) / 3600000, 2),
                    "profit_at_first_add": round(short_profit(open_rate, first_rate), 5),
                    "profit_at_second_add": round(short_profit(open_rate, second_rate), 5),
                    "extra_drop_after_first_add": round(short_profit(first_rate, second_rate), 5),
                    "delta_abs": round(delta_abs, 5),
                    "delta_direction": "improved" if delta_abs > 1e-9 else "worsened" if delta_abs < -1e-9 else "same",
                    "exit_reason": trade.get("exit_reason", ""),
                    "baseline_exit_reason": base_trade.get("exit_reason", ""),
                    "close_position_1h": round(safe_float(row_1h["close_position"]), 5),
                    "body_ratio_1h": round(safe_float(row_1h["body_ratio"]), 5),
                    "range_pct_1h": round(safe_float(row_1h["range_pct"]), 5),
                    "ret_1h": round(safe_float(row_1h["ret_1h"]), 5),
                    "ret_3h": round(safe_float(row_1h["ret_3h"]), 5),
                    "ret_6h": round(safe_float(row_1h["ret_6h"]), 5),
                    "ret_12h": round(safe_float(row_1h["ret_12h"]), 5),
                    "ret_24h": round(safe_float(row_1h["ret_24h"]), 5),
                    "dist_ema20_1h": round(safe_float(row_1h["dist_ema20"]), 5),
                    "dist_ema50_1h": round(safe_float(row_1h["dist_ema50"]), 5),
                    "ema20_slope_3_1h": round(safe_float(row_1h["ema20_slope_3"]), 5),
                    "ema50_slope_3_1h": round(safe_float(row_1h["ema50_slope_3"]), 5),
                    "atr_pct_1h": round(safe_float(row_1h["atr_pct"]), 5),
                    "vol_ratio_24_1h": round(safe_float(row_1h["vol_ratio_24"]), 5),
                    "lower_wick_ratio_1h": round(safe_float(row_1h["lower_wick_ratio"]), 5),
                    "upper_wick_ratio_1h": round(safe_float(row_1h["upper_wick_ratio"]), 5),
                    "ret_4h_1": round(safe_float(row_4h["ret_1h"]), 5),
                    "ret_4h_3": round(safe_float(row_4h["ret_3h"]), 5),
                    "dist_ema20_4h": round(safe_float(row_4h["dist_ema20"]), 5),
                    "dist_ema50_4h": round(safe_float(row_4h["dist_ema50"]), 5),
                    "ema20_slope_3_4h": round(safe_float(row_4h["ema20_slope_3"]), 5),
                    "ema50_slope_3_4h": round(safe_float(row_4h["ema50_slope_3"]), 5),
                    "atr_pct_4h": round(safe_float(row_4h["atr_pct"]), 5),
                }
            )

    fields = list(rows[0].keys())
    out_csv = OUTPUT_DIR / "second_add15_candle_features.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
