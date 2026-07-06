from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
USER_DATA = HERE.parents[1]
ROOT = USER_DATA.parent
BACKTEST_ZIP = USER_DATA / "backtest_results" / "backtest-result-2026-06-30_03-24-30.zip"
STRATEGY_NAME = "DualTrendCombinedShortPullbackShapeV1Strategy"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
OUT_CSV = USER_DATA / "analysis" / "positive13_reach5_diagnosis.csv"
OUT_MD = USER_DATA / "reports" / "positive13_reach5_diagnosis.md"


@dataclass
class CandleCache:
    candles_5m: dict[str, pd.DataFrame]
    candles_1h: dict[str, pd.DataFrame]


def pair_to_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def load_trades() -> list[dict]:
    with zipfile.ZipFile(BACKTEST_ZIP) as zf:
        data = json.loads(zf.read(BACKTEST_ZIP.stem + ".json"))
    return data["strategy"][STRATEGY_NAME]["trades"]


def load_candles(pair: str, timeframe: str, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    key = f"{pair}|{timeframe}"
    if key in cache:
        return cache[key]
    path = DATA_DIR / f"{pair_to_stem(pair)}-{timeframe}-futures.feather"
    df = pd.read_feather(path)
    if "date" not in df.columns:
        raise ValueError(f"Missing date column in {path}")
    df["date"] = pd.to_datetime(df["date"], utc=True)
    cache[key] = df.sort_values("date").reset_index(drop=True)
    return cache[key]


def profit_from_price(open_rate: float, price: float, is_short: bool) -> float:
    if is_short:
        return (open_rate - price) / open_rate
    return (price - open_rate) / open_rate


def profit_extreme(df: pd.DataFrame, open_rate: float, is_short: bool) -> pd.Series:
    if is_short:
        return (open_rate - df["low"]) / open_rate
    return (df["high"] - open_rate) / open_rate


def profit_close(df: pd.DataFrame, open_rate: float, is_short: bool) -> pd.Series:
    if is_short:
        return (open_rate - df["close"]) / open_rate
    return (df["close"] - open_rate) / open_rate


def adverse_extreme(df: pd.DataFrame, open_rate: float, is_short: bool) -> pd.Series:
    if is_short:
        return (df["high"] - open_rate) / open_rate
    return (open_rate - df["low"]) / open_rate


def rolling_features(df_5m: pd.DataFrame, idx: int) -> dict[str, float | bool]:
    node = df_5m.iloc[idx]
    closes = df_5m["close"]
    ema20 = closes.ewm(span=20, adjust=False).mean().iloc[idx]
    ema50 = closes.ewm(span=50, adjust=False).mean().iloc[idx]
    start_1h = max(0, idx - 12)
    start_3h = max(0, idx - 36)
    start_6h = max(0, idx - 72)
    close_now = float(node["close"])
    ret_1h = close_now / float(closes.iloc[start_1h]) - 1.0 if idx > start_1h else 0.0
    ret_3h = close_now / float(closes.iloc[start_3h]) - 1.0 if idx > start_3h else 0.0
    ret_6h = close_now / float(closes.iloc[start_6h]) - 1.0 if idx > start_6h else 0.0
    recent = closes.iloc[max(0, idx - 12): idx + 1].pct_change().dropna()
    vol_1h = float(recent.std()) if not recent.empty else 0.0
    close_vs_ema20 = close_now / float(ema20) - 1.0 if ema20 else 0.0
    close_vs_ema50 = close_now / float(ema50) - 1.0 if ema50 else 0.0
    trend_up = close_now > ema20 > ema50
    trend_down = close_now < ema20 < ema50
    candle_range = max(float(node["high"]) - float(node["low"]), 1e-12)
    body_ratio = abs(float(node["close"]) - float(node["open"])) / candle_range
    close_position = (float(node["close"]) - float(node["low"])) / candle_range
    return {
        "node_ret_1h": ret_1h,
        "node_ret_3h": ret_3h,
        "node_ret_6h": ret_6h,
        "node_vol_1h": vol_1h,
        "node_close_vs_ema20": close_vs_ema20,
        "node_close_vs_ema50": close_vs_ema50,
        "node_trend_up": trend_up,
        "node_trend_down": trend_down,
        "node_body_ratio": body_ratio,
        "node_close_position": close_position,
    }


def classify_trade(final_profit: float, future_mfe: float) -> str:
    if future_mfe >= 0.10:
        return "reach10plus"
    if final_profit >= 0.05:
        return "exit_5_to_10"
    if final_profit >= 0.02:
        return "giveback_to_2_5"
    if final_profit >= 0:
        return "giveback_to_0_2"
    return "giveback_below_0"


def analyze() -> pd.DataFrame:
    trades = load_trades()
    cache = CandleCache(candles_5m={}, candles_1h={})
    rows: list[dict] = []
    for trade in trades:
        open_ts = pd.Timestamp(trade["open_date"], tz="UTC")
        close_ts = pd.Timestamp(trade["close_date"], tz="UTC")
        open_rate = float(trade["open_rate"])
        is_short = bool(trade["is_short"])
        candles_5m = load_candles(trade["pair"], "5m", cache.candles_5m)
        window = candles_5m[(candles_5m["date"] >= open_ts) & (candles_5m["date"] <= close_ts)].reset_index(drop=True)
        if window.empty:
            continue
        extreme_profit = profit_extreme(window, open_rate, is_short)
        overall_mfe = float(extreme_profit.max())
        if overall_mfe < 0.05:
            continue
        first5_idx = int(extreme_profit.ge(0.05).idxmax())
        node_time = pd.Timestamp(window.iloc[first5_idx]["date"])
        after_5 = window.iloc[first5_idx:].reset_index(drop=True)
        future_extreme = profit_extreme(after_5, open_rate, is_short)
        future_close_profit = profit_close(after_5, open_rate, is_short)
        future_mfe = float(future_extreme.max())
        future_mae_after5 = float(adverse_extreme(after_5, open_rate, is_short).max())
        min_close_profit_after5 = float(future_close_profit.min())
        node_close_profit = float(profit_from_price(open_rate, float(window.iloc[first5_idx]["close"]), is_short))
        before_5 = window.iloc[: first5_idx + 1]
        adverse_before5 = float(adverse_extreme(before_5, open_rate, is_short).max())
        bars_to_5 = first5_idx + 1
        hours_to_5 = bars_to_5 * 5 / 60.0
        node_feats = rolling_features(window, first5_idx)
        category = classify_trade(float(trade["profit_ratio"]), future_mfe)
        rows.append(
            {
                "pair": trade["pair"],
                "enter_tag": trade.get("enter_tag", ""),
                "is_short": is_short,
                "open_date": trade["open_date"],
                "close_date": trade["close_date"],
                "hours_to_5pct": hours_to_5,
                "bars_to_5pct": bars_to_5,
                "node_time": node_time.isoformat(),
                "node_close_profit": node_close_profit,
                "overall_mfe": overall_mfe,
                "future_mfe_after_5pct": future_mfe,
                "future_close_min_profit_after_5pct": min_close_profit_after5,
                "future_adverse_after_5pct": future_mae_after5,
                "adverse_before_5pct": adverse_before5,
                "final_profit": float(trade["profit_ratio"]),
                "exit_reason": trade["exit_reason"],
                "category": category,
                **node_feats,
            }
        )
    return pd.DataFrame(rows)


def fmt_pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def build_report(df: pd.DataFrame) -> str:
    total = len(df)
    counts = df["category"].value_counts().to_dict()
    reached10 = counts.get("reach10plus", 0)
    lines: list[str] = []
    lines.append("# Positive13 Baseline 5% 节点诊断")
    lines.append("")
    lines.append("基线策略：`DualTrendCombinedShortPullbackShapeV1Strategy`")
    lines.append("")
    lines.append("区间：`2023-06-18 -> 2026-05-08`，使用 `1h + 5m detail` 回测结果逐笔诊断。")
    lines.append("")
    lines.append("## 样本概览")
    lines.append("")
    lines.append(f"- 全部 baseline 交易：280")
    lines.append(f"- 至少到过 `+5%` 的交易：{total}")
    lines.append(f"- 到过 `+5%` 后最终还能到 `+10%+`：{reached10} ({reached10 / total:.1%})")
    lines.append("")
    lines.append("| 分类 | 数量 | 占到过5%样本 |")
    lines.append("|---|---:|---:|")
    for key in ["reach10plus", "exit_5_to_10", "giveback_to_2_5", "giveback_to_0_2", "giveback_below_0"]:
        value = counts.get(key, 0)
        lines.append(f"| {key} | {value} | {value / total:.1%} |")
    lines.append("")
    lines.append("## 各组均值")
    lines.append("")
    summary = (
        df.groupby("category")[
            [
                "hours_to_5pct",
                "adverse_before_5pct",
                "node_close_profit",
                "future_mfe_after_5pct",
                "future_close_min_profit_after_5pct",
                "final_profit",
                "node_ret_1h",
                "node_ret_3h",
                "node_close_vs_ema20",
                "node_close_vs_ema50",
            ]
        ]
        .mean()
        .sort_index()
    )
    lines.append("| 分类 | 到5%耗时(h) | 5%前不利波动 | 5%节点收盘利润 | 5%后最高利润 | 5%后最低收盘利润 | 最终利润 | 节点前1h收益 | 节点前3h收益 | 节点相对EMA20 | 节点相对EMA50 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for category, row in summary.iterrows():
        lines.append(
            "| "
            + category
            + " | "
            + f"{row['hours_to_5pct']:.2f}"
            + " | "
            + fmt_pct(row["adverse_before_5pct"])
            + " | "
            + fmt_pct(row["node_close_profit"])
            + " | "
            + fmt_pct(row["future_mfe_after_5pct"])
            + " | "
            + fmt_pct(row["future_close_min_profit_after_5pct"])
            + " | "
            + fmt_pct(row["final_profit"])
            + " | "
            + fmt_pct(row["node_ret_1h"])
            + " | "
            + fmt_pct(row["node_ret_3h"])
            + " | "
            + fmt_pct(row["node_close_vs_ema20"])
            + " | "
            + fmt_pct(row["node_close_vs_ema50"])
            + " |"
        )
    lines.append("")
    lines.append("## Tag 拆解")
    lines.append("")
    tag_counts = pd.crosstab(df["enter_tag"], df["category"])
    tag_counts["total_reach5"] = tag_counts.sum(axis=1)
    if "reach10plus" not in tag_counts.columns:
        tag_counts["reach10plus"] = 0
    tag_counts["reach10_rate"] = tag_counts["reach10plus"] / tag_counts["total_reach5"]
    lines.append("| enter_tag | 到过5%样本 | 其中到10%+ | 到10%+比例 |")
    lines.append("|---|---:|---:|---:|")
    for tag, row in tag_counts.sort_values("reach10_rate", ascending=False).iterrows():
        lines.append(
            f"| {tag} | {int(row['total_reach5'])} | {int(row['reach10plus'])} | {row['reach10_rate']:.1%} |"
        )
    lines.append("")
    strong = df[
        (df["hours_to_5pct"] <= df["hours_to_5pct"].median())
        & (df["adverse_before_5pct"] <= df["adverse_before_5pct"].median())
    ]
    if not strong.empty:
        strong10 = (strong["category"] == "reach10plus").mean()
        overall10 = (df["category"] == "reach10plus").mean()
        lines.append("## 一个简单的“强单”候选条件")
        lines.append("")
        lines.append("候选条件：")
        lines.append("")
        lines.append(
            f"- 到 `+5%` 的速度不慢：`hours_to_5pct <= {df['hours_to_5pct'].median():.2f}h`"
        )
        lines.append(
            f"- 达到 `+5%` 之前的不利波动不大：`adverse_before_5pct <= {fmt_pct(df['adverse_before_5pct'].median())}`"
        )
        lines.append("")
        lines.append(f"- 全体到10%+比例：`{overall10:.1%}`")
        lines.append(f"- 满足候选条件后的到10%+比例：`{strong10:.1%}`")
        lines.append("")
        lines.append("这不是实盘可直接照抄的最终规则，但能帮助我们做下一步“5%全平 / 5%平半”的条件分流测试。")
    return "\n".join(lines)


def main() -> None:
    df = analyze().sort_values(["open_date", "pair"]).reset_index(drop=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    report = build_report(df)
    OUT_MD.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
