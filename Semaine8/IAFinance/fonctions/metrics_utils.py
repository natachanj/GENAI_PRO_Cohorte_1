import pandas as pd
import numpy as np

def max_drawdown(series: pd.Series) -> float:
    roll_max = series.cummax()
    dd = series / roll_max - 1.0
    return float(dd.min())

def compute_metrics(prices: pd.DataFrame) -> pd.DataFrame:
    rets = prices.pct_change().dropna()
    ann = 252
    rows = []
    for t in prices.columns:
        s = prices[t].dropna()
        if len(s) < 30:
            continue
        r = rets[t].dropna()
        perf_ann = (s.iloc[-1] / s.iloc[0]) ** (ann / max(len(s),1)) - 1
        vol_ann  = r.std() * np.sqrt(ann)
        mdd = max_drawdown(s)
        sma20  = s.rolling(20).mean().iloc[-1] if len(s) >= 20  else np.nan
        sma50  = s.rolling(50).mean().iloc[-1] if len(s) >= 50  else np.nan
        sma200 = s.rolling(200).mean().iloc[-1] if len(s) >= 200 else np.nan

        delta = s.diff()
        up, down = delta.clip(lower=0), -delta.clip(upper=0)
        roll_up, roll_down = up.rolling(14).mean(), down.rolling(14).mean()
        rs = (roll_up / (roll_down + 1e-9)).iloc[-1] if len(roll_up.dropna()) else np.nan
        rsi = 100 - (100 / (1 + rs)) if pd.notna(rs) else np.nan

        rows.append({
            "ticker": t,
            "price": s.iloc[-1],
            "perf_ann": perf_ann,
            "vol_ann": vol_ann,
            "mdd": mdd,
            "sma20": sma20,
            "sma50": sma50,
            "sma200": sma200,
            "rsi": rsi
        })

    df = pd.DataFrame(rows)

    def trend_state(row):
        if pd.notna(row["sma200"]):
            return "au-dessus_SMA200" if row["price"] > row["sma200"] else "sous_SMA200"
        if pd.notna(row["sma50"]):
            return "au-dessus_SMA50" if row["price"] > row["sma50"] else "sous_SMA50"
        return "inconnu"

    if not df.empty:
        df["trend"] = df.apply(trend_state, axis=1)
    return df
