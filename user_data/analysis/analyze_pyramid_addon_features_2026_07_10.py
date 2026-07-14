from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/freqtrade/user_data")
RESULT_DIR = ROOT / "analysis" / "pyramid_risk_budget_2026-07-10"
DATA_DIR = ROOT / "data" / "binance" / "futures"
OUT_CSV = RESULT_DIR / "pyramid_addon_feature_diagnosis.csv"
OUT_SUMMARY = RESULT_DIR / "pyramid_addon_threshold_scan.csv"

BASELINE_STRATEGY = "DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy"
CANDIDATE_STRATEGY = "DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy"


def load_strategy_result(strategy: str) -> dict:
    for path in sorted(RESULT_DIR.glob("*.zip"), reverse=True):
        with zipfile.ZipFile(path) as archive:
            names = [
                name
                for name in archive.namelist()
                if name.endswith(".json") and "_config" not in name and ".meta" not in name
            ]
            if not names:
                continue
            payload = json.loads(archive.read(names[0]))
            if strategy in payload.get("strategy", {}):
                result = payload["strategy"][strategy]
                if result.get("backtest_start") == "2023-06-18 00:00:00" and result.get(
                    "backtest_end"
                ) == "2026-06-18 00:00:00":
                    return result
    raise RuntimeError(f"No matching 3y result found for {strategy}")


def pair_filename(pair: str, timeframe: str) -> Path:
    stem = pair.replace("/", "_").replace(":", "_")
    return DATA_DIR / f"{stem}-{timeframe}-futures.feather"


def load_features(pair: str) -> pd.DataFrame:
    df = pd.read_feather(pair_filename(pair, "1h")).copy()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    # OHLCV timestamps mark candle open; features are usable only after close.
    df["available_date"] = df["date"] + pd.Timedelta(hours=1)
    candle_range = (df["high"] - df["low"]).replace(0, np.nan)
    df["close_position"] = (df["close"] - df["low"]) / candle_range
    df["body_ratio"] = (df["close"] - df["open"]).abs() / candle_range
    df["ret_1h"] = df["close"].pct_change(1)
    df["ret_3h"] = df["close"].pct_change(3)
    df["ret_6h"] = df["close"].pct_change(6)
    df["ret_12h"] = df["close"].pct_change(12)
    df["ret_24h"] = df["close"].pct_change(24)
    df["ema20"] = df["close"].ewm(span=20, adjust=False, min_periods=20).mean()
    df["ema20_distance"] = (df["ema20"] - df["close"]) / df["ema20"]
    df["ema20_slope3"] = df["ema20"].pct_change(3)
    previous_close = df["close"].shift(1)
    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = true_range.rolling(14, min_periods=14).mean()
    df["atr_pct"] = df["atr14"] / df["close"]
    df["atr_pct_rank_30d"] = df["atr_pct"].rolling(720, min_periods=240).rank(pct=True)

    inf = pd.read_feather(pair_filename(pair, "4h")).copy()
    inf["date"] = pd.to_datetime(inf["date"], utc=True)
    inf["available_date"] = inf["date"] + pd.Timedelta(hours=4)
    inf["ema50_4h"] = inf["close"].ewm(span=50, adjust=False, min_periods=50).mean()
    inf["ema50_slope3_4h"] = inf["ema50_4h"].pct_change(3)
    inf["distance_ema50_4h"] = (inf["ema50_4h"] - inf["close"]) / inf["ema50_4h"]
    return pd.merge_asof(
        df.sort_values("available_date"),
        inf[["available_date", "ema50_slope3_4h", "distance_ema50_4h"]].sort_values("available_date"),
        on="available_date",
        direction="backward",
    )


def trade_key(trade: dict) -> tuple[str, str, str]:
    return trade["pair"], trade["open_date"], trade["enter_tag"]


def entry_orders(trade: dict) -> list[dict]:
    entry_side = "sell" if trade.get("is_short") else "buy"
    return [order for order in trade.get("orders", []) if order.get("ft_order_side") == entry_side]


def threshold_scan(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    features = [
        "add_profit",
        "add_delay_h",
        "close_position",
        "body_ratio",
        "ret_3h",
        "ret_6h",
        "ret_12h",
        "ret_24h",
        "ema20_distance",
        "ema20_slope3",
        "atr_pct",
        "atr_pct_rank_30d",
        "ema50_slope3_4h",
        "distance_ema50_4h",
        "stop_distance_from_add",
    ]
    total_positive = frame.loc[frame["delta_profit_abs"] > 0, "delta_profit_abs"].sum()
    total_negative = frame.loc[frame["delta_profit_abs"] < 0, "delta_profit_abs"].sum()
    for feature in features:
        valid = frame.dropna(subset=[feature])
        if len(valid) < 20:
            continue
        for quantile in (0.20, 0.30, 0.40, 0.60, 0.70, 0.80):
            threshold = float(valid[feature].quantile(quantile))
            for direction in ("keep_le", "keep_ge"):
                kept = valid[valid[feature] <= threshold] if direction == "keep_le" else valid[valid[feature] >= threshold]
                removed = valid.drop(index=kept.index)
                removed_positive = removed.loc[removed["delta_profit_abs"] > 0, "delta_profit_abs"].sum()
                removed_negative = removed.loc[removed["delta_profit_abs"] < 0, "delta_profit_abs"].sum()
                rows.append(
                    {
                        "feature": feature,
                        "direction": direction,
                        "quantile": quantile,
                        "threshold": threshold,
                        "kept": len(kept),
                        "removed": len(removed),
                        "kept_delta_profit_abs": kept["delta_profit_abs"].sum(),
                        "removed_positive_profit": removed_positive,
                        "removed_negative_profit": removed_negative,
                        "estimated_improvement": -removed["delta_profit_abs"].sum(),
                        "positive_profit_kill_pct": (
                            removed_positive / total_positive * 100 if total_positive > 0 else 0.0
                        ),
                        "negative_loss_removed_pct": (
                            removed_negative / total_negative * 100 if total_negative < 0 else 0.0
                        ),
                    }
                )
    return pd.DataFrame(rows).sort_values(
        ["estimated_improvement", "positive_profit_kill_pct"], ascending=[False, True]
    )


def main() -> None:
    baseline = load_strategy_result(BASELINE_STRATEGY)
    candidate = load_strategy_result(CANDIDATE_STRATEGY)
    baseline_map = {trade_key(trade): trade for trade in baseline["trades"]}
    feature_cache: dict[str, pd.DataFrame] = {}
    rows: list[dict] = []

    for trade in candidate["trades"]:
        orders = entry_orders(trade)
        if len(orders) < 2:
            continue
        pair = trade["pair"]
        baseline_trade = baseline_map.get(trade_key(trade))
        if baseline_trade is None:
            continue
        add_order = orders[1]
        add_time = pd.to_datetime(add_order["order_filled_timestamp"], unit="ms", utc=True)
        add_rate = float(add_order["safe_price"])
        add_stake = float(add_order["cost"])
        if pair not in feature_cache:
            feature_cache[pair] = load_features(pair)
        features = feature_cache[pair]
        candles = features[features["available_date"] <= add_time]
        if candles.empty:
            continue
        candle = candles.iloc[-1]
        open_rate = float(trade["open_rate"])
        add_profit = (open_rate - add_rate) / open_rate if trade["is_short"] else (add_rate - open_rate) / open_rate
        initial_stop = float(trade["initial_stop_loss_abs"])
        stop_distance = (initial_stop - add_rate) / add_rate if trade["is_short"] else (add_rate - initial_stop) / add_rate
        row = {
            "pair": pair,
            "open_date": trade["open_date"],
            "add_date": add_time.isoformat(),
            "add_delay_h": (add_time - pd.Timestamp(trade["open_date"])).total_seconds() / 3600.0,
            "add_rate": add_rate,
            "add_stake": add_stake,
            "add_profit": add_profit,
            "stop_distance_from_add": stop_distance,
            "candidate_profit_abs": float(trade["profit_abs"]),
            "baseline_profit_abs": float(baseline_trade["profit_abs"]),
            "delta_profit_abs": float(trade["profit_abs"]) - float(baseline_trade["profit_abs"]),
            "candidate_profit_ratio": float(trade["profit_ratio"]),
            "baseline_profit_ratio": float(baseline_trade["profit_ratio"]),
            "candidate_exit_reason": trade["exit_reason"],
            "baseline_exit_reason": baseline_trade["exit_reason"],
        }
        for feature in (
            "close_position",
            "body_ratio",
            "ret_1h",
            "ret_3h",
            "ret_6h",
            "ret_12h",
            "ret_24h",
            "ema20_distance",
            "ema20_slope3",
            "atr_pct",
            "atr_pct_rank_30d",
            "ema50_slope3_4h",
            "distance_ema50_4h",
        ):
            row[feature] = float(candle[feature]) if pd.notna(candle[feature]) else np.nan
        rows.append(row)

    result = pd.DataFrame(rows)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    threshold_scan(result).to_csv(OUT_SUMMARY, index=False, encoding="utf-8-sig")
    print(f"rows={len(result)} delta={result['delta_profit_abs'].sum():.3f}")
    print(pd.read_csv(OUT_SUMMARY).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
