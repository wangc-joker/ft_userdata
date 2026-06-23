from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
DEFAULT_CONFIG = USER_DATA / "config.dryrun.dualtrend.combined.top50.positive13.max3.json"
DEFAULT_STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
DEFAULT_STOPLOSS = -0.06
BASELINE_QR = 0.73
BASELINE_FB = 0.673

ENRICHED_COLUMNS = [
    "trade_id", "pair", "side", "is_short", "entry_tag", "open_date", "close_date",
    "is_open", "open_rate", "close_rate", "current_rate", "current_profit_ratio",
    "stake_amount", "amount", "leverage", "profit_abs", "profit_ratio", "fee_open",
    "fee_close", "funding_fees", "exit_reason", "trade_duration_hours", "stop_price",
    "risk_abs", "risk_source", "mae_pct", "mfe_pct", "max_favorable_price",
    "max_adverse_price", "quick_reverse_1h", "quick_reverse_2h", "quick_reverse_3h",
    "quick_reverse_4h", "quick_reverse_5h", "quick_reverse_1h_5h", "false_breakdown",
    "false_breakdown_12h_low", "false_breakdown_24h_low", "false_breakout",
    "false_breakout_12h_high", "false_breakout_24h_high", "compression_boundary_source",
    "range_market", "btc_4h_regime", "btc_1d_regime", "pair_4h_regime",
    "atr_percentile_1h", "atr_percentile_4h", "pair_ema50_slope_4h",
    "distance_to_ema50_4h", "distance_to_ema50_1d", "signal_price",
    "signal_price_source", "estimated_slippage_pct", "slippage_level", "actual_fee_pct",
    "funding_fee_pct", "funding_fee_to_profit_abs", "cost_total_pct",
    "concurrent_trades_at_entry", "max_concurrent_trades_during_trade", "was_slot_full",
    "data_warnings",
]


@dataclass
class Context:
    config: dict[str, Any]
    config_path: Path
    output_dir: Path
    warnings: list[str] = field(default_factory=list)
    ohlcv_cache: dict[tuple[str, str], pd.DataFrame | None] = field(default_factory=dict)

    @property
    def strategy(self) -> str:
        return str(self.config.get("strategy", DEFAULT_STRATEGY))

    @property
    def max_open_trades(self) -> int:
        return int(self.config.get("max_open_trades", 3))

    @property
    def pairs(self) -> list[str]:
        return list(self.config.get("exchange", {}).get("pair_whitelist", []))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Positive13 dry-run monitoring reports")
    parser.add_argument("--mode", choices=("daily", "weekly", "full"), required=True)
    parser.add_argument("--date", help="Daily report date (YYYY-MM-DD)")
    parser.add_argument("--start-date", help="Optional inclusive start date")
    parser.add_argument("--end-date", help="Weekly/full inclusive end date")
    parser.add_argument("--db-path", help="Explicit Freqtrade dry-run SQLite database")
    parser.add_argument("--trade-export", help="Fallback Freqtrade trade export (.csv or .json)")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Freqtrade config path")
    parser.add_argument("--output-dir", default=str(REPORTS_DIR), help="Markdown report directory")
    return parser.parse_args()


def utc_timestamp(value: Any) -> pd.Timestamp | pd.NaT:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return pd.NaT
    return pd.to_datetime(value, utc=True, errors="coerce")


def day_start(value: str | None, fallback: date) -> pd.Timestamp:
    target = date.fromisoformat(value) if value else fallback
    return pd.Timestamp(datetime.combine(target, datetime.min.time()), tz="UTC")


def safe_float(value: Any, default: float = np.nan) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def json_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sqlite_from_url(db_url: str) -> Path | None:
    if not db_url.startswith("sqlite:///"):
        return None
    raw = db_url.removeprefix("sqlite:///")
    if raw.startswith("/freqtrade/user_data/"):
        return USER_DATA / Path(raw).name
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else ROOT / candidate


def discover_database(ctx: Context, explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Dry-run database not found: {path}")
        return path
    config_db = ctx.config.get("db_url")
    if config_db:
        path = sqlite_from_url(str(config_db))
        if path and path.exists():
            return path
        ctx.warnings.append(f"Config db_url does not resolve to an existing SQLite file: {config_db}")
    tokens = {"positive13", "dualtrend"}
    candidates = [p for p in USER_DATA.glob("*.sqlite") if any(t in p.name.lower() for t in tokens)]
    if candidates:
        return max(candidates, key=lambda p: p.stat().st_mtime)
    standard = [USER_DATA / name for name in ("tradesv3.dryrun.sqlite", "tradesv3.sqlite", "dryrun.sqlite")]
    found = [p for p in standard if p.exists()]
    if found:
        return max(found, key=lambda p: p.stat().st_mtime)
    ctx.warnings.append(
        "No Positive13 dry-run database found. Old NFI databases were intentionally ignored; use --db-path when the bot database exists."
    )
    return None


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()}


def read_trades(source_path: Path | None, ctx: Context) -> pd.DataFrame:
    if source_path is None:
        return pd.DataFrame()
    if source_path.suffix.lower() == ".csv":
        try:
            return pd.read_csv(source_path)
        except Exception as exc:
            raise RuntimeError(f"Unable to read trade export {source_path}: {exc}") from exc
    if source_path.suffix.lower() == ".json":
        try:
            payload = json.loads(source_path.read_text(encoding="utf-8-sig"))
            if isinstance(payload, dict):
                payload = payload.get("trades", payload.get("data", payload.get("results", [])))
            if not isinstance(payload, list):
                raise ValueError("JSON must be a trade list or contain trades/data/results")
            return pd.DataFrame(payload)
        except Exception as exc:
            raise RuntimeError(f"Unable to read trade export {source_path}: {exc}") from exc
    try:
        with sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "trades" not in tables:
                raise ValueError("SQLite database has no 'trades' table")
            cols = table_columns(conn, "trades")
            df = pd.read_sql_query("SELECT * FROM trades", conn)
    except (sqlite3.Error, ValueError) as exc:
        raise RuntimeError(f"Unable to read dry-run database {source_path}: {exc}") from exc
    strategy_col = "strategy" if "strategy" in cols else None
    if strategy_col and df[strategy_col].notna().any():
        matched = df[df[strategy_col] == ctx.strategy]
        if matched.empty and not df.empty:
            ctx.warnings.append(
                f"Database contains {len(df)} trades but none for strategy {ctx.strategy}; no foreign-strategy trades were imported."
            )
            return df.iloc[0:0].copy()
        df = matched.copy()
    return df


def pick(df: pd.DataFrame, names: list[str], default: Any = np.nan) -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series(default, index=df.index)


def normalize_trades(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(columns=ENRICHED_COLUMNS)
    out = pd.DataFrame(index=raw.index)
    mappings = {
        "trade_id": ["id", "trade_id"], "pair": ["pair"], "is_open": ["is_open"],
        "open_rate": ["open_rate"], "close_rate": ["close_rate"], "stake_amount": ["stake_amount"],
        "amount": ["amount"], "leverage": ["leverage"], "profit_abs": ["close_profit_abs", "profit_abs", "realized_profit"],
        "profit_ratio": ["close_profit", "profit_ratio"], "fee_open": ["fee_open"],
        "fee_close": ["fee_close"], "funding_fees": ["funding_fees"],
        "exit_reason": ["exit_reason"], "entry_tag": ["enter_tag", "entry_tag"],
        "is_short": ["is_short"], "stop_price": ["initial_stop_loss", "stop_loss"],
        "open_rate_requested": ["open_rate_requested"], "fee_open_cost": ["fee_open_cost"],
        "fee_close_cost": ["fee_close_cost"],
    }
    for target, sources in mappings.items():
        out[target] = pick(raw, sources)
    out["open_date"] = pick(raw, ["open_date", "open_date_utc"]).map(utc_timestamp)
    out["close_date"] = pick(raw, ["close_date", "close_date_utc"]).map(utc_timestamp)
    out["is_open"] = out["is_open"].fillna(False).astype(bool)
    out["is_short"] = out["is_short"].fillna(False).astype(bool)
    out["side"] = np.where(out["is_short"], "short", "long")
    for col in ("open_rate", "close_rate", "stake_amount", "amount", "leverage", "profit_abs", "profit_ratio", "fee_open", "fee_close", "funding_fees", "stop_price", "open_rate_requested", "fee_open_cost", "fee_close_cost"):
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.sort_values(["open_date", "trade_id"]).reset_index(drop=True)


def symbol_key(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    previous = df["close"].shift(1)
    true_range = pd.concat(
        [df["high"] - df["low"], (df["high"] - previous).abs(), (df["low"] - previous).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=max(20, window // 3)).rank(pct=True)


def read_ohlcv(ctx: Context, pair: str, timeframe: str) -> pd.DataFrame | None:
    cache_key = (pair, timeframe)
    if cache_key in ctx.ohlcv_cache:
        return ctx.ohlcv_cache[cache_key]
    path = DATA_DIR / f"{symbol_key(pair)}-{timeframe}-futures.feather"
    if not path.exists():
        ctx.warnings.append(f"Missing OHLCV: {path.name}")
        ctx.ohlcv_cache[cache_key] = None
        return None
    try:
        df = pd.read_feather(path)
        required = {"date", "open", "high", "low", "close"}
        if not required.issubset(df.columns):
            raise ValueError(f"missing columns {sorted(required - set(df.columns))}")
        df["date"] = pd.to_datetime(df["date"], utc=True)
        df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
        df["ema50"] = ema(df["close"], 50)
        slope_bars = 3
        df["ema50_slope"] = df["ema50"] / df["ema50"].shift(slope_bars) - 1.0
        df["atr_pct"] = atr(df) / df["close"]
        df["atr_percentile"] = rolling_percentile(df["atr_pct"], 720 if timeframe == "1h" else 180)
        df["regime"] = np.select(
            [(df["close"] > df["ema50"]) & (df["ema50_slope"] > 0), (df["close"] < df["ema50"]) & (df["ema50_slope"] < 0)],
            ["up", "down"], default="range",
        )
        if timeframe == "1h":
            df["pre_low_12"] = df["low"].shift(1).rolling(12).min()
            df["pre_low_24"] = df["low"].shift(1).rolling(24).min()
            df["pre_high_12"] = df["high"].shift(1).rolling(12).max()
            df["pre_high_24"] = df["high"].shift(1).rolling(24).max()
        ctx.ohlcv_cache[cache_key] = df
        return df
    except Exception as exc:
        ctx.warnings.append(f"Failed to read {path.name}: {exc}")
        ctx.ohlcv_cache[cache_key] = None
        return None


def row_at(df: pd.DataFrame | None, timestamp: pd.Timestamp) -> pd.Series | None:
    if df is None or df.empty or pd.isna(timestamp):
        return None
    idx = df["date"].searchsorted(timestamp, side="right") - 1
    return df.iloc[idx] if idx >= 0 else None


def regime_at(ctx: Context, pair: str, timeframe: str, timestamp: pd.Timestamp) -> tuple[str, float, float, float]:
    row = row_at(read_ohlcv(ctx, pair, timeframe), timestamp)
    if row is None:
        return "unknown", np.nan, np.nan, np.nan
    close = safe_float(row.get("close"))
    ema50_value = safe_float(row.get("ema50"))
    distance = close / ema50_value - 1.0 if close > 0 and ema50_value > 0 else np.nan
    return str(row.get("regime", "unknown")), safe_float(row.get("ema50_slope")), distance, safe_float(row.get("atr_percentile"))


def reached_half_r(row: pd.Series, is_short: bool, open_rate: float, half_r: float) -> bool:
    return safe_float(row["low"]) <= open_rate - half_r if is_short else safe_float(row["high"]) >= open_rate + half_r


def reversal_close(row: pd.Series, is_short: bool, boundary: float) -> bool:
    close = safe_float(row["close"])
    return close > boundary if is_short else close < boundary


def path_features(ctx: Context, trade: pd.Series, end_time: pd.Timestamp) -> dict[str, Any]:
    result: dict[str, Any] = {name: np.nan for name in (
        "mae_pct", "mfe_pct", "max_favorable_price", "max_adverse_price",
        "quick_reverse_1h", "quick_reverse_2h", "quick_reverse_3h", "quick_reverse_4h", "quick_reverse_5h",
        "quick_reverse_1h_5h", "false_breakdown", "false_breakdown_12h_low", "false_breakdown_24h_low",
        "false_breakout", "false_breakout_12h_high", "false_breakout_24h_high",
    )}
    df = read_ohlcv(ctx, str(trade["pair"]), "1h")
    if df is None or df.empty:
        result["data_warnings"] = "missing_pair_1h"
        return result
    open_time = trade["open_date"]
    window = df[(df["date"] >= open_time.floor("h")) & (df["date"] <= end_time.ceil("h"))]
    if window.empty:
        result["data_warnings"] = "no_ohlcv_during_trade"
        return result
    open_rate = safe_float(trade["open_rate"])
    is_short = bool(trade["is_short"])
    lows, highs = window["low"], window["high"]
    if is_short:
        result["max_favorable_price"] = safe_float(lows.min())
        result["max_adverse_price"] = safe_float(highs.max())
        result["mfe_pct"] = max(0.0, (open_rate - result["max_favorable_price"]) / open_rate)
        result["mae_pct"] = max(0.0, (result["max_adverse_price"] - open_rate) / open_rate)
    else:
        result["max_favorable_price"] = safe_float(highs.max())
        result["max_adverse_price"] = safe_float(lows.min())
        result["mfe_pct"] = max(0.0, (result["max_favorable_price"] - open_rate) / open_rate)
        result["mae_pct"] = max(0.0, (open_rate - result["max_adverse_price"]) / open_rate)

    stop_price = safe_float(trade["stop_price"])
    if not math.isfinite(stop_price) or stop_price <= 0:
        stop_price = open_rate * (1.0 + abs(DEFAULT_STOPLOSS) if is_short else 1.0 - abs(DEFAULT_STOPLOSS))
        risk_source = "strategy_stoploss_6pct_approx"
    else:
        risk_source = "database_initial_stop_loss"
    risk_abs = abs(open_rate - stop_price)
    result.update({"stop_price": stop_price, "risk_abs": risk_abs, "risk_source": risk_source})
    half_r = 0.5 * risk_abs
    post = window[window["date"] > open_time.floor("h")].head(24).reset_index(drop=True)
    favorable_seen = False
    for hour in range(1, 6):
        event = False
        if len(post) >= hour:
            bar = post.iloc[hour - 1]
            event = (not favorable_seen) and reversal_close(bar, is_short, open_rate)
            favorable_seen = favorable_seen or reached_half_r(bar, is_short, open_rate, half_r)
        result[f"quick_reverse_{hour}h"] = bool(event)
    result["quick_reverse_1h_5h"] = any(bool(result[f"quick_reverse_{h}h"]) for h in range(1, 6))

    entry_row = row_at(df, open_time)
    boundaries = {
        "12": safe_float(entry_row.get("pre_low_12")) if entry_row is not None else np.nan,
        "24": safe_float(entry_row.get("pre_low_24")) if entry_row is not None else np.nan,
        "12_high": safe_float(entry_row.get("pre_high_12")) if entry_row is not None else np.nan,
        "24_high": safe_float(entry_row.get("pre_high_24")) if entry_row is not None else np.nan,
    }
    def false_event(boundary: float) -> bool | float:
        if not math.isfinite(boundary):
            return np.nan
        favorable = False
        for _, bar in post.iterrows():
            if not favorable and reversal_close(bar, is_short, boundary):
                return True
            favorable = favorable or reached_half_r(bar, is_short, open_rate, half_r)
        return False
    if is_short:
        result["false_breakdown_12h_low"] = false_event(boundaries["12"])
        result["false_breakdown_24h_low"] = false_event(boundaries["24"])
        result["false_breakdown"] = result["false_breakdown_12h_low"]
        result["false_breakout"] = False
    else:
        result["false_breakout_12h_high"] = false_event(boundaries["12_high"])
        result["false_breakout_24h_high"] = false_event(boundaries["24_high"])
        result["false_breakout"] = result["false_breakout_12h_high"]
        result["false_breakdown"] = False
    result["compression_boundary_source"] = "pre_entry_12h_and_24h_extreme_approx"
    result["data_warnings"] = ""
    return result


def concurrency_features(trades: pd.DataFrame, index: int, max_slots: int, end_time: pd.Timestamp) -> tuple[int, int, bool]:
    trade = trades.iloc[index]
    entry = trade["open_date"]
    finish = trade["close_date"] if pd.notna(trade["close_date"]) else end_time
    active_at_entry = ((trades["open_date"] <= entry) & (trades["close_date"].isna() | (trades["close_date"] > entry))).sum()
    events: list[tuple[pd.Timestamp, int]] = []
    overlap = trades[(trades["open_date"] <= finish) & (trades["close_date"].isna() | (trades["close_date"] >= entry))]
    for _, other in overlap.iterrows():
        events.append((max(entry, other["open_date"]), 1))
        other_end = other["close_date"] if pd.notna(other["close_date"]) else finish
        events.append((min(finish, other_end), -1))
    running = peak = 0
    for _, delta in sorted(events, key=lambda item: (item[0], -item[1])):
        running += delta
        peak = max(peak, running)
    return int(active_at_entry), int(peak), bool(active_at_entry >= max_slots)


def enrich_trades(trades: pd.DataFrame, ctx: Context, now: pd.Timestamp) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=ENRICHED_COLUMNS)
    records: list[dict[str, Any]] = []
    btc4 = "BTC/USDT:USDT"
    for index, trade in trades.iterrows():
        end_time = trade["close_date"] if pd.notna(trade["close_date"]) else now
        record = trade.to_dict()
        path = path_features(ctx, trade, end_time)
        record.update(path)
        pair = str(trade["pair"])
        open_time = trade["open_date"]
        pair4_regime, slope4, dist4, atr4 = regime_at(ctx, pair, "4h", open_time)
        _, _, dist1d, _ = regime_at(ctx, pair, "1d", open_time)
        btc4_regime, _, _, _ = regime_at(ctx, btc4, "4h", open_time)
        btc1_regime, _, _, _ = regime_at(ctx, btc4, "1d", open_time)
        row1 = row_at(read_ohlcv(ctx, pair, "1h"), open_time)
        atr1 = safe_float(row1.get("atr_percentile")) if row1 is not None else np.nan
        abs_slopes = []
        pair4 = read_ohlcv(ctx, pair, "4h")
        if pair4 is not None:
            historical = pair4[pair4["date"] <= open_time]["ema50_slope"].abs().dropna().tail(180)
            abs_slopes = historical.tolist()
        threshold = float(np.quantile(abs_slopes, 0.30)) if abs_slopes else np.nan
        range_market = pair4_regime == "range" or (math.isfinite(threshold) and abs(slope4) <= threshold)
        current_rate = safe_float(trade["close_rate"])
        if bool(trade["is_open"]):
            latest = row_at(read_ohlcv(ctx, pair, "1h"), now)
            current_rate = safe_float(latest.get("close")) if latest is not None else np.nan
        open_rate = safe_float(trade["open_rate"])
        direction = -1.0 if bool(trade["is_short"]) else 1.0
        leverage = safe_float(trade["leverage"], 1.0)
        current_profit = direction * (current_rate / open_rate - 1.0) * leverage if open_rate > 0 and math.isfinite(current_rate) else np.nan
        requested = safe_float(trade["open_rate_requested"])
        signal_price = requested
        signal_source = "open_rate_requested"
        if not math.isfinite(signal_price) or signal_price <= 0:
            signal_price = safe_float(row1.get("close")) if row1 is not None else np.nan
            signal_source = "entry_1h_close_approx"
        if open_rate > 0 and signal_price > 0:
            slippage = open_rate / signal_price - 1.0 if not bool(trade["is_short"]) else signal_price / open_rate - 1.0
        else:
            slippage = np.nan
        abs_slip = abs(slippage) if math.isfinite(slippage) else np.nan
        slip_level = "unknown" if not math.isfinite(abs_slip) else ("low" if abs_slip < 0.0003 else "light" if abs_slip < 0.0005 else "medium/heavy watch" if abs_slip <= 0.001 else "heavy warning")
        stake = safe_float(trade["stake_amount"])
        fee_cost = safe_float(trade["fee_open_cost"], 0.0) + safe_float(trade["fee_close_cost"], 0.0)
        fee_rate = safe_float(trade["fee_open"], 0.0) + (0.0 if bool(trade["is_open"]) else safe_float(trade["fee_close"], 0.0))
        actual_fee_pct = fee_cost / stake if stake > 0 and fee_cost > 0 else fee_rate
        funding = safe_float(trade["funding_fees"], 0.0)
        funding_pct = abs(funding) / stake if stake > 0 else np.nan
        profit_abs = safe_float(trade["profit_abs"])
        funding_profit_ratio = abs(funding) / abs(profit_abs) if math.isfinite(profit_abs) and abs(profit_abs) > 0 else np.nan
        concurrent, peak, slot_full = concurrency_features(trades, index, ctx.max_open_trades, now)
        record.update({
            "current_rate": current_rate, "current_profit_ratio": current_profit,
            "trade_duration_hours": max(0.0, (end_time - open_time).total_seconds() / 3600.0),
            "range_market": bool(range_market), "btc_4h_regime": btc4_regime, "btc_1d_regime": btc1_regime,
            "pair_4h_regime": pair4_regime, "atr_percentile_1h": atr1, "atr_percentile_4h": atr4,
            "pair_ema50_slope_4h": slope4, "distance_to_ema50_4h": dist4, "distance_to_ema50_1d": dist1d,
            "signal_price": signal_price, "signal_price_source": signal_source,
            "estimated_slippage_pct": slippage, "slippage_level": slip_level,
            "actual_fee_pct": actual_fee_pct, "funding_fee_pct": funding_pct,
            "funding_fee_to_profit_abs": funding_profit_ratio,
            "cost_total_pct": actual_fee_pct + funding_pct + (abs_slip if math.isfinite(abs_slip) else 0.0),
            "concurrent_trades_at_entry": concurrent, "max_concurrent_trades_during_trade": peak,
            "was_slot_full": slot_full,
        })
        records.append(record)
    result = pd.DataFrame(records)
    for col in ENRICHED_COLUMNS:
        if col not in result:
            result[col] = np.nan
    return result[ENRICHED_COLUMNS].sort_values(["open_date", "trade_id"]).reset_index(drop=True)


def profit_factor(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()
    wins = values[values > 0].sum()
    losses = abs(values[values < 0].sum())
    return float(wins / losses) if losses > 0 else (float("inf") if wins > 0 else np.nan)


def max_drawdown_pct(trades: pd.DataFrame) -> float:
    if trades.empty:
        return np.nan
    closed = trades.loc[~trades["is_open"].astype(bool)].sort_values("close_date")
    if closed.empty:
        return np.nan
    returns = closed["profit_ratio"].fillna(0.0)
    equity = (1.0 + returns).cumprod()
    return float(((equity.cummax() - equity) / equity.cummax()).max())


def max_loss_streak(trades: pd.DataFrame) -> int:
    if trades.empty:
        return 0
    streak = peak = 0
    closed = trades.loc[~trades["is_open"].astype(bool)].sort_values("close_date")
    for value in closed["profit_ratio"].fillna(0.0):
        streak = streak + 1 if value < 0 else 0
        peak = max(peak, streak)
    return peak


def stats_row(closed: pd.DataFrame, label: str, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, Any]:
    profits = pd.to_numeric(closed.get("profit_ratio", pd.Series(dtype=float)), errors="coerce")
    short_mask = closed["is_short"].astype(bool) if "is_short" in closed else pd.Series(False, index=closed.index, dtype=bool)
    return {
        "period": label, "start_date": start, "end_date": end, "closed_trades": len(closed),
        "profit_abs": closed.get("profit_abs", pd.Series(dtype=float)).sum(), "profit_pct_sum": profits.sum(),
        "profit_factor": profit_factor(profits), "max_drawdown_pct": max_drawdown_pct(closed),
        "winrate": float((profits > 0).mean()) if len(profits) else np.nan,
        "avg_profit": profits.mean() if len(profits) else np.nan,
        "avg_duration_hours": closed.get("trade_duration_hours", pd.Series(dtype=float)).mean(),
        "total_fee_pct": closed.get("actual_fee_pct", pd.Series(dtype=float)).sum(),
        "total_funding_fee": closed.get("funding_fees", pd.Series(dtype=float)).sum(),
        "avg_slippage_pct": closed.get("estimated_slippage_pct", pd.Series(dtype=float)).abs().mean(),
        "max_slippage_pct": closed.get("estimated_slippage_pct", pd.Series(dtype=float)).abs().max(),
        "quick_reverse_rate": closed.get("quick_reverse_1h_5h", pd.Series(dtype=float)).mean(),
        "false_breakdown_rate": closed.loc[short_mask].get("false_breakdown", pd.Series(dtype=float)).mean(),
        "false_breakout_rate": closed.loc[~short_mask].get("false_breakout", pd.Series(dtype=float)).mean(),
        "range_market_rate": closed.get("range_market", pd.Series(dtype=float)).mean(),
        "max_loss_streak": max_loss_streak(closed),
    }


def period_slice(enriched: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    closed = enriched[(~enriched["is_open"]) & enriched["close_date"].between(start, end, inclusive="both")].copy()
    open_now = enriched[enriched["is_open"]].copy()
    return closed, open_now


def pair_tag_matrix(closed: pd.DataFrame) -> pd.DataFrame:
    columns = ["pair", "entry_tag", "side", "trades", "profit_abs", "profit_factor", "winrate", "avg_mae", "avg_mfe", "quick_reverse_rate", "false_breakdown_rate", "false_breakout_rate", "range_market_rate"]
    if closed.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for keys, group in closed.groupby(["pair", "entry_tag", "side"], dropna=False):
        short_mask = group["is_short"].astype(bool)
        rows.append({
            "pair": keys[0], "entry_tag": keys[1], "side": keys[2], "trades": len(group),
            "profit_abs": group["profit_abs"].sum(), "profit_factor": profit_factor(group["profit_ratio"]),
            "winrate": (group["profit_ratio"] > 0).mean(), "avg_mae": group["mae_pct"].mean(),
            "avg_mfe": group["mfe_pct"].mean(), "quick_reverse_rate": group["quick_reverse_1h_5h"].mean(),
            "false_breakdown_rate": group.loc[short_mask, "false_breakdown"].mean(),
            "false_breakout_rate": group.loc[~short_mask, "false_breakout"].mean(),
            "range_market_rate": group["range_market"].mean(),
        })
    return pd.DataFrame(rows, columns=columns).sort_values(["profit_abs", "trades"], ascending=[True, False])


def risk_events(enriched: pd.DataFrame) -> pd.DataFrame:
    columns = ["trade_id", "pair", "entry_tag", "side", "event", "severity", "value", "open_date", "close_date"]
    rows: list[dict[str, Any]] = []
    checks = [
        ("quick_reverse", "quick_reverse_1h_5h", "YELLOW"), ("false_breakdown", "false_breakdown", "YELLOW"),
        ("false_breakout", "false_breakout", "YELLOW"), ("range_market", "range_market", "YELLOW"),
        ("slot_full", "was_slot_full", "YELLOW"),
    ]
    for _, trade in enriched.iterrows():
        common = {k: trade.get(k) for k in ("trade_id", "pair", "entry_tag", "side", "open_date", "close_date")}
        for event, field_name, severity in checks:
            if trade.get(field_name) is True or trade.get(field_name) == 1:
                rows.append({**common, "event": event, "severity": severity, "value": trade.get(field_name)})
        slip = safe_float(trade.get("estimated_slippage_pct"))
        if math.isfinite(slip) and abs(slip) > 0.001:
            rows.append({**common, "event": "slippage_heavy", "severity": "ORANGE", "value": slip})
        funding_ratio = safe_float(trade.get("funding_fee_to_profit_abs"))
        if math.isfinite(funding_ratio) and funding_ratio > 0.2:
            rows.append({**common, "event": "funding_fee_over_20pct_profit", "severity": "ORANGE", "value": funding_ratio})
    return pd.DataFrame(rows, columns=columns)


def risk_grade(closed: pd.DataFrame, warning_count: int) -> tuple[str, str, list[str]]:
    if len(closed) < 5:
        reasons = [f"Only {len(closed)} closed trades; statistical sample is insufficient."]
        if warning_count:
            reasons.append(f"There are {warning_count} data/config warnings.")
        return "YELLOW", "Continue dry-run; do not add capital.", reasons
    pf = profit_factor(closed["profit_ratio"])
    dd = max_drawdown_pct(closed)
    streak = max_loss_streak(closed)
    avg_slip = closed["estimated_slippage_pct"].abs().mean()
    matrix = pair_tag_matrix(closed)
    bad_group = not matrix.empty and bool(((matrix["profit_factor"] < 0.7) & (matrix["trades"] >= 3)).any())
    red = pf < 1.0 or dd > 0.12 or streak >= 8 or (math.isfinite(avg_slip) and avg_slip > 0.0015)
    orange = pf < 1.2 or dd >= 0.10 or streak >= 5 or bad_group or (math.isfinite(avg_slip) and avg_slip >= 0.001)
    qr = closed["quick_reverse_1h_5h"].mean()
    fb = closed.loc[closed["is_short"].astype(bool), "false_breakdown"].mean()
    yellow = pf < 1.5 or dd >= 0.08 or qr > BASELINE_QR * 1.15 or fb > BASELINE_FB * 1.15 or (math.isfinite(avg_slip) and avg_slip >= 0.0005) or warning_count > 0
    if red:
        return "RED", "Pause new entries; let existing positions exit by strategy and return to offline diagnosis.", [f"PF={pf:.2f}, MaxDD={dd:.2%}, loss streak={streak}, avg slippage={avg_slip:.3%}."]
    if orange:
        return "ORANGE", "Pause capital increases and inspect manually.", [f"PF={pf:.2f}, MaxDD={dd:.2%}, loss streak={streak}, bad pair/tag group={bad_group}."]
    if yellow:
        return "YELLOW", "Continue dry-run; do not add capital.", [f"PF={pf:.2f}, MaxDD={dd:.2%}, quick reverse={qr:.1%}, false breakdown={fb:.1%}."]
    return "GREEN", "Continue dry-run.", [f"PF={pf:.2f}, MaxDD={dd:.2%}, execution costs remain within limits."]


def fmt(value: Any, kind: str = "number") -> str:
    if value is None or (isinstance(value, float) and not math.isfinite(value)) or pd.isna(value):
        return "N/A"
    if kind == "pct":
        return f"{float(value):.2%}"
    if kind == "money":
        return f"{float(value):.4f}"
    if kind == "date":
        return pd.Timestamp(value).strftime("%Y-%m-%d %H:%M UTC")
    return f"{float(value):.3f}" if isinstance(value, (float, np.floating)) else str(value)


def markdown_table(df: pd.DataFrame, columns: list[tuple[str, str, str]], limit: int = 100) -> str:
    headers = [label for _, label, _ in columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    if df.empty:
        lines.append("| " + " | ".join(["No data"] + [""] * (len(headers) - 1)) + " |")
        return "\n".join(lines)
    for _, row in df.head(limit).iterrows():
        values = [fmt(row.get(col), kind).replace("|", "\\|") for col, _, kind in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def daily_report(ctx: Context, closed: pd.DataFrame, open_now: pd.DataFrame, stats: dict[str, Any], grade: str, action: str, reasons: list[str], target: date, db_path: Path | None) -> str:
    trade_cols = [("pair", "Pair", "text"), ("side", "Side", "text"), ("entry_tag", "Entry tag", "text"), ("open_date", "Open", "date"), ("close_date", "Close", "date"), ("profit_abs", "Profit", "money"), ("profit_ratio", "Profit %", "pct"), ("exit_reason", "Exit", "text"), ("trade_duration_hours", "Hours", "number"), ("mae_pct", "MAE", "pct"), ("mfe_pct", "MFE", "pct"), ("quick_reverse_1h_5h", "Quick reverse", "text"), ("false_breakdown", "False down", "text"), ("false_breakout", "False up", "text"), ("btc_4h_regime", "BTC 4H", "text"), ("range_market", "Range", "text"), ("actual_fee_pct", "Fee", "pct"), ("funding_fees", "Funding", "money"), ("estimated_slippage_pct", "Slippage", "pct")]
    open_cols = [("pair", "Pair", "text"), ("side", "Side", "text"), ("entry_tag", "Entry tag", "text"), ("open_date", "Open", "date"), ("open_rate", "Open rate", "number"), ("current_profit_ratio", "Current P/L", "pct"), ("trade_duration_hours", "Hours", "number"), ("mae_pct", "MAE", "pct"), ("mfe_pct", "MFE", "pct"), ("btc_4h_regime", "BTC 4H", "text"), ("range_market", "Range", "text")]
    event_counts = risk_events(pd.concat([closed, open_now], ignore_index=True))["event"].value_counts() if not closed.empty or not open_now.empty else pd.Series(dtype=int)
    warnings = "\n".join(f"- {w}" for w in ctx.warnings) or "- None"
    reason_lines = "\n".join(f"- {r}" for r in reasons)
    sample_note = "\nCurrent dry-run sample is insufficient for statistical conclusions.\n" if len(closed) < 5 else "\n"
    return f"""# Positive13 Dry-Run Daily Report - {target.isoformat()}

## Overview

- Strategy: `{ctx.strategy}`
- Pair pool: Positive13 ({len(ctx.pairs)} pairs)
- max_open_trades: {ctx.max_open_trades}
- Mode: futures / isolated / dry-run
- Database: `{db_path or 'not found'}`
- Open positions: {len(open_now)}

## Closed Trades

{markdown_table(closed, trade_cols)}

## Current Positions

{markdown_table(open_now, open_cols)}

## Daily Statistics

| Metric | Value |
| --- | --- |
| Closed trades | {stats['closed_trades']} |
| Profit abs | {fmt(stats['profit_abs'], 'money')} |
| Profit ratio sum | {fmt(stats['profit_pct_sum'], 'pct')} |
| Win rate | {fmt(stats['winrate'], 'pct')} |
| Profit factor | {fmt(stats['profit_factor'])} |
| Max intraday drawdown | {fmt(stats['max_drawdown_pct'], 'pct')} |
| Average profit | {fmt(stats['avg_profit'], 'pct')} |
| Average duration | {fmt(stats['avg_duration_hours'])} h |
| Total fee rate | {fmt(stats['total_fee_pct'], 'pct')} |
| Total funding fee | {fmt(stats['total_funding_fee'], 'money')} |
| Average slippage | {fmt(stats['avg_slippage_pct'], 'pct')} |

## Risk Events

| Event | Count |
| --- | ---: |
| Quick reverse | {int(event_counts.get('quick_reverse', 0))} |
| False breakdown | {int(event_counts.get('false_breakdown', 0))} |
| False breakout | {int(event_counts.get('false_breakout', 0))} |
| Range market | {int(event_counts.get('range_market', 0))} |
| Heavy slippage | {int(event_counts.get('slippage_heavy', 0))} |
| Funding warning | {int(event_counts.get('funding_fee_over_20pct_profit', 0))} |
| Slot full | {int(event_counts.get('slot_full', 0))} |

## Decision

- Risk level: **{grade}**
- Action: **{action}**
{reason_lines}
{sample_note}""" + (f"\n## Warnings\n\n{warnings}\n" if ctx.warnings else "\n")


def weekly_report(ctx: Context, closed: pd.DataFrame, open_now: pd.DataFrame, stats: dict[str, Any], matrix: pd.DataFrame, grade: str, action: str, reasons: list[str], start: pd.Timestamp, end: pd.Timestamp, db_path: Path | None) -> str:
    short_mask = closed["is_short"].astype(bool) if "is_short" in closed else pd.Series(False, index=closed.index, dtype=bool)
    short = closed.loc[short_mask]
    long = closed.loc[~short_mask]
    event_df = risk_events(closed)
    worst_pair = closed.groupby("pair")["profit_abs"].sum().sort_values().head(1) if not closed.empty else pd.Series(dtype=float)
    worst_tag = closed.groupby("entry_tag")["profit_abs"].sum().sort_values().head(1) if not closed.empty else pd.Series(dtype=float)
    max_slip_pair = closed.groupby("pair")["estimated_slippage_pct"].apply(lambda x: x.abs().mean()).sort_values(ascending=False).head(1) if not closed.empty else pd.Series(dtype=float)
    max_funding_pair = closed.groupby("pair")["funding_fees"].apply(lambda x: x.abs().sum()).sort_values(ascending=False).head(1) if not closed.empty else pd.Series(dtype=float)
    matrix_cols = [("pair", "Pair", "text"), ("entry_tag", "Entry tag", "text"), ("side", "Side", "text"), ("trades", "Trades", "number"), ("profit_abs", "Profit", "money"), ("profit_factor", "PF", "number"), ("winrate", "Win rate", "pct"), ("avg_mae", "Avg MAE", "pct"), ("avg_mfe", "Avg MFE", "pct"), ("quick_reverse_rate", "Quick reverse", "pct"), ("false_breakdown_rate", "False down", "pct"), ("range_market_rate", "Range", "pct")]
    comparisons = [
        ("PF below 1.5", stats["profit_factor"] < 1.5 if math.isfinite(safe_float(stats["profit_factor"])) else "insufficient"),
        ("MaxDD near/above 10%", stats["max_drawdown_pct"] >= 0.10 if math.isfinite(safe_float(stats["max_drawdown_pct"])) else "insufficient"),
        ("Average slippage at heavy level", stats["avg_slippage_pct"] >= 0.001 if math.isfinite(safe_float(stats["avg_slippage_pct"])) else "insufficient"),
        ("Cost exceeds fee2x + heavy proxy (0.20%)", closed["cost_total_pct"].mean() > 0.002 if not closed.empty else "insufficient"),
    ]
    compare_rows = "\n".join(f"| {name} | {value} |" for name, value in comparisons)
    reasons_md = "\n".join(f"- {r}" for r in reasons)
    warnings = "\n".join(f"- {w}" for w in ctx.warnings) or "- None"
    sample_note = "\nCurrent dry-run sample is insufficient for statistical conclusions.\n" if len(closed) < 5 else "\n"
    return f"""# Positive13 Dry-Run Weekly Report - {end.date().isoformat()}

## Overview

- Period: {start.date().isoformat()} to {end.date().isoformat()}
- Strategy: `{ctx.strategy}`
- Database: `{db_path or 'not found'}`
- Closed trades: {len(closed)}; open positions: {len(open_now)}
- Profit: {fmt(stats['profit_abs'], 'money')} ({fmt(stats['profit_pct_sum'], 'pct')} sum)
- PF: {fmt(stats['profit_factor'])}; MaxDD: {fmt(stats['max_drawdown_pct'], 'pct')}; Win rate: {fmt(stats['winrate'], 'pct')}
- Average profit: {fmt(stats['avg_profit'], 'pct')}; average duration: {fmt(stats['avg_duration_hours'])} h
- Long: {len(long)} trades / {fmt(long['profit_abs'].sum(), 'money')} profit
- Short: {len(short)} trades / {fmt(short['profit_abs'].sum(), 'money')} profit

## Backtest Guardrails

Reference: 3y baseline PF 2.00 / MaxDD 7.66%; fee2x + heavy PF 1.72 / MaxDD 10.89%; recent-year PF 2.00.

| Check | Result |
| --- | --- |
{compare_rows}

## Pair x Entry Tag x Side

{markdown_table(matrix, matrix_cols)}

## Risk Features

| Metric | Value |
| --- | --- |
| Quick reverse rate | {fmt(stats['quick_reverse_rate'], 'pct')} |
| False breakdown rate | {fmt(stats['false_breakdown_rate'], 'pct')} |
| False breakout rate | {fmt(stats['false_breakout_rate'], 'pct')} |
| Range market rate | {fmt(stats['range_market_rate'], 'pct')} |
| Average slippage | {fmt(stats['avg_slippage_pct'], 'pct')} |
| Maximum slippage | {fmt(stats['max_slippage_pct'], 'pct')} |
| Total fee rate | {fmt(stats['total_fee_pct'], 'pct')} |
| Total funding fee | {fmt(stats['total_funding_fee'], 'money')} |

BTC 4H regime distribution: {closed['btc_4h_regime'].value_counts(dropna=False).to_dict() if not closed.empty else {}}

Pair 4H regime distribution: {closed['pair_4h_regime'].value_counts(dropna=False).to_dict() if not closed.empty else {}}

## Anomalies

- Worst pair: {worst_pair.to_dict()}
- Worst entry tag: {worst_tag.to_dict()}
- Highest average-slippage pair: {max_slip_pair.to_dict()}
- Highest funding-cost pair: {max_funding_pair.to_dict()}
- Risk events: {event_df['event'].value_counts().to_dict() if not event_df.empty else {}}

## Weekly Decision

- Risk level: **{grade}**
- Continue dry-run: **Yes**
- Pause new entries: **{'Yes' if grade == 'RED' else 'No'}**
- Manual inspection required: **{'Yes' if grade in ('ORANGE', 'RED') else 'No'}**
- Return to offline optimization: **{'Yes' if grade == 'RED' else 'No'}**
- Consider small-capital live trading: **No until sample and execution gates are met**
- Action: **{action}**
{reasons_md}
{sample_note}""" + (f"\n## Warnings\n\n{warnings}\n" if ctx.warnings else "\n")


def monitoring_schema() -> pd.DataFrame:
    descriptions = {
        "trade_id": ("integer", "Freqtrade trade identifier", "trades.id", "direct"),
        "pair": ("string", "Trading pair", "trades.pair", "direct"),
        "side": ("string", "long or short", "trades.is_short", "mapped"),
        "quick_reverse_1h_5h": ("boolean", "Entry-price reversal within first five 1H bars before +0.5R", "OHLCV + trade", "sequential path test"),
        "false_breakdown": ("boolean", "Short closes above approximate 12H compression low before +0.5R", "1H OHLCV", "pre-entry 12-bar low approximation"),
        "false_breakout": ("boolean", "Long closes below approximate 12H compression high before +0.5R", "1H OHLCV", "pre-entry 12-bar high approximation"),
        "range_market": ("boolean", "Pair 4H is range or EMA50 slope is in lowest 30%", "4H OHLCV", "regime and rolling slope quantile"),
        "estimated_slippage_pct": ("float", "Direction-adjusted entry slippage", "trade + 1H OHLCV", "requested price preferred; signal close fallback"),
        "actual_fee_pct": ("float", "Entry and exit fee share of stake", "trades fee fields", "fee cost / stake or fee rates"),
        "funding_fee_pct": ("float", "Absolute funding fee share of stake", "trades.funding_fees", "abs(funding) / stake"),
        "cost_total_pct": ("float", "Conservative fee, funding and slippage total", "derived", "fee + abs(funding) + abs(slippage)"),
    }
    rows = []
    for name in ENRICHED_COLUMNS:
        dtype, description, source, calculation = descriptions.get(name, ("float/string", name.replace("_", " "), "trade database or local OHLCV", "direct or derived; see dryrun_monitor.py"))
        rows.append({"field_name": name, "type": dtype, "description": description, "source": source, "calculation": calculation, "nullable": name not in {"trade_id", "pair", "side", "is_short", "is_open", "open_date", "open_rate"}})
    return pd.DataFrame(rows)


def template_text() -> str:
    return """# Positive13 Dry-Run Monitoring Template

Generated by `user_data/analysis/dryrun_monitor.py`.

## Reporting cadence

- Daily: closed trades for the selected UTC day plus all currently open positions.
- Weekly: closed trades for the trailing seven UTC days plus all currently open positions.
- Full: all trades since the selected database began.

## Required review

Review P/L, PF, drawdown, MAE/MFE, quick reverse, approximate false breakdown/breakout, range-market exposure, slippage, fees, funding and slot pressure. The false-breakdown boundaries use the pre-entry 12/24-bar extreme approximation unless strategy custom data becomes available.

## Risk levels

GREEN continues dry-run. YELLOW continues observation without adding capital. ORANGE pauses capital increases and requires manual review. RED recommends pausing new entries while existing positions exit according to strategy.
"""


def recommendation_text(ctx: Context, grade: str, closed_count: int) -> str:
    pairs = ", ".join(ctx.pairs)
    return f"""# Positive13 Final Dry-Run Recommendation

## Current Decision

Continue dry-run with **Positive13 + Combined + max_open_trades=3**. Do not change the strategy, remove pairs, disable entry tags, split the bot, or add slots during this observation phase.

- Current risk level: **{grade}**
- Closed dry-run samples: **{closed_count}**
- Strategy file: `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py`
- Strategy: `{ctx.strategy}`
- Config: `{ctx.config_path}`
- Pair pool: {pairs}
- max_open_trades: {ctx.max_open_trades}
- Keep long: Yes
- Keep both short entry tags: Yes
- Remove pairs: No
- Split bot: No
- Modify strategy: No

## Monitoring Priorities

The highest-priority fields are false breakdown, quick reverse, range-market exposure, actual slippage, fees, funding cost, MAE/MFE and slot saturation. Entry slippage uses requested price when stored; otherwise it is an estimate against the entry 1H close. False-breakdown and false-breakout use pre-entry 12/24-bar extrema because compression custom data is not stored in the trade database.

## Small-Capital Gate

Only consider small-capital live trading after at least 30 closed trades and at least four full observation weeks, with PF >= 1.5, MaxDD < 8%, no persistent pair/tag PF below 0.7, average slippage below 0.05%, no execution/data incidents, and false-breakdown/quick-reverse rates not materially above the historical diagnostic baseline.

## Mandatory Pause Gate

Pause new entries if PF < 1.0, MaxDD > 12%, the loss streak reaches eight trades, actual slippage persistently exceeds 0.10%, a serious API/data anomaly appears, or a single-day loss breaches the operator's approved capital threshold. Existing positions should continue to exit according to the unchanged strategy.
"""


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    output_dir = Path(args.output_dir).resolve()
    ctx = Context(json_config(config_path), config_path, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp.now(tz="UTC")
    report_day = date.fromisoformat(args.date) if args.date else now.date()
    end_day = date.fromisoformat(args.end_date) if args.end_date else report_day
    if args.mode == "daily":
        start = day_start(args.start_date or args.date, report_day)
        end = start + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    elif args.mode == "weekly":
        end = day_start(args.end_date, end_day) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        start = day_start(args.start_date, end_day - timedelta(days=6))
    else:
        end = day_start(args.end_date, end_day) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        start = day_start(args.start_date, date(1970, 1, 1))

    if args.db_path and args.trade_export:
        raise ValueError("Use either --db-path or --trade-export, not both")
    db_path = discover_database(ctx, args.trade_export or args.db_path)
    raw = read_trades(db_path, ctx)
    normalized = normalize_trades(raw)
    enriched = enrich_trades(normalized, ctx, now)
    write_csv(enriched, ANALYSIS_DIR / "dryrun_trades_enriched.csv")
    write_csv(monitoring_schema(), ANALYSIS_DIR / "dryrun_monitoring_schema.csv")
    (REPORTS_DIR / "dryrun_monitoring_template.md").write_text(template_text(), encoding="utf-8")

    daily_rows = []
    if enriched.empty:
        daily_rows.append(stats_row(enriched, report_day.isoformat(), day_start(None, report_day), day_start(None, report_day) + pd.Timedelta(days=1)))
    else:
        first = enriched["close_date"].dropna().min()
        cursor = first.floor("D") if pd.notna(first) else start.floor("D")
        while cursor <= min(end, now).floor("D"):
            daily_closed, _ = period_slice(enriched, cursor, cursor + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
            daily_rows.append(stats_row(daily_closed, cursor.date().isoformat(), cursor, cursor + pd.Timedelta(days=1)))
            cursor += pd.Timedelta(days=1)
    daily_summary = pd.DataFrame(daily_rows)
    write_csv(daily_summary, ANALYSIS_DIR / "dryrun_daily_summary.csv")

    weekly_rows = []
    week_end = end.floor("D")
    for offset in range(8):
        current_end = week_end - pd.Timedelta(days=7 * offset)
        current_start = current_end - pd.Timedelta(days=6)
        weekly_closed, _ = period_slice(enriched, current_start, current_end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
        weekly_rows.append(stats_row(weekly_closed, current_end.date().isoformat(), current_start, current_end))
        if enriched.empty or (enriched["open_date"].min() >= current_start):
            break
    write_csv(pd.DataFrame(weekly_rows), ANALYSIS_DIR / "dryrun_weekly_summary.csv")

    closed, open_now = period_slice(enriched, start, end)
    stats = stats_row(closed, args.mode, start, end)
    matrix = pair_tag_matrix(closed)
    events = risk_events(enriched)
    write_csv(matrix, ANALYSIS_DIR / "dryrun_pair_tag_matrix.csv")
    write_csv(events, ANALYSIS_DIR / "dryrun_risk_events.csv")
    grade, action, reasons = risk_grade(closed, len(ctx.warnings))

    daily_target = report_day
    daily_start = day_start(args.date, daily_target)
    daily_closed, daily_open = period_slice(enriched, daily_start, daily_start + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
    daily_stats = stats_row(daily_closed, "daily", daily_start, daily_start + pd.Timedelta(days=1))
    daily_grade, daily_action, daily_reasons = risk_grade(daily_closed, len(ctx.warnings))
    daily_path = output_dir / f"dryrun_daily_{daily_target.strftime('%Y%m%d')}.md"
    daily_path.write_text(daily_report(ctx, daily_closed, daily_open, daily_stats, daily_grade, daily_action, daily_reasons, daily_target, db_path), encoding="utf-8")

    weekly_end = day_start(args.end_date, end_day) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    weekly_start = weekly_end.floor("D") - pd.Timedelta(days=6)
    weekly_closed, weekly_open = period_slice(enriched, weekly_start, weekly_end)
    weekly_stats = stats_row(weekly_closed, "weekly", weekly_start, weekly_end)
    weekly_matrix = pair_tag_matrix(weekly_closed)
    weekly_grade, weekly_action, weekly_reasons = risk_grade(weekly_closed, len(ctx.warnings))
    weekly_path = output_dir / f"dryrun_weekly_{end_day.strftime('%Y%m%d')}.md"
    weekly_path.write_text(weekly_report(ctx, weekly_closed, weekly_open, weekly_stats, weekly_matrix, weekly_grade, weekly_action, weekly_reasons, weekly_start, weekly_end, db_path), encoding="utf-8")

    (REPORTS_DIR / "positive13_final_dryrun_recommendation.md").write_text(recommendation_text(ctx, grade, len(enriched[~enriched["is_open"]])), encoding="utf-8")
    print(json.dumps({
        "database": str(db_path) if db_path else None, "trades": len(enriched),
        "closed_trades": int((~enriched["is_open"]).sum()) if not enriched.empty else 0,
        "open_trades": int(enriched["is_open"].sum()) if not enriched.empty else 0,
        "risk_level": grade, "warnings": ctx.warnings,
        "daily_report": str(daily_path), "weekly_report": str(weekly_path),
    }, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
