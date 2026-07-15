import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from utils import apply_custom_css

st.set_page_config(
    page_title="Portfolio | Leonardo de Andrade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_custom_css()

st.markdown('<h1 class="gradient-text">📊 Financial Analytics Portfolio</h1>', unsafe_allow_html=True)
st.markdown("#### by Leonardo de Andrade")

st.markdown(
    """
    <div class="disclaimer-box">
    <strong>⚠️ Disclaimer</strong><br><br>
    All data shown in this application is <strong>entirely fictitious</strong>,
    generated with the Python library <code>Faker</code>. No real company,
    client, or employer data is used anywhere in this project.
    <br><br>
    This project exists solely to demonstrate technical skills in
    <strong>Python, pandas, data visualization, and Streamlit</strong> for
    portfolio and job interview purposes.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("#### What this project demonstrates")
st.markdown(
    """
    - Data generation and manipulation with **pandas**
    - Interactive dashboards built with **Streamlit**
    - Data visualization with **Plotly** (waterfall, pie, and choropleth map charts)
    - Live currency conversion via a public exchange rate API
    - Clean, modular Python code structure (shared utils, multi-page app)
    """
)

st.divider()

if st.button("Open the Dashboard →", type="primary"):
    st.switch_page("views/dashboard.py")
