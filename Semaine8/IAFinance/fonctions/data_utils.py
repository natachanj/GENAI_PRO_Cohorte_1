import yfinance as yf
import pandas as pd

def load_prices(tickers, start_date, end_date):
    """
    Télécharge les prix ajustés via yfinance et renvoie un DataFrame propre.
    Colonnes = tickers.
    """
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=False
    )

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Adj Close"].copy()
    else:
        prices = data[["Adj Close"]].copy()
        if isinstance(tickers, list) and len(tickers) == 1:
            prices.columns = [tickers[0]]

    prices = prices.ffill().dropna(how="any")
    return prices
