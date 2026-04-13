import argparse
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path("/freqtrade")
USER_DATA = ROOT / "user_data"
STRATEGIES = USER_DATA / "strategies"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
CONFIG_PATH = USER_DATA / "config.backtest.futures.top9.json"
ENTER_TAG = "long_1h_highbase_breakout"

FEATURE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_center_shift_up",
    "near_major_high",
    "high_base_compression",
    "base_tight",
    "major_breakout",
    "breakout_volume_expansion",
    "bull_body_expansion",
    "rsi",
    "rsi_1d",
    "downtrend_1d",
    "bear_exhaustion_1d",
    "daily_center_lifting",
    "daily_not_making_new_lows",
    "daily_not_breaking_down",
    "close_1d",
    "ema_slow_1d",
    "mature_high_base",
    "breakout_close_near_high",
    "breakout_body_strength",
    "breakout_distance_ok",
    "breakout_daily_bias_ok",
    "long_breakout_probe",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--backtest-zip", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def load_config() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config.setdefault("candle_type_def", "futures")
    config.setdefault("runmode", "backtest")
    return config


def load_strategy(strategy_name: str, config: dict):
    if str(USER_DATA) not in sys.path:
        sys.path.insert(0, str(USER_DATA))
    if str(STRATEGIES) not in sys.path:
        sys.path.insert(0, str(STRATEGIES))
    path = STRATEGIES / f"{strategy_name}.py"
    spec = importlib.util.spec_from_file_location(strategy_name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    cls = getattr(mod, strategy_name)
    cfg = dict(config)
    cfg["strategy"] = strategy_name
    return cls(cfg)


def read_pair_dataframe(pair: str, timeframe: str) -> pd.DataFrame:
    pair_file = pair.replace("/", "_").replace(":", "_")
    path = DATA_DIR / f"{pair_file}-{timeframe}-futures.feather"
    df = pd.read_feather(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


class StaticDP:
    def __init__(self, pair_frames: dict[str, dict[str, pd.DataFrame]]):
        self.pair_frames = pair_frames

    def historic_ohlcv(self, pair_: str, timeframe: str, candle_type: str = ""):
        return self.get_pair_dataframe(pair_, timeframe, candle_type)

    def get_pair_dataframe(self, pair_: str, timeframe: str, candle_type: str = ""):
        return self.pair_frames[pair_][timeframe].copy()

    def market(self, pair_: str):
        base, quote = pair_.split("/")[0], "USDT"
        return {"quote": quote, "base": base, "spot": False}


def load_backtest_trades(zip_path: Path, strategy_name: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        entry_name = next(
            name
            for name in zf.namelist()
            if name.endswith(".json")
            and "_config" not in name
            and f"_{strategy_name}.json" not in name
        )
        report = json.loads(zf.read(entry_name))
    trades = report["strategy"][strategy_name]["trades"]
    df = pd.DataFrame(trades)
    df = df[df["enter_tag"] == ENTER_TAG].copy()
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True)
    df["close_date"] = pd.to_datetime(df["close_date"], utc=True)
    df["signal_date"] = df["open_date"] - pd.Timedelta(hours=1)
    df["profit_pct"] = df["profit_ratio"] * 100.0
    return df


def build_signal_frame(strategy_name: str, pairs: list[str]) -> pd.DataFrame:
    config = load_config()
    strategy = load_strategy(strategy_name, config)
    pair_frames = {
        pair: {
            "1h": read_pair_dataframe(pair, "1h"),
            "1d": read_pair_dataframe(pair, "1d"),
        }
        for pair in pairs
    }
    strategy.dp = StaticDP(pair_frames)
    raw_map = {pair: pair_frames[pair]["1h"].copy() for pair in pairs}
    indicator_map = strategy.advise_all_indicators(raw_map)
    frames: list[pd.DataFrame] = []
    for pair in pairs:
        frame = strategy.populate_entry_trend(indicator_map[pair].copy(), {"pair": pair})
        keep_cols = ["date", "enter_tag"] + [c for c in FEATURE_COLUMNS if c in frame.columns]
        picked = frame[keep_cols].copy()
        picked["pair"] = pair
        frames.append(picked)
    return pd.concat(frames, ignore_index=True)


def summarize_samples(merged: pd.DataFrame) -> dict:
    winners = merged[merged["profit_pct"] > 0].copy()
    losers = merged[merged["profit_pct"] <= 0].copy()

    numeric_cols = []
    bool_cols = []
    for col in FEATURE_COLUMNS:
        if col not in merged.columns:
            continue
        series = merged[col]
        if pd.api.types.is_bool_dtype(series) or series.dropna().isin([True, False]).all():
            bool_cols.append(col)
        elif pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)

    summary = {
        "sample_count": int(len(merged)),
        "winner_count": int(len(winners)),
        "loser_count": int(len(losers)),
        "pairs": merged["pair"].value_counts().to_dict(),
        "profit_pct": {
            "mean": round(float(merged["profit_pct"].mean()), 4),
            "median": round(float(merged["profit_pct"].median()), 4),
            "sum": round(float(merged["profit_pct"].sum()), 4),
        },
        "winners_vs_losers": {"numeric": {}, "bool_true_rate": {}},
    }

    for col in numeric_cols:
        summary["winners_vs_losers"]["numeric"][col] = {
            "winner_mean": round(float(winners[col].mean()), 6) if len(winners) else None,
            "loser_mean": round(float(losers[col].mean()), 6) if len(losers) else None,
            "delta": round(float(winners[col].mean() - losers[col].mean()), 6)
            if len(winners) and len(losers)
            else None,
        }

    for col in bool_cols:
        winner_rate = float(winners[col].fillna(False).astype(bool).mean()) if len(winners) else None
        loser_rate = float(losers[col].fillna(False).astype(bool).mean()) if len(losers) else None
        summary["winners_vs_losers"]["bool_true_rate"][col] = {
            "winner_rate": round(winner_rate, 6) if winner_rate is not None else None,
            "loser_rate": round(loser_rate, 6) if loser_rate is not None else None,
            "delta": round(winner_rate - loser_rate, 6)
            if winner_rate is not None and loser_rate is not None
            else None,
        }

    return summary


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    trades = load_backtest_trades(Path(args.backtest_zip), args.strategy)
    pairs = sorted(trades["pair"].unique().tolist())
    signal_frame = build_signal_frame(args.strategy, pairs)

    merged = trades.merge(
        signal_frame,
        left_on=["pair", "signal_date"],
        right_on=["pair", "date"],
        how="left",
        validate="one_to_one",
    )

    sample_csv = output_dir / f"{args.strategy}_breakout_samples.csv"
    summary_json = output_dir / f"{args.strategy}_breakout_summary.json"

    merged.sort_values(["open_date", "pair"]).to_csv(sample_csv, index=False)
    summary_json.write_text(
        json.dumps(summarize_samples(merged), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"saved samples: {sample_csv}")
    print(f"saved summary: {summary_json}")


if __name__ == "__main__":
    main()
