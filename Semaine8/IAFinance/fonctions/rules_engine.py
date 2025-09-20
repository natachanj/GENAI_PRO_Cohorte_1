import pandas as pd

def rules_engine(metrics_df: pd.DataFrame, profil: str):
    """
    Renvoie : signals (action/stop/tp), weights (égal-pondéré par défaut).
    Règles simples et transparentes par profil.
    """
    profil = profil.lower().strip()
    n = len(metrics_df)
    weights = {t: 1.0/n for t in metrics_df["ticker"]} if n > 0 else {}
    signals = {}

    for _, row in metrics_df.iterrows():
        t = row["ticker"]

        has200 = pd.notna(row["sma200"])
        cond_up200 = (row["price"] > row["sma200"]) if has200 else False
        cond_up50  = (row["price"] > row["sma50"]) if pd.notna(row["sma50"]) else False
        cond_stack = (row["sma20"] > row["sma50"] > row["sma200"]) if (pd.notna(row["sma20"]) and pd.notna(row["sma50"]) and pd.notna(row["sma200"])) else False
        rsi_ok = (row["rsi"] < 70) if pd.notna(row["rsi"]) else True

        if profil == "prudent":
            if has200 and cond_up200:
                action, stop, tp = "DCA mensuel", -0.10, 0.15
            else:
                action, stop, tp = "Attendre (sous SMA200)", -0.10, 0.15

        elif profil == "equilibre":
            cond = ((cond_up200 if has200 else cond_up50) and cond_up50)
            action = "50% DCA + 50% lump sum" if cond else "DCA mensuel"
            stop, tp = -0.12, 0.20

        else:  # dynamique
            cond = (cond_stack or (cond_up50 and (row["sma50"] > row["sma200"] if pd.notna(row["sma200"]) else True))) and rsi_ok
            action = "Lump sum" if cond else "Attendre ou DCA"
            stop, tp = -0.15, "trailing 10%"

        signals[t] = {"action": action, "stop": stop, "tp": tp}

    return signals, weights
