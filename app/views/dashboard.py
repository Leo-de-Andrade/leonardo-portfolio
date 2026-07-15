import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    ISO3,
    CURRENCY_SYMBOLS,
    apply_custom_css,
    format_money,
    get_exchange_rates,
    load_data,
    render_icon,
)

st.set_page_config(
    page_title="Dashboard | Leonardo de Andrade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_custom_css()

df = load_data()
rates = get_exchange_rates()

all_countries = sorted(df["country"].unique())
all_categories = sorted(df["category"].unique())

# Values from the previous run (or defaults), used only to build the
# popover button labels ("Country (6)") before the widgets below re-render.
selected_countries_prev = st.session_state.get("country_filter", all_countries)
selected_categories_prev = st.session_state.get("category_filter", all_categories)

# ---------------------------------------------------------------------------
# Sticky filter bar
# Country and Category use st.popover so they behave like a compact dropdown:
# click to open, pick your options, click elsewhere to close it again --
# instead of a long list of tags always taking up space.
# ---------------------------------------------------------------------------
with st.container(key="filter_bar"):
    c1, c2, c3, c4, c5, c6 = st.columns([1.4, 1.4, 1.2, 1, 1.3, 1.2])
    with c1:
        with st.popover(f"🌎 Country ({len(selected_countries_prev)})", use_container_width=True):
            countries = st.multiselect(
                "Country", all_countries, default=all_countries,
                key="country_filter", label_visibility="collapsed",
            )
    with c2:
        with st.popover(f"🏷️ Category ({len(selected_categories_prev)})", use_container_width=True):
            categories = st.multiselect(
                "Category", all_categories, default=all_categories,
                key="category_filter", label_visibility="collapsed",
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

symbol = CURRENCY_SYMBOLS.get(currency, "")

st.markdown(
    f'<h1 class="gradient-text">{render_icon(36)}Corporate Expense Analysis</h1>',
    unsafe_allow_html=True,
)
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

# ---------------------------------------------------------------------------
# Map -- bigger, more realistic (land/ocean colors, natural earth projection),
# values converted to the selected currency and shown in millions.
# ---------------------------------------------------------------------------
st.subheader("Expenses by Country")
by_country = df_f.groupby("country")["amount_usd"].sum().reset_index()
by_country["iso3"] = by_country["country"].map(ISO3)
rate = rates.get(currency, 1.0)
by_country["amount_millions"] = by_country["amount_usd"] * rate / 1_000_000

fig_map = px.choropleth(
    by_country,
    locations="iso3",
    color="amount_millions",
    hover_name="country",
    color_continuous_scale=["#c7d2fe", "#6366f1", "#312e81"],
    labels={"amount_millions": f"{currency} (M)"},
)
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>" + symbol + " %{z:.2f}M<extra></extra>"
)
fig_map.update_geos(
    lataxis_range=[-58, 33],
    lonaxis_range=[-120, -30],
    showland=True,
    landcolor="#1e293b",
    showocean=True,
    oceancolor="#0c1e3e",
    showcountries=True,
    countrycolor="rgba(255,255,255,0.3)",
    showcoastlines=True,
    coastlinecolor="rgba(255,255,255,0.2)",
    bgcolor="rgba(0,0,0,0)",
    projection_type="natural earth",
)
fig_map.update_layout(
    height=620,
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#e8eaf6",
    margin=dict(t=10, b=10, l=0, r=0),
    coloraxis_colorbar=dict(title=f"{currency} (M)", ticksuffix="M"),
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Monthly trend -- transparent background, no gridlines, thicker line,
# values in millions of the selected currency.
# ---------------------------------------------------------------------------
st.subheader("Monthly Trend")
monthly = df_f.groupby("month")["amount_usd"].sum().reset_index()
monthly["amount_millions"] = monthly["amount_usd"] * rate / 1_000_000

fig_line = go.Figure(
    go.Scatter(
        x=monthly["month"],
        y=monthly["amount_millions"],
        mode="lines",
        line=dict(width=4, color="#818cf8", shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(129, 140, 248, 0.15)",
        hovertemplate="%{x}<br>" + symbol + " %{y:.2f}M<extra></extra>",
    )
)
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#e8eaf6",
    margin=dict(t=10, b=10),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False, ticksuffix="M"),
)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------------------------------------------------------
# Detailed data -- custom HTML table so the header can have the blue
# background + bold white font (st.dataframe's header can't be restyled
# this precisely).
# ---------------------------------------------------------------------------
with st.expander("View detailed data"):
    display_df = (
        df_f[["date", "country", "cost_center", "category", "description", "amount_usd", "approved"]]
        .sort_values("date", ascending=False)
        .copy()
    )
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    display_df["amount_usd"] = display_df["amount_usd"].apply(
        lambda v: format_money(v, currency, rates, decimals, in_millions)
    )
    display_df.columns = [
        "Date", "Country", "Cost Center", "Category", "Description", "Amount", "Approved",
    ]
    html_table = display_df.to_html(index=False, classes="custom-table", escape=False)
    st.markdown(f'<div class="table-scroll">{html_table}</div>', unsafe_allow_html=True)
