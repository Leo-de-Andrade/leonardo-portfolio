"""
Shared utilities for the portfolio dashboard.

Centralizing data loading, currency conversion, and styling here means both
pages (Home and Dashboard) reuse the exact same logic instead of duplicating
code -- the same "single source of truth" principle you'd apply in an
Alteryx workflow with a shared macro.
"""

import pandas as pd
import requests
import streamlit as st

DATA_PATH = "data/financial_sample.csv"

# Fallback exchange rates, used ONLY if the live API request fails (e.g. no
# internet access, API temporarily down, or rate-limited). This guarantees
# the app never crashes just because a third-party service is unavailable.
# Values are rough mid-2026 approximations for the safety-net case only.
FALLBACK_RATES = {
    "USD": 1.0,
    "BRL": 5.4,
    "ARS": 1200.0,
    "CLP": 950.0,
    "COP": 4100.0,
    "MXN": 18.5,
    "PEN": 3.75,
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "BRL": "R$",
    "ARS": "AR$",
    "CLP": "CH$",
    "COP": "CO$",
    "MXN": "MX$",
    "PEN": "S/",
}

ISO3 = {
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Chile": "CHL",
    "Colombia": "COL",
    "Mexico": "MEX",
    "Peru": "PER",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


@st.cache_data(ttl=3600)  # refresh once per hour -- no need for per-second rates
def get_exchange_rates() -> dict:
    """
    Fetches live USD exchange rates from a free, key-less public API
    (open.er-api.com). Falls back to static approximate rates if the
    request fails for any reason, so the app degrades gracefully instead
    of crashing.
    """
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        response.raise_for_status()
        data = response.json()
        rates = data.get("rates", {})
        # Only keep the currencies this app actually offers
        result = {code: rates[code] for code in FALLBACK_RATES if code in rates}
        return result if result else FALLBACK_RATES
    except Exception:
        return FALLBACK_RATES


def format_money(value_usd: float, currency: str, rates: dict, decimals: int, in_millions: bool) -> str:
    rate = rates.get(currency, 1.0)
    converted = value_usd * rate
    symbol = CURRENCY_SYMBOLS.get(currency, "")
    if in_millions:
        converted = converted / 1_000_000
        suffix = "M"
    else:
        suffix = ""
    return f"{symbol} {converted:,.{decimals}f}{suffix}"


def apply_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 25%,
                        #1e3a8a 60%, #0c1e3e 100%);
            background-attachment: fixed;
        }
        h1, h2, h3, h4, p, span, label, .stMarkdown, .stCaption {
            color: #e8eaf6 !important;
        }
        .kpi-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(6px);
        }
        .kpi-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #a5b4fc !important;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff !important;
        }
        .st-key-filter_bar {
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(30, 27, 75, 0.88);
            backdrop-filter: blur(10px);
            padding: 1rem 1.2rem 0.4rem 1.2rem;
            border-radius: 0 0 16px 16px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
            margin-bottom: 1.5rem;
        }
        .disclaimer-box {
            background: rgba(255, 255, 255, 0.07);
            border-left: 4px solid #818cf8;
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            margin: 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
