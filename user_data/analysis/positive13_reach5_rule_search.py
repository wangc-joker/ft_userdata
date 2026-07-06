from __future__ import annotations

from itertools import combinations
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
USER_DATA = HERE.parents[1]
IN_CSV = USER_DATA / "analysis" / "positive13_reach5_diagnosis.csv"
OUT_CSV = USER_DATA / "analysis" / "positive13_reach5_rule_candidates.csv"
OUT_MD = USER_DATA / "reports" / "positive13_reach5_rule_search.md"


FEATURES = {
    "hours_to_5pct": {
        "dir": "le",
        "thresholds": [8, 10, 12, 14, 16, 18, 20, 24],
    },
    "adverse_before_5pct": {
        "dir": "le",
        "thresholds": [0.0025, 0.005, 0.0075, 0.01, 0.0125],
    },
    "node_close_profit": {
        "dir": "ge",
        "thresholds": [0.048, 0.05, 0.052, 0.055, 0.06],
    },
    "node_ret_1h": {
        "dir": "le",
        "thresholds": [-0.01, -0.015, -0.02, -0.03, -0.05],
    },
    "node_ret_3h": {
        "dir": "le",
        "thresholds": [-0.015, -0.02, -0.03, -0.04, -0.06],
    },
    "node_close_vs_ema20": {
        "dir": "le",
        "thresholds": [-0.005, -0.01, -0.015, -0.02, -0.03],
    },
    "node_close_vs_ema50": {
        "dir": "le",
        "thresholds": [-0.005, -0.01, -0.015, -0.02, -0.03],
    },
    "node_body_ratio": {
        "dir": "ge",
        "thresholds": [0.2, 0.3, 0.4, 0.5, 0.6],
    },
    "node_close_position": {
        "dir": "le",
        "thresholds": [0.2, 0.3, 0.4, 0.5, 0.6],
    },
}


def apply_rule(df: pd.DataFrame, rule: list[tuple[str, str, float]]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for feature, op, threshold in rule:
        if op == "le":
            mask &= df[feature] <= threshold
        elif op == "ge":
            mask &= df[feature] >= threshold
        else:
            raise ValueError(op)
    return mask


def rule_text(rule: list[tuple[str, str, float]]) -> str:
    parts = []
    for feature, op, threshold in rule:
        symbol = "<=" if op == "le" else ">="
        parts.append(f"{feature} {symbol} {threshold}")
    return " AND ".join(parts)


def search(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    total = len(df)
    base_rate = df["target"].mean()
    base_avg = df["final_profit"].mean()

    single_rules: list[list[tuple[str, str, float]]] = []
    for feature, spec in FEATURES.items():
        for threshold in spec["thresholds"]:
            single_rules.append([(feature, spec["dir"], threshold)])

    all_rules = list(single_rules)
    for left, right in combinations(single_rules, 2):
        if left[0][0] == right[0][0]:
            continue
        all_rules.append(left + right)

    for rule in all_rules:
        mask = apply_rule(df, rule)
        selected = df[mask]
        rejected = df[~mask]
        if len(selected) < 12:
            continue
        coverage = len(selected) / total
        hit_rate = selected["target"].mean()
        selected_avg = selected["final_profit"].mean()
        rejected_avg = rejected["final_profit"].mean() if len(rejected) else 0.0

        # proxy A: strong holds baseline final outcome, weak exits at +5%
        # proxy B: strong half at +5 and remaining keeps baseline final minus 5% on half
        proxy_full_profit = (
            selected["final_profit"].sum() + len(rejected) * 0.05
        ) / total
        proxy_half_profit = (
            (selected["final_profit"] * 0.5 + 0.025).sum() + len(rejected) * 0.05
        ) / total
        rows.append(
            {
                "rule": rule_text(rule),
                "terms": len(rule),
                "selected": len(selected),
                "coverage": coverage,
                "hit_rate_reach10": hit_rate,
                "lift_vs_base": hit_rate - base_rate,
                "selected_avg_final_profit": selected_avg,
                "rejected_avg_final_profit": rejected_avg,
                "base_avg_final_profit": base_avg,
                "proxy_full_profit_from_reach5": proxy_full_profit,
                "proxy_half_profit_from_reach5": proxy_half_profit,
            }
        )
    result = pd.DataFrame(rows)
    result = result.sort_values(
        ["proxy_full_profit_from_reach5", "hit_rate_reach10", "coverage"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return result


def build_report(df: pd.DataFrame) -> str:
    top_full = df.sort_values(
        ["proxy_full_profit_from_reach5", "hit_rate_reach10", "coverage"],
        ascending=[False, False, False],
    ).head(12)
    top_balanced = df[
        (df["coverage"] >= 0.25)
        & (df["coverage"] <= 0.75)
    ].sort_values(
        ["hit_rate_reach10", "proxy_full_profit_from_reach5", "coverage"],
        ascending=[False, False, False],
    ).head(12)

    lines: list[str] = []
    lines.append("# Positive13 Reach5 Strong Rule Search")
    lines.append("")
    lines.append("基于 `positive13_reach5_diagnosis.csv` 对可解释的单变量/双变量规则进行枚举搜索。")
    lines.append("")
    lines.append("说明：")
    lines.append("")
    lines.append("- `hit_rate_reach10`：被识别为强单后，后续还能到 10%+ 的比例")
    lines.append("- `coverage`：强单规则覆盖的 reach5 样本比例")
    lines.append("- `proxy_full_profit_from_reach5`：弱单 5% 全平、强单继续 baseline 的粗略代理")
    lines.append("- `proxy_half_profit_from_reach5`：弱单 5% 全平、强单 5% 平半后继续的粗略代理")
    lines.append("")
    lines.append("## Top 12: Proxy Full Profit")
    lines.append("")
    lines.append("| rule | terms | selected | coverage | hit_rate_reach10 | lift_vs_base | proxy_full_profit_from_reach5 | proxy_half_profit_from_reach5 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for _, row in top_full.iterrows():
        lines.append(
            f"| {row['rule']} | {int(row['terms'])} | {int(row['selected'])} | {row['coverage']:.1%} | "
            f"{row['hit_rate_reach10']:.1%} | {row['lift_vs_base']:.1%} | "
            f"{row['proxy_full_profit_from_reach5']:.2%} | {row['proxy_half_profit_from_reach5']:.2%} |"
        )
    lines.append("")
    lines.append("## Top 12: Balanced Coverage")
    lines.append("")
    lines.append("| rule | selected | coverage | hit_rate_reach10 | proxy_full_profit_from_reach5 |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in top_balanced.iterrows():
        lines.append(
            f"| {row['rule']} | {int(row['selected'])} | {row['coverage']:.1%} | "
            f"{row['hit_rate_reach10']:.1%} | {row['proxy_full_profit_from_reach5']:.2%} |"
        )
    return "\n".join(lines)


def main() -> None:
    df = pd.read_csv(IN_CSV)
    df["target"] = df["category"].eq("reach10plus")
    result = search(df)
    result.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    OUT_MD.write_text(build_report(result), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
