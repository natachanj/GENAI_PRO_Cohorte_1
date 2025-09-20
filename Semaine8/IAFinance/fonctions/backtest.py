import pandas as pd
from .metrics_utils import max_drawdown

def backtest_sma50(series: pd.Series):
    """
    Backtest simple : Buy&Hold vs. stratégie SMA50 (100% investi si prix > SMA50).
    """
    s = series.dropna()
    sma50 = s.rolling(50).mean()
    pos = (s > sma50).astype(int)
    r = s.pct_change().fillna(0.0)
    ret_sma = (pos.shift(1).fillna(0) * r)
    ret_bh  = r
    df = pd.DataFrame({
        "eq_sma50": (1+ret_sma).cumprod(),
        "eq_bh": (1+ret_bh).cumprod()
    })
    return df
