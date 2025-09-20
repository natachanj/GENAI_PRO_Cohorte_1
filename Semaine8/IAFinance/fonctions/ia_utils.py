# fonctions/ia_utils.py
import time
from openai import OpenAI

def build_ia_context(profil, horizon, date, metrics_df, signals, weights, names_by_ticker):
    rows = []
    for _, r in metrics_df.iterrows():
        t = r["ticker"]
        rows.append({
            "ticker": t,
            "company": names_by_ticker.get(t, t),
            "price": float(r["price"]),
            "perf_ann": float(r["perf_ann"]),
            "vol_ann": float(r["vol_ann"]),
            "mdd": float(r["mdd"]),
            "trend": r.get("trend"),
            "sma20": float(r["sma20"]) if r["sma20"] == r["sma20"] else None,
            "sma50": float(r["sma50"]) if r["sma50"] == r["sma50"] else None,
            "sma200": float(r["sma200"]) if r["sma200"] == r["sma200"] else None,
            "rsi": float(r["rsi"]) if r["rsi"] == r["rsi"] else None,
            "signal": signals.get(t, {})
        })
    return {
        "profil": profil,
        "horizon_months": horizon,
        "date": str(date),
        "weights": weights,
        "tickers_summary": rows
    }

def generate_advice_openai(client, context_obj, model="gpt-4o-mini", max_tokens=280, retries=2, timeout=30):
    system_prompt = (
        "Tu es un conseiller pédagogique qui s'adresse à un public non initié. "
        "Rédige en français simple, phrases courtes, aucun jargon, aucun acronyme non expliqué. "
        "Ne promets jamais de performance. Bâtis des conseils concrets, actionnables, faciles à suivre."
    )

    user_prompt = (
        "À partir du CONTEXTE JSON suivant (profil, horizon, liste de titres avec "
        "nom d'entreprise, ticker, tendance, volatilité, RSI et signaux), "
        "produis un texte très simple et structuré, au format ci-dessous, sans ajouter d'autres rubriques.\n\n"
        "FORMAT EXIGÉ (strict) :\n"
        "Profil et horizon (1 ligne)\n"
        "Pour chaque titre, répète exactement ces 4 puces :\n"
        "- Idée rapide : …\n"
        "- Pourquoi : …\n"
        "- Comment : …\n"
        "- À surveiller : …\n"
        "Puis termine par :\n"
        "Règles simples pour toutes : (3 puces maximum, protection / prise de gains / diversification)\n"
        "Dernière ligne : rappel clair que c’est pédagogique, pas un conseil personnalisé.\n\n"
        f"CONTEXTE JSON :\n{context_obj}\n\n"
        "Contraintes de style :\n"
        "- Français courant (niveau lycée), pas de termes techniques non expliqués.\n"
        "- 170 à 230 mots au total.\n"
        "- Cite systématiquement les titres sous la forme « Nom (TICKER) ».\n"
    )

    import time
    last_err = None
    for _ in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            last_err = e
            time.sleep(1.2)
    raise RuntimeError(f"Echec génération IA : {last_err}")
