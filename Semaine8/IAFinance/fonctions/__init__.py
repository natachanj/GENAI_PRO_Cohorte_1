# fonctions/__init__.py
from .data_utils import load_prices
from .metrics_utils import compute_metrics, max_drawdown
from .rules_engine import rules_engine
from .reporting import render_report_md
from .ia_utils import build_ia_context, generate_advice_openai
from .backtest import backtest_sma50
from .symbols import (
    detect_tickers, validate_tickers_yf, resolve_company_names, guess_tickers_with_ai
)
