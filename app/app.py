"""
App de portfólio: Análise de Despesas Corporativas (dados 100% fictícios).

Por que essa estrutura de código?
- Cada gráfico/filtro é uma função separada -> fica fácil de ler, testar e
  reaproveitar em outros projetos seus.
- Uso @st.cache_data para não recarregar o CSV toda vez que você mexe em um
  filtro -- é a mesma lógica de "carregar uma vez, reusar depois" que você já
  usa no Alteryx quando monta um workflow.

Rode localmente com: streamlit run app/app.py
"""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Análise de Despesas | Leonardo de Andrade",
    page_icon="📊",
    layout="wide",
)

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv("data/financeiro_ficticio.csv", parse_dates=["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)
    return df

def cabecalho():
    st.title("📊 Análise de Despesas Corporativas — Projeto de Portfólio")
    st.caption(
        "Todos os dados nesta página são **fictícios**, gerados com a biblioteca "
        "Faker para fins de demonstração de habilidades técnicas (Python, pandas, "
        "Streamlit). Nenhuma informação real de empresa é utilizada."
    )
    st.divider()

def filtros_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    paises = st.sidebar.multiselect(
        "País", options=sorted(df["pais"].unique()), default=sorted(df["pais"].unique())
    )
    categorias = st.sidebar.multiselect(
        "Categoria", options=sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
    )
    apenas_aprovados = st.sidebar.checkbox("Somente aprovados", value=False)

    df_filtrado = df[df["pais"].isin(paises) & df["categoria"].isin(categorias)]
    if apenas_aprovados:
        df_filtrado = df_filtrado[df_filtrado["aprovado"]]
    return df_filtrado

def indicadores(df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Despesas", f"US$ {df['valor_usd'].sum():,.0f}")
    col2.metric("Nº de Transações", f"{len(df):,}")
    col3.metric("Ticket Médio", f"US$ {df['valor_usd'].mean():,.0f}")
    taxa_aprovacao = df["aprovado"].mean() * 100 if len(df) else 0
    col4.metric("Taxa de Aprovação", f"{taxa_aprovacao:.1f}%")

def graficos(df: pd.DataFrame):
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("Despesas por Categoria")
        por_categoria = df.groupby("categoria")["valor_usd"].sum().sort_values(ascending=False)
        st.bar_chart(por_categoria)

    with col_dir:
        st.subheader("Despesas por País")
        por_pais = df.groupby("pais")["valor_usd"].sum().sort_values(ascending=False)
        st.bar_chart(por_pais)

    st.subheader("Evolução Mensal")
    evolucao = df.groupby("mes_ano")["valor_usd"].sum()
    st.line_chart(evolucao)

def tabela_detalhada(df: pd.DataFrame):
    with st.expander("Ver dados detalhados"):
        st.dataframe(
            df[["data", "pais", "centro_custo", "categoria", "descricao", "valor_usd", "aprovado"]]
            .sort_values("data", ascending=False),
            use_container_width=True,
        )

def main():
    cabecalho()
    df = carregar_dados()
    df_filtrado = filtros_sidebar(df)
    indicadores(df_filtrado)
    st.divider()
    graficos(df_filtrado)
    st.divider()
    tabela_detalhada(df_filtrado)

if __name__ == "__main__":
    main()
