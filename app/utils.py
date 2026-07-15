"""
Shared utilities for the portfolio dashboard.

Centralizing data loading, currency conversion, and styling here means both
pages (Home and Dashboard) reuse the exact same logic instead of duplicating
code -- the same "single source of truth" principle you'd apply in an
Alteryx workflow with a shared macro.
"""

import base64

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


def render_icon(size: int = 36) -> str:
    """
    A small trending-up icon with a gradient stroke, used instead of a plain
    emoji next to page titles -- matches the app's purple-to-blue theme.
    """
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"
         xmlns="http://www.w3.org/2000/svg" style="vertical-align:-6px; margin-right:6px;">
      <defs>
        <linearGradient id="iconGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#a5b4fc"/>
          <stop offset="100%" stop-color="#4338ca"/>
        </linearGradient>
      </defs>
      <path d="M3 17L9 11L13 15L21 5" stroke="url(#iconGrad)" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M21 5H15" stroke="url(#iconGrad)" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M21 5V11" stroke="url(#iconGrad)" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """


def _ticker_background_data_uri() -> str:
    """
    A faint, looping chart-line pattern used as a subtle animated background
    -- a nod to the financial theme without distracting from the content.
    Encoded as base64 to avoid any CSS quoting/escaping issues.
    """
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
    <polyline points="0,150 30,120 60,140 90,80 120,100 150,50 180,90 210,40 240,70 270,30 300,60"
              fill="none" stroke="white" stroke-width="2" opacity="0.35"/>
    </svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def apply_custom_css():
    bg_pattern = _ticker_background_data_uri()
    st.markdown(
        f"""
        <style>
        /* ---- Base background: gradient + faint animated chart-line pattern ---- */
        .stApp {{
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 25%,
                        #1e3a8a 60%, #0c1e3e 100%);
            background-attachment: fixed;
            position: relative;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background-image: url('{bg_pattern}');
            background-repeat: repeat;
            background-size: 300px 200px;
            opacity: 0.06;
            animation: tickerScroll 25s linear infinite;
            z-index: 0;
            pointer-events: none;
        }}
        @keyframes tickerScroll {{
            from {{ background-position: 0 0; }}
            to {{ background-position: -300px 0; }}
        }}
        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            position: relative;
            z-index: 1;
        }}

        /* ---- Hide the built-in multi-page sidebar entirely ---- */
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
        }}

        /* ---- Base text color ---- */
        h1, h2, h3, h4, p, span, label, .stMarkdown, .stCaption {{
            color: #e8eaf6 !important;
        }}

        /* ---- Gradient title text (matches the page background) ---- */
        .gradient-text {{
            background: linear-gradient(135deg, #c7d2fe, #818cf8, #60a5fa) !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            color: transparent !important;
            display: inline-block;
        }}

        /* ---- KPI cards ---- */
        .kpi-card {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(6px);
        }}
        .kpi-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #a5b4fc !important;
            margin-bottom: 0.35rem;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff !important;
        }}

        /* ---- Sticky filter bar ---- */
        .st-key-filter_bar {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(30, 27, 75, 0.92);
            backdrop-filter: blur(10px);
            padding: 1rem 1.2rem 0.6rem 1.2rem;
            border-radius: 0 0 16px 16px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
            margin-bottom: 1.5rem;
        }}

        /* ---- Disclaimer box ---- */
        .disclaimer-box {{
            background: rgba(255, 255, 255, 0.07);
            border-left: 4px solid #818cf8;
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            margin: 1.2rem 0;
        }}

        /* ---- Multiselect tags: gradient instead of default red ---- */
        [data-baseweb="tag"] {{
            background: linear-gradient(135deg, #6366f1, #4338ca) !important;
            color: #ffffff !important;
            border: none !important;
        }}
        [data-baseweb="tag"] svg {{
            fill: #ffffff !important;
        }}

        /* ---- Popover panel (used for the compact Country/Category dropdowns) ---- */
        [data-baseweb="popover"] {{
            background: #1e1b4b !important;
        }}

        /* ---- Checkbox accent color, matching the theme ---- */
        input[type="checkbox"] {{
            accent-color: #6366f1;
        }}

        /* ---- Custom HTML table (View detailed data) ---- */
        .table-scroll {{
            max-height: 480px;
            overflow-y: auto;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        .custom-table thead th {{
            background: linear-gradient(135deg, #4338ca, #3730a3);
            color: #ffffff !important;
            font-weight: 700;
            padding: 0.6rem 0.9rem;
            position: sticky;
            top: 0;
            text-align: left;
            z-index: 2;
        }}
        .custom-table tbody td {{
            padding: 0.5rem 0.9rem;
            color: #e8eaf6;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .custom-table tbody tr:nth-child(even) {{
            background: rgba(255, 255, 255, 0.03);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
