import streamlit as st
import plotly.express as px
import polars as pl 
from utils.data_utils import load_sales_data
from utils.background import set_background
from utils.stores_map_utils import get_filiais_coordinates, render_filiais_map

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
set_background("images/97647.jpg")

st.sidebar.title("📊 Filtros")
df = load_sales_data()

filiais = df.select("nmFilial").unique().to_series().to_list()
anos = df.select(pl.col("dtVenda").dt.year()).unique().to_series().sort().to_list()

with st.sidebar.expander("🎯 Filtros de Visualização", expanded=True):
  
    select_all_filiais = st.checkbox("Selecionar todas as filiais", value=True)
    select_all_anos = st.checkbox("Selecionar todos os anos", value=True)

   
    selected_filiais = st.multiselect(
        "🏢 Filiais",
        options=filiais,
        default=filiais if select_all_filiais else [],
        help="Selecione uma ou mais filiais"
    )

    selected_anos = st.multiselect(
        "📅 Anos de Venda",
        options=anos,
        default=anos if select_all_anos else [],
        help="Selecione um ou mais anos"
    )


if not selected_filiais or not selected_anos:
    st.warning("⚠️ Selecione pelo menos uma filial e um ano para visualizar os dados.")


df_filtered = df.filter(
    pl.col("nmFilial").is_in(selected_filiais) & 
    pl.col("dtVenda").dt.year().is_in(selected_anos)
) if selected_filiais and selected_anos else pl.DataFrame()

# Métricas
if df_filtered.shape[0] > 0:
    total_vendas = df_filtered.select(pl.col("vlVenda").sum()).item()
    meta_media = df_filtered.select(pl.col("txMeta").mean()).item()
    quantidade_vendas = df_filtered.shape[0]
    meta_max = df_filtered.select(pl.col("txMeta").max()).item()
    meta_min = df_filtered.select(pl.col("txMeta").min()).item()
    ticket_medio = total_vendas / quantidade_vendas

    metas_atingidas = df_filtered.filter(pl.col("txMeta") >= 100).shape[0]
    percentual_atingidas = metas_atingidas / quantidade_vendas * 100
else:
    total_vendas = 0
    meta_media = 0
    quantidade_vendas = 0
    meta_max = 0
    meta_min = 0
    ticket_medio = 0
    percentual_atingidas = 0


st.title("📈 Dashboard de Vendas")

col1, col2, col3,col4 = st.columns(4)
col1.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("🎯 Média da Meta", f"{meta_media:.2f}%")
col3.metric("📦 Quantidade de Vendas", f"{quantidade_vendas}")
col4.metric("📊 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Vendas por Filial
st.subheader("🔹Vendas por Filial")
vendas_filial = df_filtered.group_by("nmFilial").agg(pl.col("vlVenda").sum()).to_pandas()

fig1 = px.pie(
    vendas_filial,
    names="nmFilial",
    values="vlVenda",
    title="Distribuição de Vendas por Filial",
    hole=0
)

fig1.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig1.update_traces(textinfo="percent+label")
st.plotly_chart(fig1, use_container_width=True)

# Vendas Mensais 

df_filtered = df_filtered.with_columns([
    (pl.col("dtVenda").dt.strftime("%Y-%m")).alias("AnoMes")
])
vendas_mes = df_filtered.group_by(["AnoMes", "nmFilial"]).agg(pl.col("vlVenda").sum()).sort("AnoMes").to_pandas()

fig2 = px.line(vendas_mes, x="AnoMes", y="vlVenda", color="nmFilial", title="Vendas por Mês e Filial")

fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("🔹Vendas por Ano")

# Vendas por Ano
vendas_ano = df_filtered.with_columns([
    pl.col("dtVenda").dt.year().alias("Ano")
]).group_by("Ano").agg(
    pl.col("vlVenda").sum().alias("TotalAno")
).sort("Ano").to_pandas()

fig3 = px.bar(
    vendas_ano,
    x="Ano",
    y="TotalAno",
    text_auto=True,
    labels={"TotalAno": "Total de Vendas"},
    title="Total de Vendas por Ano"
)

fig3.update_layout(
    xaxis_title="Ano",
    yaxis_title="Total de Vendas",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)


st.plotly_chart(fig3, use_container_width=True)

# Meta de Vendas por Filial
st.subheader("🔹Meta vs Realizado por Filial")

meta_vs_realizado = df_filtered.group_by("nmFilial").agg([
    pl.col("vlVenda").sum().alias("TotalVendas"),
    pl.col("txMeta").mean().alias("MetaMedia")
]).to_pandas()

fig4 = px.bar(
    meta_vs_realizado.melt(id_vars=["nmFilial"], value_vars=["TotalVendas", "MetaMedia"]),
    x="nmFilial", y="value", color="variable",
    barmode="group", text_auto=True,
    title="Meta Média vs Vendas por Filial"
)
fig4.update_layout(xaxis_title="Filial", yaxis_title="Valor",paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig4, use_container_width=True)

# Meta x Venda
st.subheader("🔹Meta vs Venda")

fig5 = px.scatter(
    df_filtered.to_pandas(),
    x="txMeta",
    y="vlVenda",
    color="nmFilial",
    title="Meta (%) vs Venda (R$)",
    labels={"txMeta": "Meta (%)", "vlVenda": "Venda (R$)"}
)

fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig5, use_container_width=True)

# Mapa com as Filiais da Empresa
filiais_coords = get_filiais_coordinates()
render_filiais_map(filiais_coords)


# Tabela
st.subheader("🔹 Tabela de Dados")
st.dataframe(df_filtered.sort("dtVenda", descending=True).to_pandas(), use_container_width=True)

