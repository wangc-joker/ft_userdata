import json
import pandas as pd
from pathlib import Path
import importlib.util
import sys

root = Path('/freqtrade')
strategies = root / 'user_data' / 'strategies'
config_path = root / 'user_data' / 'config.backtest.futures.top9.json'
user_data = root / 'user_data'
data1h = root / 'user_data' / 'data' / 'binance' / 'futures' / 'ZEC_USDT_USDT-1h-futures.feather'
data1d = root / 'user_data' / 'data' / 'binance' / 'futures' / 'ZEC_USDT_USDT-1d-futures.feather'
if str(user_data) not in sys.path:
    sys.path.insert(0, str(user_data))
if str(strategies) not in sys.path:
    sys.path.insert(0, str(strategies))
config = json.loads(config_path.read_text(encoding='utf-8'))
config.setdefault('candle_type_def', 'futures')
config.setdefault('runmode', 'backtest')

def load_strategy(name):
    path = strategies / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = getattr(mod, name)
    cfg = dict(config)
    cfg['strategy'] = name
    return cls(cfg)

def read_feather(path):
    df = pd.read_feather(path)
    df['date'] = pd.to_datetime(df['date'], utc=True)
    return df

pair = 'ZEC/USDT:USDT'
raw1h = read_feather(data1h)
raw1d = read_feather(data1d)

class DP:
    def historic_ohlcv(self, pair_, timeframe, candle_type=''):
        return self.get_pair_dataframe(pair_, timeframe, candle_type)
    def get_pair_dataframe(self, pair_, timeframe, candle_type=''):
        if timeframe == '1d':
            return raw1d.copy()
        if timeframe == '1h':
            return raw1h.copy()
        raise KeyError(timeframe)
    def market(self, pair_):
        return {'quote': 'USDT', 'base': 'ZEC', 'spot': False}

base = load_strategy('Top9RegimeMainBreakoutProbeStrategy')
narrow = load_strategy('Top9RegimeMainExhaustionProbeBaseOnlyStrategy')
for strat in (base, narrow):
    strat.dp = DP()

base_map = base.advise_all_indicators({pair: raw1h.copy()})
narrow_map = narrow.advise_all_indicators({pair: raw1h.copy()})
base_df = base.populate_entry_trend(base_map[pair].copy(), {'pair': pair})
narrow_df = narrow.populate_entry_trend(narrow_map[pair].copy(), {'pair': pair})
idx = pd.Timestamp('2026-04-07 21:00:00', tz='UTC')
cols = [
    'close','high','open','volume','major_high_72','major_high_168','trade_center_shift_up',
    'near_major_high','high_base_compression','base_tight','major_breakout','breakout_volume_expansion',
    'bull_body_expansion','rsi','rsi_1d','downtrend_1d','bear_exhaustion_1d','daily_center_lifting',
    'mature_high_base','breakout_close_near_high','breakout_body_strength','breakout_distance_ok',
    'breakout_daily_bias_ok','long_breakout_probe','enter_long','enter_tag'
]
out = {}
for label, frame in [('base', base_df), ('narrow', narrow_df)]:
    row = frame.loc[frame['date'] == idx].iloc[0]
    out[label] = {}
    for c in cols:
        if c in frame.columns:
            v = row[c]
            try:
                import numpy as np
                if isinstance(v, np.generic):
                    v = v.item()
            except Exception:
                pass
            if pd.isna(v):
                v = None
            out[label][c] = v
print(json.dumps(out, ensure_ascii=False, indent=2, default=str))