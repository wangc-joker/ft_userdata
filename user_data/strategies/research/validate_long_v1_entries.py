from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


USER_DATA = Path("/freqtrade/user_data")
RESULTS = USER_DATA / "backtest_results"
DATA = USER_DATA / "data" / "binance" / "futures"
OUT = USER_DATA / "strategies" / "research" / "long_v1_validation"


def load_result(prefix: str) -> dict:
    zips = sorted(RESULTS.glob(f"{prefix}-*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise FileNotFoundError(prefix)
    with zipfile.ZipFile(zips[-1]) as zf:
        json_name = [n for n in zf.namelist() if n.endswith(".json") and not n.endswith("_config.json")][0]
        data = json.loads(zf.read(json_name))
    return data["strategy"]["DualTrendCompressionRestartLongV1Strategy"]


def pair_file(pair: str) -> Path:
    symbol = pair.replace("/", "_").replace(":", "_")
    return DATA / f"{symbol}-1h-futures.feather"


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def indicators(pair: str) -> pd.DataFrame:
    df = pd.read_feather(pair_file(pair))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").set_index("date")
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    df["atr_ref"] = df["atr"].shift(1)
    df["compression_high"] = df["high"].shift(1).rolling(12).max()
    df["pullback_low_12"] = df["low"].shift(1).rolling(12).min()
    df["return_24h"] = df["close"].shift(1) / df["close"].shift(25) - 1
    df["recent_high_24"] = df["high"].shift(1).rolling(24).max()
    df["pullback_depth_long"] = (df["recent_high_24"] - df["pullback_low_12"]) / df["recent_high_24"]
    candle_range = (df["high"] - df["low"]).replace(0, pd.NA)
    df["close_position"] = (df["close"] - df["low"]) / candle_range
    df["body_pct_of_range"] = (df["close"] - df["open"]).abs() / candle_range
    df["long_pullback_stop"] = df["pullback_low_12"] - 0.2 * df["atr_ref"]
    df["long_pullback_risk_pct"] = (df["close"] - df["long_pullback_stop"]) / df["close"]
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = load_result("long_v1_fixed_full")
    frames = {}
    rows = []
    for trade in result["trades"]:
        pair = trade["pair"]
        if pair not in frames:
            frames[pair] = indicators(pair)
        df = frames[pair]
        open_time = pd.Timestamp(trade["open_date"])
        signal_candidates = df[df.index < open_time]
        candle = signal_candidates.iloc[-1] if not signal_candidates.empty else df.loc[:open_time].iloc[-1]
        risk_from_signal_close = float(candle["long_pullback_risk_pct"])
        risk_from_trade_open = (float(trade["open_rate"]) - float(candle["long_pullback_stop"])) / float(trade["open_rate"])
        rows.append(
            {
                "pair": pair,
                "open_date": trade["open_date"],
                "enter_tag": trade["enter_tag"],
                "profit_ratio": trade["profit_ratio"],
                "close_position": float(candle["close_position"]),
                "body_pct_of_range": float(candle["body_pct_of_range"]),
                "return_24h": float(candle["return_24h"]),
                "pullback_depth_long": float(candle["pullback_depth_long"]),
                "risk_from_signal_close": risk_from_signal_close,
                "risk_from_trade_open": risk_from_trade_open,
                "initial_stop": float(candle["long_pullback_stop"]),
                "trade_initial_stop": trade["initial_stop_loss_abs"],
                "close_position_ok": float(candle["close_position"]) >= 0.72,
                "signal_risk_ok": 0.005 <= risk_from_signal_close <= 0.05,
                "trade_open_risk_ok": risk_from_trade_open <= 0.05,
            }
        )
    out = pd.DataFrame(rows)
    out_path = OUT / "long_v1_entry_filter_validation.csv"
    out.to_csv(out_path, index=False)
    summary = {
        "trades": int(len(out)),
        "close_position_min": float(out["close_position"].min()),
        "close_position_violations": int((~out["close_position_ok"]).sum()),
        "signal_risk_max": float(out["risk_from_signal_close"].max()),
        "signal_risk_violations": int((~out["signal_risk_ok"]).sum()),
        "trade_open_risk_max": float(out["risk_from_trade_open"].max()),
        "trade_open_risk_gt_5pct": int((~out["trade_open_risk_ok"]).sum()),
        "csv": str(out_path),
    }
    summary_path = OUT / "long_v1_entry_filter_validation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
