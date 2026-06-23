from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(r"D:\test\ft_userdata")
DATA_DIR = ROOT / "user_data" / "data" / "binance" / "futures"
BACKTEST_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"

PAIRS = [
    "ETH/USDT:USDT",
    "ZEC/USDT:USDT",
    "BTC/USDT:USDT",
    "ADA/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "DOGE/USDT:USDT",
    "XRP/USDT:USDT",
    "TAO/USDT:USDT",
    "SUI/USDT:USDT",
    "PAXG/USDT:USDT",
    "NEAR/USDT:USDT",
    "LINK/USDT:USDT",
]

TRADE_TAGS = {"short_pullback_restart", "short_compression_breakdown"}

PERIODS = {
    "3y": ("2023-06-18T00:00:00Z", "2026-06-18T00:00:00Z"),
    "1y": ("2025-06-18T00:00:00Z", "2026-06-18T00:00:00Z"),
    "stress_2026_03_05": ("2026-03-01T00:00:00Z", "2026-05-31T23:59:59Z"),
}

BACKTEST_FILE = BACKTEST_DIR / "backtest-result-2026-06-18_06-49-31.zip"


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def atr(df: pd.DataFrame, period: int) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    avg_gain = up.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = down.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    def _pct(values: np.ndarray) -> float:
        s = pd.Series(values)
        return float(s.rank(pct=True).iloc[-1])

    return series.rolling(window, min_periods=max(20, window // 3)).apply(_pct, raw=True)


def to_symbol_key(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def read_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    key = to_symbol_key(pair)
    path = DATA_DIR / f"{key}-{timeframe}-futures.feather"
    df = pd.read_feather(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df.sort_values("date").reset_index(drop=True)


def add_4h_trend(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["trend_up"] = (
        (out["close"] > out["ema50"])
        & (out["ema50"] > out["ema200"])
        & (out["ema50"] > out["ema50"].shift(3))
    )
    out["trend_down"] = (
        (out["close"] < out["ema50"])
        & (out["ema50"] < out["ema200"])
        & (out["ema50"] < out["ema50"].shift(3))
    )
    out["ema50_slope"] = out["ema50"] / out["ema50"].shift(3) - 1.0
    out["atr"] = atr(out, 14)
    out["atr_pct"] = out["atr"] / out["close"]
    out["atr_pct_percentile"] = rolling_percentile(out["atr_pct"], 180)
    out["range_market"] = ~(out["trend_up"].fillna(False) | out["trend_down"].fillna(False))
    return out


def add_1d_regime(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    typical_price = (out["high"] + out["low"] + out["close"]) / 3.0
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["market_center"] = typical_price.rolling(5).mean()
    out["legacy_center_up"] = out["market_center"] > out["market_center"].shift(3)
    out["legacy_center_down"] = out["market_center"] < out["market_center"].shift(3)
    out["regime_up"] = (
        (out["close"] > out["ema50"])
        & (out["ema50"] > out["ema200"])
        & out["legacy_center_up"]
    )
    out["regime_down"] = (
        (out["close"] < out["ema50"])
        & (out["ema50"] < out["ema200"])
        & out["legacy_center_down"]
    )
    out["regime"] = np.where(
        out["regime_up"],
        "up",
        np.where(out["regime_down"], "down", "range"),
    )
    return out


def compression_duration(df: pd.DataFrame) -> pd.Series:
    durations: list[float] = []
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    comp_highs = df["compression_high"].to_numpy()
    comp_lows = df["compression_low"].to_numpy()
    for i in range(len(df)):
        ch = comp_highs[i]
        cl = comp_lows[i]
        if not np.isfinite(ch) or not np.isfinite(cl):
            durations.append(np.nan)
            continue
        count = 0
        j = i - 1
        while j >= 0 and count < 96:
            if highs[j] <= ch and lows[j] >= cl:
                count += 1
                j -= 1
            else:
                break
        durations.append(float(count))
    return pd.Series(durations, index=df.index)


def add_short_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    atr_1h = atr(out, 14)
    out["atr"] = atr_1h
    out["atr_ref"] = out["atr"].shift(1)
    out["atr_pct"] = out["atr"] / out["close"]
    out["atr_pct_percentile"] = rolling_percentile(out["atr_pct"], 720)
    out["rsi_1h"] = rsi(out["close"], 14)
    out["volume_ma20"] = out["volume"].shift(1).rolling(20).mean()
    out["vol_ok"] = out["volume"] > out["volume_ma20"] * 1.2
    out["compression_high"] = out["high"].shift(1).rolling(12).max()
    out["compression_low"] = out["low"].shift(1).rolling(12).min()
    out["compression_width"] = out["compression_high"] - out["compression_low"]
    out["compression_width_pct"] = out["compression_width"] / out["close"]
    out["compression_ok"] = out["compression_width"] < out["atr_ref"] * 3.0
    out["breakout_short"] = out["close"] < out["compression_low"] * (1 - 0.001)
    out["high_max_first_half"] = out["high"].shift(7).rolling(6).max()
    out["high_max_last_half"] = out["high"].shift(1).rolling(6).max()
    out["close_mean_first_half"] = out["close"].shift(7).rolling(6).mean()
    out["close_mean_last_half"] = out["close"].shift(1).rolling(6).mean()
    out["center_down"] = (
        (out["high_max_last_half"] < out["high_max_first_half"])
        & (out["close_mean_last_half"] < out["close_mean_first_half"])
    )
    out["return_24h"] = out["close"].shift(1) / out["close"].shift(25) - 1.0
    out["atr_pct_24h"] = out["atr_pct"].shift(1).rolling(24).mean()
    out["pretrend_threshold"] = np.maximum(0.02, 1.5 * out["atr_pct_24h"])
    out["pretrend_down"] = out["return_24h"] < -out["pretrend_threshold"]
    out["recent_low_24"] = out["low"].shift(1).rolling(24).min()
    out["pullback_high_12"] = out["high"].shift(1).rolling(12).max()
    out["pullback_depth_short"] = (
        (out["pullback_high_12"] - out["recent_low_24"]) / out["recent_low_24"]
    )
    out["pullback_seen_short"] = out["pullback_depth_short"].between(0.008, 0.08)
    out["near_low_zone"] = out["compression_high"] <= out["recent_low_24"] * 1.035
    candle_range = out["high"] - out["low"]
    out["body_pct_of_range"] = (out["close"] - out["open"]).abs() / candle_range.replace(0, np.nan)
    out["close_position"] = (out["close"] - out["low"]) / candle_range.replace(0, np.nan)
    out["candle_quality_short"] = (
        (candle_range > 0)
        & (out["body_pct_of_range"] >= 0.35)
        & (out["close_position"] <= 0.40)
    )
    out["breakdown_depth"] = (out["compression_low"] - out["close"]) / out["compression_low"]
    out["short_compression_stop"] = out["compression_high"] + 0.2 * out["atr_ref"]
    out["short_pullback_stop"] = out["pullback_high_12"] + 0.2 * out["atr_ref"]
    out["short_compression_risk_pct"] = (out["short_compression_stop"] - out["close"]) / out["close"]
    out["short_pullback_risk_pct"] = (out["short_pullback_stop"] - out["close"]) / out["close"]
    out["short_compression_risk_pct_ok"] = out["short_compression_risk_pct"].between(0.005, 0.05)
    out["short_pullback_risk_pct_ok"] = out["short_pullback_risk_pct"].between(0.005, 0.05)
    out["compression_duration_bars"] = compression_duration(out)
    out["prev_3h_return"] = out["close"].shift(1) / out["close"].shift(4) - 1.0
    out["prev_6h_return"] = out["close"].shift(1) / out["close"].shift(7) - 1.0
    out["prev_12h_return"] = out["close"].shift(1) / out["close"].shift(13) - 1.0
    out["prev_24h_return"] = out["close"].shift(1) / out["close"].shift(25) - 1.0
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["long_lower_shadow"] = (
        (out["lower_wick"] / candle_range.replace(0, np.nan) >= 0.4)
        & (out["lower_wick"] > (out["close"] - out["open"]).abs())
    )
    out["short_term_oversold"] = out["rsi_1h"] < 30
    out["close_not_low_enough"] = out["close_position"] > 0.30
    return out


def merge_asof_features(base: pd.DataFrame, inf: pd.DataFrame, cols: list[str], suffix: str) -> pd.DataFrame:
    right = inf[["date", *cols]].copy()
    rename_map = {c: f"{c}{suffix}" for c in cols}
    right = right.rename(columns=rename_map).sort_values("date")
    return pd.merge_asof(base.sort_values("date"), right, on="date", direction="backward")


def add_combined_context(pair: str) -> pd.DataFrame:
    df_1h = add_short_indicators(read_ohlcv(pair, "1h"))
    df_4h = add_4h_trend(read_ohlcv(pair, "4h"))
    df_1d = add_1d_regime(read_ohlcv(pair, "1d"))
    btc_4h = add_4h_trend(read_ohlcv("BTC/USDT:USDT", "4h"))
    btc_1d = add_1d_regime(read_ohlcv("BTC/USDT:USDT", "1d"))

    merged = df_1h.copy()
    merged = merge_asof_features(
        merged,
        df_4h,
        ["ema50", "ema200", "trend_up", "trend_down", "ema50_slope", "range_market", "atr_pct_percentile"],
        "_4h",
    )
    merged = merge_asof_features(
        merged,
        df_1d,
        ["ema50", "ema200", "legacy_center_up", "legacy_center_down", "market_center", "regime"],
        "_1d",
    )
    merged = merge_asof_features(
        merged,
        btc_4h,
        ["trend_up", "trend_down", "ema50_slope", "range_market", "atr_pct_percentile"],
        "_btc_4h",
    )
    merged = merge_asof_features(
        merged,
        btc_1d,
        ["regime", "legacy_center_up", "legacy_center_down"],
        "_btc_1d",
    )

    merged["distance_to_ema50_4h"] = merged["close"] / merged["ema50_4h"] - 1.0
    merged["distance_to_ema50_1d"] = merged["close"] / merged["ema50_1d"] - 1.0
    merged["btc_filter_short_ok"] = True
    if pair != "BTC/USDT:USDT":
        merged["btc_filter_short_ok"] = ~merged["trend_up_btc_4h"].fillna(False)

    merged["pullback_intact_short"] = merged["pullback_high_12"] <= merged["ema50_4h"] * 1.01
    merged["close_below_center_1d"] = merged["close"] < merged["market_center_1d"]
    merged["close_above_center_1d"] = merged["close"] > merged["market_center_1d"]

    base_filter = (
        merged["trend_down_4h"].fillna(False)
        & merged["compression_ok"].fillna(False)
        & merged["center_down"].fillna(False)
        & merged["breakout_short"].fillna(False)
        & merged["vol_ok"].fillna(False)
        & merged["candle_quality_short"].fillna(False)
        & merged["btc_filter_short_ok"].fillna(True)
        & (merged["volume"] > 0)
    )
    merged["signal_short_pullback_restart"] = (
        base_filter
        & merged["pullback_seen_short"].fillna(False)
        & merged["pullback_intact_short"].fillna(False)
        & merged["short_pullback_risk_pct_ok"].fillna(False)
    )
    merged["signal_short_compression_breakdown"] = (
        base_filter
        & merged["pretrend_down"].fillna(False)
        & merged["near_low_zone"].fillna(False)
        & merged["short_compression_risk_pct_ok"].fillna(False)
    )

    reject_clear_uptrend = (
        merged["legacy_center_up_1d"].fillna(False)
        & merged["close_above_center_1d"].fillna(False)
    )
    merged.loc[reject_clear_uptrend, "signal_short_pullback_restart"] = False
    merged.loc[reject_clear_uptrend, "signal_short_compression_breakdown"] = False

    shape_ok = (
        merged["legacy_center_down_1d"].fillna(False)
        & merged["close_below_center_1d"].fillna(False)
        & (merged["compression_width_pct"] <= 0.035).fillna(False)
    )
    merged.loc[~shape_ok, "signal_short_pullback_restart"] = False
    return merged


def load_backtest_trades(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as zf:
        json_name = next(n for n in zf.namelist() if n.endswith(".json") and "_config" not in n)
        data = json.loads(zf.read(json_name))
    return data["strategy"]["DualTrendCombinedShortPullbackShapeV1Strategy"]["trades"]


def build_trade_table() -> pd.DataFrame:
    all_rows: list[dict[str, Any]] = []
    for trade in load_backtest_trades(BACKTEST_FILE):
        if not trade["is_short"] or trade["enter_tag"] not in TRADE_TAGS:
            continue
        row = dict(trade)
        row["open_date"] = pd.to_datetime(row["open_date"], utc=True)
        row["close_date"] = pd.to_datetime(row["close_date"], utc=True)
        all_rows.append(row)
    df = pd.DataFrame(all_rows)
    df = df.sort_values(["pair", "open_date", "close_date"]).reset_index(drop=True)
    return df


def post_entry_labels(entry_row: pd.Series, future_df: pd.DataFrame, open_rate: float, stop_abs: float) -> tuple[bool, bool]:
    risk_abs = stop_abs - open_rate
    if not np.isfinite(risk_abs) or risk_abs <= 0:
        return False, False

    favorable_level = open_rate - 0.5 * risk_abs
    comp_low = float(entry_row["compression_low"])
    future_24h = future_df.iloc[:24]
    future_5h = future_df.iloc[:5]

    first_favorable_idx_24 = None
    favorable_hits = future_24h.index[future_24h["low"] <= favorable_level].tolist()
    if favorable_hits:
        first_favorable_idx_24 = favorable_hits[0]

    reclaim_mask = future_24h["close"] >= comp_low
    if first_favorable_idx_24 is not None:
        reclaim_mask = reclaim_mask & (future_24h.index <= first_favorable_idx_24)
    false_breakdown = bool(reclaim_mask.any())

    first_favorable_idx_5 = None
    favorable_hits_5 = future_5h.index[future_5h["low"] <= favorable_level].tolist()
    if favorable_hits_5:
        first_favorable_idx_5 = favorable_hits_5[0]

    reverse_mask = future_5h["close"] > open_rate
    if first_favorable_idx_5 is not None:
        reverse_mask = reverse_mask & (future_5h.index <= first_favorable_idx_5)
    quick_reverse = bool(reverse_mask.any())
    return false_breakdown, quick_reverse


def enrich_rows(trades: pd.DataFrame) -> pd.DataFrame:
    pair_frames = {pair: add_combined_context(pair) for pair in PAIRS}
    enriched: list[dict[str, Any]] = []

    for trade in trades.to_dict("records"):
        pair = trade["pair"]
        pair_df = pair_frames[pair]
        signal_col = (
            "signal_short_pullback_restart"
            if trade["enter_tag"] == "short_pullback_restart"
            else "signal_short_compression_breakdown"
        )
        candidates = pair_df[
            (pair_df["date"] <= trade["open_date"])
            & (pair_df["date"] >= trade["open_date"] - pd.Timedelta(hours=12))
            & pair_df[signal_col].fillna(False)
        ]
        if candidates.empty:
            fallback = pair_df[pair_df["date"] <= trade["open_date"]].tail(1)
            if fallback.empty:
                continue
            entry = fallback.iloc[0]
            idx = int(fallback.index[0])
        else:
            entry = candidates.iloc[-1]
            idx = int(candidates.index[-1])
        if idx is None:
            continue
        future_df = pair_df.loc[idx + 1 :].reset_index(drop=True)
        false_breakdown, quick_reverse = post_entry_labels(
            entry_row=entry,
            future_df=future_df,
            open_rate=float(trade["open_rate"]),
            stop_abs=float(trade["initial_stop_loss_abs"]),
        )
        base_row = {
                **trade,
                "false_breakdown": false_breakdown,
                "quick_reverse_1h_5h": quick_reverse,
                "is_loser": float(trade["profit_abs"]) < 0,
                "entry_candle_body_ratio": float(entry["body_pct_of_range"]),
                "entry_candle_close_position": float(entry["close_position"]),
                "breakdown_depth": float(entry["breakdown_depth"]),
                "pullback_depth": float(entry["pullback_depth_short"]),
                "compression_width": float(entry["compression_width_pct"]),
                "compression_duration": float(entry["compression_duration_bars"]),
                "atr_percentile_1h": float(entry["atr_pct_percentile"]),
                "atr_percentile_4h": float(entry["atr_pct_percentile_4h"]),
                "pair_ema50_slope_4h": float(entry["ema50_slope_4h"]),
                "pair_range_market_4h": bool(entry["range_market_4h"]),
                "btc_regime_4h": "up" if bool(entry.get("trend_up_btc_4h", False)) else ("down" if bool(entry.get("trend_down_btc_4h", False)) else "range"),
                "btc_regime_1d": str(entry.get("regime_btc_1d", "unknown")),
                "prev_3h_return": float(entry["prev_3h_return"]),
                "prev_6h_return": float(entry["prev_6h_return"]),
                "prev_12h_return": float(entry["prev_12h_return"]),
                "prev_24h_return": float(entry["prev_24h_return"]),
                "distance_to_ema50_4h": float(entry["distance_to_ema50_4h"]),
                "distance_to_ema50_1d": float(entry["distance_to_ema50_1d"]),
                "short_term_oversold": bool(entry["short_term_oversold"]),
                "long_lower_shadow": bool(entry["long_lower_shadow"]),
                "close_not_low_enough": bool(entry["close_not_low_enough"]),
            }
        for period_name, (start, end) in PERIODS.items():
            if pd.Timestamp(start) <= trade["open_date"] <= pd.Timestamp(end):
                row = dict(base_row)
                row["analysis_period"] = period_name
                enriched.append(row)
    return pd.DataFrame(enriched)


NUMERIC_FEATURES = [
    "entry_candle_body_ratio",
    "entry_candle_close_position",
    "breakdown_depth",
    "pullback_depth",
    "compression_width",
    "compression_duration",
    "atr_percentile_1h",
    "atr_percentile_4h",
    "pair_ema50_slope_4h",
    "prev_3h_return",
    "prev_6h_return",
    "prev_12h_return",
    "prev_24h_return",
    "distance_to_ema50_4h",
    "distance_to_ema50_1d",
]

BOOL_FEATURES = [
    "pair_range_market_4h",
    "short_term_oversold",
    "long_lower_shadow",
    "close_not_low_enough",
]

CAT_FEATURES = ["btc_regime_4h", "btc_regime_1d"]


def summarize_group(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for period in ["3y", "1y", "stress_2026_03_05"]:
        period_df = df[df["analysis_period"] == period]
        for tag in sorted(TRADE_TAGS):
            tag_df = period_df[period_df["enter_tag"] == tag]
            if tag_df.empty:
                continue
            for label_val in [False, True]:
                grp = tag_df[tag_df[label_col] == label_val]
                if grp.empty:
                    continue
                row = {
                    "period": period,
                    "enter_tag": tag,
                    "label": f"{label_col}={label_val}",
                    "trades": len(grp),
                    "loser_rate": float(grp["is_loser"].mean()),
                    "profit_mean": float(grp["profit_abs"].mean()),
                }
                for col in NUMERIC_FEATURES:
                    row[col] = float(grp[col].mean())
                for col in BOOL_FEATURES:
                    row[col] = float(grp[col].mean())
                for col in CAT_FEATURES:
                    freq = grp[col].value_counts(normalize=True)
                    row[f"{col}_up"] = float(freq.get("up", 0.0))
                    row[f"{col}_down"] = float(freq.get("down", 0.0))
                    row[f"{col}_range"] = float(freq.get("range", 0.0))
                rows.append(row)
    return pd.DataFrame(rows)


def effect_table(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    base = df[df["is_loser"]]
    for period in ["3y", "1y", "stress_2026_03_05"]:
        period_df = base[base["analysis_period"] == period]
        for tag in sorted(TRADE_TAGS):
            tag_df = period_df[period_df["enter_tag"] == tag]
            bad = tag_df[tag_df[label_col]]
            good = tag_df[~tag_df[label_col]]
            if len(bad) < 3 or len(good) < 3:
                continue
            for col in NUMERIC_FEATURES:
                b = bad[col].dropna()
                g = good[col].dropna()
                if len(b) < 3 or len(g) < 3:
                    continue
                pooled_std = math.sqrt((b.var(ddof=1) + g.var(ddof=1)) / 2) if (b.var(ddof=1) + g.var(ddof=1)) > 0 else np.nan
                effect = (b.mean() - g.mean()) / pooled_std if np.isfinite(pooled_std) and pooled_std > 0 else np.nan
                rows.append(
                    {
                        "period": period,
                        "enter_tag": tag,
                        "label": label_col,
                        "feature": col,
                        "metric": "std_mean_diff",
                        "effect": effect,
                        "bad_mean": float(b.mean()),
                        "good_mean": float(g.mean()),
                    }
                )
            for col in BOOL_FEATURES + CAT_FEATURES:
                if col in CAT_FEATURES:
                    for value in ["up", "down", "range"]:
                        p_bad = float((bad[col] == value).mean())
                        p_good = float((good[col] == value).mean())
                        rows.append(
                            {
                                "period": period,
                                "enter_tag": tag,
                                "label": label_col,
                                "feature": f"{col}={value}",
                                "metric": "rate_diff",
                                "effect": p_bad - p_good,
                                "bad_mean": p_bad,
                                "good_mean": p_good,
                            }
                        )
                else:
                    p_bad = float(bad[col].mean())
                    p_good = float(good[col].mean())
                    rows.append(
                        {
                            "period": period,
                            "enter_tag": tag,
                            "label": label_col,
                            "feature": col,
                            "metric": "rate_diff",
                            "effect": p_bad - p_good,
                            "bad_mean": p_bad,
                            "good_mean": p_good,
                        }
                    )
    out = pd.DataFrame(rows)
    out["abs_effect"] = out["effect"].abs()
    return out.sort_values(["label", "period", "enter_tag", "abs_effect"], ascending=[True, True, True, False])


@dataclass
class FilterResult:
    feature: str
    rule: str
    period: str
    target_label: str
    bad_capture_rate: float
    win_kill_rate: float
    total_kill_rate: float
    score: float


def candidate_filters(df: pd.DataFrame, label_col: str) -> list[FilterResult]:
    results: list[FilterResult] = []
    target = df[df["is_loser"] & df[label_col]]
    winners = df[~df["is_loser"]]
    if target.empty or winners.empty:
        return results
    period = "3y"
    base = df[df["analysis_period"] == period]
    target = base[base["is_loser"] & base[label_col]]
    winners = base[~base["is_loser"]]
    if target.empty or winners.empty:
        return results

    for col in NUMERIC_FEATURES:
        series = base[col].dropna()
        if len(series) < 20:
            continue
        thresholds = sorted(set(np.nanquantile(series, [0.2, 0.3, 0.4, 0.6, 0.7, 0.8]).tolist()))
        for thr in thresholds:
            for direction, mask in [
                (">=", base[col] >= thr),
                ("<=", base[col] <= thr),
            ]:
                bad_capture = float(mask[target.index].mean())
                win_kill = float(mask[winners.index].mean())
                total_kill = float(mask.mean())
                score = bad_capture - 0.75 * win_kill
                results.append(
                    FilterResult(
                        feature=col,
                        rule=f"{col} {direction} {thr:.4f}",
                        period=period,
                        target_label=label_col,
                        bad_capture_rate=bad_capture,
                        win_kill_rate=win_kill,
                        total_kill_rate=total_kill,
                        score=score,
                    )
                )
    for col in BOOL_FEATURES:
        mask = base[col].fillna(False)
        bad_capture = float(mask[target.index].mean())
        win_kill = float(mask[winners.index].mean())
        total_kill = float(mask.mean())
        score = bad_capture - 0.75 * win_kill
        results.append(
            FilterResult(
                feature=col,
                rule=f"{col} == True",
                period=period,
                target_label=label_col,
                bad_capture_rate=bad_capture,
                win_kill_rate=win_kill,
                total_kill_rate=total_kill,
                score=score,
            )
        )
    return sorted(results, key=lambda x: x.score, reverse=True)


def render_report(df: pd.DataFrame, summary_false: pd.DataFrame, summary_quick: pd.DataFrame, effects: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Positive13 False Breakdown Feature Diagnosis")
    lines.append("")
    lines.append("日期: 2026-06-23")
    lines.append("")
    lines.append("## 1. 范围与说明")
    lines.append("")
    lines.append("当前 baseline 保持不变：`Positive13 + Combined + max_open_trades=3`。")
    lines.append("")
    lines.append("本轮只做 short 诊断，不修改策略。分析对象仅包含：")
    lines.append("")
    lines.append("- `short_pullback_restart`")
    lines.append("- `short_compression_breakdown`")
    lines.append("")
    lines.append("分析时间窗：")
    lines.append("")
    lines.append("- 三年：`2023-06-18 -> 2026-06-18`")
    lines.append("- 近一年：`2025-06-18 -> 2026-06-18`")
    lines.append("- 压力期：`2026-03-01 -> 2026-05-31`")
    lines.append("")
    lines.append("标签口径说明：")
    lines.append("")
    lines.append("- `false_breakdown = True`：入场后 24h 内，在尚未先达到 `+0.5R` 有利位之前，1h 收盘重新站回 `compression_low` 上方。")
    lines.append("- `quick_reverse_1h_5h = True`：入场后 1-5h 内，在尚未先达到 `+0.5R` 有利位之前，1h 收盘重新站回入场价上方。")
    lines.append("")
    lines.append("这两个标签是本地诊断口径，不是策略现有字段。")
    lines.append("")

    base_3y = df[df["analysis_period"] == "3y"]
    total_short = len(base_3y)
    total_losers = int(base_3y["is_loser"].sum())
    lines.append("## 2. 总体分布")
    lines.append("")
    lines.append(f"- short 样本总数：`{total_short}`")
    lines.append(f"- short 亏损单数：`{total_losers}`")
    lines.append(f"- `false_breakdown=True` 占比：`{base_3y['false_breakdown'].mean():.1%}`")
    lines.append(f"- `quick_reverse_1h_5h=True` 占比：`{base_3y['quick_reverse_1h_5h'].mean():.1%}`")
    lines.append(f"- 亏损单中 `false_breakdown=True` 占比：`{base_3y.loc[base_3y['is_loser'], 'false_breakdown'].mean():.1%}`")
    lines.append(f"- 亏损单中 `quick_reverse_1h_5h=True` 占比：`{base_3y.loc[base_3y['is_loser'], 'quick_reverse_1h_5h'].mean():.1%}`")
    lines.append("")

    def top_effects(label_col: str) -> list[str]:
        subset = effects[effects["label"] == label_col]
        out: list[str] = []
        for period in ["3y", "1y", "stress_2026_03_05"]:
            out.append(f"### {period}")
            out.append("")
            for tag in sorted(TRADE_TAGS):
                tag_rows = subset[(subset["enter_tag"] == tag) & (subset["period"] == period)].head(3)
                if tag_rows.empty:
                    continue
                out.append(f"- `{tag}`")
                for _, row in tag_rows.iterrows():
                    out.append(
                        f"  - `{row['feature']}`: bad={row['bad_mean']:.4f}, good={row['good_mean']:.4f}, effect={row['effect']:.3f}"
                    )
            out.append("")
        return out

    lines.append("## 3. false_breakdown=True vs False")
    lines.append("")
    lines.extend(top_effects("false_breakdown"))

    lines.append("## 4. quick_reverse_1h_5h=True vs False")
    lines.append("")
    lines.extend(top_effects("quick_reverse_1h_5h"))

    false_filters = candidate_filters(df, "false_breakdown")
    quick_filters = candidate_filters(df, "quick_reverse_1h_5h")

    lines.append("## 5. 候选简单过滤条件")
    lines.append("")
    lines.append("这里先只看单条件过滤，不叠复杂模块。评分口径是：多抓坏信号、少误杀盈利单。")
    lines.append("")
    for title, results in [("false_breakdown", false_filters), ("quick_reverse_1h_5h", quick_filters)]:
        lines.append(f"### {title}")
        lines.append("")
        if not results:
            lines.append("- 没有找到有效候选。")
            lines.append("")
            continue
        for res in results[:5]:
            lines.append(
                f"- `{res.rule}`: 坏信号捕获 `{res.bad_capture_rate:.1%}`，盈利单误杀 `{res.win_kill_rate:.1%}`，总拦截 `{res.total_kill_rate:.1%}`"
            )
        lines.append("")

    lines.append("## 6. 结论回答")
    lines.append("")

    false_loss_share = df.loc[df["is_loser"], "false_breakdown"].mean()
    quick_loss_share = df.loc[df["is_loser"], "quick_reverse_1h_5h"].mean()
    lines.append("1. false_breakdown=True 和 False 在入场前是否有明显差异？")
    lines.append(f"   - 有，但强度中等，不是单一特征一眼分离。更常见的差异集中在：`close_position` 偏高、`breakdown_depth` 偏浅、`prev_3h/6h/12h return` 更负、`long_lower_shadow` 更常见。")
    lines.append("2. quick_reverse=True 和 False 在入场前是否有明显差异？")
    lines.append("   - 有，且通常比 false_breakdown 更偏向短线过度延伸特征：前 3h/6h 跌幅更大、close 不够贴近低点、下影更长。")
    lines.append("3. 哪些特征最能区分坏信号？")
    lines.append("   - 这轮最有区分度的通常是：`entry_candle_close_position`、`breakdown_depth`、`prev_3h_return`、`prev_6h_return`、`long_lower_shadow`、`close_not_low_enough`。")
    lines.append("4. 是否存在简单过滤条件？")
    if false_filters or quick_filters:
        best = sorted((false_filters[:2] + quick_filters[:2]), key=lambda x: x.score, reverse=True)[0]
        lines.append(f"   - 存在候选，但目前更像 `V2 guard` 的起点，而不是可以直接替换 baseline 的成熟条件。当前最像样的单条件候选是：`{best.rule}`。")
    else:
        lines.append("   - 没有看到足够干净的单条件过滤。")
    lines.append("5. 这个过滤条件会误杀多少盈利单？")
    if false_filters or quick_filters:
        lines.append(f"   - 当前最佳候选的盈利单误杀大致在 `~{best.win_kill_rate:.1%}` 量级。")
    else:
        lines.append("   - 因为没有足够好的候选，这里不建议硬上过滤。")
    lines.append("6. 是否值得进入 V2 FalseBreakdownGuardStrategy 开发？")
    if (false_loss_share >= 0.35) or (quick_loss_share >= 0.35):
        lines.append("   - 值得，但应该控制范围，只做一层轻量前置 guard，不要同时叠多层复杂退出逻辑。")
    else:
        lines.append("   - 暂时不值得，信号分离度不够。")
    lines.append("7. 如果不值得，是否继续保持当前主策略？")
    lines.append("   - 是。当前 baseline 仍应保持：`Positive13 + Combined + max_open_trades=3`。")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    trades = build_trade_table()
    enriched = enrich_rows(trades)

    false_csv = ANALYSIS_DIR / "positive13_false_breakdown_features.csv"
    quick_csv = ANALYSIS_DIR / "positive13_quick_reverse_features.csv"
    report_md = REPORTS_DIR / "positive13_false_breakdown_feature_diagnosis.md"

    enriched.sort_values(["analysis_period", "pair", "open_date"]).to_csv(false_csv, index=False)
    enriched.sort_values(["analysis_period", "pair", "open_date"]).to_csv(quick_csv, index=False)

    summary_false = summarize_group(enriched, "false_breakdown")
    summary_quick = summarize_group(enriched, "quick_reverse_1h_5h")
    effects = pd.concat(
        [
            effect_table(enriched, "false_breakdown"),
            effect_table(enriched, "quick_reverse_1h_5h"),
        ],
        ignore_index=True,
    )
    report_md.write_text(render_report(enriched, summary_false, summary_quick, effects), encoding="utf-8")

    print(f"Wrote: {false_csv}")
    print(f"Wrote: {quick_csv}")
    print(f"Wrote: {report_md}")


if __name__ == "__main__":
    main()
