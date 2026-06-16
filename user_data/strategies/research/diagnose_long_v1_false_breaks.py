from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


USER_DATA = Path("/freqtrade/user_data")
RESULTS = USER_DATA / "backtest_results"
DATA = USER_DATA / "data" / "binance" / "futures"
OUT = USER_DATA / "strategies" / "research" / "long_v1_false_breaks"


def load_result(prefix: str, strategy: str) -> dict:
    zips = sorted(RESULTS.glob(f"{prefix}-*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise FileNotFoundError(prefix)
    with zipfile.ZipFile(zips[-1]) as zf:
        json_name = [n for n in zf.namelist() if n.endswith(".json") and not n.endswith("_config.json")][0]
        data = json.loads(zf.read(json_name))
    return data["strategy"][strategy]


def pair_file(pair: str) -> Path:
    symbol = pair.replace("/", "_").replace(":", "_")
    return DATA / f"{symbol}-1h-futures.feather"


def atr(dataframe: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = dataframe["close"].shift(1)
    tr = pd.concat(
        [
            dataframe["high"] - dataframe["low"],
            (dataframe["high"] - prev_close).abs(),
            (dataframe["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def indicators(pair: str) -> pd.DataFrame:
    df = pd.read_feather(pair_file(pair))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").set_index("date")
    df["atr_ref"] = atr(df).shift(1)
    df["compression_high"] = df["high"].shift(1).rolling(12).max()
    df["pullback_low_12"] = df["low"].shift(1).rolling(12).min()
    df["long_pullback_stop"] = df["pullback_low_12"] - 0.2 * df["atr_ref"]
    return df


def pct(value: float) -> float:
    return round(value * 100, 4)


def summarize(group: pd.DataFrame) -> dict:
    if group.empty:
        return {
            "trades": 0,
            "false_break_3h_pct": 0.0,
            "false_break_6h_pct": 0.0,
            "hit_half_r_6h_pct": 0.0,
            "hit_1r_12h_pct": 0.0,
            "avg_max_favorable_r": 0.0,
            "median_max_favorable_r": 0.0,
            "avg_max_adverse_r": 0.0,
            "median_max_adverse_r": 0.0,
        }
    return {
        "trades": int(len(group)),
        "false_break_3h_pct": pct(group["false_break_3h"].mean()),
        "false_break_6h_pct": pct(group["false_break_6h"].mean()),
        "hit_half_r_6h_pct": pct(group["hit_half_r_6h"].mean()),
        "hit_1r_12h_pct": pct(group["hit_1r_12h"].mean()),
        "avg_max_favorable_r": round(float(group["max_favorable_r"].mean()), 3),
        "median_max_favorable_r": round(float(group["max_favorable_r"].median()), 3),
        "avg_max_adverse_r": round(float(group["max_adverse_r"].mean()), 3),
        "median_max_adverse_r": round(float(group["max_adverse_r"].median()), 3),
    }


def diagnose(prefix: str, strategy: str, sample_label: str) -> tuple[pd.DataFrame, dict]:
    result = load_result(prefix, strategy)
    frames: dict[str, pd.DataFrame] = {}
    rows = []
    for trade in result["trades"]:
        if trade.get("enter_tag") != "long_pullback_restart":
            continue
        pair = trade["pair"]
        if pair not in frames:
            frames[pair] = indicators(pair)
        df = frames[pair]

        open_time = pd.Timestamp(trade["open_date"])
        close_time = pd.Timestamp(trade["close_date"])
        signal_candidates = df[df.index < open_time]
        if signal_candidates.empty:
            continue
        signal = signal_candidates.iloc[-1]
        compression_high = float(signal["compression_high"])
        signal_stop = float(signal["long_pullback_stop"])
        open_rate = float(trade["open_rate"])
        risk = (open_rate - signal_stop) / open_rate
        if not pd.notna(compression_high) or not pd.notna(risk) or risk <= 0:
            continue

        horizon = df[(df.index >= open_time) & (df.index <= min(close_time, open_time + pd.Timedelta(hours=12)))]
        first3 = horizon[horizon.index <= open_time + pd.Timedelta(hours=3)]
        first6 = horizon[horizon.index <= open_time + pd.Timedelta(hours=6)]
        first12 = horizon[horizon.index <= open_time + pd.Timedelta(hours=12)]
        if first12.empty:
            continue

        max_fav = (float(first12["high"].max()) - open_rate) / open_rate / risk
        max_adv = (open_rate - float(first12["low"].min())) / open_rate / risk
        rows.append(
            {
                "sample": sample_label,
                "pair": pair,
                "open_date": trade["open_date"],
                "close_date": trade["close_date"],
                "profit_ratio": float(trade["profit_ratio"]),
                "is_win": float(trade["profit_ratio"]) > 0,
                "risk_pct": risk,
                "compression_high": compression_high,
                "false_break_3h": bool((first3["close"] < compression_high).any()) if not first3.empty else False,
                "false_break_6h": bool((first6["close"] < compression_high).any()) if not first6.empty else False,
                "hit_half_r_6h": bool((((first6["high"] - open_rate) / open_rate) >= 0.5 * risk).any())
                if not first6.empty
                else False,
                "hit_1r_12h": bool((((first12["high"] - open_rate) / open_rate) >= risk).any()),
                "max_favorable_r": max_fav,
                "max_adverse_r": max_adv,
            }
        )

    detail = pd.DataFrame(rows)
    summary = {
        "sample": sample_label,
        "all": summarize(detail),
        "wins": summarize(detail[detail["is_win"]]),
        "losses": summarize(detail[~detail["is_win"]]),
    }
    if not detail.empty:
        losses = detail[~detail["is_win"]]
        summary["loss_false_break_3h_count"] = int(losses["false_break_3h"].sum())
        summary["loss_false_break_6h_count"] = int(losses["false_break_6h"].sum())
        summary["loss_count"] = int(len(losses))
    return detail, summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    strategy = "DualTrendCompressionRestartLongV1Strategy"
    details = []
    summaries = []
    for prefix, label in [
        ("long_v1_fixed_full", "full_20221001_20260507"),
        ("long_v1_fixed_recent", "recent_20250101_20260507"),
    ]:
        detail, summary = diagnose(prefix, strategy, label)
        details.append(detail)
        summaries.append(summary)

    detail_out = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    detail_path = OUT / "long_v1_false_break_diagnostics.csv"
    summary_path = OUT / "long_v1_false_break_diagnostics_summary.json"
    detail_out.to_csv(detail_path, index=False)
    summary_path.write_text(json.dumps(summaries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"csv": str(detail_path), "summary": str(summary_path), "summaries": summaries}, indent=2))


if __name__ == "__main__":
    main()
