from __future__ import annotations

import json
import math
import zipfile
from itertools import combinations
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
USER_DATA = HERE.parents[1]
BACKTEST_DIR = USER_DATA / "backtest_results"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"

BACKTESTS = [
    ("Baseline", "backtest-result-2026-07-01_07-56-02.zip", "DualTrendBaselineStrategy"),
    ("Guard", "backtest-result-2026-07-01_07-56-03.zip", "DualTrendGuardStrategy"),
]

OUT_CSV = USER_DATA / "analysis" / "dualtrend_reach5_structure_first2y.csv"
OUT_RULE_CSV = USER_DATA / "analysis" / "dualtrend_reach5_structure_rules_first2y.csv"
OUT_MD = USER_DATA / "reports" / "dualtrend_reach5_structure_first2y_2026-07-01.md"


def pair_to_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def load_backtest_trades(zip_name: str, strategy_name: str) -> list[dict]:
    path = BACKTEST_DIR / zip_name
    with zipfile.ZipFile(path) as zf:
        json_name = [n for n in zf.namelist() if n.endswith(".json") and "meta" not in n][0]
        data = json.loads(zf.read(json_name))
    return data["strategy"][strategy_name]["trades"]


class CandleStore:
    def __init__(self) -> None:
        self.cache: dict[tuple[str, str], pd.DataFrame] = {}

    def load(self, pair: str, timeframe: str) -> pd.DataFrame:
        key = (pair, timeframe)
        if key in self.cache:
            return self.cache[key]
        path = DATA_DIR / f"{pair_to_stem(pair)}-{timeframe}-futures.feather"
        df = pd.read_feather(path)
        df["date"] = pd.to_datetime(df["date"], utc=True)
        df = df.sort_values("date").reset_index(drop=True)
        self.cache[key] = df
        return df


def profit_from_close(open_rate: float, close: float, is_short: bool) -> float:
    if is_short:
        return (open_rate - close) / open_rate
    return (close - open_rate) / open_rate


def profit_from_extreme(df: pd.DataFrame, open_rate: float, is_short: bool) -> pd.Series:
    if is_short:
        return (open_rate - df["low"]) / open_rate
    return (df["high"] - open_rate) / open_rate


def adverse_from_extreme(df: pd.DataFrame, open_rate: float, is_short: bool) -> pd.Series:
    if is_short:
        return (df["high"] - open_rate) / open_rate
    return (open_rate - df["low"]) / open_rate


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def slope_pct(series: pd.Series, lookback: int) -> pd.Series:
    prev = series.shift(lookback)
    return (series - prev) / prev


def add_1h_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["atr"] = (out["high"] - out["low"]).rolling(14, min_periods=14).mean()
    out["atr_pct"] = out["atr"] / out["close"]
    out["body_ratio"] = (out["close"] - out["open"]).abs() / (out["high"] - out["low"]).clip(lower=1e-12)
    out["close_position"] = (out["close"] - out["low"]) / (out["high"] - out["low"]).clip(lower=1e-12)
    out["ret_1h"] = out["close"].pct_change(1)
    out["ret_3h"] = out["close"].pct_change(3)
    out["ret_6h"] = out["close"].pct_change(6)
    out["ret_12h"] = out["close"].pct_change(12)
    out["ret_24h"] = out["close"].pct_change(24)
    out["recent_high_24h"] = out["high"].rolling(24, min_periods=12).max()
    out["recent_low_24h"] = out["low"].rolling(24, min_periods=12).min()
    out["range_width_24h"] = (out["recent_high_24h"] - out["recent_low_24h"]) / out["close"]
    out["range_position_24h"] = (out["close"] - out["recent_low_24h"]) / (
        out["recent_high_24h"] - out["recent_low_24h"]
    ).clip(lower=1e-12)
    out["legacy_market_center"] = ((out["high"] + out["low"] + out["close"]) / 3.0).rolling(5).mean()
    out["legacy_center_slope_3"] = out["legacy_market_center"] / out["legacy_market_center"].shift(3) - 1.0
    out["close_vs_center"] = out["close"] / out["legacy_market_center"] - 1.0
    return out


def add_4h_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["ema50_slope_3"] = slope_pct(out["ema50"], 3)
    out["ema50_slope_6"] = slope_pct(out["ema50"], 6)
    out["close_vs_ema50"] = out["close"] / out["ema50"] - 1.0
    out["close_vs_ema200"] = out["close"] / out["ema200"] - 1.0
    out["trend_down"] = (out["close"] < out["ema20"]) & (out["ema20"] < out["ema50"])
    out["trend_up"] = (out["close"] > out["ema20"]) & (out["ema20"] > out["ema50"])
    return out


def add_1d_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["ema50_slope_3"] = slope_pct(out["ema50"], 3)
    out["close_vs_ema50"] = out["close"] / out["ema50"] - 1.0
    out["legacy_market_center"] = ((out["high"] + out["low"] + out["close"]) / 3.0).rolling(5).mean()
    out["legacy_center_slope_3"] = out["legacy_market_center"] / out["legacy_market_center"].shift(3) - 1.0
    out["close_vs_center"] = out["close"] / out["legacy_market_center"] - 1.0
    return out


def last_row_before(df: pd.DataFrame, ts: pd.Timestamp) -> pd.Series | None:
    sliced = df[df["date"] <= ts]
    if sliced.empty:
        return None
    return sliced.iloc[-1]


def bool_int(value) -> int:
    return int(bool(value)) if pd.notna(value) else 0


def analyze_trades() -> pd.DataFrame:
    store = CandleStore()
    rows: list[dict] = []
    btc_1h = add_1h_features(store.load("BTC/USDT:USDT", "1h"))
    btc_4h = add_4h_features(store.load("BTC/USDT:USDT", "4h"))
    btc_1d = add_1d_features(store.load("BTC/USDT:USDT", "1d"))

    for label, zip_name, strategy_name in BACKTESTS:
        trades = load_backtest_trades(zip_name, strategy_name)
        for trade in trades:
            if trade.get("enter_tag") != "short_pullback_restart":
                continue
            if not bool(trade.get("is_short", False)):
                continue

            open_ts = pd.Timestamp(trade["open_date"], tz="UTC")
            close_ts = pd.Timestamp(trade["close_date"], tz="UTC")
            open_rate = float(trade["open_rate"])
            pair = trade["pair"]

            pair_5m = store.load(pair, "5m")
            pair_1h = add_1h_features(store.load(pair, "1h"))
            pair_4h = add_4h_features(store.load(pair, "4h"))
            pair_1d = add_1d_features(store.load(pair, "1d"))

            trade_5m = pair_5m[(pair_5m["date"] >= open_ts) & (pair_5m["date"] <= close_ts)].reset_index(drop=True)
            if trade_5m.empty:
                continue

            profit_path = profit_from_extreme(trade_5m, open_rate, True)
            overall_mfe = float(profit_path.max())
            if overall_mfe < 0.05:
                continue

            first5_idx = int(profit_path.ge(0.05).idxmax())
            node_5m = trade_5m.iloc[first5_idx]
            node_ts = pd.Timestamp(node_5m["date"])
            after_5m = trade_5m.iloc[first5_idx:].reset_index(drop=True)
            future_mfe = float(profit_from_extreme(after_5m, open_rate, True).max())
            future_close_min = float(((open_rate - after_5m["close"]) / open_rate).min())
            adverse_before_5 = float(adverse_from_extreme(trade_5m.iloc[: first5_idx + 1], open_rate, True).max())
            hours_to_5 = (first5_idx + 1) * 5 / 60.0
            node_close_profit = profit_from_close(open_rate, float(node_5m["close"]), True)
            target = int(future_mfe >= 0.10)

            p1 = last_row_before(pair_1h, node_ts)
            p4 = last_row_before(pair_4h, node_ts)
            p1d = last_row_before(pair_1d, node_ts)
            b1 = last_row_before(btc_1h, node_ts)
            b4 = last_row_before(btc_4h, node_ts)
            b1d = last_row_before(btc_1d, node_ts)
            if any(x is None for x in [p1, p4, p1d, b1, b4, b1d]):
                continue

            rows.append(
                {
                    "strategy_label": label,
                    "strategy_name": strategy_name,
                    "pair": pair,
                    "open_date": trade["open_date"],
                    "close_date": trade["close_date"],
                    "final_profit": float(trade["profit_ratio"]),
                    "profit_abs": float(trade["profit_abs"]),
                    "exit_reason": trade["exit_reason"],
                    "hours_to_5pct": hours_to_5,
                    "adverse_before_5pct": adverse_before_5,
                    "overall_mfe": overall_mfe,
                    "future_mfe_after_5pct": future_mfe,
                    "future_close_min_after_5pct": future_close_min,
                    "node_time": node_ts.isoformat(),
                    "node_close_profit": node_close_profit,
                    "target_reach10": target,
                    "pair_1h_body_ratio": float(p1["body_ratio"]),
                    "pair_1h_close_position": float(p1["close_position"]),
                    "pair_1h_ret_1h": float(p1["ret_1h"]),
                    "pair_1h_ret_3h": float(p1["ret_3h"]),
                    "pair_1h_ret_6h": float(p1["ret_6h"]),
                    "pair_1h_ret_12h": float(p1["ret_12h"]),
                    "pair_1h_ret_24h": float(p1["ret_24h"]),
                    "pair_1h_atr_pct": float(p1["atr_pct"]),
                    "pair_1h_close_vs_ema20": float(p1["close"] / p1["ema20"] - 1.0) if p1["ema20"] else math.nan,
                    "pair_1h_close_vs_ema50": float(p1["close"] / p1["ema50"] - 1.0) if p1["ema50"] else math.nan,
                    "pair_1h_close_vs_ema200": float(p1["close"] / p1["ema200"] - 1.0) if p1["ema200"] else math.nan,
                    "pair_1h_range_width_24h": float(p1["range_width_24h"]),
                    "pair_1h_range_position_24h": float(p1["range_position_24h"]),
                    "pair_1h_center_slope_3": float(p1["legacy_center_slope_3"]),
                    "pair_1h_close_vs_center": float(p1["close_vs_center"]),
                    "pair_4h_ema50_slope_3": float(p4["ema50_slope_3"]),
                    "pair_4h_ema50_slope_6": float(p4["ema50_slope_6"]),
                    "pair_4h_close_vs_ema50": float(p4["close_vs_ema50"]),
                    "pair_4h_close_vs_ema200": float(p4["close_vs_ema200"]),
                    "pair_4h_trend_down": bool_int(p4["trend_down"]),
                    "pair_4h_trend_up": bool_int(p4["trend_up"]),
                    "pair_1d_ema50_slope_3": float(p1d["ema50_slope_3"]),
                    "pair_1d_close_vs_ema50": float(p1d["close_vs_ema50"]),
                    "pair_1d_center_slope_3": float(p1d["legacy_center_slope_3"]),
                    "pair_1d_close_vs_center": float(p1d["close_vs_center"]),
                    "btc_1h_ret_6h": float(b1["ret_6h"]),
                    "btc_1h_ret_24h": float(b1["ret_24h"]),
                    "btc_4h_ema50_slope_3": float(b4["ema50_slope_3"]),
                    "btc_4h_close_vs_ema50": float(b4["close_vs_ema50"]),
                    "btc_4h_trend_down": bool_int(b4["trend_down"]),
                    "btc_4h_trend_up": bool_int(b4["trend_up"]),
                    "btc_1d_ema50_slope_3": float(b1d["ema50_slope_3"]),
                    "btc_1d_close_vs_ema50": float(b1d["close_vs_ema50"]),
                    "btc_1d_center_slope_3": float(b1d["legacy_center_slope_3"]),
                    "btc_1d_close_vs_center": float(b1d["close_vs_center"]),
                }
            )

    df = pd.DataFrame(rows)
    numeric_cols = [c for c in df.columns if c not in {"strategy_label", "strategy_name", "pair", "open_date", "close_date", "exit_reason", "node_time"}]
    for col in numeric_cols:
        if col not in {"pair_4h_trend_down", "pair_4h_trend_up", "btc_4h_trend_down", "btc_4h_trend_up", "target_reach10"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


RULE_FEATURES = {
    "adverse_before_5pct": ("le", [0.010, 0.012, 0.014, 0.016]),
    "hours_to_5pct": ("le", [16, 20, 24, 28, 32]),
    "pair_4h_ema50_slope_3": ("le", [-0.010, -0.0075, -0.005, -0.0025]),
    "pair_4h_close_vs_ema50": ("le", [-0.03, -0.02, -0.01, 0.0]),
    "pair_1h_ret_6h": ("le", [-0.02, -0.015, -0.01, -0.005]),
    "pair_1h_range_position_24h": ("le", [0.20, 0.30, 0.40, 0.50]),
    "btc_4h_trend_down": ("eq", [1]),
    "btc_1d_close_vs_ema50": ("le", [-0.03, -0.02, -0.01, 0.0]),
}


def apply_rule(df: pd.DataFrame, rule: list[tuple[str, str, float | int]]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for feature, op, threshold in rule:
        if op == "le":
            mask &= df[feature] <= threshold
        elif op == "ge":
            mask &= df[feature] >= threshold
        elif op == "eq":
            mask &= df[feature] == threshold
        else:
            raise ValueError(op)
    return mask


def rule_text(rule: list[tuple[str, str, float | int]]) -> str:
    symbol_map = {"le": "<=", "ge": ">=", "eq": "=="}
    return " AND ".join(f"{f} {symbol_map[o]} {v}" for f, o, v in rule)


def search_rules(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for strategy_label, scoped in df.groupby("strategy_label"):
        base_hit = scoped["target_reach10"].mean()
        base_avg = scoped["final_profit"].mean()
        single_rules: list[list[tuple[str, str, float | int]]] = []
        for feature, (op, thresholds) in RULE_FEATURES.items():
            for threshold in thresholds:
                single_rules.append([(feature, op, threshold)])
        rules = list(single_rules)
        for left, right in combinations(single_rules, 2):
            if left[0][0] == right[0][0]:
                continue
            rules.append(left + right)
        for rule in rules:
            mask = apply_rule(scoped, rule)
            selected = scoped[mask]
            rejected = scoped[~mask]
            if len(selected) < 8:
                continue
            coverage = len(selected) / len(scoped)
            if coverage < 0.15 or coverage > 0.75:
                continue
            hit_rate = selected["target_reach10"].mean()
            avg_final = selected["final_profit"].mean()
            proxy_full = (selected["final_profit"].sum() + len(rejected) * 0.05) / len(scoped)
            rows.append(
                {
                    "strategy_label": strategy_label,
                    "rule": rule_text(rule),
                    "terms": len(rule),
                    "selected": len(selected),
                    "coverage": coverage,
                    "hit_rate_reach10": hit_rate,
                    "lift_vs_base": hit_rate - base_hit,
                    "selected_avg_final_profit": avg_final,
                    "base_avg_final_profit": base_avg,
                    "proxy_full_profit_from_reach5": proxy_full,
                }
            )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["strategy_label", "proxy_full_profit_from_reach5", "hit_rate_reach10", "coverage"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)


def fmt_pct(v: float) -> str:
    return f"{v * 100:.2f}%"


SUMMARY_FEATURES = [
    "hours_to_5pct",
    "adverse_before_5pct",
    "pair_1h_ret_6h",
    "pair_1h_range_position_24h",
    "pair_4h_ema50_slope_3",
    "pair_4h_close_vs_ema50",
    "pair_1d_center_slope_3",
    "btc_4h_trend_down",
    "btc_1d_close_vs_ema50",
    "final_profit",
]


def build_report(df: pd.DataFrame, rules: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# DualTrend Reach5 结构诊断")
    lines.append("")
    lines.append("日期: 2026-07-01")
    lines.append("")
    lines.append("目的:")
    lines.append("")
    lines.append("- 只看 `short_pullback_restart`")
    lines.append("- 只看已经先走到 `+5%` 的空头单")
    lines.append("- 对比这些单在 `+5%` 节点时的结构差异，判断哪些更像应该继续放行到 `+10%+` 的真强单")
    lines.append("")
    lines.append("样本口径:")
    lines.append("")
    lines.append("- 配置: `D:\\test\\ft_userdata\\user_data\\config.backtest.dualtrend.combined.top30.max6.json`")
    lines.append("- 周期: `1h + 5m detail`")
    lines.append("- 区间: `2022-11-11 -> 2024-11-11`")
    lines.append("- 策略: `DualTrendBaselineStrategy`, `DualTrendGuardStrategy`")
    lines.append("")
    for strategy_label, scoped in df.groupby("strategy_label"):
        total = len(scoped)
        hit = int(scoped["target_reach10"].sum())
        miss = total - hit
        lines.append(f"## {strategy_label}")
        lines.append("")
        lines.append(f"- reach5 样本数: `{total}`")
        lines.append(f"- 最终还能到 `+10%+`: `{hit}` ({hit / total:.1%})")
        lines.append(f"- 到了 `+5%` 后没到 `+10%`: `{miss}` ({miss / total:.1%})")
        lines.append("")
        grp = scoped.groupby("target_reach10")[SUMMARY_FEATURES].mean()
        lines.append("| 分组 | 到5%耗时 | 5%前不利波动 | 前6h收益 | 24h区间位置 | 4H EMA50斜率 | 距4H EMA50 | 1D center slope | BTC 4H downtrend | BTC距1D EMA50 | 最终利润 |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for key in [1, 0]:
            if key not in grp.index:
                continue
            row = grp.loc[key]
            name = "reach10plus" if key == 1 else "giveback_before10"
            lines.append(
                f"| {name} | {row['hours_to_5pct']:.2f}h | {fmt_pct(row['adverse_before_5pct'])} | "
                f"{fmt_pct(row['pair_1h_ret_6h'])} | {row['pair_1h_range_position_24h']:.2f} | "
                f"{fmt_pct(row['pair_4h_ema50_slope_3'])} | {fmt_pct(row['pair_4h_close_vs_ema50'])} | "
                f"{fmt_pct(row['pair_1d_center_slope_3'])} | {row['btc_4h_trend_down']:.2f} | "
                f"{fmt_pct(row['btc_1d_close_vs_ema50'])} | {fmt_pct(row['final_profit'])} |"
            )
        lines.append("")
        rule_rows = rules[rules["strategy_label"] == strategy_label].head(6)
        if not rule_rows.empty:
            lines.append("### 候选简单规则")
            lines.append("")
            lines.append("| rule | coverage | reach10命中率 | 相对基线提升 | proxy_full_profit |")
            lines.append("|---|---:|---:|---:|---:|")
            for _, row in rule_rows.iterrows():
                lines.append(
                    f"| {row['rule']} | {row['coverage']:.1%} | {row['hit_rate_reach10']:.1%} | "
                    f"{row['lift_vs_base']:.1%} | {fmt_pct(row['proxy_full_profit_from_reach5'])} |"
                )
            lines.append("")

    lines.append("## 总结")
    lines.append("")
    lines.append("这轮结构诊断主要回答一个问题: 到了 `+5%` 之后，什么样的空头单更值得继续等 `+10%+`。")
    lines.append("")
    lines.append("从样本上通常会重点关注这几类差异:")
    lines.append("")
    lines.append("- 更快到 `+5%`")
    lines.append("- 到 `+5%` 前回撤更小")
    lines.append("- `+5%` 当下仍处于 4H 下行趋势中")
    lines.append("- 价格相对 4H EMA50 仍明显偏弱")
    lines.append("- BTC 大级别没有逆向抬头")
    lines.append("")
    lines.append("如果这些条件在 `Baseline / Guard` 里都表现一致，下一步就值得围绕它们做更窄的一轮真实回测验证。")
    return "\n".join(lines) + "\n"


def main() -> None:
    df = analyze_trades()
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    rules = search_rules(df)
    rules.to_csv(OUT_RULE_CSV, index=False, encoding="utf-8-sig")
    OUT_MD.write_text(build_report(df, rules), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_RULE_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
