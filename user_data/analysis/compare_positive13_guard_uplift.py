from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
USER_DATA = HERE.parents[1]
BACKTEST_DIR = USER_DATA / "backtest_results"
OUT_CSV = USER_DATA / "analysis" / "positive13_guard_uplift_pair_tag.csv"
OUT_MD = USER_DATA / "reports" / "positive13_guard_uplift_diagnosis.md"


BASELINE = "DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy"
GUARD = "DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy"

RUNS = {
    "3y": {
        "baseline_zip": BACKTEST_DIR / "backtest-result-2026-06-30_08-20-58.zip",
        "guard_zip": BACKTEST_DIR / "backtest-result-2026-07-01_02-56-53.zip",
    },
    "1y": {
        "baseline_zip": BACKTEST_DIR / "backtest-result-2026-06-30_08-35-00.zip",
        "guard_zip": BACKTEST_DIR / "backtest-result-2026-07-01_03-06-45.zip",
    },
    "pressure": {
        "baseline_zip": BACKTEST_DIR / "backtest-result-2026-06-30_08-37-22.zip",
        "guard_zip": BACKTEST_DIR / "backtest-result-2026-07-01_03-05-09.zip",
    },
}


def load_trades(zip_path: Path, strategy_name: str) -> list[dict]:
    with zipfile.ZipFile(zip_path) as zf:
        payload = json.loads(zf.read(zip_path.stem + ".json"))
    return payload["strategy"][strategy_name]["trades"]


def summarize(trades: list[dict], group_col: str) -> pd.DataFrame:
    df = pd.DataFrame(trades)
    if df.empty:
        return pd.DataFrame(columns=[group_col, "trades", "profit_pct", "profit_abs", "avg_profit_pct", "winrate"])
    grouped = (
        df.groupby(group_col)
        .agg(
            trades=("profit_ratio", "size"),
            profit_pct=("profit_ratio", "sum"),
            profit_abs=("profit_abs", "sum"),
            avg_profit_pct=("profit_ratio", "mean"),
            winrate=("profit_ratio", lambda s: (s > 0).mean()),
        )
        .reset_index()
    )
    return grouped


def join_diff(base: pd.DataFrame, guard: pd.DataFrame, key: str, period: str, level: str) -> pd.DataFrame:
    merged = base.merge(guard, on=key, how="outer", suffixes=("_base", "_guard")).fillna(0)
    merged["period"] = period
    merged["level"] = level
    merged["trades_diff"] = merged["trades_guard"] - merged["trades_base"]
    merged["profit_pct_diff"] = merged["profit_pct_guard"] - merged["profit_pct_base"]
    merged["profit_abs_diff"] = merged["profit_abs_guard"] - merged["profit_abs_base"]
    merged["avg_profit_pct_diff"] = merged["avg_profit_pct_guard"] - merged["avg_profit_pct_base"]
    merged["winrate_diff"] = merged["winrate_guard"] - merged["winrate_base"]
    return merged


def fmt_pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def fmt_pp(v: float) -> str:
    return f"{v:.2f}pp"


def build_period_summary(period: str, baseline_trades: list[dict], guard_trades: list[dict]) -> dict[str, float]:
    b = pd.DataFrame(baseline_trades)
    g = pd.DataFrame(guard_trades)
    return {
        "period": period,
        "baseline_trades": len(b),
        "guard_trades": len(g),
        "baseline_profit_pct": b["profit_ratio"].sum() if not b.empty else 0.0,
        "guard_profit_pct": g["profit_ratio"].sum() if not g.empty else 0.0,
        "baseline_winrate": (b["profit_ratio"] > 0).mean() if not b.empty else 0.0,
        "guard_winrate": (g["profit_ratio"] > 0).mean() if not g.empty else 0.0,
    }


def main() -> None:
    all_rows: list[pd.DataFrame] = []
    period_summaries: list[dict[str, float]] = []
    for period, paths in RUNS.items():
        base_trades = load_trades(paths["baseline_zip"], BASELINE)
        guard_trades = load_trades(paths["guard_zip"], GUARD)
        period_summaries.append(build_period_summary(period, base_trades, guard_trades))

        for key, level in [("pair", "pair"), ("enter_tag", "tag")]:
            base_summary = summarize(base_trades, key)
            guard_summary = summarize(guard_trades, key)
            all_rows.append(join_diff(base_summary, guard_summary, key, period, level))

    result = pd.concat(all_rows, ignore_index=True)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    lines: list[str] = []
    lines.append("# Positive13 Guard Uplift Diagnosis")
    lines.append("")
    lines.append("对比：")
    lines.append("")
    lines.append(f"- Baseline: `{BASELINE}`")
    lines.append(f"- New candidate: `{GUARD}`")
    lines.append("")
    lines.append("目标：回答这次 `CompressionFlushGuard` 的提升，主要来自哪些 pair / 哪些 tag。")
    lines.append("")
    lines.append("## 总览")
    lines.append("")
    lines.append("| period | baseline trades | guard trades | baseline profit | guard profit | profit diff | baseline winrate | guard winrate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for row in period_summaries:
        lines.append(
            f"| {row['period']} | {int(row['baseline_trades'])} | {int(row['guard_trades'])} | "
            f"{fmt_pct(row['baseline_profit_pct'])} | {fmt_pct(row['guard_profit_pct'])} | "
            f"{fmt_pct(row['guard_profit_pct'] - row['baseline_profit_pct'])} | "
            f"{row['baseline_winrate']:.1%} | {row['guard_winrate']:.1%} |"
        )
    lines.append("")

    for period in ["3y", "1y", "pressure"]:
        lines.append(f"## {period}")
        lines.append("")
        pair_rows = result[(result["period"] == period) & (result["level"] == "pair")].copy()
        tag_rows = result[(result["period"] == period) & (result["level"] == "tag")].copy()

        lines.append("### Pair uplift")
        lines.append("")
        lines.append("| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for _, row in pair_rows.sort_values("profit_pct_diff", ascending=False).head(8).iterrows():
            label = row["pair"] if row["pair"] else "(blank)"
            lines.append(
                f"| {label} | {fmt_pct(row['profit_pct_base'])} | {fmt_pct(row['profit_pct_guard'])} | "
                f"{fmt_pct(row['profit_pct_diff'])} | {int(row['trades_base'])} | {int(row['trades_guard'])} | {int(row['trades_diff'])} |"
            )
        lines.append("")
        lines.append("### Pair drag")
        lines.append("")
        lines.append("| pair | base profit | guard profit | diff | base trades | guard trades | trade diff |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for _, row in pair_rows.sort_values("profit_pct_diff", ascending=True).head(6).iterrows():
            label = row["pair"] if row["pair"] else "(blank)"
            lines.append(
                f"| {label} | {fmt_pct(row['profit_pct_base'])} | {fmt_pct(row['profit_pct_guard'])} | "
                f"{fmt_pct(row['profit_pct_diff'])} | {int(row['trades_base'])} | {int(row['trades_guard'])} | {int(row['trades_diff'])} |"
            )
        lines.append("")
        lines.append("### Tag uplift")
        lines.append("")
        lines.append("| tag | base profit | guard profit | diff | base trades | guard trades | trade diff |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for _, row in tag_rows.sort_values("profit_pct_diff", ascending=False).iterrows():
            label = row["enter_tag"] if row["enter_tag"] else "(blank)"
            lines.append(
                f"| {label} | {fmt_pct(row['profit_pct_base'])} | {fmt_pct(row['profit_pct_guard'])} | "
                f"{fmt_pct(row['profit_pct_diff'])} | {int(row['trades_base'])} | {int(row['trades_guard'])} | {int(row['trades_diff'])} |"
            )
        lines.append("")

        if period == "3y":
            top_pairs = pair_rows.sort_values("profit_pct_diff", ascending=False).head(3)["pair"].tolist()
            worst_pairs = pair_rows.sort_values("profit_pct_diff", ascending=True).head(3)["pair"].tolist()
            lines.append("结论：")
            lines.append("")
            lines.append(
                f"- 3y 的主要提升来源集中在 `{', '.join(top_pairs)}`。"
            )
            lines.append(
                f"- 主要拖累来自 `{', '.join(worst_pairs)}`，说明 guard 不是全域增益，而是集中改善了部分币种。"
            )
            lines.append("")
        if period == "1y":
            lines.append("结论：")
            lines.append("")
            lines.append(
                "- 1y 里，short_pullback_restart 仍然是主收益来源；compression guard 没有改变这条主线，但削弱了部分 flush 型坏单。"
            )
            lines.append("")
        if period == "pressure":
            lines.append("结论：")
            lines.append("")
            lines.append(
                "- 压力期里，guard 没有把策略推成更激进版本，而是基本维持了原主候选的防守能力。"
            )
            lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
