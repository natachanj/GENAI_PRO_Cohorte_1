# fonctions/symbols.py
import re, time
from typing import List, Dict, Tuple
import yfinance as yf

# Heuristique rapide : ressemble à un ticker US ?
_TICKER_RE = re.compile(r"^[A-Z][A-Z0-9\.\-]{0,7}$")

def _looks_like_ticker(token: str) -> bool:
    return bool(_TICKER_RE.match(token.strip().upper()))

def validate_tickers_yf(tickers: List[str], min_rows: int = 5) -> List[str]:
    """Garde les tickers qui ont au moins quelques lignes d'historique récent."""
    out = []
    for t in tickers:
        try:
            df = yf.Ticker(t).history(period="6mo", auto_adjust=False)
            if df is not None and len(df) >= min_rows:
                out.append(t)
        except Exception:
            continue
        time.sleep(0.05)  # éviter de spammer
    return out

def resolve_company_names(tickers: List[str]) -> Dict[str, str]:
    """Mappe ticker -> nom officiel (longName/shortName), fallback au ticker."""
    names = {}
    for t in tickers:
        name = t
        try:
            info = yf.Ticker(t).get_info()
            name = info.get("longName") or info.get("shortName") or t
        except Exception:
            pass
        names[t] = name
        time.sleep(0.05)
    return names

# ---------- Détection via IA (OpenAI) ----------
def guess_tickers_with_ai(assets_text: str, client, model: str = "gpt-4o-mini") -> List[Tuple[str, str]]:
    """
    Retourne une liste (ticker, company_name) devinée à partir du texte utilisateur.
    Format de sortie attendu du modèle : une liste JSON d'objets {ticker, company}
    """
    sys = (
        "Tu es un assistant financier. À partir d'une liste d'actifs ou de noms d'entreprises, "
        "renvoie uniquement un JSON de la forme "
        "[{\"ticker\":\"AAPL\",\"company\":\"Apple Inc.\"}, ...]. "
        "Utilise les tickers US (NASDAQ/NYSE) quand c'est pertinent. "
        "Ne renvoie rien d'autre que ce JSON."
    )
    user = f"Actifs saisis: {assets_text}\nExtrait les tickers et les noms officiels."

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.0,
        max_tokens=300
    )
    content = resp.choices[0].message.content.strip()

    import json
    try:
        data = json.loads(content)
        out = []
        for item in data:
            tick = str(item.get("ticker","")).strip().upper()
            comp = str(item.get("company","")).strip()
            if tick:
                out.append((tick, comp or tick))
        return out
    except Exception:
        # fallback extrêmement simple: découpe par coma/espace et garde les tokens "ticker-like"
        tokens = re.split(r"[,\s;]+", assets_text)
        return [(tok.upper(), tok.upper()) for tok in tokens if _looks_like_ticker(tok)]

def detect_tickers(assets_text: str, client=None) -> List[str]:
    """
    Détecte des tickers à partir d'un texte (noms ou tickers).
    - Si tout ressemble déjà à des tickers : renvoie tel quel (après validation).
    - Sinon : si client OpenAI fourni -> IA pour mapper nom -> ticker, puis validation.
    """
    raw_tokens = [t for t in re.split(r"[,\s;]+", assets_text) if t.strip()]
    if raw_tokens and all(_looks_like_ticker(t) for t in raw_tokens):
        return validate_tickers_yf([t.upper() for t in raw_tokens])

    if client is None:
        # Sans IA : on ne peut pas convertir des noms -> tickers de façon fiable
        # On tente une validation naïve de tokens qui ressemblent à des tickers
        maybe = [t.upper() for t in raw_tokens if _looks_like_ticker(t)]
        return validate_tickers_yf(maybe)

    # IA -> tickers, puis validation Yahoo
    pairs = guess_tickers_with_ai(assets_text, client)
    guessed = [t for (t, _) in pairs]
    return validate_tickers_yf(guessed)
