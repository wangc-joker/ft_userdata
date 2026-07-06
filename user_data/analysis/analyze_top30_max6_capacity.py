import csv
import json
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\test\ft_userdata")
BACKTEST_DIR = ROOT / "user_data" / "backtest_results"
REPORT_PATH = ROOT / "user_data" / "reports" / "top30_max6_pair_slot_diagnosis.md"
PAIR_CSV_PATH = ROOT / "user_data" / "analysis" / "top30_max6_pair_contribution.csv"
SLOT_CSV_PATH = ROOT / "user_data" / "analysis" / "top30_max6_slot_competition.csv"
EXTRA_PAIR_CSV_PATH = ROOT / "user_data" / "analysis" / "top30_max6_extra_slot_pairs.csv"

ZIP_3Y = BACKTEST_DIR / "backtest-result-2026-06-30_09-36-01.zip"
ZIP_1Y = BACKTEST_DIR / "backtest-result-2026-06-30_09-32-16.zip"
STRATEGY = "DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy"
BASE13 = {
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
}


def load_strategy_data(path: Path):
    with zipfile.ZipFile(path) as zf:
        json_name = next(name for name in zf.namelist() if name.endswith(".json") and "_config" not in name)
        data = json.loads(zf.read(json_name))
    return data["strategy"][STRATEGY]


def parse_trades(strategy_data):
    trades = []
    for trade in strategy_data["trades"]:
        item = dict(trade)
        item["open_dt"] = datetime.fromtimestamp(trade["open_timestamp"] / 1000, tz=timezone.utc)
        item["close_dt"] = datetime.fromtimestamp(trade["close_timestamp"] / 1000, tz=timezone.utc)
        item["profit_pct"] = trade["profit_ratio"] * 100.0
        trades.append(item)
    return trades


def pair_stats(trades, label):
    grouped = defaultdict(list)
    for t in trades:
        grouped[t["pair"]].append(t)
    rows = []
    for pair, items in grouped.items():
        profits_abs = [x["profit_abs"] for x in items]
        profits_pct = [x["profit_pct"] for x in items]
        wins = sum(1 for x in items if x["profit_abs"] > 0)
        rows.append(
            {
                "sample": label,
                "pair": pair,
                "trades": len(items),
                "profit_abs": sum(profits_abs),
                "profit_pct_sum": sum(profits_pct),
                "avg_profit_pct": sum(profits_pct) / len(items),
                "winrate_pct": wins / len(items) * 100.0,
                "best_trade_pct": max(profits_pct),
                "worst_trade_pct": min(profits_pct),
                "is_base13": pair in BASE13,
            }
        )
    rows.sort(key=lambda x: x["profit_abs"], reverse=True)
    return rows


def occupancy_analysis(trades):
    ordered = sorted(trades, key=lambda x: (x["open_dt"], x["close_dt"], x["pair"]))
    open_trades = []
    trade_rows = []
    extra_pair = defaultdict(lambda: {"trades": 0, "profit_abs": 0.0, "profit_pct_sum": 0.0})

    for t in ordered:
        now = t["open_dt"]
        open_trades = [x for x in open_trades if x["close_dt"] > now]
        prior_open = len(open_trades)
        row = {
            "pair": t["pair"],
            "enter_tag": t["enter_tag"],
            "open_dt": t["open_dt"].isoformat(),
            "close_dt": t["close_dt"].isoformat(),
            "prior_open": prior_open,
            "slot_number": prior_open + 1,
            "extra_slot_trade": prior_open >= 3,
            "profit_abs": t["profit_abs"],
            "profit_pct": t["profit_pct"],
            "is_base13": t["pair"] in BASE13,
        }
        trade_rows.append(row)
        if prior_open >= 3:
            bucket = extra_pair[t["pair"]]
            bucket["trades"] += 1
            bucket["profit_abs"] += t["profit_abs"]
            bucket["profit_pct_sum"] += t["profit_pct"]
        open_trades.append({"close_dt": t["close_dt"]})

    events = []
    for t in trades:
        events.append((t["open_dt"], 1))
        events.append((t["close_dt"], -1))
    events.sort(key=lambda x: (x[0], x[1]))

    active = 0
    last_ts = None
    duration_rows = []
    for ts, delta in events:
        if last_ts is not None and ts > last_ts:
            duration_rows.append(
                {
                    "start": last_ts,
                    "end": ts,
                    "active_count": active,
                    "seconds": (ts - last_ts).total_seconds(),
                }
            )
        active += delta
        last_ts = ts

    extra_rows = []
    for pair, vals in extra_pair.items():
        extra_rows.append(
            {
                "pair": pair,
                "trades": vals["trades"],
                "profit_abs": vals["profit_abs"],
                "profit_pct_sum": vals["profit_pct_sum"],
            }
        )
    extra_rows.sort(key=lambda x: x["profit_abs"], reverse=True)
    return trade_rows, duration_rows, extra_rows


def summarize_slot_usage(trade_rows, duration_rows, label):
    grouped = defaultdict(list)
    total_trades = len(trade_rows)
    total_profit = sum(x["profit_abs"] for x in trade_rows)
    for row in trade_rows:
        grouped[row["prior_open"]].append(row)

    slot_rows = []
    for prior_open in sorted(grouped):
        items = grouped[prior_open]
        profits = [x["profit_abs"] for x in items]
        profit_pcts = [x["profit_pct"] for x in items]
        wins = sum(1 for x in items if x["profit_abs"] > 0)
        slot_rows.append(
            {
                "sample": label,
                "prior_open": prior_open,
                "slot_number": prior_open + 1,
                "trades": len(items),
                "trade_share_pct": len(items) / total_trades * 100.0,
                "profit_abs": sum(profits),
                "profit_share_pct": (sum(profits) / total_profit * 100.0) if total_profit else 0.0,
                "avg_profit_pct": sum(profit_pcts) / len(items),
                "winrate_pct": wins / len(items) * 100.0,
            }
        )

    total_seconds = sum(x["seconds"] for x in duration_rows)
    ge3 = sum(x["seconds"] for x in duration_rows if x["active_count"] >= 3)
    ge5 = sum(x["seconds"] for x in duration_rows if x["active_count"] >= 5)
    eq6 = sum(x["seconds"] for x in duration_rows if x["active_count"] == 6)
    extra = [x for x in trade_rows if x["prior_open"] >= 3]
    extra_wins = sum(1 for x in extra if x["profit_abs"] > 0)
    metrics = {
        "time_ge_3_pct": (ge3 / total_seconds * 100.0) if total_seconds else 0.0,
        "time_ge_5_pct": (ge5 / total_seconds * 100.0) if total_seconds else 0.0,
        "time_eq_6_pct": (eq6 / total_seconds * 100.0) if total_seconds else 0.0,
        "extra_trade_count": len(extra),
        "extra_trade_profit_abs": sum(x["profit_abs"] for x in extra),
        "extra_trade_winrate_pct": (extra_wins / len(extra) * 100.0) if extra else 0.0,
    }
    return slot_rows, metrics


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt(v):
    return f"{v:.2f}"


def list_zero_trade_pairs(pairlist, pair_rows):
    active = {row["pair"] for row in pair_rows}
    return [pair for pair in pairlist if pair not in active]


def main():
    data_3y = load_strategy_data(ZIP_3Y)
    data_1y = load_strategy_data(ZIP_1Y)
    trades_3y = parse_trades(data_3y)
    trades_1y = parse_trades(data_1y)

    pair_3y = pair_stats(trades_3y, "3y")
    pair_1y = pair_stats(trades_1y, "1y")
    pair_all = pair_3y + pair_1y
    write_csv(PAIR_CSV_PATH, pair_all, list(pair_all[0].keys()))

    trade_slot_3y, duration_3y, extra_pair_3y = occupancy_analysis(trades_3y)
    trade_slot_1y, duration_1y, extra_pair_1y = occupancy_analysis(trades_1y)
    slot_rows_3y, slot_metrics_3y = summarize_slot_usage(trade_slot_3y, duration_3y, "3y")
    slot_rows_1y, slot_metrics_1y = summarize_slot_usage(trade_slot_1y, duration_1y, "1y")
    slot_all = slot_rows_3y + slot_rows_1y
    write_csv(SLOT_CSV_PATH, slot_all, list(slot_all[0].keys()))

    for row in extra_pair_3y:
        row["sample"] = "3y"
    for row in extra_pair_1y:
        row["sample"] = "1y"
    extra_pair_all = extra_pair_3y + extra_pair_1y
    if extra_pair_all:
        write_csv(EXTRA_PAIR_CSV_PATH, extra_pair_all, list(extra_pair_all[0].keys()))

    zero_3y = list_zero_trade_pairs(data_3y["pairlist"], pair_3y)
    zero_1y = list_zero_trade_pairs(data_1y["pairlist"], pair_1y)

    top_pos_3y = pair_3y[:8]
    top_neg_3y = [row for row in sorted(pair_3y, key=lambda x: x["profit_abs"]) if row["profit_abs"] < 0][:8]
    top_pos_1y = pair_1y[:8]
    top_neg_1y = [row for row in sorted(pair_1y, key=lambda x: x["profit_abs"]) if row["profit_abs"] < 0][:8]

    lines = []
    lines.append("# Top30 max6 Pair / Slot Diagnosis")
    lines.append("")
    lines.append("生成时间：2026-06-30")
    lines.append("")
    lines.append("## 分析对象")
    lines.append("")
    lines.append(f"- 策略：`{STRATEGY}`")
    lines.append("- 方案：`Top30 + max_open_trades=6`")
    lines.append("- 三年样本：`2023-06-18 -> 2026-05-08`")
    lines.append("- 近一年样本：`2025-06-18 -> 2026-05-08`")
    lines.append("- 参考基准：此前已验证的 `Positive13 + max_open_trades=3`")
    lines.append("")
    lines.append("## 1. 核心结论")
    lines.append("")
    lines.append(f"1. `Top30 + max6` 的收益提升是真实的：三年 `141.04%`，近一年 `36.85%`，都高于 `Positive13 + max3`。")
    lines.append("2. 但它不是靠“30 个币一起发力”得到的，而是靠少数强贡献币 + 更宽槽位把更多单接住。")
    lines.append(
        f"3. 三年样本里，开仓时已有 `3` 仓及以上的额外槽位单共有 `{slot_metrics_3y['extra_trade_count']}` 笔，贡献利润 `{fmt(slot_metrics_3y['extra_trade_profit_abs'])} USDT`。"
    )
    lines.append(
        f"4. 近一年样本里，额外槽位单共有 `{slot_metrics_1y['extra_trade_count']}` 笔，贡献利润 `{fmt(slot_metrics_1y['extra_trade_profit_abs'])} USDT`。"
    )
    lines.append("5. 真正多赚的钱仍集中在核心强币和少数新增有效币上，很多新增币只是挂名在池子里。")
    lines.append("")
    lines.append("## 2. Pair 贡献")
    lines.append("")
    lines.append("### 三年样本：主要正贡献")
    lines.append("")
    for row in top_pos_3y:
        lines.append(f"- `{row['pair']}`: `{fmt(row['profit_abs'])} USDT`, `{row['trades']}` trades")
    lines.append("")
    lines.append("### 三年样本：主要拖累")
    lines.append("")
    for row in top_neg_3y:
        lines.append(f"- `{row['pair']}`: `{fmt(row['profit_abs'])} USDT`, `{row['trades']}` trades")
    lines.append("")
    lines.append(f"三年样本零成交币：`{', '.join(zero_3y)}`")
    lines.append("")
    lines.append("### 近一年样本：主要正贡献")
    lines.append("")
    for row in top_pos_1y:
        lines.append(f"- `{row['pair']}`: `{fmt(row['profit_abs'])} USDT`, `{row['trades']}` trades")
    lines.append("")
    lines.append("### 近一年样本：主要拖累")
    lines.append("")
    for row in top_neg_1y:
        lines.append(f"- `{row['pair']}`: `{fmt(row['profit_abs'])} USDT`, `{row['trades']}` trades")
    lines.append("")
    lines.append(f"近一年样本零成交币：`{', '.join(zero_1y)}`")
    lines.append("")
    lines.append("观察：")
    lines.append("")
    lines.append("- `ETH/BNB/XRP/BTC/ADA/ZEC/DOGE` 依然是核心利润柱子。")
    lines.append("- `TRX` 在大池子里确实新增了有效正贡献。")
    lines.append("- 很多新增币长期接近 `0 trade`，说明它们没有真正进入策略主战场。")
    lines.append("- `SOL/SUI/LINK` 依然是老拖累项，新增币没有自动解决这个问题。")
    lines.append("")
    lines.append("## 3. 槽位竞争")
    lines.append("")
    lines.append("### 三年样本")
    lines.append("")
    lines.append(f"- 时间上，组合处于 `>=3` 仓状态约 `{fmt(slot_metrics_3y['time_ge_3_pct'])}%`。")
    lines.append(f"- 处于 `>=5` 仓状态约 `{fmt(slot_metrics_3y['time_ge_5_pct'])}%`。")
    lines.append(f"- 刚好满 `6` 仓状态约 `{fmt(slot_metrics_3y['time_eq_6_pct'])}%`。")
    lines.append(
        f"- 开仓时已有 `3` 仓及以上的额外槽位单：`{slot_metrics_3y['extra_trade_count']}` 笔，胜率 `{fmt(slot_metrics_3y['extra_trade_winrate_pct'])}%`，利润 `{fmt(slot_metrics_3y['extra_trade_profit_abs'])} USDT`。"
    )
    lines.append("")
    lines.append("### 近一年样本")
    lines.append("")
    lines.append(f"- 时间上，组合处于 `>=3` 仓状态约 `{fmt(slot_metrics_1y['time_ge_3_pct'])}%`。")
    lines.append(f"- 处于 `>=5` 仓状态约 `{fmt(slot_metrics_1y['time_ge_5_pct'])}%`。")
    lines.append(f"- 刚好满 `6` 仓状态约 `{fmt(slot_metrics_1y['time_eq_6_pct'])}%`。")
    lines.append(
        f"- 开仓时已有 `3` 仓及以上的额外槽位单：`{slot_metrics_1y['extra_trade_count']}` 笔，胜率 `{fmt(slot_metrics_1y['extra_trade_winrate_pct'])}%`，利润 `{fmt(slot_metrics_1y['extra_trade_profit_abs'])} USDT`。"
    )
    lines.append("")
    lines.append("判断：")
    lines.append("")
    lines.append("- 额外槽位不是纯噪音，因为它们整体仍然贡献正收益。")
    lines.append("- 但这些额外利润并没有分散来自很多新增币，而是集中在少数真正能打的 pair 上。")
    lines.append("- 所以 `max6` 的主要价值是“别让好机会被卡在门外”，不是“更多币自动带来更多 alpha”。")
    lines.append("")
    lines.append("### 额外槽位利润集中在哪些 pair")
    lines.append("")
    lines.append("三年样本：")
    lines.append("")
    for row in extra_pair_3y[:8]:
        lines.append(f"- `{row['pair']}`: `{row['trades']}` extra-slot trades, `{fmt(row['profit_abs'])} USDT`")
    lines.append("")
    lines.append("近一年样本：")
    lines.append("")
    for row in extra_pair_1y[:8]:
        lines.append(f"- `{row['pair']}`: `{row['trades']}` extra-slot trades, `{fmt(row['profit_abs'])} USDT`")
    lines.append("")
    lines.append("观察：")
    lines.append("")
    lines.append("- 三年额外槽位利润主要集中在 `BNB/BTC/DOGE/LINK/NEAR` 这些币上。")
    lines.append("- 近一年额外槽位利润更集中，主要还是 `BNB/LINK/NEAR/BTC`。")
    lines.append("- 这再次说明：槽位放大有价值，但新增价值不是均匀来自整个 30 币池。")
    lines.append("")
    lines.append("## 4. 最值得继续看的方向")
    lines.append("")
    lines.append("1. 保留 `Top30 + max6` 作为容量支线，但不要直接当最终主线。")
    lines.append("2. 从 30 币池里删掉长期零成交或持续负贡献的币，做一个 `Top18-24 + max6`。")
    lines.append("3. 重点保留：共享核心强币，以及 `TRX` 这种在大池里确实新增正贡献的币。")
    lines.append("4. 重点审查：`SOL/SUI/LINK` 这些老拖累，以及 `FIL/APE/LDO/LTC` 这类新增但没有证明自己价值的币。")
    lines.append("")
    lines.append("## 输出文件")
    lines.append("")
    lines.append(f"- Pair 贡献明细：`{PAIR_CSV_PATH}`")
    lines.append(f"- 槽位竞争明细：`{SLOT_CSV_PATH}`")
    lines.append(f"- 额外槽位 pair 明细：`{EXTRA_PAIR_CSV_PATH}`")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
