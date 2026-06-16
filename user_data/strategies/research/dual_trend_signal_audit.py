from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_SYMBOLS = [
    "BTC",
    "ETH",
    "BNB",
    "SOL",
    "XRP",
    "DOGE",
    "ADA",
    "LINK",
    "NEAR",
    "SUI",
    "TRX",
    "ZEC",
    "TAO",
]

ENTRY_TAGS = [
    "long_compression_breakout",
    "long_pullback_restart",
    "short_compression_breakdown",
    "short_pullback_restart",
]


@dataclass(frozen=True)
class AuditParams:
    trend_ema_fast_4h: int = 50
    trend_ema_slow_4h: int = 200
    trend_slope_lookback_4h: int = 3
    atr_period_1h: int = 14
    volume_ma_window_1h: int = 20
    compression_window: int = 12
    compression_half_window: int = 6
    pretrend_window: int = 24
    compression_atr_multiplier: float = 3.0
    volume_breakout_multiplier: float = 1.2
    breakout_buffer: float = 0.001
    stop_atr_buffer: float = 0.2
    min_stop_distance: float = 0.005
    max_stop_distance: float = 0.05
    pullback_min_depth: float = 0.008
    pullback_max_depth: float = 0.08
    high_zone_buffer: float = 0.965
    low_zone_buffer: float = 1.035
    candle_body_min: float = 0.35
    long_close_position_min: float = 0.60
    short_close_position_max: float = 0.40


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit DualTrendCompressionRestartStrategy candidate signals from local "
            "Freqtrade futures feather data."
        )
    )
    parser.add_argument(
        "--data-dir",
        default="user_data/data/binance/futures",
        help="Directory containing *_USDT_USDT-1h-futures.feather and 4h files.",
    )
    parser.add_argument(
        "--output-dir",
        default="user_data/strategies/research/dual_trend_signal_audit_runs",
        help="Base output directory. A timestamped run folder will be created inside it.",
    )
    parser.add_argument(
        "--symbols",
        nargs="*",
        default=DEFAULT_SYMBOLS,
        help="Base symbols to audit, for example BTC ETH SOL.",
    )
    parser.add_argument(
        "--timerange",
        default=None,
        help="Optional UTC date range: YYYY-MM-DD:YYYY-MM-DD, YYYY-MM-DD:, or :YYYY-MM-DD.",
    )
    parser.add_argument(
        "--no-btc-filter",
        action="store_true",
        help="Disable BTC 4h market-direction filter for non-BTC symbols.",
    )
    parser.add_argument(
        "--chart-days",
        type=int,
        default=180,
        help="Number of latest days to include in each lightweight HTML signal chart.",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip lightweight HTML chart generation.",
    )
    return parser.parse_args()


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    for suffix in ("/USDT:USDT", "/USDT", "_USDT_USDT"):
        if symbol.endswith(suffix):
            symbol = symbol[: -len(suffix)]
    return symbol.replace("-", "_")


def parse_timerange(timerange: str | None) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    if not timerange:
        return None, None
    if ":" not in timerange:
        raise ValueError("--timerange must use START:END format")
    start_raw, end_raw = timerange.split(":", 1)
    start = pd.Timestamp(start_raw, tz="UTC") if start_raw else None
    end = pd.Timestamp(end_raw, tz="UTC") if end_raw else None
    return start, end


def read_ohlcv(data_dir: Path, symbol: str, timeframe: str) -> pd.DataFrame:
    path = data_dir / f"{symbol}_USDT_USDT-{timeframe}-futures.feather"
    if not path.exists():
        raise FileNotFoundError(path)
    dataframe = pd.read_feather(path)
    expected = {"date", "open", "high", "low", "close", "volume"}
    missing = expected.difference(dataframe.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    dataframe["date"] = pd.to_datetime(dataframe["date"], utc=True).astype("datetime64[ns, UTC]")
    dataframe = dataframe.sort_values("date").reset_index(drop=True)
    return dataframe


def apply_timerange(
    dataframe: pd.DataFrame,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> pd.DataFrame:
    if start is not None:
        dataframe = dataframe[dataframe["date"] >= start]
    if end is not None:
        dataframe = dataframe[dataframe["date"] <= end]
    return dataframe.reset_index(drop=True)


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def atr(dataframe: pd.DataFrame, period: int) -> pd.Series:
    prev_close = dataframe["close"].shift(1)
    true_range = pd.concat(
        [
            dataframe["high"] - dataframe["low"],
            (dataframe["high"] - prev_close).abs(),
            (dataframe["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def add_4h_indicators(dataframe: pd.DataFrame, params: AuditParams) -> pd.DataFrame:
    dataframe = dataframe.copy()
    dataframe["ema50_4h_src"] = ema(dataframe["close"], params.trend_ema_fast_4h)
    dataframe["ema200_4h_src"] = ema(dataframe["close"], params.trend_ema_slow_4h)
    dataframe["trend_up_4h_src"] = (
        (dataframe["close"] > dataframe["ema50_4h_src"])
        & (dataframe["ema50_4h_src"] > dataframe["ema200_4h_src"])
        & (
            dataframe["ema50_4h_src"]
            > dataframe["ema50_4h_src"].shift(params.trend_slope_lookback_4h)
        )
    )
    dataframe["trend_down_4h_src"] = (
        (dataframe["close"] < dataframe["ema50_4h_src"])
        & (dataframe["ema50_4h_src"] < dataframe["ema200_4h_src"])
        & (
            dataframe["ema50_4h_src"]
            < dataframe["ema50_4h_src"].shift(params.trend_slope_lookback_4h)
        )
    )
    return dataframe[
        [
            "date",
            "ema50_4h_src",
            "ema200_4h_src",
            "trend_up_4h_src",
            "trend_down_4h_src",
        ]
    ]


def merge_informative(
    base: pd.DataFrame,
    informative: pd.DataFrame,
    rename_map: dict[str, str],
) -> pd.DataFrame:
    right = informative.rename(columns=rename_map).sort_values("date")
    return pd.merge_asof(
        base.sort_values("date"),
        right,
        on="date",
        direction="backward",
    ).reset_index(drop=True)


def forward_rolling_max(series: pd.Series, window: int) -> pd.Series:
    return series.shift(-1).iloc[::-1].rolling(window, min_periods=1).max().iloc[::-1]


def forward_rolling_min(series: pd.Series, window: int) -> pd.Series:
    return series.shift(-1).iloc[::-1].rolling(window, min_periods=1).min().iloc[::-1]


def add_1h_indicators(dataframe: pd.DataFrame, params: AuditParams) -> pd.DataFrame:
    dataframe = dataframe.copy()
    cw = params.compression_window
    hw = params.compression_half_window
    pw = params.pretrend_window

    dataframe["atr_1h"] = atr(dataframe, params.atr_period_1h)
    dataframe["atr_ref"] = dataframe["atr_1h"].shift(1)
    dataframe["atr_pct"] = dataframe["atr_1h"] / dataframe["close"]
    dataframe["volume_ma20"] = dataframe["volume"].shift(1).rolling(params.volume_ma_window_1h).mean()
    dataframe["vol_ok"] = dataframe["volume"] > dataframe["volume_ma20"] * params.volume_breakout_multiplier

    dataframe["compression_high"] = dataframe["high"].shift(1).rolling(cw).max()
    dataframe["compression_low"] = dataframe["low"].shift(1).rolling(cw).min()
    dataframe["compression_width"] = dataframe["compression_high"] - dataframe["compression_low"]
    dataframe["compression_width_pct"] = dataframe["compression_width"] / dataframe["close"]
    dataframe["compression_ok"] = (
        dataframe["compression_width"] < dataframe["atr_ref"] * params.compression_atr_multiplier
    )

    dataframe["breakout_long"] = (
        dataframe["close"] > dataframe["compression_high"] * (1 + params.breakout_buffer)
    )
    dataframe["breakout_short"] = (
        dataframe["close"] < dataframe["compression_low"] * (1 - params.breakout_buffer)
    )

    dataframe["low_min_first_half"] = dataframe["low"].shift(hw + 1).rolling(hw).min()
    dataframe["low_min_last_half"] = dataframe["low"].shift(1).rolling(hw).min()
    dataframe["high_max_first_half"] = dataframe["high"].shift(hw + 1).rolling(hw).max()
    dataframe["high_max_last_half"] = dataframe["high"].shift(1).rolling(hw).max()
    dataframe["close_mean_first_half"] = dataframe["close"].shift(hw + 1).rolling(hw).mean()
    dataframe["close_mean_last_half"] = dataframe["close"].shift(1).rolling(hw).mean()
    dataframe["center_up"] = (
        (dataframe["low_min_last_half"] > dataframe["low_min_first_half"])
        & (dataframe["close_mean_last_half"] > dataframe["close_mean_first_half"])
    )
    dataframe["center_down"] = (
        (dataframe["high_max_last_half"] < dataframe["high_max_first_half"])
        & (dataframe["close_mean_last_half"] < dataframe["close_mean_first_half"])
    )

    dataframe["return_24h"] = dataframe["close"].shift(1) / dataframe["close"].shift(pw + 1) - 1
    dataframe["atr_pct_24h"] = dataframe["atr_pct"].shift(1).rolling(pw).mean()
    dataframe["pretrend_threshold"] = np.maximum(0.02, 1.5 * dataframe["atr_pct_24h"])
    dataframe["pretrend_up"] = dataframe["return_24h"] > dataframe["pretrend_threshold"]
    dataframe["pretrend_down"] = dataframe["return_24h"] < -dataframe["pretrend_threshold"]

    dataframe["recent_high_24"] = dataframe["high"].shift(1).rolling(pw).max()
    dataframe["recent_low_24"] = dataframe["low"].shift(1).rolling(pw).min()
    dataframe["pullback_low_12"] = dataframe["low"].shift(1).rolling(cw).min()
    dataframe["pullback_high_12"] = dataframe["high"].shift(1).rolling(cw).max()
    dataframe["pullback_depth_long"] = (
        dataframe["recent_high_24"] - dataframe["pullback_low_12"]
    ) / dataframe["recent_high_24"]
    dataframe["pullback_depth_short"] = (
        dataframe["pullback_high_12"] - dataframe["recent_low_24"]
    ) / dataframe["recent_low_24"]
    dataframe["pullback_seen_long"] = dataframe["pullback_depth_long"].between(
        params.pullback_min_depth,
        params.pullback_max_depth,
    )
    dataframe["pullback_seen_short"] = dataframe["pullback_depth_short"].between(
        params.pullback_min_depth,
        params.pullback_max_depth,
    )
    dataframe["pullback_intact_long"] = dataframe["pullback_low_12"] >= dataframe["ema50_4h"] * 0.99
    dataframe["pullback_intact_short"] = dataframe["pullback_high_12"] <= dataframe["ema50_4h"] * 1.01

    dataframe["near_high_zone"] = dataframe["compression_low"] >= dataframe["recent_high_24"] * params.high_zone_buffer
    dataframe["near_low_zone"] = dataframe["compression_high"] <= dataframe["recent_low_24"] * params.low_zone_buffer

    candle_range = dataframe["high"] - dataframe["low"]
    dataframe["body_pct_of_range"] = (dataframe["close"] - dataframe["open"]).abs() / candle_range.replace(0, np.nan)
    dataframe["close_position"] = (dataframe["close"] - dataframe["low"]) / candle_range.replace(0, np.nan)
    dataframe["candle_quality_long"] = (
        (candle_range > 0)
        & (dataframe["body_pct_of_range"] >= params.candle_body_min)
        & (dataframe["close_position"] >= params.long_close_position_min)
    )
    dataframe["candle_quality_short"] = (
        (candle_range > 0)
        & (dataframe["body_pct_of_range"] >= params.candle_body_min)
        & (dataframe["close_position"] <= params.short_close_position_max)
    )

    dataframe["long_compression_stop"] = dataframe["compression_low"] - params.stop_atr_buffer * dataframe["atr_ref"]
    dataframe["long_pullback_stop"] = dataframe["pullback_low_12"] - params.stop_atr_buffer * dataframe["atr_ref"]
    dataframe["short_compression_stop"] = dataframe["compression_high"] + params.stop_atr_buffer * dataframe["atr_ref"]
    dataframe["short_pullback_stop"] = dataframe["pullback_high_12"] + params.stop_atr_buffer * dataframe["atr_ref"]
    dataframe["long_compression_risk_pct"] = (dataframe["close"] - dataframe["long_compression_stop"]) / dataframe["close"]
    dataframe["long_pullback_risk_pct"] = (dataframe["close"] - dataframe["long_pullback_stop"]) / dataframe["close"]
    dataframe["short_compression_risk_pct"] = (dataframe["short_compression_stop"] - dataframe["close"]) / dataframe["close"]
    dataframe["short_pullback_risk_pct"] = (dataframe["short_pullback_stop"] - dataframe["close"]) / dataframe["close"]

    for column in [
        "long_compression_risk_pct",
        "long_pullback_risk_pct",
        "short_compression_risk_pct",
        "short_pullback_risk_pct",
    ]:
        dataframe[f"{column}_ok"] = dataframe[column].between(
            params.min_stop_distance,
            params.max_stop_distance,
        )

    dataframe["future_close_6h"] = dataframe["close"].shift(-6)
    dataframe["future_close_24h"] = dataframe["close"].shift(-24)
    dataframe["future_close_72h"] = dataframe["close"].shift(-72)
    dataframe["future_high_24h"] = forward_rolling_max(dataframe["high"], 24)
    dataframe["future_low_24h"] = forward_rolling_min(dataframe["low"], 24)
    return dataframe


def add_signals(dataframe: pd.DataFrame, params: AuditParams, use_btc_filter: bool) -> pd.DataFrame:
    dataframe = dataframe.copy()
    trend_up = dataframe["trend_up_4h"].fillna(False)
    trend_down = dataframe["trend_down_4h"].fillna(False)
    btc_long_ok = dataframe["btc_filter_long_ok"].fillna(True) if use_btc_filter else True
    btc_short_ok = dataframe["btc_filter_short_ok"].fillna(True) if use_btc_filter else True

    dataframe["long_compression_breakout"] = (
        trend_up
        & dataframe["pretrend_up"]
        & dataframe["compression_ok"]
        & dataframe["center_up"]
        & dataframe["breakout_long"]
        & dataframe["vol_ok"]
        & dataframe["near_high_zone"]
        & dataframe["candle_quality_long"]
        & dataframe["long_compression_risk_pct_ok"]
        & btc_long_ok
    )
    dataframe["long_pullback_restart"] = (
        trend_up
        & dataframe["pullback_seen_long"]
        & dataframe["pullback_intact_long"]
        & dataframe["compression_ok"]
        & dataframe["center_up"]
        & dataframe["breakout_long"]
        & dataframe["vol_ok"]
        & dataframe["candle_quality_long"]
        & dataframe["long_pullback_risk_pct_ok"]
        & btc_long_ok
    )
    dataframe["short_compression_breakdown"] = (
        trend_down
        & dataframe["pretrend_down"]
        & dataframe["compression_ok"]
        & dataframe["center_down"]
        & dataframe["breakout_short"]
        & dataframe["vol_ok"]
        & dataframe["near_low_zone"]
        & dataframe["candle_quality_short"]
        & dataframe["short_compression_risk_pct_ok"]
        & btc_short_ok
    )
    dataframe["short_pullback_restart"] = (
        trend_down
        & dataframe["pullback_seen_short"]
        & dataframe["pullback_intact_short"]
        & dataframe["compression_ok"]
        & dataframe["center_down"]
        & dataframe["breakout_short"]
        & dataframe["vol_ok"]
        & dataframe["candle_quality_short"]
        & dataframe["short_pullback_risk_pct_ok"]
        & btc_short_ok
    )
    return dataframe


def evaluate_r_path(
    dataframe: pd.DataFrame,
    signal_index: int,
    side: str,
    entry: float,
    stop: float,
    horizon: int,
) -> dict[str, float | int | str | bool]:
    risk = entry - stop if side == "long" else stop - entry
    result: dict[str, float | int | str | bool] = {
        f"first_event_{horizon}h": "invalid",
        f"bars_to_first_event_{horizon}h": np.nan,
        f"hit_tp1_before_stop_{horizon}h": False,
        f"hit_tp2_before_stop_{horizon}h": False,
        f"hit_stop_before_tp1_{horizon}h": False,
        f"max_r_{horizon}h": np.nan,
        f"min_r_{horizon}h": np.nan,
    }
    if not np.isfinite(risk) or risk <= 0:
        return result

    future = dataframe.iloc[signal_index + 1 : signal_index + 1 + horizon]
    if future.empty:
        result[f"first_event_{horizon}h"] = "no_data"
        return result

    tp1 = entry + risk if side == "long" else entry - risk
    tp2 = entry + 2 * risk if side == "long" else entry - 2 * risk
    if side == "long":
        result[f"max_r_{horizon}h"] = (future["high"].max() - entry) / risk
        result[f"min_r_{horizon}h"] = (future["low"].min() - entry) / risk
    else:
        result[f"max_r_{horizon}h"] = (entry - future["low"].min()) / risk
        result[f"min_r_{horizon}h"] = (entry - future["high"].max()) / risk

    first_event = "none"
    bars_to_first = np.nan
    tp1_seen_before_stop = False
    stop_seen_before_tp1 = False
    tp2_seen_before_stop = False
    for offset, (_, candle) in enumerate(future.iterrows(), start=1):
        if side == "long":
            stop_hit = candle["low"] <= stop
            tp1_hit = candle["high"] >= tp1
            tp2_hit = candle["high"] >= tp2
        else:
            stop_hit = candle["high"] >= stop
            tp1_hit = candle["low"] <= tp1
            tp2_hit = candle["low"] <= tp2

        if first_event == "none":
            if stop_hit and tp1_hit:
                first_event = "ambiguous"
                bars_to_first = offset
            elif stop_hit:
                first_event = "stop"
                bars_to_first = offset
                stop_seen_before_tp1 = True
            elif tp1_hit:
                first_event = "tp1"
                bars_to_first = offset
                tp1_seen_before_stop = True

        if not stop_seen_before_tp1 and tp1_hit:
            tp1_seen_before_stop = True
        if not stop_seen_before_tp1 and tp2_hit:
            tp2_seen_before_stop = True
        if stop_hit and not tp1_seen_before_stop:
            stop_seen_before_tp1 = True

    result[f"first_event_{horizon}h"] = first_event
    result[f"bars_to_first_event_{horizon}h"] = bars_to_first
    result[f"hit_tp1_before_stop_{horizon}h"] = tp1_seen_before_stop
    result[f"hit_tp2_before_stop_{horizon}h"] = tp2_seen_before_stop
    result[f"hit_stop_before_tp1_{horizon}h"] = stop_seen_before_tp1
    return result


def signal_rows(symbol: str, dataframe: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    stop_map = {
        "long_compression_breakout": ("long", "long_compression_stop", "long_compression_risk_pct"),
        "long_pullback_restart": ("long", "long_pullback_stop", "long_pullback_risk_pct"),
        "short_compression_breakdown": ("short", "short_compression_stop", "short_compression_risk_pct"),
        "short_pullback_restart": ("short", "short_pullback_stop", "short_pullback_risk_pct"),
    }
    for tag, (side, stop_col, risk_col) in stop_map.items():
        hits = dataframe[dataframe[tag].fillna(False)]
        for signal_index, candle in hits.iterrows():
            close = float(candle["close"])
            stop = float(candle[stop_col])
            path_24h = evaluate_r_path(dataframe, signal_index, side, close, stop, 24)
            path_72h = evaluate_r_path(dataframe, signal_index, side, close, stop, 72)
            if side == "long":
                ret_6h = candle["future_close_6h"] / close - 1
                ret_24h = candle["future_close_24h"] / close - 1
                ret_72h = candle["future_close_72h"] / close - 1
                mfe_24h = candle["future_high_24h"] / close - 1
                mae_24h = candle["future_low_24h"] / close - 1
            else:
                ret_6h = close / candle["future_close_6h"] - 1
                ret_24h = close / candle["future_close_24h"] - 1
                ret_72h = close / candle["future_close_72h"] - 1
                mfe_24h = close / candle["future_low_24h"] - 1
                mae_24h = close / candle["future_high_24h"] - 1
            rows.append(
                {
                    "symbol": symbol,
                    "pair": f"{symbol}/USDT:USDT",
                    "date": candle["date"],
                    "entry_tag": tag,
                    "side": side,
                    "close": close,
                    "initial_stop": stop,
                    "risk_pct": candle[risk_col],
                    "trend_up_4h": bool(candle.get("trend_up_4h", False)),
                    "trend_down_4h": bool(candle.get("trend_down_4h", False)),
                    "compression_width_pct": candle["compression_width_pct"],
                    "volume_ratio": candle["volume"] / candle["volume_ma20"] if candle["volume_ma20"] else np.nan,
                    "body_pct_of_range": candle["body_pct_of_range"],
                    "close_position": candle["close_position"],
                    "forward_ret_6h": ret_6h,
                    "forward_ret_24h": ret_24h,
                    "forward_ret_72h": ret_72h,
                    "mfe_24h": mfe_24h,
                    "mae_24h": mae_24h,
                    **path_24h,
                    **path_72h,
                }
            )
    return rows


def summarize_signals(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "entry_tag",
                "side",
                "signals",
                "first_signal",
                "last_signal",
                "avg_risk_pct",
                "median_risk_pct",
                "avg_forward_ret_24h",
                "median_forward_ret_24h",
                "avg_mfe_24h",
                "avg_mae_24h",
                "tp1_before_stop_72h_rate",
                "tp2_before_stop_72h_rate",
                "stop_before_tp1_72h_rate",
                "avg_max_r_72h",
                "avg_min_r_72h",
            ]
        )
    grouped = signals.groupby(["symbol", "entry_tag", "side"], dropna=False)
    summary = grouped.agg(
        signals=("date", "count"),
        first_signal=("date", "min"),
        last_signal=("date", "max"),
        avg_risk_pct=("risk_pct", "mean"),
        median_risk_pct=("risk_pct", "median"),
        avg_forward_ret_6h=("forward_ret_6h", "mean"),
        avg_forward_ret_24h=("forward_ret_24h", "mean"),
        median_forward_ret_24h=("forward_ret_24h", "median"),
        avg_forward_ret_72h=("forward_ret_72h", "mean"),
        avg_mfe_24h=("mfe_24h", "mean"),
        avg_mae_24h=("mae_24h", "mean"),
        tp1_before_stop_24h_rate=("hit_tp1_before_stop_24h", "mean"),
        tp2_before_stop_24h_rate=("hit_tp2_before_stop_24h", "mean"),
        stop_before_tp1_24h_rate=("hit_stop_before_tp1_24h", "mean"),
        avg_max_r_24h=("max_r_24h", "mean"),
        avg_min_r_24h=("min_r_24h", "mean"),
        tp1_before_stop_72h_rate=("hit_tp1_before_stop_72h", "mean"),
        tp2_before_stop_72h_rate=("hit_tp2_before_stop_72h", "mean"),
        stop_before_tp1_72h_rate=("hit_stop_before_tp1_72h", "mean"),
        avg_max_r_72h=("max_r_72h", "mean"),
        avg_min_r_72h=("min_r_72h", "mean"),
    ).reset_index()
    return summary.sort_values(["signals", "symbol", "entry_tag"], ascending=[False, True, True])


def summarize_by_group(signals: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame()
    grouped = signals.groupby(group_cols, dropna=False)
    return grouped.agg(
        signals=("date", "count"),
        avg_risk_pct=("risk_pct", "mean"),
        avg_forward_ret_24h=("forward_ret_24h", "mean"),
        median_forward_ret_24h=("forward_ret_24h", "median"),
        avg_forward_ret_72h=("forward_ret_72h", "mean"),
        tp1_before_stop_24h_rate=("hit_tp1_before_stop_24h", "mean"),
        tp2_before_stop_24h_rate=("hit_tp2_before_stop_24h", "mean"),
        stop_before_tp1_24h_rate=("hit_stop_before_tp1_24h", "mean"),
        avg_max_r_24h=("max_r_24h", "mean"),
        avg_min_r_24h=("min_r_24h", "mean"),
        tp1_before_stop_72h_rate=("hit_tp1_before_stop_72h", "mean"),
        tp2_before_stop_72h_rate=("hit_tp2_before_stop_72h", "mean"),
        stop_before_tp1_72h_rate=("hit_stop_before_tp1_72h", "mean"),
        avg_max_r_72h=("max_r_72h", "mean"),
        avg_min_r_72h=("min_r_72h", "mean"),
    ).reset_index()


def summarize_pairs(audited: dict[str, pd.DataFrame], signals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    signal_counts = signals.groupby("symbol").size().to_dict() if not signals.empty else {}
    for symbol, dataframe in audited.items():
        rows.append(
            {
                "symbol": symbol,
                "rows_1h": len(dataframe),
                "start": dataframe["date"].min(),
                "end": dataframe["date"].max(),
                "trend_up_4h_hours": int(dataframe["trend_up_4h"].fillna(False).sum()),
                "trend_down_4h_hours": int(dataframe["trend_down_4h"].fillna(False).sum()),
                "compression_ok_hours": int(dataframe["compression_ok"].fillna(False).sum()),
                "vol_ok_hours": int(dataframe["vol_ok"].fillna(False).sum()),
                "signal_count": int(signal_counts.get(symbol, 0)),
            }
        )
    return pd.DataFrame(rows).sort_values(["signal_count", "symbol"], ascending=[False, True])


def write_csv(dataframe: pd.DataFrame, path: Path) -> None:
    dataframe.to_csv(path, index=False, encoding="utf-8-sig")


def percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{value:.2%}"


def number(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, (int, np.integer)):
        return str(value)
    return f"{value:.2f}"


def markdown_table(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return ""
    as_text = dataframe.copy()
    for column in as_text.columns:
        as_text[column] = as_text[column].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(as_text.columns)
    rows = as_text.values.tolist()
    widths = [
        max(len(header), *(len(row[idx]) for row in rows))
        for idx, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(
        header.ljust(widths[idx]) for idx, header in enumerate(headers)
    ) + " |"
    sep_line = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body])


def write_markdown_report(
    path: Path,
    pair_summary: pd.DataFrame,
    tag_summary: pd.DataFrame,
    global_tag_summary: pd.DataFrame,
    yearly_tag_summary: pd.DataFrame,
    signals: pd.DataFrame,
    args: argparse.Namespace,
    params: AuditParams,
    missing: list[str],
) -> None:
    lines = [
        "# 双周期顺势压缩再启动策略信号审计报告",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"- 数据目录：`{args.data_dir}`",
        f"- BTC 过滤：{'关闭' if args.no_btc_filter else '开启'}",
        f"- timerange：`{args.timerange or '全部本地数据'}`",
        f"- 交易对：`{', '.join(args.symbols)}`",
        "",
        "## 参数快照",
        "",
        "```text",
        *[f"{key} = {value}" for key, value in params.__dict__.items()],
        "```",
        "",
    ]
    if missing:
        lines.extend(
            [
                "## 缺失数据",
                "",
                *[f"- {item}" for item in missing],
                "",
            ]
        )

    lines.extend(["## Pair 概览", ""])
    if pair_summary.empty:
        lines.append("没有可审计的交易对。")
    else:
        lines.append(markdown_table(pair_summary))
    lines.append("")

    lines.extend(["## 全局 Entry Tag 概览", ""])
    if global_tag_summary.empty:
        lines.append("没有触发任何信号。")
    else:
        table = global_tag_summary.copy()
        for col in [
            "avg_risk_pct",
            "avg_forward_ret_24h",
            "median_forward_ret_24h",
            "avg_forward_ret_72h",
            "tp1_before_stop_24h_rate",
            "tp2_before_stop_24h_rate",
            "stop_before_tp1_24h_rate",
            "tp1_before_stop_72h_rate",
            "tp2_before_stop_72h_rate",
            "stop_before_tp1_72h_rate",
        ]:
            table[col] = table[col].map(percent)
        for col in ["avg_max_r_24h", "avg_min_r_24h", "avg_max_r_72h", "avg_min_r_72h"]:
            table[col] = table[col].map(number)
        lines.append(markdown_table(table))
    lines.append("")

    lines.extend(["## Entry Tag 概览", ""])
    if tag_summary.empty:
        lines.append("没有触发任何信号。")
    else:
        table = tag_summary.copy()
        for col in [
            "avg_risk_pct",
            "median_risk_pct",
            "avg_forward_ret_6h",
            "avg_forward_ret_24h",
            "median_forward_ret_24h",
            "avg_forward_ret_72h",
            "avg_mfe_24h",
            "avg_mae_24h",
            "tp1_before_stop_24h_rate",
            "tp2_before_stop_24h_rate",
            "stop_before_tp1_24h_rate",
            "tp1_before_stop_72h_rate",
            "tp2_before_stop_72h_rate",
            "stop_before_tp1_72h_rate",
        ]:
            table[col] = table[col].map(percent)
        for col in ["avg_max_r_24h", "avg_min_r_24h", "avg_max_r_72h", "avg_min_r_72h"]:
            table[col] = table[col].map(number)
        lines.append(markdown_table(table))
    lines.append("")

    lines.extend(["## 年度 Entry Tag 概览", ""])
    if yearly_tag_summary.empty:
        lines.append("没有年度汇总。")
    else:
        table = yearly_tag_summary.copy()
        for col in [
            "avg_risk_pct",
            "avg_forward_ret_24h",
            "median_forward_ret_24h",
            "avg_forward_ret_72h",
            "tp1_before_stop_24h_rate",
            "tp2_before_stop_24h_rate",
            "stop_before_tp1_24h_rate",
            "tp1_before_stop_72h_rate",
            "tp2_before_stop_72h_rate",
            "stop_before_tp1_72h_rate",
        ]:
            table[col] = table[col].map(percent)
        for col in ["avg_max_r_24h", "avg_min_r_24h", "avg_max_r_72h", "avg_min_r_72h"]:
            table[col] = table[col].map(number)
        lines.append(markdown_table(table.head(80)))
    lines.append("")

    lines.extend(["## 最近信号样本", ""])
    if signals.empty:
        lines.append("没有样本。")
    else:
        sample = signals.sort_values("date", ascending=False).head(30).copy()
        for col in [
            "risk_pct",
            "compression_width_pct",
            "forward_ret_6h",
            "forward_ret_24h",
            "forward_ret_72h",
            "mfe_24h",
            "mae_24h",
        ]:
            sample[col] = sample[col].map(percent)
        lines.append(
            markdown_table(sample[
                [
                    "date",
                    "symbol",
                    "entry_tag",
                    "side",
                    "close",
                    "risk_pct",
                    "forward_ret_24h",
                    "mfe_24h",
                    "mae_24h",
                ]
            ])
        )
    lines.append("")

    lines.extend(
        [
            "## 解读提醒",
            "",
            "- 这是信号审计，不是完整交易回测。",
            "- forward_ret / MFE / MAE 用未来价格做事后观察，只用于判断信号形态是否值得继续实现。",
            "- 后续正式策略仍必须单独实现仓位、止损、分批止盈、protections 和完整回测。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def html_chart(symbol: str, dataframe: pd.DataFrame, signals: pd.DataFrame, chart_days: int) -> str:
    if dataframe.empty:
        return "<p>No data.</p>"
    end = dataframe["date"].max()
    start = end - pd.Timedelta(days=chart_days)
    data = dataframe[dataframe["date"] >= start].copy().reset_index(drop=True)
    signal_data = signals[(signals["symbol"] == symbol) & (signals["date"] >= start)].copy()
    if data.empty:
        return "<p>No data in chart window.</p>"

    width = 1200
    height = 420
    pad = 36
    closes = data["close"].astype(float)
    ymin = float(closes.min())
    ymax = float(closes.max())
    if ymax <= ymin:
        ymax = ymin + 1.0

    def x_at(idx: int) -> float:
        if len(data) <= 1:
            return pad
        return pad + idx * (width - 2 * pad) / (len(data) - 1)

    def y_at(price: float) -> float:
        return height - pad - (price - ymin) * (height - 2 * pad) / (ymax - ymin)

    max_points = 900
    step = max(1, len(data) // max_points)
    points = " ".join(
        f"{x_at(i):.1f},{y_at(float(data.loc[i, 'close'])):.1f}"
        for i in range(0, len(data), step)
    )
    marker_lines = []
    date_to_idx = {value: idx for idx, value in enumerate(data["date"])}
    tag_colors = {
        "long_compression_breakout": "#0f9d58",
        "long_pullback_restart": "#40a852",
        "short_compression_breakdown": "#d93025",
        "short_pullback_restart": "#e67c73",
    }
    for _, row in signal_data.iterrows():
        idx = date_to_idx.get(row["date"])
        if idx is None:
            continue
        color = tag_colors.get(row["entry_tag"], "#444")
        x = x_at(idx)
        y = y_at(float(row["close"]))
        marker = "▲" if row["side"] == "long" else "▼"
        marker_lines.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="16" '
            f'text-anchor="middle">{marker}</text>'
        )

    counts = signal_data.groupby("entry_tag").size().to_dict() if not signal_data.empty else {}
    count_items = "".join(
        f"<li>{html.escape(tag)}: {counts.get(tag, 0)}</li>"
        for tag in ENTRY_TAGS
    )
    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(symbol)} signal audit</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    svg {{ border: 1px solid #ddd; background: #fff; max-width: 100%; height: auto; }}
    .meta {{ color: #555; }}
  </style>
</head>
<body>
  <h1>{html.escape(symbol)}/USDT:USDT 信号审计</h1>
  <p class="meta">窗口：最近 {chart_days} 天，本图仅显示 close 线和 entry_tag 标记。</p>
  <svg viewBox="0 0 {width} {height}" role="img">
    <line x1="{pad}" y1="{height - pad}" x2="{width - pad}" y2="{height - pad}" stroke="#ddd" />
    <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height - pad}" stroke="#ddd" />
    <polyline fill="none" stroke="#1f77b4" stroke-width="1.5" points="{points}" />
    {''.join(marker_lines)}
    <text x="{pad}" y="22" font-size="12" fill="#555">{ymax:.6g}</text>
    <text x="{pad}" y="{height - 8}" font-size="12" fill="#555">{ymin:.6g}</text>
  </svg>
  <h2>窗口内信号数</h2>
  <ul>{count_items}</ul>
</body>
</html>
"""


def write_html_index(output_dir: Path, chart_paths: Iterable[Path]) -> None:
    links = "\n".join(
        f'<li><a href="{html.escape(path.name)}">{html.escape(path.stem)}</a></li>'
        for path in chart_paths
    )
    content = f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Signal audit charts</title></head>
<body>
<h1>Signal audit charts</h1>
<ul>
{links}
</ul>
</body>
</html>
"""
    (output_dir / "charts_index.html").write_text(content, encoding="utf-8")


def audit_symbol(
    symbol: str,
    data_dir: Path,
    params: AuditParams,
    btc_4h: pd.DataFrame,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
    use_btc_filter: bool,
) -> pd.DataFrame:
    one_hour = read_ohlcv(data_dir, symbol, "1h")
    four_hour = read_ohlcv(data_dir, symbol, "4h")
    one_hour = apply_timerange(one_hour, start, end)
    four_hour_ind = add_4h_indicators(four_hour, params)
    dataframe = merge_informative(
        one_hour,
        four_hour_ind,
        {
            "ema50_4h_src": "ema50_4h",
            "ema200_4h_src": "ema200_4h",
            "trend_up_4h_src": "trend_up_4h",
            "trend_down_4h_src": "trend_down_4h",
        },
    )
    btc_ind = btc_4h.rename(
        columns={
            "trend_up_4h_src": "btc_trend_up_4h",
            "trend_down_4h_src": "btc_trend_down_4h",
        }
    )[["date", "btc_trend_up_4h", "btc_trend_down_4h"]]
    dataframe = merge_informative(dataframe, btc_ind, {})
    dataframe["btc_filter_long_ok"] = True
    dataframe["btc_filter_short_ok"] = True
    if use_btc_filter and symbol != "BTC":
        dataframe["btc_filter_long_ok"] = ~dataframe["btc_trend_down_4h"].fillna(False)
        dataframe["btc_filter_short_ok"] = ~dataframe["btc_trend_up_4h"].fillna(False)

    dataframe = add_1h_indicators(dataframe, params)
    dataframe = add_signals(dataframe, params, use_btc_filter)
    return dataframe


def main() -> int:
    args = parse_args()
    params = AuditParams()
    data_dir = Path(args.data_dir)
    output_base = Path(args.output_dir)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_base / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    start, end = parse_timerange(args.timerange)
    symbols = [normalize_symbol(symbol) for symbol in args.symbols]

    missing: list[str] = []
    audited: dict[str, pd.DataFrame] = {}
    signal_records: list[dict] = []

    btc_4h = add_4h_indicators(read_ohlcv(data_dir, "BTC", "4h"), params)

    for symbol in symbols:
        try:
            dataframe = audit_symbol(
                symbol,
                data_dir,
                params,
                btc_4h,
                start,
                end,
                use_btc_filter=not args.no_btc_filter,
            )
        except FileNotFoundError as exc:
            missing.append(str(exc))
            continue
        audited[symbol] = dataframe
        signal_records.extend(signal_rows(symbol, dataframe))

    signals = pd.DataFrame(signal_records)
    if not signals.empty:
        signals = signals.sort_values(["date", "symbol", "entry_tag"]).reset_index(drop=True)
        signals["year"] = pd.to_datetime(signals["date"], utc=True).dt.year
        signals["month"] = pd.to_datetime(signals["date"], utc=True).dt.strftime("%Y-%m")
    tag_summary = summarize_signals(signals)
    global_tag_summary = summarize_by_group(signals, ["entry_tag", "side"]).sort_values(
        ["signals", "entry_tag"],
        ascending=[False, True],
    ) if not signals.empty else pd.DataFrame()
    yearly_tag_summary = summarize_by_group(signals, ["year", "entry_tag", "side"]).sort_values(
        ["year", "signals"],
        ascending=[True, False],
    ) if not signals.empty else pd.DataFrame()
    monthly_tag_summary = summarize_by_group(signals, ["month", "entry_tag", "side"]).sort_values(
        ["month", "signals"],
        ascending=[True, False],
    ) if not signals.empty else pd.DataFrame()
    side_summary = summarize_by_group(signals, ["side"]).sort_values(
        ["signals"],
        ascending=[False],
    ) if not signals.empty else pd.DataFrame()
    pair_summary = summarize_pairs(audited, signals)

    write_csv(pair_summary, output_dir / "summary_by_pair.csv")
    write_csv(tag_summary, output_dir / "summary_by_pair_tag.csv")
    write_csv(global_tag_summary, output_dir / "summary_by_tag.csv")
    write_csv(yearly_tag_summary, output_dir / "summary_by_year_tag.csv")
    write_csv(monthly_tag_summary, output_dir / "summary_by_month_tag.csv")
    write_csv(side_summary, output_dir / "summary_by_side.csv")
    write_csv(signals, output_dir / "signals.csv")
    write_markdown_report(
        output_dir / "report.md",
        pair_summary,
        tag_summary,
        global_tag_summary,
        yearly_tag_summary,
        signals,
        args,
        params,
        missing,
    )

    chart_paths: list[Path] = []
    if not args.no_html:
        for symbol, dataframe in audited.items():
            path = output_dir / f"chart_{symbol}.html"
            path.write_text(
                html_chart(symbol, dataframe, signals, args.chart_days),
                encoding="utf-8",
            )
            chart_paths.append(path)
        write_html_index(output_dir, chart_paths)

    print(f"output_dir={output_dir.resolve()}")
    print(f"pairs_audited={len(audited)}")
    print(f"signals={len(signals)}")
    if missing:
        print("missing_files=")
        for item in missing:
            print(item)
    if not tag_summary.empty:
        print(tag_summary.head(20).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
