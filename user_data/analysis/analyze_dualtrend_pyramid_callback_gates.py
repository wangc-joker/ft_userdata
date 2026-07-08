from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/freqtrade/user_data")
sys.path.insert(0, "/freqtrade/user_data/strategies")

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


ROOT = Path("/freqtrade/user_data")
DATA_DIR = ROOT / "data" / "binance" / "futures"
BACKTEST_JSON = (
    ROOT
    / "backtest_results"
    / "inspect_031432"
    / "backtest-result-2026-07-07_03-14-32.json"
)
OUT_CSV = ROOT / "analysis" / "dualtrend_pyramid_callback_gates.csv"
OUT_MD = ROOT / "reports" / "dualtrend_pyramid_callback_gates_2026-07-07.md"

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


class DummyDP:
    def __init__(self, pair_frames: dict[tuple[str, str], pd.DataFrame]):
        self.pair_frames = pair_frames

    def get_pair_dataframe(self, pair: str, timeframe: str) -> pd.DataFrame:
        return self.pair_frames.get((pair, timeframe), pd.DataFrame()).copy()


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

    pair_frames: dict[tuple[str, str], pd.DataFrame] = {}
    btc_4h = load_ohlcv("BTC/USDT:USDT", "4h")
    pair_frames[("BTC/USDT:USDT", "4h")] = btc_4h
    strat.dp = DummyDP(pair_frames)

    for pair in PAIRLIST:
        inf_4h = load_ohlcv(pair, "4h")
        inf_4h = strat.populate_indicators_4h(inf_4h.copy(), {"pair": pair})
        pair_frames[(pair, "4h")] = inf_4h
    strat.dp = DummyDP(pair_frames)

    results: dict[str, pd.DataFrame] = {}
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
    signal_frames = build_signal_frames()
    data = json.loads(BACKTEST_JSON.read_text(encoding="utf-8"))
    strat_name = next(iter(data["strategy"]))
    trades = pd.DataFrame(data["strategy"][strat_name]["trades"])
    trades["open_date"] = pd.to_datetime(trades["open_date"], utc=True)
    trades["close_date"] = pd.to_datetime(trades["close_date"], utc=True)

    rows: list[dict] = []
    for _, trade in trades.iterrows():
        if trade["enter_tag"] != "short_pullback_restart" or not bool(trade["is_short"]):
            continue

        pair = trade["pair"]
        df = signal_frames[pair]
        in_trade = df[(df["date"] > trade["open_date"]) & (df["date"] <= trade["close_date"])].copy()

        if in_trade.empty:
            rows.append(
                {
                    "pair": pair,
                    "open_date": trade["open_date"],
                    "close_date": trade["close_date"],
                    "bars": 0,
                    "profit_positive_bars": 0,
                    "profit_in_cap_bars": 0,
                    "probe_signal_bars": 0,
                    "profit_and_probe_bars": 0,
                    "profit_and_tag_bars": 0,
                    "profit_and_probe_first": None,
                    "profit_and_probe_max": None,
                }
            )
            continue

        in_trade["current_profit"] = in_trade["close"].apply(lambda x: short_profit(float(trade["open_rate"]), float(x)))
        profit_positive = in_trade["current_profit"] >= 0.0001
        profit_in_cap = profit_positive & (in_trade["current_profit"] <= 0.03)
        probe_signal = in_trade["short_reinforce_probe"].fillna(False)
        tag_signal = (in_trade.get("enter_short", 0) == 1) & (in_trade.get("enter_tag", "") == "short_pullback_restart")
        profit_and_probe = profit_in_cap & probe_signal
        profit_and_tag = profit_in_cap & tag_signal

        first_probe = None
        max_probe = None
        if profit_and_probe.any():
            first_probe = float(in_trade.loc[profit_and_probe, "current_profit"].iloc[0])
            max_probe = float(in_trade.loc[profit_and_probe, "current_profit"].max())

        rows.append(
            {
                "pair": pair,
                "open_date": trade["open_date"],
                "close_date": trade["close_date"],
                "bars": int(len(in_trade)),
                "profit_positive_bars": int(profit_positive.sum()),
                "profit_in_cap_bars": int(profit_in_cap.sum()),
                "probe_signal_bars": int(probe_signal.sum()),
                "profit_and_probe_bars": int(profit_and_probe.sum()),
                "profit_and_tag_bars": int(profit_and_tag.sum()),
                "profit_and_probe_first": first_probe,
                "profit_and_probe_max": max_probe,
                "final_profit": float(trade["profit_ratio"]),
                "max_profit": short_profit(float(trade["open_rate"]), float(trade["min_rate"])),
            }
        )

    result = pd.DataFrame(rows)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    total = len(result)
    trades_with_profit = int((result["profit_positive_bars"] > 0).sum()) if total else 0
    trades_with_probe = int((result["probe_signal_bars"] > 0).sum()) if total else 0
    trades_with_profit_and_probe = int((result["profit_and_probe_bars"] > 0).sum()) if total else 0
    trades_with_profit_and_tag = int((result["profit_and_tag_bars"] > 0).sum()) if total else 0

    lines = [
        "# DualTrend 加仓回调门槛诊断",
        "",
        f"- 样本 short_pullback_restart 交易数: {total}",
        f"- 持仓期间出现盈利 bar 的交易数: {trades_with_profit}",
        f"- 持仓期间出现结构强化 probe 的交易数: {trades_with_probe}",
        f"- 持仓期间同时满足 `盈利 + probe强化` 的交易数: {trades_with_profit_and_probe}",
        f"- 持仓期间同时满足 `盈利 + 原tag再次信号` 的交易数: {trades_with_profit_and_tag}",
        "",
        f"- 明细: `{OUT_CSV}`",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
