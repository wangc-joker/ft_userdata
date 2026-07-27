from __future__ import annotations

import argparse
import base64
import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "user_data" / "config.dryrun.dualtrend.longmicro.positive13.max3.json"
DEFAULT_DATABASE = ROOT / "user_data" / "analysis" / "signal_collision_shadow.sqlite"
SELECTED_FEATURES = (
    "close",
    "enter_initial_stop",
    "enter_risk_pct",
    "atr_pct",
    "body_pct_of_range",
    "close_position",
    "compression_width_pct",
    "pullback_depth_short",
    "pullback_depth_long_1h",
    "trend_up_4h",
    "trend_down_4h",
    "long_strong_trend_context",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only live signal collision shadow collector for the LongMicro bot"
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    parser.add_argument("--base-url", default="http://127.0.0.1:8086")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--since", help="Ignore signal executions before this UTC timestamp")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--summary", action="store_true")
    return parser.parse_args()


def parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        result = datetime.fromisoformat(text)
    except ValueError:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


class ApiClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        token = base64.b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
        self.headers = {"Authorization": f"Basic {token}"}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(f"{self.base_url}{path}{query}", headers=self.headers)
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


def configure_database(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS signal_candidates (
            strategy TEXT NOT NULL,
            pair TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            expected_entry_date TEXT NOT NULL,
            side TEXT NOT NULL,
            entry_tag TEXT NOT NULL,
            first_observed_at TEXT NOT NULL,
            last_observed_at TEXT NOT NULL,
            classification TEXT NOT NULL,
            open_trades_before INTEGER NOT NULL,
            max_open_trades INTEGER NOT NULL,
            matched_trade_id INTEGER,
            trade_open_date TEXT,
            trade_close_date TEXT,
            trade_is_open INTEGER,
            trade_profit_ratio REAL,
            trade_profit_abs REAL,
            trade_exit_reason TEXT,
            feature_json TEXT NOT NULL,
            PRIMARY KEY (strategy, pair, signal_date, side, entry_tag)
        );
        CREATE TABLE IF NOT EXISTS collector_runs (
            observed_at TEXT PRIMARY KEY,
            strategy TEXT,
            pair_count INTEGER NOT NULL,
            candidate_count INTEGER NOT NULL,
            error_count INTEGER NOT NULL,
            errors_json TEXT NOT NULL
        );
        """
    )


def normalized_trades(payload: Any) -> list[dict[str, Any]]:
    rows = payload.get("trades", []) if isinstance(payload, dict) else payload
    return list(rows or [])


def trade_interval(trade: dict[str, Any]) -> tuple[datetime | None, datetime | None]:
    return parse_date(trade.get("open_date")), parse_date(trade.get("close_date"))


def match_trade(
    trades: list[dict[str, Any]],
    pair: str,
    tag: str,
    expected_entry: datetime,
) -> dict[str, Any] | None:
    tolerance = timedelta(minutes=15)
    matches: list[tuple[timedelta, dict[str, Any]]] = []
    for trade in trades:
        if trade.get("pair") != pair or str(trade.get("enter_tag") or "") != tag:
            continue
        opened, _ = trade_interval(trade)
        if opened is None:
            continue
        distance = abs(opened - expected_entry)
        if distance <= tolerance:
            matches.append((distance, trade))
    return min(matches, key=lambda item: item[0])[1] if matches else None


def occupancy_before(
    trades: list[dict[str, Any]], expected_entry: datetime, matched_trade_id: Any
) -> int:
    count = 0
    for trade in trades:
        if matched_trade_id is not None and trade.get("trade_id", trade.get("id")) == matched_trade_id:
            continue
        opened, closed = trade_interval(trade)
        if opened and opened <= expected_entry and (closed is None or closed > expected_entry):
            count += 1
    return count


def latest_signals(payload: dict[str, Any]) -> list[dict[str, Any]]:
    columns = list(payload.get("columns", []))
    rows: list[dict[str, Any]] = []
    for values in payload.get("data", []):
        row = dict(zip(columns, values))
        long_signal = row.get("enter_long") in (1, 1.0, True)
        short_signal = row.get("enter_short") in (1, 1.0, True)
        if long_signal == short_signal:
            continue
        row["side"] = "long" if long_signal else "short"
        rows.append(row)
    return rows


def upsert_candidate(
    conn: sqlite3.Connection,
    observed_at: str,
    strategy: str,
    max_open_trades: int,
    trades: list[dict[str, Any]],
    row: dict[str, Any],
    timeframe_minutes: int,
) -> None:
    signal_date = parse_date(row.get("date"))
    if signal_date is None:
        return
    expected_entry = signal_date + timedelta(minutes=timeframe_minutes)
    tag = str(row.get("enter_tag") or "")
    pair = str(row["pair"])
    matched = match_trade(trades, pair, tag, expected_entry)
    matched_id = matched.get("trade_id", matched.get("id")) if matched else None
    occupied = occupancy_before(trades, expected_entry, matched_id)
    if matched:
        classification = "admitted"
    elif occupied >= max_open_trades:
        classification = "shadow_rejected_slot_full"
    else:
        classification = "shadow_not_admitted_other"

    features = {name: row.get(name) for name in SELECTED_FEATURES if name in row}
    values = (
        strategy,
        pair,
        iso(signal_date),
        iso(expected_entry),
        row["side"],
        tag,
        observed_at,
        observed_at,
        classification,
        occupied,
        max_open_trades,
        matched_id,
        matched.get("open_date") if matched else None,
        matched.get("close_date") if matched else None,
        int(bool(matched.get("is_open"))) if matched else None,
        matched.get("profit_ratio", matched.get("close_profit")) if matched else None,
        matched.get("profit_abs", matched.get("close_profit_abs")) if matched else None,
        matched.get("exit_reason") if matched else None,
        json.dumps(features, ensure_ascii=True, separators=(",", ":")),
    )
    conn.execute(
        """
        INSERT INTO signal_candidates (
            strategy, pair, signal_date, expected_entry_date, side, entry_tag,
            first_observed_at, last_observed_at, classification, open_trades_before,
            max_open_trades, matched_trade_id, trade_open_date, trade_close_date,
            trade_is_open, trade_profit_ratio, trade_profit_abs, trade_exit_reason,
            feature_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(strategy, pair, signal_date, side, entry_tag) DO UPDATE SET
            last_observed_at=excluded.last_observed_at,
            classification=excluded.classification,
            open_trades_before=excluded.open_trades_before,
            max_open_trades=excluded.max_open_trades,
            matched_trade_id=excluded.matched_trade_id,
            trade_open_date=excluded.trade_open_date,
            trade_close_date=excluded.trade_close_date,
            trade_is_open=excluded.trade_is_open,
            trade_profit_ratio=excluded.trade_profit_ratio,
            trade_profit_abs=excluded.trade_profit_abs,
            trade_exit_reason=excluded.trade_exit_reason,
            feature_json=excluded.feature_json
        """,
        values,
    )


def refresh_matched_trades(conn: sqlite3.Connection, trades: list[dict[str, Any]], observed_at: str) -> None:
    for trade in trades:
        trade_id = trade.get("trade_id", trade.get("id"))
        if trade_id is None:
            continue
        conn.execute(
            """
            UPDATE signal_candidates SET
                last_observed_at=?,
                trade_open_date=?,
                trade_close_date=?,
                trade_is_open=?,
                trade_profit_ratio=?,
                trade_profit_abs=?,
                trade_exit_reason=?
            WHERE matched_trade_id=?
            """,
            (
                observed_at,
                trade.get("open_date"),
                trade.get("close_date"),
                int(bool(trade.get("is_open"))),
                trade.get("profit_ratio", trade.get("close_profit")),
                trade.get("profit_abs", trade.get("close_profit_abs")),
                trade.get("exit_reason"),
                trade_id,
            ),
        )


def collect_once(args: argparse.Namespace) -> tuple[int, int]:
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    api_config = config["api_server"]
    client = ApiClient(args.base_url, api_config["username"], api_config["password"])
    shown = client.get("/api/v1/show_config")
    whitelist_payload = client.get("/api/v1/whitelist")
    closed_trades = normalized_trades(client.get("/api/v1/trades", {"limit": 1000}))
    open_trades = normalized_trades(client.get("/api/v1/status"))
    trades_by_id: dict[Any, dict[str, Any]] = {}
    for trade in closed_trades + open_trades:
        trade_id = trade.get("trade_id", trade.get("id"))
        trades_by_id[trade_id if trade_id is not None else id(trade)] = trade
    trades = list(trades_by_id.values())
    pairs = list(whitelist_payload.get("whitelist", whitelist_payload.get("pairs", [])))
    if not pairs and isinstance(whitelist_payload.get("data"), list):
        pairs = list(whitelist_payload["data"])

    observed = iso(datetime.now(timezone.utc))
    strategy = str(shown.get("strategy", config.get("strategy", "")))
    max_open_trades = int(shown.get("max_open_trades", config.get("max_open_trades", 3)))
    since = parse_date(args.since)
    database = Path(args.database)
    database.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    candidate_count = 0

    with sqlite3.connect(database) as conn:
        configure_database(conn)
        refresh_matched_trades(conn, trades, observed)
        for pair in pairs:
            try:
                payload = client.get(
                    "/api/v1/pair_candles",
                    {"pair": pair, "timeframe": "1h", "limit": args.limit},
                )
                timeframe_minutes = max(1, int(payload.get("timeframe_ms", 3600000)) // 60000)
                for row in latest_signals(payload):
                    signal_date = parse_date(row.get("date"))
                    if signal_date is None:
                        continue
                    expected_entry = signal_date + timedelta(minutes=timeframe_minutes)
                    if since is not None and expected_entry < since:
                        continue
                    row["pair"] = pair
                    upsert_candidate(
                        conn,
                        observed,
                        strategy,
                        max_open_trades,
                        trades,
                        row,
                        timeframe_minutes,
                    )
                    candidate_count += 1
            except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
                errors.append(f"{pair}: {exc}")
        conn.execute(
            "INSERT OR REPLACE INTO collector_runs VALUES (?, ?, ?, ?, ?, ?)",
            (observed, strategy, len(pairs), candidate_count, len(errors), json.dumps(errors)),
        )
        conn.commit()
    return candidate_count, len(errors)


def print_summary(database: Path) -> None:
    if not database.exists():
        print(f"No shadow database yet: {database}")
        return
    with sqlite3.connect(database) as conn:
        configure_database(conn)
        total = conn.execute("SELECT COUNT(*) FROM signal_candidates").fetchone()[0]
        rows = conn.execute(
            """
            SELECT classification, COUNT(*),
                   SUM(CASE WHEN side='long' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN side='short' THEN 1 ELSE 0 END)
            FROM signal_candidates GROUP BY classification ORDER BY classification
            """
        ).fetchall()
        latest = conn.execute(
            "SELECT observed_at, candidate_count, error_count FROM collector_runs ORDER BY observed_at DESC LIMIT 1"
        ).fetchone()
    print(f"Shadow candidates: {total}")
    for classification, count, longs, shorts in rows:
        print(f"  {classification}: {count} (long {longs}, short {shorts})")
    if latest:
        print(f"Last collection: {latest[0]}, scanned signals {latest[1]}, errors {latest[2]}")


def main() -> int:
    args = parse_args()
    database = Path(args.database)
    if args.summary and not args.watch:
        print_summary(database)
        return 0

    while True:
        try:
            candidates, errors = collect_once(args)
            print(
                f"{iso(datetime.now(timezone.utc))} collected {candidates} candidate rows, {errors} errors",
                flush=True,
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
            print(f"collector error: {exc}", file=sys.stderr, flush=True)
            if not args.watch:
                return 1
        if not args.watch:
            print_summary(database)
            return 0
        time.sleep(max(30, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
