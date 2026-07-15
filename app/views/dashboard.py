import sys
from pathlib import Path

# Streamlit's navigation runner doesn't automatically add the app/ folder to
# sys.path when executing a page inside views/, so "import utils" would fail
# without this. This adds the parent folder (app/) explicitly.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import ISO3, apply_custom_css, format_money, get_exchange_rates, load_data

st.set_page_config(page_title="Dashboard | Leonardo de Andrade", page_icon="📊", layout="wide")
apply_custom_css()

df = load_data()
rates = get_exchange_rates()

# ---------------------------------------------------------------------------
# Sticky filter bar
# Using st.container(key=...) attaches a CSS class "st-key-filter_bar" to
# this specific container, which is what the CSS in utils.py targets to make
# it stick to the top of the page while scrolling.
# ---------------------------------------------------------------------------
with st.container(key="filter_bar"):
    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1.2, 1, 1.3, 1.2])
    with c1:
        countries = st.multiselect(
            "Country", sorted(df["country"].unique()), default=sorted(df["country"].unique())
        )
    with c2:
        categories = st.multiselect(
            "Category", sorted(df["category"].unique()), default=sorted(df["category"].unique())
        )
    with c3:
        currency = st.selectbox("Currency", list(rates.keys()), index=0)
    with c4:
        decimals = st.number_input("Decimals", min_value=0, max_value=4, value=0, step=1)
    with c5:
        in_millions = st.checkbox("Show in millions", value=False)
    with c6:
        approved_only = st.checkbox("Approved only", value=False)

df_f = df[df["country"].isin(countries) & df["category"].isin(categories)]
if approved_only:
    df_f = df_f[df_f["approved"]]

st.title("📊 Corporate Expense Analysis")
st.caption("All figures are fictitious and generated purely for demonstration purposes.")

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
total = df_f["amount_usd"].sum()
count = len(df_f)
avg = df_f["amount_usd"].mean() if count else 0
approval_rate = df_f["approved"].mean() * 100 if count else 0

kpis = [
    ("Total Expenses", format_money(total, currency, rates, decimals, in_millions)),
    ("Transactions", f"{count:,}"),
    ("Average Ticket", format_money(avg, currency, rates, decimals, in_millions)),
    ("Approval Rate", f"{approval_rate:.1f}%"),
]
kpi_cols = st.columns(4)
for col, (label, value) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

st.divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Expenses by Category")
    by_cat = df_f.groupby("category")["amount_usd"].sum().sort_values(ascending=False)
    fig_wf = go.Figure(
        go.Waterfall(
            x=by_cat.index.tolist(),
            y=by_cat.values.tolist(),
            connector={"line": {"color": "rgba(200,200,255,0.25)"}},
            increasing={"marker": {"color": "#6366f1"}},
            decreasing={"marker": {"color": "#a5b4fc"}},
            totals={"marker": {"color": "#312e81"}},
        )
    )
    fig_wf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eaf6",
        margin=dict(t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_wf, use_container_width=True)

with col_right:
    st.subheader("Approval Status")
    approval_counts = df_f["approved"].value_counts().rename({True: "Approved", False: "Rejected"})
    fig_pie = px.pie(
        names=approval_counts.index,
        values=approval_counts.values,
        color_discrete_sequence=["#6366f1", "#c7d2fe"],
        hole=0.45,
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eaf6",
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Expenses by Country")
by_country = df_f.groupby("country")["amount_usd"].sum().reset_index()
by_country["iso3"] = by_country["country"].map(ISO3)
fig_map = px.choropleth(
    by_country,
    locations="iso3",
    color="amount_usd",
    hover_name="country",
    color_continuous_scale=["#c7d2fe", "#6366f1", "#312e81"],
)
fig_map.update_geos(
    lataxis_range=[-58, 33],
    lonaxis_range=[-120, -30],
    showcountries=True,
    countrycolor="rgba(255,255,255,0.25)",
    showcoastlines=False,
    bgcolor="rgba(0,0,0,0)",
)
fig_map.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e8eaf6",
    margin=dict(t=10, b=10, l=0, r=0),
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()
st.subheader("Monthly Trend")
monthly = df_f.groupby("month")["amount_usd"].sum()
st.line_chart(monthly)

with st.expander("View detailed data"):
    st.dataframe(
        df_f[["date", "country", "cost_center", "category", "description", "amount_usd", "approved"]]
        .sort_values("date", ascending=False),
        use_container_width=True,
    )
