# fonctions/reporting.py
import pandas as pd

def _fmt_pct(x, digits=1):
    try:
        return f"{float(x):.{digits}%}"
    except Exception:
        return "-"

def _fmt_num(x, digits=2):
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return "-"

def render_report_md(
    tickers, profil, metrics_df: pd.DataFrame, signals: dict, weights: dict,
    disclaimer: str, horizon: int, date, names_by_ticker: dict
) -> str:
    lines = []
    lines.append(f"## Rapport stratégique — {date}")
    lines.append("")
    lines.append(f"**Profil :** {profil} &nbsp;&nbsp;|&nbsp;&nbsp; **Horizon :** {horizon} mois")
    lines.append("")
    lines.append(f"> {disclaimer}")
    lines.append("")
    # Tableau des métriques
    lines.append("### Indicateurs clés")
    cols = ["Entreprise", "Prix", "Perf annuelle", "Vol annuelle", "Max Drawdown", "Tendance", "RSI", "SMA20", "SMA50", "SMA200"]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + " --- |"*len(cols))

    for _, row in metrics_df.iterrows():
        t = row["ticker"]
        name = names_by_ticker.get(t, t)
        ent = f"{name} ({t})"
        price = _fmt_num(row["price"])
        perf  = _fmt_pct(row["perf_ann"])
        vol   = _fmt_pct(row["vol_ann"])
        mdd   = _fmt_pct(row["mdd"])
        trend = str(row.get("trend","-"))
        rsi   = _fmt_num(row.get("rsi"),1)
        sma20 = _fmt_num(row.get("sma20"))
        sma50 = _fmt_num(row.get("sma50"))
        sma200= _fmt_num(row.get("sma200"))
        lines.append(f"| {ent} | {price} | {perf} | {vol} | {mdd} | {trend} | {rsi} | {sma20} | {sma50} | {sma200} |")

    lines.append("")
    # Signaux & pondérations
    lines.append("### Signaux & pondérations")
    for t in tickers:
        if t not in signals: 
            continue
        s = signals[t]; w = weights.get(t, 0.0)
        name = names_by_ticker.get(t, t)
        lines.append(f"- **{name} ({t})** — *Action* : {s['action']} &nbsp;|&nbsp; *Stop* : {s['stop']} &nbsp;|&nbsp; *TP* : {s['tp']} &nbsp;|&nbsp; *Poids* : {int(round(w*100))}%")

    lines.append("")
    # Notes
    lines += [
        "### Rappels méthodologiques",
        "- DCA = achats périodiques montants constants ; Lump sum = en 1 à 3 tranches selon volatilité.",
        "- Les règles sont déterministes (SMA/RSI) et à adapter au contexte de marché.",
        "- Respectez la discipline de **gestion du risque** (stops/prise de profits, taille de position)."
    ]
    return "\n".join(lines)
