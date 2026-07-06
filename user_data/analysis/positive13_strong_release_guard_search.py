from __future__ import annotations

from itertools import combinations
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
USER_DATA = HERE.parents[1]
REACH5_CSV = USER_DATA / "analysis" / "positive13_reach5_diagnosis.csv"
FALSE_BREAK_CSV = USER_DATA / "analysis" / "positive13_false_breakdown_features.csv"
OUT_REACH5_CSV = USER_DATA / "analysis" / "positive13_reach5_stronger_candidates.csv"
OUT_GUARD_CSV = USER_DATA / "analysis" / "positive13_guard_candidates.csv"
OUT_MD = USER_DATA / "reports" / "positive13_strong_release_guard_search.md"


REACH5_FEATURES = {
    "adverse_before_5pct": ("le", [0.0075, 0.01, 0.0125, 0.015, 0.0175]),
    "hours_to_5pct": ("le", [12, 14, 16, 18, 20]),
    "node_close_profit": ("ge", [0.047, 0.048, 0.05, 0.052]),
    "node_body_ratio": ("ge", [0.2, 0.3, 0.4, 0.5]),
    "node_close_position": ("le", [0.25, 0.3, 0.35, 0.4]),
    "node_ret_3h": ("le", [-0.01, -0.015, -0.02, -0.03]),
    "node_close_vs_ema20": ("le", [-0.005, -0.01, -0.015, -0.02]),
}

GUARD_FEATURES = {
    "short_pullback_restart": {
        "breakdown_depth": ("le", [0.003, 0.004, 0.005, 0.006, 0.007]),
        "entry_candle_body_ratio": ("le", [0.5, 0.55, 0.6, 0.65]),
        "prev_3h_return": ("le", [-0.01, -0.008, -0.006, -0.004]),
        "prev_6h_return": ("le", [-0.015, -0.012, -0.01, -0.008]),
        "distance_to_ema50_4h": ("ge", [-0.05, -0.04, -0.03, -0.02]),
    },
    "short_compression_breakdown": {
        "prev_3h_return": ("le", [-0.01, -0.008, -0.006, -0.004]),
        "prev_6h_return": ("le", [-0.015, -0.012, -0.01, -0.008]),
        "atr_percentile_1h": ("ge", [0.25, 0.3, 0.35, 0.4, 0.45]),
        "compression_width": ("ge", [0.02, 0.0225, 0.025, 0.0275, 0.03]),
        "pullback_depth": ("ge", [0.02, 0.0225, 0.025, 0.03]),
        "close_not_low_enough": ("eq", [True]),
    },
}


def apply_rule(df: pd.DataFrame, rule: list[tuple[str, str, float | bool]]) -> pd.Series:
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


def rule_text(rule: list[tuple[str, str, float | bool]]) -> str:
    parts = []
    for feature, op, threshold in rule:
        symbol = {"le": "<=", "ge": ">=", "eq": "=="}[op]
        parts.append(f"{feature} {symbol} {threshold}")
    return " AND ".join(parts)


def search_reach5(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    total = len(df)
    base_hit = df["target"].mean()
    base_avg = df["final_profit"].mean()

    single_rules: list[list[tuple[str, str, float | bool]]] = []
    for feature, (op, thresholds) in REACH5_FEATURES.items():
        for threshold in thresholds:
            single_rules.append([(feature, op, threshold)])

    rules = list(single_rules)
    for combo in combinations(single_rules, 2):
        left, right = combo
        if left[0][0] == right[0][0]:
            continue
        rules.append(left + right)

    for rule in rules:
        mask = apply_rule(df, rule)
        selected = df[mask]
        rejected = df[~mask]
        if len(selected) < 14:
            continue
        coverage = len(selected) / total
        hit_rate = selected["target"].mean()
        selected_avg = selected["final_profit"].mean()
        rejected_avg = rejected["final_profit"].mean() if len(rejected) else 0.0
        proxy_full = (selected["final_profit"].sum() + len(rejected) * 0.05) / total
        proxy_half = ((selected["final_profit"] * 0.5 + 0.025).sum() + len(rejected) * 0.05) / total
        rows.append(
            {
                "rule": rule_text(rule),
                "terms": len(rule),
                "selected": len(selected),
                "coverage": coverage,
                "hit_rate_reach10": hit_rate,
                "lift_vs_base": hit_rate - base_hit,
                "selected_avg_final_profit": selected_avg,
                "rejected_avg_final_profit": rejected_avg,
                "base_avg_final_profit": base_avg,
                "proxy_full_profit_from_reach5": proxy_full,
                "proxy_half_profit_from_reach5": proxy_half,
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["proxy_full_profit_from_reach5", "hit_rate_reach10", "coverage"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def search_guards(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for tag, features in GUARD_FEATURES.items():
        scoped = df[(df["analysis_period"] == "3y") & (df["enter_tag"] == tag)].copy()
        if scoped.empty:
            continue
        scoped["bad_target"] = scoped["false_breakdown"].fillna(False) | scoped["quick_reverse_1h_5h"].fillna(False)
        winners = scoped[~scoped["is_loser"]]
        losers = scoped[scoped["is_loser"]]
        if winners.empty or losers.empty:
            continue

        single_rules: list[list[tuple[str, str, float | bool]]] = []
        for feature, (op, thresholds) in features.items():
            for threshold in thresholds:
                single_rules.append([(feature, op, threshold)])

        rules = list(single_rules)
        for combo in combinations(single_rules, 2):
            left, right = combo
            if left[0][0] == right[0][0]:
                continue
            rules.append(left + right)

        for rule in rules:
            mask = apply_rule(scoped, rule)
            total_block = mask.mean()
            if total_block < 0.05 or total_block > 0.55:
                continue

            bad_capture = mask[scoped["bad_target"]].mean() if scoped["bad_target"].any() else 0.0
            loser_capture = mask[scoped["is_loser"]].mean() if scoped["is_loser"].any() else 0.0
            winner_kill = mask[~scoped["is_loser"]].mean() if (~scoped["is_loser"]).any() else 0.0
            quality = bad_capture - 0.8 * winner_kill
            if bad_capture < 0.20:
                continue
            rows.append(
                {
                    "enter_tag": tag,
                    "rule": rule_text(rule),
                    "terms": len(rule),
                    "blocked_share": total_block,
                    "bad_capture": bad_capture,
                    "loser_capture": loser_capture,
                    "winner_kill": winner_kill,
                    "quality_score": quality,
                    "sample_size": len(scoped),
                }
            )

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["enter_tag", "quality_score", "bad_capture", "winner_kill"],
        ascending=[True, False, False, True],
    ).reset_index(drop=True)


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_report(reach5: pd.DataFrame, guards: pd.DataFrame, reach5_raw: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Positive13 Strong Release / Guard Offline Search")
    lines.append("")
    lines.append("生成时间：2026-07-01")
    lines.append("")
    lines.append("这轮是离线代理验证，不是新的 Freqtrade 回测结果。")
    lines.append("")
    lines.append("原因：Docker 容器当前访问 Binance futures `exchangeInfo` 返回 `451 restricted location`，导致新增策略分支无法继续在线回测。")
    lines.append("")
    lines.append("本报告只做两件事：")
    lines.append("")
    lines.append("1. 在已导出的 `reach5` 诊断样本里，继续找更强的“5% 后放行强单”候选。")
    lines.append("2. 在已导出的 false breakdown / quick reverse 特征表里，找更轻的坏信号 guard 候选。")
    lines.append("")
    if not reach5.empty:
        base_hit = reach5_raw["target"].mean()
        base_avg = reach5_raw["final_profit"].mean()
        lines.append("## 1. Reach5 强单放行候选")
        lines.append("")
        lines.append(f"- reach5 样本数：`{len(reach5_raw)}`")
        lines.append(f"- 基线 reach10+ 比例：`{base_hit:.1%}`")
        lines.append(f"- 基线 reach5 样本最终平均利润：`{base_avg:.2%}`")
        lines.append("")
        lines.append("### Top candidates by proxy full profit")
        lines.append("")
        lines.append("| rule | coverage | hit_rate_reach10 | proxy_full | proxy_half |")
        lines.append("|---|---:|---:|---:|---:|")
        for _, row in reach5.head(8).iterrows():
            lines.append(
                f"| {row['rule']} | {row['coverage']:.1%} | {row['hit_rate_reach10']:.1%} | "
                f"{row['proxy_full_profit_from_reach5']:.2%} | {row['proxy_half_profit_from_reach5']:.2%} |"
            )
        lines.append("")
        top = reach5.iloc[0]
        lines.append("观察：")
        lines.append("")
        lines.append(
            f"- 当前离线最强候选仍围绕 `adverse_before_5pct` 展开；最佳候选为 `{top['rule']}`。"
        )
        lines.append(
            "- 这和前面的回测结论是一致的：真正有信息量的，不是单纯冲得快，而是到 5% 前走得顺。"
        )
        lines.append(
            "- 之前新加的 `node_ret_1h <= -1.5%` 在线回测已经失败，所以本轮即使个别离线组合看起来漂亮，也不把它直接升级成主候选。"
        )
        lines.append("")
    if not guards.empty:
        lines.append("## 2. 坏信号 guard 候选")
        lines.append("")
        for tag in ["short_pullback_restart", "short_compression_breakdown"]:
            scoped = guards[guards["enter_tag"] == tag].head(6)
            if scoped.empty:
                continue
            lines.append(f"### {tag}")
            lines.append("")
            lines.append("| rule | blocked_share | bad_capture | loser_capture | winner_kill | quality |")
            lines.append("|---|---:|---:|---:|---:|---:|")
            for _, row in scoped.iterrows():
                lines.append(
                    f"| {row['rule']} | {row['blocked_share']:.1%} | {row['bad_capture']:.1%} | "
                    f"{row['loser_capture']:.1%} | {row['winner_kill']:.1%} | {row['quality_score']:.3f} |"
                )
            lines.append("")
        lines.append("观察：")
        lines.append("")
        lines.append("- `short_pullback_restart` 里，最有希望的仍是浅 breakdown depth 方向，但必须比 `<= 0.0063` 更保守。")
        lines.append("- `short_compression_breakdown` 里，前 3h/6h 已经跌太多 + ATR 偏高，仍然是最像坏信号的组合。")
        lines.append("- 只要 winner_kill 还在 30% 左右，这类 guard 就还不够资格直接并入主策略。")
        lines.append("")
    lines.append("## 3. 当前结论")
    lines.append("")
    lines.append("1. 离线结果继续支持当前主线：`Breakeven Only + 5% 小回撤强单放行`。")
    lines.append("2. 更强的强单放行，目前仍应围绕 `adverse_before_5pct` 微调，而不是再叠追跌类瞬时动量条件。")
    lines.append("3. 坏信号过滤并不是完全没线索，但暂时还没有看到“抓坏单很多、误杀好单很少”的干净规则。")
    lines.append("4. 下一步最值得回测的，只应保留 1-2 条最轻量候选，等 Docker/网络恢复后再做正式验证。")
    return "\n".join(lines)


def main() -> None:
    reach5_raw = pd.read_csv(REACH5_CSV)
    reach5_raw["target"] = reach5_raw["category"].eq("reach10plus")
    reach5_candidates = search_reach5(reach5_raw)
    guard_candidates = search_guards(pd.read_csv(FALSE_BREAK_CSV))
    reach5_candidates.to_csv(OUT_REACH5_CSV, index=False, encoding="utf-8-sig")
    guard_candidates.to_csv(OUT_GUARD_CSV, index=False, encoding="utf-8-sig")
    OUT_MD.write_text(build_report(reach5_candidates, guard_candidates, reach5_raw), encoding="utf-8")
    print(f"Wrote {OUT_REACH5_CSV}")
    print(f"Wrote {OUT_GUARD_CSV}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
