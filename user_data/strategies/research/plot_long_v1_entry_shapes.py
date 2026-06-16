from __future__ import annotations

import html
import json
import zipfile
from pathlib import Path

import pandas as pd


USER_DATA = Path("/freqtrade/user_data")
RESULTS = USER_DATA / "backtest_results"
DATA = USER_DATA / "data" / "binance" / "futures"
OUT = USER_DATA / "strategies" / "research" / "long_v1_entry_visuals"


def load_backtest(zip_name_prefix: str) -> dict:
    zips = sorted(RESULTS.glob(f"{zip_name_prefix}-*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise FileNotFoundError(f"No zip found for {zip_name_prefix}")
    with zipfile.ZipFile(zips[-1]) as zf:
        json_name = [n for n in zf.namelist() if n.endswith(".json") and not n.endswith("_config.json")][0]
        return json.loads(zf.read(json_name))["strategy"]["DualTrendCompressionRestartLongV1Strategy"]


def pair_to_file(pair: str, timeframe: str) -> Path:
    symbol = pair.replace("/", "_").replace(":", "_")
    return DATA / f"{symbol}-{timeframe}-futures.feather"


def load_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    df = pd.read_feather(pair_to_file(pair, timeframe))
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df.set_index("date").sort_index()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def add_shape_context(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema50"] = ema(out["close"], 50)
    out["compression_high"] = out["high"].shift(1).rolling(12).max()
    out["compression_low"] = out["low"].shift(1).rolling(12).min()
    out["recent_high_24"] = out["high"].shift(1).rolling(24).max()
    out["pullback_low_12"] = out["low"].shift(1).rolling(12).min()
    out["pullback_depth_long"] = (out["recent_high_24"] - out["pullback_low_12"]) / out["recent_high_24"]
    out["return_24h"] = out["close"].shift(1) / out["close"].shift(25) - 1
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    out["atr_ref"] = out["atr"].shift(1)
    out["atr_pct"] = out["atr"] / out["close"]
    candle_range = out["high"] - out["low"]
    out["close_position"] = (out["close"] - out["low"]) / candle_range
    return out


def line_path(points, x_scale, y_scale) -> str:
    parts = []
    for i, (xv, yv) in enumerate(points):
        if pd.isna(yv):
            continue
        cmd = "M" if not parts else "L"
        parts.append(f"{cmd}{x_scale(xv):.1f},{y_scale(float(yv)):.1f}")
    return " ".join(parts)


def svg_text(x, y, text, size=14, weight="400", fill="#292524") -> str:
    lines = str(text).split("\n")
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * size * 1.35}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{html.escape(line)}</text>'
        )
    return "\n".join(out)


def plot_logic_diagram() -> Path:
    w, h = 1500, 860
    boxes = [
        ("Universe", "BNB / XRP / DOGE / ZEC", 70, 95, 260, 105),
        ("Dual trend", "Pair 4h uptrend\nBTC 4h uptrend", 390, 95, 260, 125),
        ("Compression", "Last 12x1h range is tight\nvolume breakout ok", 710, 95, 300, 125),
        ("Pullback", "24h recent high exists\n12h pullback low intact\npullback depth <= 5%", 1070, 95, 340, 150),
        ("Restart candle", "Break above compression high\nclose near candle top >= 0.72\nclose > 4h EMA50", 300, 410, 340, 150),
        ("Risk gate", "ATR% <= 5%\n24h return in [-2%, 12%]\nstop distance 0.5%-5%", 710, 410, 330, 150),
        ("Entry point", "Enter long at restart close\ninitial stop = pullback low - 0.2 ATR\nROI target = +5%", 1080, 410, 350, 150),
        ("Exit control", "Structural stop / trailing stop\nstale loss 72h\ntrend flip under +3%", 710, 690, 350, 135),
    ]
    arrows = [
        (330, 148, 390, 148),
        (650, 148, 710, 148),
        (1010, 148, 1070, 148),
        (1240, 250, 470, 410),
        (640, 485, 710, 485),
        (1040, 485, 1080, 485),
        (1230, 560, 885, 690),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#f7f4ed"/>',
        svg_text(70, 48, "Long V1 入场形态逻辑图", 26, "700"),
    ]
    for title, body, x, y, bw, bh in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="#ffffff" stroke="#d6d3d1" stroke-width="2"/>')
        parts.append(svg_text(x + 18, y + 32, title, 18, "700"))
        parts.append(svg_text(x + 18, y + 64, body, 15))
    for x1, y1, x2, y2 in arrows:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#57534e" stroke-width="3" marker-end="url(#arrow)"/>')
    parts.insert(
        1,
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#57534e"/></marker></defs>',
    )
    parts.append(svg_text(70, 810, "形态摘要：高周期同向 -> 1h 窄幅压缩 -> 可控回踩 -> 强势重启阳线 -> 入场，止损放在回踩低点下方。", 18))
    parts.append("</svg>")
    out = OUT / "long_v1_entry_logic_diagram.svg"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def plot_trade(trade: dict, idx: int) -> Path:
    pair = trade["pair"]
    entry_time = pd.Timestamp(trade["open_date"])
    exit_time = pd.Timestamp(trade["close_date"])
    df = add_shape_context(load_ohlcv(pair, "1h"))
    h4 = load_ohlcv(pair, "4h")
    h4["ema50_4h"] = ema(h4["close"], 50)
    h4["ema200_4h"] = ema(h4["close"], 200)

    start = entry_time - pd.Timedelta(hours=54)
    end = entry_time + pd.Timedelta(hours=42)
    win = df.loc[start:end].copy()
    h4_win = h4.loc[start:end].copy()
    row = df.loc[:entry_time].iloc[-1]

    entry = float(trade["open_rate"])
    stop = float(trade["initial_stop_loss_abs"])
    target = entry * 1.05
    exit_rate = float(trade["close_rate"])
    lows = [win["low"].min(), stop]
    highs = [win["high"].max(), target]
    y_min, y_max = min(lows), max(highs)
    pad = (y_max - y_min) * 0.12
    y_min -= pad
    y_max += pad

    w, h = 1500, 900
    left, top, chart_w, chart_h = 80, 120, 1320, 480
    h4_top, h4_h = 675, 150
    times = list(win.index)

    def x_scale(ts):
        pos = times.index(ts) if ts in win.index else max(0, min(len(times) - 1, int((ts - times[0]) / pd.Timedelta(hours=1))))
        return left + pos * chart_w / max(1, len(times) - 1)

    def y_scale(v):
        return top + (y_max - v) * chart_h / (y_max - y_min)

    h4_min = min(h4_win["close"].min(), h4_win["ema50_4h"].min(), h4_win["ema200_4h"].min())
    h4_max = max(h4_win["close"].max(), h4_win["ema50_4h"].max(), h4_win["ema200_4h"].max())
    h4_pad = (h4_max - h4_min) * 0.12
    h4_min -= h4_pad
    h4_max += h4_pad

    def h4_x(ts):
        return left + (ts - h4_win.index[0]) / (h4_win.index[-1] - h4_win.index[0]) * chart_w

    def h4_y(v):
        return h4_top + (h4_max - v) * h4_h / (h4_max - h4_min)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#f7f4ed"/>',
        f'<rect x="{left}" y="{top}" width="{chart_w}" height="{chart_h}" fill="#fbfaf6" stroke="#d6d3d1"/>',
        f'<rect x="{left}" y="{h4_top}" width="{chart_w}" height="{h4_h}" fill="#fbfaf6" stroke="#d6d3d1"/>',
        svg_text(80, 50, f"{idx}. {pair} Long V1 真实入场 | {entry_time:%Y-%m-%d %H:%M} UTC | profit {trade['profit_ratio'] * 100:.2f}% | exit {trade['exit_reason']}", 22, "700"),
    ]

    candle_w = chart_w / len(win) * 0.55
    for ts, r in win.iterrows():
        x = x_scale(ts)
        color = "#178f62" if r["close"] >= r["open"] else "#c75050"
        parts.append(f'<line x1="{x:.1f}" y1="{y_scale(r["low"]):.1f}" x2="{x:.1f}" y2="{y_scale(r["high"]):.1f}" stroke="{color}" stroke-width="1.2"/>')
        y1 = y_scale(max(r["open"], r["close"]))
        y2 = y_scale(min(r["open"], r["close"]))
        parts.append(f'<rect x="{x - candle_w / 2:.1f}" y="{y1:.1f}" width="{candle_w:.1f}" height="{max(1.2, y2 - y1):.1f}" fill="{color}" opacity="0.82"/>')

    series = [
        ("1h EMA50", win["ema50"], "#2563eb", "1.8"),
        ("12h compression high", win["compression_high"], "#8b5cf6", "1.5"),
        ("12h compression low", win["compression_low"], "#8b5cf6", "1.5"),
        ("24h recent high", win["recent_high_24"], "#d97706", "1.5"),
        ("12h pullback low", win["pullback_low_12"], "#0f766e", "1.5"),
    ]
    for _, ser, color, width in series:
        points = list(zip(win.index, ser))
        parts.append(f'<path d="{line_path(points, x_scale, y_scale)}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    for label, value, color, dash in [
        ("entry", entry, "#111827", ""),
        ("initial stop", stop, "#dc2626", "stroke-dasharray='8 6'"),
        ("ROI +5%", target, "#16a34a", "stroke-dasharray='8 6'"),
    ]:
        y = y_scale(value)
        parts.append(f"<line x1='{left}' y1='{y:.1f}' x2='{left + chart_w}' y2='{y:.1f}' stroke='{color}' stroke-width='2' {dash}/>")
        parts.append(svg_text(left + chart_w + 10, y + 4, label, 13, "600", color))

    ex = x_scale(entry_time)
    parts.append(f'<polygon points="{ex-9:.1f},{y_scale(entry)+16:.1f} {ex+9:.1f},{y_scale(entry)+16:.1f} {ex:.1f},{y_scale(entry)-6:.1f}" fill="#111827"/>')
    if win.index[0] <= exit_time <= win.index[-1]:
        xx = x_scale(exit_time)
        yy = y_scale(exit_rate)
        parts.append(f'<line x1="{xx-9:.1f}" y1="{yy-9:.1f}" x2="{xx+9:.1f}" y2="{yy+9:.1f}" stroke="#7c2d12" stroke-width="3"/>')
        parts.append(f'<line x1="{xx+9:.1f}" y1="{yy-9:.1f}" x2="{xx-9:.1f}" y2="{yy+9:.1f}" stroke="#7c2d12" stroke-width="3"/>')

    h4_series = [
        ("4h close", h4_win["close"], "#334155"),
        ("4h EMA50", h4_win["ema50_4h"], "#2563eb"),
        ("4h EMA200", h4_win["ema200_4h"], "#9333ea"),
    ]
    for _, ser, color in h4_series:
        parts.append(f'<path d="{line_path(list(zip(h4_win.index, ser)), h4_x, h4_y)}" fill="none" stroke="{color}" stroke-width="2"/>')
    parts.append(f'<line x1="{ex:.1f}" y1="{h4_top}" x2="{ex:.1f}" y2="{h4_top + h4_h}" stroke="#111827" stroke-width="1.5"/>')

    metrics = (
        "Entry filters at signal candle\n"
        f"close_position={row['close_position']:.2f} >= 0.72\n"
        f"ATR%={row['atr_pct']:.2%} <= 5.00%\n"
        f"24h return={row['return_24h']:.2%} in [-2%, 12%]\n"
        f"pullback_depth={row['pullback_depth_long']:.2%} <= 5%\n"
        f"entry risk={(entry - stop) / entry:.2%}"
    )
    parts.append('<rect x="1060" y="420" width="320" height="155" rx="10" fill="#fff7ed" stroke="#fed7aa"/>')
    parts.append(svg_text(1080, 448, metrics, 14))
    parts.append(svg_text(80, 640, "下方为 4h 趋势：入场时价格在 4h EMA50 / EMA200 上方，且 BTC 4h 过滤为向上。", 16, "600"))

    legend = "颜色：紫=压缩高低点，橙=24h 前高，青=12h 回踩低点，黑=入场，红=初始止损，绿=+5% 目标"
    parts.append(svg_text(80, 865, legend, 15))
    parts.append("</svg>")

    safe_pair = pair.split("/")[0].lower()
    out = OUT / f"long_v1_entry_{idx}_{safe_pair}_{entry_time:%Y%m%d_%H%M}.svg"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    result = load_backtest("long_v1_full")
    trades = [t for t in result["trades"] if not t["is_open"]]
    picks = []
    for pair in ["BNB/USDT:USDT", "DOGE/USDT:USDT", "XRP/USDT:USDT", "ZEC/USDT:USDT"]:
        candidates = [t for t in trades if t["pair"] == pair and t["profit_ratio"] > 0]
        if candidates:
            picks.append(sorted(candidates, key=lambda t: t["open_date"])[-1])
    outputs = [plot_logic_diagram()]
    for i, trade in enumerate(picks, 1):
        outputs.append(plot_trade(trade, i))
    print("\n".join(str(p) for p in outputs))


if __name__ == "__main__":
    main()
