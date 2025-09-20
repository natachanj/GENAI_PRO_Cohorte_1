# app.py — LeCoinStat Invest (IA décide la répartition, détails visibles, sans graphiques)

import matplotlib
matplotlib.use("Agg")  # backend non-GUI

import os, json
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # requis (même si non affiché)
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# Fonctions locales
from fonctions import (
    load_prices, compute_metrics, rules_engine,
    render_report_md, build_ia_context, generate_advice_openai,
    detect_tickers, resolve_company_names
)

load_dotenv()

# ---------- Identité & mentions ----------
APP_TITLE = "LeCoinStat Invest — Conseiller d'actions"
SUBTITLE  = "Analyse claire, plan d’achat et budget guidé."
DISCLAIMER = (
    "Contenu éducatif. Pas un conseil en investissement personnalisé. "
    "Faites vos propres vérifications (DYOR). Les performances passées ne sont pas garanties."
)

# ---------- Helpers “français simple” ----------
def vol_bucket(vol):
    if vol is None or (isinstance(vol, float) and np.isnan(vol)): return "indéterminée"
    if vol < 0.20: return "faible"
    if vol < 0.30: return "moyenne"
    return "élevée"

def trend_sentence(trend):
    if trend == "au-dessus_SMA200":
        return "Tendance plutôt positive (au-dessus de la moyenne long terme)."
    if trend == "au-dessus_SMA50":
        return "Tendance courte positive (au-dessus de la moyenne récente)."
    if trend == "sous_SMA200":
        return "Sous la moyenne long terme : prudence."
    if trend == "sous_SMA50":
        return "Sous la moyenne récente : prudence."
    return "Tendance difficile à déterminer."

def rsi_sentence(rsi):
    if rsi is None or (isinstance(rsi, float) and np.isnan(rsi)): return "RSI non disponible."
    if rsi >= 70: return f"RSI {rsi:.0f} : niveau élevé (possible surchauffe)."
    if rsi <= 30: return f"RSI {rsi:.0f} : niveau bas (possible survendu)."
    return f"RSI {rsi:.0f} : zone neutre."

def action_sentence(sig_action, stop, tp):
    a = (sig_action or "").lower()
    if "attendre" in a:
        base = "Attente recommandée (tendance peu favorable)"
    elif "50%" in a:
        base = "50% maintenant + reste en achats étalés"
    elif "lump" in a:
        base = "Achat en une ou deux fois"
    else:
        base = "Achats étalés chaque mois"
    stop_txt = f"Protection ≈ {stop:.0%}" if isinstance(stop, (int, float)) else f"Protection : {stop}"
    tp_txt   = f"Prise de gains ≈ {tp:.0%}" if isinstance(tp, (int, float)) else f"Prise de gains : {tp}"
    return f"{base}. {stop_txt}. {tp_txt}."

# ---------- Rendu cartes ----------
def make_cards_md(metrics_df, signals, weights, names_by_ticker, alloc_df=None):
    alloc_map = {}
    if alloc_df is not None and not alloc_df.empty:
        for _, r in alloc_df.iterrows():
            alloc_map[r["ticker"]] = {
                "total": r["total"], "now": r["now"],
                "per_month": r["per_month"], "months": int(r["months"]),
                "mode": r["mode"]
            }

    cards = []
    for _, row in metrics_df.iterrows():
        t = row["ticker"]
        name = names_by_ticker.get(t, t)
        price = row["price"]
        vb = vol_bucket(row.get("vol_ann"))
        trend = trend_sentence(row.get("trend"))
        rsi_txt = rsi_sentence(row.get("rsi"))
        sig = signals.get(t, {})
        action_txt = action_sentence(sig.get("action",""), sig.get("stop","-"), sig.get("tp","-"))
        weight = int(round(weights.get(t, 0.0)*100))

        alloc_line = ""
        if t in alloc_map:
            a = alloc_map[t]
            if a["per_month"] > 0:
                alloc_line = f'<li><strong>Budget :</strong> total ≈ {a["total"]:.0f} € | maintenant ≈ {a["now"]:.0f} € | achats étalés ≈ {a["per_month"]:.0f} €/mois × {a["months"]} (mode : {a["mode"]})</li>'
            else:
                alloc_line = f'<li><strong>Budget :</strong> total ≈ {a["total"]:.0f} € | maintenant ≈ {a["now"]:.0f} € (mode : {a["mode"]})</li>'

        card = f"""
<div class="card">
  <div class="card-header">{name} ({t})</div>
  <div class="card-body">
    <p><strong>Prix actuel :</strong> {price:.2f}</p>
    <ul>
      <li><strong>Tendance :</strong> {trend}</li>
      <li><strong>Variations de prix :</strong> {vb}</li>
      <li><strong>RSI :</strong> {rsi_txt}</li>
      <li><strong>Comment procéder :</strong> {action_txt}</li>
      <li><strong>Pondération proposée :</strong> {weight}%</li>
      {alloc_line}
    </ul>
  </div>
</div>
"""
        cards.append(card)
    return "\n".join(cards)

# ---------- IA : décider les poids ----------
def decide_weights_with_ai(client, metrics_df: pd.DataFrame, profil: str, model="gpt-4o-mini", retries=2, timeout=30):
    """
    Demande à l'IA des poids par ticker qui :
      - sont entre 0 et 0.6,
      - somment à 1,
      - respectent le profil (prudent/équilibre/dynamique).
    Retourne (weights: dict[ticker->float], rationale: str).
    """
    ctx = {
        "profil": profil,
        "tickers": [
            {
                "ticker": r["ticker"],
                "perf_ann": float(r["perf_ann"]),
                "vol_ann": float(r["vol_ann"]),
                "mdd": float(r["mdd"]),
                "trend": r.get("trend"),
                "rsi": None if pd.isna(r.get("rsi")) else float(r["rsi"])
            } for _, r in metrics_df.iterrows()
        ],
        "constraints": {
            "max_weight": 0.60,
            "sum_to_one": True,
            "min_assets": min(2, len(metrics_df))
        },
        "guidelines": {
            "prudent": "favoriser volatilité plus faible et drawdown réduit; éviter RSI>75",
            "equilibre": "mix entre momentum/tendance et risque modéré",
            "dynamique": "favoriser momentum/tendance forte même si volatilité plus élevée; éviter RSI>80"
        }
    }

    system = (
        "Tu es un assistant d'allocation de portefeuille. "
        "RÉPONDS UNIQUEMENT en JSON valide. "
        "Calcule des poids par titre qui respectent: 0<=w<=0.6, somme=1. "
        "Tiens compte du profil de risque et des métriques fournies. "
        "Retourne un JSON: {\"weights\": {\"AAPL\":0.35,...}, \"rationale\":\"(≤120 mots FR)\"}."
    )
    user = f"Contexte pour allouer les poids (FR) :\n{json.dumps(ctx, ensure_ascii=False)}"

    last_err = None
    for _ in range(retries+1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                temperature=0.1,
                max_tokens=300,
                timeout=timeout
            )
            content = resp.choices[0].message.content.strip()
            data = json.loads(content)
            weights = data.get("weights", {})
            rationale = data.get("rationale", "").strip()
            # nettoyage basique
            weights = {k.upper(): float(v) for k,v in weights.items() if isinstance(v,(int,float))}
            s = sum(max(0.0, min(0.6, w)) for w in weights.values())
            if s <= 0:
                raise ValueError("Somme des poids IA nulle.")
            # renormalisation pour somme=1
            weights = {k: max(0.0, min(0.6, w))/s for k,w in weights.items()}
            return weights, rationale
        except Exception as e:
            last_err = e
    raise RuntimeError(f"IA allocation échouée: {last_err}")

# ---------- Heuristique (fallback) : décide des poids sans IA ----------
def heuristic_weights(metrics_df: pd.DataFrame, profil: str) -> dict:
    """
    Score = momentum positif / risque, avec bonus tendance et pénalité RSI élevé.
    Ajuste selon profil (prudent/équilibre/dynamique). Somme normalisée à 1 et cap à 0.6.
    """
    scores = {}
    for _, r in metrics_df.iterrows():
        t = r["ticker"]
        perf = max(0.0, float(r["perf_ann"]))
        vol  = float(r["vol_ann"]) if r["vol_ann"]==r["vol_ann"] else 0.3
        mdd  = abs(float(r["mdd"])) if r["mdd"]==r["mdd"] else 0.3
        rsi  = float(r["rsi"]) if r["rsi"]==r["rsi"] else 50.0
        trend = r.get("trend","inconnu")

        trend_bonus = 0.15 if trend=="au-dessus_SMA200" else (0.05 if trend=="au-dessus_SMA50" else 0.0)
        rsi_mult = 0.75 if rsi>=75 else (1.05 if rsi<=30 else 1.0)

        # profil
        if profil == "prudent":
            base = (perf + trend_bonus) / max(1e-6, (vol*1.4 + mdd*0.8))
        elif profil == "dynamique":
            base = (perf*1.4 + trend_bonus*1.2) / max(1e-6, (vol*0.9 + mdd*0.6))
        else:  # équilibre
            base = (perf*1.1 + trend_bonus) / max(1e-6, (vol*1.1 + mdd*0.7))

        score = max(0.0, base) * rsi_mult
        scores[t] = score

    total = sum(scores.values())
    if total <= 0:
        # égal-pondéré si tout nul
        n = len(metrics_df)
        return {r["ticker"]: 1.0/n for _, r in metrics_df.iterrows()}

    # normalise + cap 0.6
    weights = {t: s/total for t,s in scores.items()}
    # cap soft : si >0.6, on plafonne puis on renormalise
    capped = {t: min(0.6, w) for t,w in weights.items()}
    s = sum(capped.values())
    weights = {t: w/s for t,w in capped.items()}
    return weights

# ---------- Allocation à partir du budget ----------
def build_allocation_plan(metrics_df, signals, weights, budget: float, months: int):
    rows = []
    for _, row in metrics_df.iterrows():
        t = row["ticker"]
        w = float(weights.get(t, 0.0))
        total = float(budget) * w
        s = signals.get(t, {})
        action = str(s.get("action", "")).lower()

        if "attendre" in action:
            now = 0.0
            stagger_total = total
            per_month = (stagger_total / months) if months > 0 else 0.0
            mode = "Attente / achats étalés"
        elif "50%" in action:
            now = 0.5 * total
            stagger_total = 0.5 * total
            per_month = (stagger_total / months) if months > 0 else 0.0
            mode = "50% maintenant + étalé"
        elif "lump" in action:
            now = total
            stagger_total = 0.0
            per_month = 0.0
            mode = "Une ou deux fois"
        else:
            now = 0.0
            stagger_total = total
            per_month = (stagger_total / months) if months > 0 else 0.0
            mode = "Achats étalés"

        rows.append({
            "ticker": t,
            "weight": w,
            "total": total,
            "now": now,
            "per_month": per_month,
            "months": months,
            "mode": mode,
            "stop": s.get("stop"),
            "tp": s.get("tp")
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        total_row = {
            "ticker": "TOTAL",
            "weight": df["weight"].sum(),
            "total": df["total"].sum(),
            "now": df["now"].sum(),
            "per_month": df["per_month"].sum(),
            "months": months, "mode": "", "stop": "", "tp": ""
        }
        df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df

def allocation_table_for_display(alloc_df, names_by_ticker):
    if alloc_df is None or alloc_df.empty:
        return pd.DataFrame()
    df = alloc_df.copy()
    df["titre"] = df["ticker"].map(lambda t: "TOTAL" if t=="TOTAL" else f"{names_by_ticker.get(t,t)} ({t})")
    def euro(x):
        try: return f"{float(x):,.0f} €".replace(",", " ")
        except: return x
    def pct(x):
        try: return f"{float(x)*100:.0f}%"
        except: return x
    df["poids"]         = df["weight"].apply(lambda v: "-" if isinstance(v, str) else pct(v))
    df["montant_total"] = df["total"].apply(euro)
    df["maintenant"]    = df["now"].apply(euro)
    df["mensuel"]       = df["per_month"].apply(euro)
    df["mois"]          = df["months"]
    df["mode"]          = df["mode"].astype(str)
    return df[["titre","poids","montant_total","maintenant","mensuel","mois","mode"]]

# ---------- Projection indicative ----------
def monthly_stats_from_history(prices: pd.DataFrame, lookback_days: int = 252):
    stats = {}
    for t in prices.columns:
        s = prices[t].dropna().iloc[-lookback_days:]
        if len(s) < 22:
            continue
        lr = np.log(s).diff().dropna()
        mu_d, sig_d = lr.mean(), lr.std()
        mu_m = mu_d * 21
        sig_m = sig_d * np.sqrt(21)
        g_med = float(np.exp(mu_m))
        g_low = float(np.exp(mu_m - sig_m))
        g_high= float(np.exp(mu_m + sig_m))
        stats[t] = {"g_med": g_med, "g_low": g_low, "g_high": g_high, "days": len(lr)}
    return stats

def _series_future_value(per_month, months, growth):
    if months <= 0 or per_month <= 0:
        return 0.0
    if abs(growth - 1.0) < 1e-9:
        return per_month * months
    return per_month * (growth**months - 1) / (growth - 1)

def project_portfolio(prices, alloc_df, months, lookback_days=252):
    if alloc_df is None or alloc_df.empty:
        return pd.DataFrame(), 0
    alloc = alloc_df[alloc_df["ticker"] != "TOTAL"].copy()
    stats = monthly_stats_from_history(prices, lookback_days=lookback_days)
    rows = []; days_used = 0
    for _, r in alloc.iterrows():
        t = r["ticker"]
        st = stats.get(t)
        if not st: 
            continue
        days_used = max(days_used, st["days"])
        g_med, g_low, g_high = st["g_med"], st["g_low"], st["g_high"]
        now = float(r["now"]); pm  = float(r["per_month"])
        invested = now + pm * months
        fv_low  = now * (g_low**months)  + _series_future_value(pm, months, g_low)
        fv_med  = now * (g_med**months)  + _series_future_value(pm, months, g_med)
        fv_high = now * (g_high**months) + _series_future_value(pm, months, g_high)
        rows.append({
            "ticker": t, "investi": invested,
            "final_bas": fv_low, "final_median": fv_med, "final_haut": fv_high,
            "gain_bas": fv_low - invested, "gain_median": fv_med - invested, "gain_haut": fv_high - invested
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        total = {
            "ticker": "TOTAL",
            "investi": df["investi"].sum(),
            "final_bas": df["final_bas"].sum(),
            "final_median": df["final_median"].sum(),
            "final_haut": df["final_haut"].sum(),
            "gain_bas": df["gain_bas"].sum(),
            "gain_median": df["gain_median"].sum(),
            "gain_haut": df["gain_haut"].sum()
        }
        df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)
    return df, days_used

def projection_table_for_display(proj_df, names_by_ticker):
    if proj_df is None or proj_df.empty:
        return pd.DataFrame()
    df = proj_df.copy()
    def euro(x):
        try: return f"{float(x):,.0f} €".replace(",", " ")
        except: return x
    df["titre"] = df["ticker"].map(lambda t: "TOTAL" if t=="TOTAL" else f"{names_by_ticker.get(t,t)} ({t})")
    df["investi"]       = df["investi"].apply(euro)
    df["final (bas)"]   = df["final_bas"].apply(euro)
    df["final (médian)"]= df["final_median"].apply(euro)
    df["final (haut)"]  = df["final_haut"].apply(euro)
    df["gain (bas)"]    = df["gain_bas"].apply(euro)
    df["gain (médian)"] = df["gain_median"].apply(euro)
    df["gain (haut)"]   = df["gain_haut"].apply(euro)
    return df[["titre","investi","final (bas)","final (médian)","final (haut)","gain (bas)","gain (médian)","gain (haut)"]]

def projection_md(days_used, months):
    if days_used <= 0:
        return ""
    approx_months = max(1, int(round(days_used/21)))
    return (
        f"### Projection indicative (non garantie)\n"
        f"- Basée sur ~{days_used} jours (~{approx_months} mois) d’historique récent.\n"
        f"- Appliquée au plan d’achats (maintenant + étalés sur {months} mois).\n"
        f"- Ce n’est **pas** une prévision : juste un repère d’ordre de grandeur."
    )

# ---------- Pipeline (avec progression) ----------
def run_pipeline(assets_text, budget, stagger_months, horizon, profil, user_api_key, progress=gr.Progress(track_tqdm=True)):
    EMPTY_DF = pd.DataFrame()

    # 0) Clé IA optionnelle
    progress(0.02, desc="Préparation…")
    api_key = (user_api_key or os.getenv("OPENAI_API_KEY", "")).strip()
    client = OpenAI(api_key=api_key) if api_key else None

    # 1) Entrées + détection titres
    assets_text = (assets_text or "").strip()
    if not assets_text:
        return ("Veuillez saisir au moins un titre (ex. Apple, Microsoft).", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")

    try:
        budget = float(budget)
        if budget <= 0:
            return ("Veuillez entrer un **budget positif** (en €).", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")
    except Exception:
        return ("Budget invalide. Exemple : 5000", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")

    progress(0.10, desc="Identification des titres…")
    tickers = detect_tickers(assets_text, client=client)
    if not tickers:
        msg = "Impossible d’identifier des titres valides."
        if not api_key:
            msg += " Astuce : ajoutez une clé OpenAI ou saisissez directement les tickers (ex. AAPL, MSFT)."
        return (msg, "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")

    END_DATE = dt.date.today()
    START_DATE = END_DATE - dt.timedelta(days=int(horizon)*30)

    # 2) Données
    progress(0.30, desc="Chargement des données de marché…")
    try:
        prices = load_prices(tickers, START_DATE, END_DATE)
    except Exception as e:
        return (f"Erreur chargement des données : {e}", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")

    # 3) Métriques + signaux
    progress(0.55, desc="Analyse & signaux…")
    try:
        metrics = compute_metrics(prices)
        if metrics.empty:
            return ("Pas assez de données pour calculer les indicateurs.", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")
        signals, _equal = rules_engine(metrics, profil)  # on ignore l'égal-pondéré
    except Exception as e:
        return (f"Erreur sur les calculs : {e}", "—", "—", "—", EMPTY_DF, EMPTY_DF, "—")

    # 4) Décision des poids (IA d'abord, sinon heuristique)
    progress(0.68, desc="Décision de la répartition…")
    alloc_expl = ""
    if client is not None:
        try:
            ai_w, rationale = decide_weights_with_ai(client, metrics, profil)
            # garde uniquement les tickers présents, renormalise
            ai_w = {t: ai_w.get(t, 0.0) for t in metrics["ticker"]}
            s = sum(ai_w.values())
            if s <= 0:
                raise ValueError("Somme IA nulle")
            weights = {t: w/s for t, w in ai_w.items()}
            alloc_expl = f"**Répartition IA :** {', '.join([f'{t} {int(round(w*100))}% ' for t,w in weights.items()])}\n\n> {rationale}"
        except Exception:
            weights = heuristic_weights(metrics, profil)
            alloc_expl = "Répartition automatique (sans IA) basée sur tendance/volatilité/drawdown."
    else:
        weights = heuristic_weights(metrics, profil)
        alloc_expl = "Répartition automatique (sans IA) basée sur tendance/volatilité/drawdown."

    # 5) Allocation du budget avec ces poids
    names_by_ticker = resolve_company_names(list(metrics["ticker"]))
    alloc_df = build_allocation_plan(metrics, signals, weights, budget, int(stagger_months))
    alloc_display = allocation_table_for_display(alloc_df, names_by_ticker)
    budget_header = (
        f"### Répartition du budget — {budget:.0f} €\n"
        f"- Achats étalés sur **{int(stagger_months)} mois** lorsque c’est indiqué par la stratégie.\n"
        f"- Objectif : **entrer progressivement** et **protéger** (limites de perte / prise de gains)."
    )

    # 6) Cartes & résumé
    header_md = f"### LeCoinStat Invest — Plan (profil {profil}, horizon {horizon} mois) — {END_DATE}\n\n> {DISCLAIMER}\n"
    cards_md = make_cards_md(metrics, signals, weights, names_by_ticker, alloc_df=alloc_df)
    summary_md = header_md + "\n" + cards_md

    # 7) Projection indicative
    progress(0.86, desc="Projection indicative…")
    proj_df, used_days = project_portfolio(prices, alloc_df, int(stagger_months))
    proj_display = projection_table_for_display(proj_df, names_by_ticker)
    proj_md = projection_md(used_days, int(stagger_months))

    # 8) Conseil IA (facultatif)
    progress(0.93, desc="Rédaction du conseil…")
    advice_text = "_Conseil automatique désactivé (aucune clé OpenAI fournie)._"
    if client is not None:
        try:
            ctx = build_ia_context(profil, horizon, END_DATE, metrics, signals, weights, names_by_ticker)
            ctx["budget_eur"] = float(budget)
            ctx["stagger_months"] = int(stagger_months)
            ctx["allocation_plan"] = alloc_df.to_dict(orient="records")
            ctx["projection"] = proj_df.to_dict(orient="records") if not proj_df.empty else []
            advice_text = generate_advice_openai(client, ctx)
        except Exception:
            advice_text = (
                "Synthèse : suivez le plan ci-dessus (montant maintenant + achats étalés). "
                "Pensez aux **limites de perte** (~10–12 %) et à la **prise de gains** (~15–20 %). "
                "La projection est indicative (non garantie)."
            )

    # 9) Détails chiffrés & Rapport
    progress(0.98, desc="Préparation des détails…")
    metrics_out = metrics[["ticker","price","perf_ann","vol_ann","mdd","trend","rsi","sma20","sma50","sma200"]].copy()
    metrics_out["ticker"] = metrics_out["ticker"].map(lambda t: f"{names_by_ticker.get(t,t)} ({t})")
    metrics_out = metrics_out.rename(columns={"ticker":"titre"}).round(4)

    report_md = render_report_md(
        tickers=tickers, profil=profil, metrics_df=metrics, signals=signals, weights=weights,
        disclaimer=DISCLAIMER, horizon=horizon, date=END_DATE, names_by_ticker=names_by_ticker
    )

    return (summary_md, advice_text, budget_header, alloc_expl, alloc_display, proj_md, proj_display, metrics_out, report_md)

# ---------- UI (sans graphiques, détails toujours visibles) ----------
THEME = gr.themes.Soft(primary_hue="blue", neutral_hue="slate")
CSS = """
body { background: #f6f8fb; }
.gradio-container { max-width: 1080px !important; }
.header {
  background: linear-gradient(135deg,#0f5fff 0%,#7aa6ff 100%);
  color: white; padding: 18px 20px; border-radius: 14px; margin-bottom: 16px;
}
.header h1 { margin: 0; font-size: 22px; font-weight: 600; }
.header p { margin: 6px 0 0 0; opacity: .95; }
.card {
  border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px 16px; margin: 12px 0;
  background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.card-header { font-weight: 600; font-size: 15px; margin-bottom: 8px; }
.card-body p { margin: 0 0 6px 0; }
.card-body ul { margin: 0; padding-left: 16px; }
"""

with gr.Blocks(title=APP_TITLE, theme=THEME, css=CSS) as demo:
    gr.HTML(f'<div class="header"><h1>LeCoinStat Invest</h1><p>{SUBTITLE}</p></div>')

    with gr.Tab("Analyse"):
        with gr.Row():
            assets = gr.Textbox(
                label="Titres (noms ou tickers, séparés par des virgules)",
                value="Apple, Microsoft, Alphabet",
                placeholder="Exemples : Apple, Microsoft, LVMH ou AAPL, MSFT, MC.PA"
            )
        with gr.Row():
            budget = gr.Number(label="Budget total (€)", value=5000, precision=0)
            stagger_months = gr.Slider(3, 12, value=6, step=1, label="Achats étalés : nombre de mois")
        with gr.Row():
            profil = gr.Radio(choices=["prudent","equilibre","dynamique"], value="equilibre", label="Votre profil")
            horizon = gr.Slider(3, 60, value=12, step=1, label="Horizon (mois)")
        with gr.Row():
            api_key_box = gr.Textbox(
                label="OpenAI API Key (facultatif — pour détecter les noms et décider la répartition)",
                type="password", placeholder="sk-..."
            )

        run_btn = gr.Button("Générer", variant="primary", scale=1)

        with gr.Tab("Résumé"):
            summary_md = gr.Markdown()
            advice_md = gr.Markdown()

        with gr.Tab("Budget — Répartition"):
            budget_md = gr.Markdown()
            alloc_expl_md = gr.Markdown()   # justification IA / heuristique
            alloc_df = gr.Dataframe(wrap=True)

        with gr.Tab("Projection (indicative)"):
            proj_md = gr.Markdown()
            proj_df = gr.Dataframe(wrap=True)

        with gr.Tab("Détails chiffrés"):
            metrics_df = gr.Dataframe(wrap=True)

        with gr.Tab("Rapport complet"):
            report_md = gr.Markdown()

        run_btn.click(
            fn=run_pipeline,
            inputs=[assets, budget, stagger_months, horizon, profil, api_key_box],
            outputs=[summary_md, advice_md, budget_md, alloc_expl_md, alloc_df, proj_md, proj_df, metrics_df, report_md]
        )

    with gr.Tab("Guide"):
        gr.Markdown(
"""
## À quoi sert l’application ?
- Donner des **idées d’actions** en français simple.
- **Décider automatiquement la répartition** entre vos titres (par l’IA si clé fournie).
- Construire un **plan d’achat** : une partie maintenant, le reste en **achats étalés** (mensuels).
- Répartir votre **budget** et afficher une **projection indicative** (bas/médian/haut).
- Rappeler la **gestion du risque** (limites de perte, prise de gains, tailles de position).

## Comment l’utiliser ?
1. Tapez des **noms** (Apple, Microsoft) ou des **tickers** (AAPL, MSFT).
2. Entrez votre **budget total** et le **nombre de mois** pour étaler vos achats.
3. Choisissez votre **profil** et votre **horizon**, puis cliquez sur **Générer**.
4. L’onglet *Budget — Répartition* montre les **montants** et la **justification** (IA ou automatique).

## Limites
- Outil **pédagogique**, pas un conseil personnalisé.
- Poids IA : **contraints** (0–60 % par titre, somme=100 %), mais à valider par vous.
- La projection est **indicative** et **non garantie**.
"""
        )

if __name__ == "__main__":
    try:
        demo.queue().launch(debug=True)  # barre de progression active
    except TypeError:
        demo.launch(debug=True)
