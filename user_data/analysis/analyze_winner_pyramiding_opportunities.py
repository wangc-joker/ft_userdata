from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

sys.path.insert(0, "/freqtrade/user_data")
sys.path.insert(0, "/freqtrade/user_data/strategies")

from DualTrendCompressionRestartShortV1Strategy import (
    DualTrendCompressionRestartShortV1Strategy,
)


ROOT = Path("/freqtrade/user_data")
DATA_DIR = ROOT / "data" / "binance" / "futures"
BACKTEST_ZIP_JSON = (
    ROOT
    / "backtest_results"
    / "inspect_031432"
    / "backtest-result-2026-07-07_03-14-32.json"
)
OUT_CSV = ROOT / "analysis" / "winner_pyramiding_opportunities.csv"
OUT_SUMMARY = ROOT / "reports" / "winner_pyramiding_opportunities_2026-07-07.md"


PAIRLIST = [
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


def pair_to_filename(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def load_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    path = DATA_DIR / f"{pair_to_filename(pair)}-{timeframe}-futures.feather"
    df = pd.read_feather(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


@dataclass
class DummyDP:
    pair_frames: dict[tuple[str, str], pd.DataFrame]

    def get_pair_dataframe(self, pair: str, timeframe: str) -> pd.DataFrame:
        df = self.pair_frames.get((pair, timeframe))
        if df is None:
            return pd.DataFrame()
        return df.copy()


def build_signal_frames() -> dict[str, pd.DataFrame]:
    strat = DualTrendCompressionRestartShortV1Strategy(
        config={
            "candle_type_def": "futures",
            "trading_mode": "futures",
            "margin_mode": "isolated",
            "stake_currency": "USDT",
            "dry_run": True,
        }
    )
    strat.dp = DummyDP({})

    pair_frames: dict[tuple[str, str], pd.DataFrame] = {}
    btc_4h = load_ohlcv("BTC/USDT:USDT", "4h")
    pair_frames[("BTC/USDT:USDT", "4h")] = btc_4h

    strat.dp = DummyDP(pair_frames)

    results: dict[str, pd.DataFrame] = {}
    for pair in PAIRLIST:
        base_1h = load_ohlcv(pair, "1h")
        inf_4h = load_ohlcv(pair, "4h")
        inf_4h = strat.populate_indicators_4h(inf_4h.copy(), {"pair": pair})
        pair_frames[(pair, "4h")] = inf_4h
    strat.dp = DummyDP(pair_frames)

    for pair in PAIRLIST:
        base_1h = load_ohlcv(pair, "1h")
        df = strat.populate_indicators(base_1h.copy(), {"pair": pair})
        if (pair, "4h") in pair_frames:
            inf_4h = pair_frames[(pair, "4h")][["date", "trend_up", "trend_down", "ema50"]].copy()
            inf_4h = inf_4h.rename(
                columns={
                    "trend_up": "trend_up_4h",
                    "trend_down": "trend_down_4h",
                    "ema50": "ema50_4h",
                }
            )
            df = pd.merge_asof(
                df.sort_values("date"),
                inf_4h.sort_values("date"),
                on="date",
                direction="backward",
            )
        df = strat.populate_entry_trend(df, {"pair": pair})
        results[pair] = df.reset_index(drop=True)
    return results


def short_profit(open_rate: float, price: float) -> float:
    return (open_rate - price) / open_rate


def main() -> None:
    data = json.loads(BACKTEST_ZIP_JSON.read_text(encoding="utf-8"))
    strat_name = next(iter(data["strategy"]))
    trades = pd.DataFrame(data["strategy"][strat_name]["trades"])
    trades["open_date"] = pd.to_datetime(trades["open_date"], utc=True)
    trades["close_date"] = pd.to_datetime(trades["close_date"], utc=True)

    signal_frames = build_signal_frames()

    rows: list[dict] = []
    for _, trade in trades.iterrows():
        if trade["enter_tag"] != "short_pullback_restart":
            continue
        if not bool(trade["is_short"]):
            continue

        pair = trade["pair"]
        df = signal_frames.get(pair)
        if df is None or df.empty:
            continue

        open_time = trade["open_date"]
        close_time = trade["close_date"]
        in_trade = df[(df["date"] > open_time) & (df["date"] <= close_time)].copy()
        if in_trade.empty:
            rows.append(
                {
                    "pair": pair,
                    "open_date": open_time,
                    "close_date": close_time,
                    "profit_ratio_final": trade["profit_ratio"],
                    "max_profit_ratio": short_profit(float(trade["open_rate"]), float(trade["min_rate"])),
                    "bars_in_trade": 0,
                    "profitable_bars": 0,
                    "same_tag_signal_bars": 0,
                    "profitable_same_tag_signal_bars": 0,
                    "first_profitable_same_tag_profit": None,
                    "max_profitable_same_tag_profit": None,
                }
            )
            continue

        in_trade["current_profit"] = in_trade["close"].apply(lambda x: short_profit(float(trade["open_rate"]), float(x)))
        same_tag = (in_trade.get("enter_short", 0) == 1) & (in_trade.get("enter_tag", "") == "short_pullback_restart")
        profitable = in_trade["current_profit"] >= 0.0
        profitable_same_tag = same_tag & profitable

        first_profit = None
        max_profit = None
        if profitable_same_tag.any():
            first_profit = float(in_trade.loc[profitable_same_tag, "current_profit"].iloc[0])
            max_profit = float(in_trade.loc[profitable_same_tag, "current_profit"].max())

        rows.append(
            {
                "pair": pair,
                "open_date": open_time,
                "close_date": close_time,
                "profit_ratio_final": float(trade["profit_ratio"]),
                "max_profit_ratio": short_profit(float(trade["open_rate"]), float(trade["min_rate"])),
                "bars_in_trade": int(len(in_trade)),
                "profitable_bars": int(profitable.sum()),
                "same_tag_signal_bars": int(same_tag.sum()),
                "profitable_same_tag_signal_bars": int(profitable_same_tag.sum()),
                "first_profitable_same_tag_profit": first_profit,
                "max_profitable_same_tag_profit": max_profit,
            }
        )

    result = pd.DataFrame(rows)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    total = len(result)
    with_signal = int((result["same_tag_signal_bars"] > 0).sum()) if total else 0
    with_profitable_signal = int((result["profitable_same_tag_signal_bars"] > 0).sum()) if total else 0
    avg_profitable_signal_bars = float(result["profitable_same_tag_signal_bars"].mean()) if total else 0.0
    avg_first_profit = (
        float(result["first_profitable_same_tag_profit"].dropna().mean())
        if total and result["first_profitable_same_tag_profit"].notna().any()
        else None
    )
    avg_max_profit = (
        float(result["max_profitable_same_tag_profit"].dropna().mean())
        if total and result["max_profitable_same_tag_profit"].notna().any()
        else None
    )

    summary = [
        "# 盈利单再次同向信号诊断",
        "",
        f"- 样本交易数: {total}",
        f"- 持仓期间出现过同 `short_pullback_restart` 信号的交易数: {with_signal}",
        f"- 持仓盈利期间出现过同 `short_pullback_restart` 信号的交易数: {with_profitable_signal}",
        f"- 平均盈利同信号 K 线数量: {avg_profitable_signal_bars:.2f}",
        f"- 首次出现盈利同信号时平均利润: {avg_first_profit:.4f}" if avg_first_profit is not None else "- 首次出现盈利同信号时平均利润: N/A",
        f"- 盈利同信号最大利润均值: {avg_max_profit:.4f}" if avg_max_profit is not None else "- 盈利同信号最大利润均值: N/A",
        "",
        "输出明细:",
        f"- `{OUT_CSV}`",
    ]
    OUT_SUMMARY.write_text("\n".join(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
