# Imports communs
import os, datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI

# Libs locales
from fonctions import (
    load_prices, compute_metrics, rules_engine,
    render_report_text, build_ia_context, generate_advice_openai,
    backtest_sma50
)

# Style matplotlib
plt.rcParams['figure.figsize'] = (8,4)
plt.rcParams['axes.grid'] = True

# Chargement clé API
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")
print("OPENAI_API_KEY défini :", api_key[:4])  # sécurité : n’affiche que les 4 premiers caractères
client = OpenAI(api_key=api_key)

# -------------------------------
# Paramètres utilisateur
TICKERS = ["AAPL", "MSFT", "GOOGL"]
HORIZON = 12
PROFIL = "equilibre"
END_DATE = dt.date.today()
START_DATE = END_DATE - dt.timedelta(days=HORIZON*30)
DISCLAIMER = "Contenu éducatif. Pas un conseil en investissement."

# -------------------------------
# 1) Données
prices = load_prices(TICKERS, START_DATE, END_DATE)

# 2) Métriques
metrics = compute_metrics(prices)

# 3) Règles
signals, weights = rules_engine(metrics, PROFIL)

# 4) Rapport déterministe
report = render_report_text(
    TICKERS, PROFIL, metrics, signals, weights,
    disclaimer=DISCLAIMER, horizon=HORIZON, date=END_DATE
)
print(report)

# 5) Conseil IA
ctx = build_ia_context(PROFIL, HORIZON, END_DATE, metrics, signals, weights)
advice = generate_advice_openai(client, ctx)
print("\n=== CONSEIL IA ===\n")
print(advice)

# 6) Mini backtest
for t in metrics["ticker"]:
    bt = backtest_sma50(prices[t])
    if not bt.empty:
        bt[["eq_bh","eq_sma50"]].plot(title=f"Backtest Buy&Hold vs SMA50 : {t}")
plt.show()
