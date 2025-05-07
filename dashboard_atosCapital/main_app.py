import streamlit as st
import plotly.express as px
from utils.data_utils import load_sales_data, vendas_por_mes, vendas_por_semana
from utils.background import set_background
from utils.stores_map_utils import get_filiais_coordinates, render_filiais_map

import polars as pl

# Configuração da página
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
set_background("images/background.jpg")

# Carrega dados
df = load_sales_data()

# Adiciona colunas auxiliares
df = df.with_columns([
    pl.col("dtVenda").dt.month().alias("Mes"),
    pl.col("dtVenda").dt.strftime("%U").cast(pl.Int32).alias("Semana"),
])

st.sidebar.image("images/logo.png", width=200)

# Sidebar - Filtros
st.sidebar.title("📊 Filtros")

filiais = df.select("nmFilial").unique().to_series().to_list()
meses = list(range(1, 13))
semanas = sorted(df.select("Semana").unique().to_series().to_list())

with st.sidebar.expander("🎯 Filtros de Visualização", expanded=True):
    select_all_filiais = st.checkbox("Selecionar todas as filiais", value=True)
    select_all_meses = st.checkbox("Selecionar todos os meses", value=True)

    selected_filiais = st.multiselect(
        "🏢 Filiais",
        options=filiais,
        default=filiais if select_all_filiais else [],
        help="Selecione uma ou mais filiais"
    )

    selected_meses = st.multiselect(
        "🗓️ Meses",
        options=meses,
        default=meses if select_all_meses else [],
        format_func=lambda x: f"{x:02d}",
        help="Selecione um ou mais meses"
    )


# Validação de filtros
if not selected_filiais or not selected_meses:
    st.warning("⚠️ Selecione pelo menos uma filial, e um mês para visualizar os dados.")
    st.stop()

# Filtra os dados
df_filtered = df.filter(
    pl.col("nmFilial").is_in(selected_filiais) & 
    pl.col("Mes").is_in(selected_meses) 
)

# Métricas principais
total_vendas = df_filtered.select(pl.col("vlVenda").sum()).item()
meta_media = df_filtered.select(pl.col("txMeta").mean()).item()
quantidade_vendas = df_filtered.shape[0]
ticket_medio = total_vendas / quantidade_vendas if quantidade_vendas else 0

# Exibe as métricas
st.title("📈 Dashboard de Vendas")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("🎯 Média da Meta", f"{meta_media:.2f}%")
col3.metric("📦 Quantidade de Vendas", f"{quantidade_vendas}")
col4.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Gráfico de vendas por mês
st.subheader("📊 Vendas por Mês")
df_mes = vendas_por_mes(df_filtered).to_pandas()
fig_mes = px.bar(df_mes, x="mes", y="venda_total", title="Total de Vendas por Mês")
st.plotly_chart(fig_mes, use_container_width=True)

# Gráfico de vendas por semana
st.subheader("📆 Vendas por Semana")
df_semana = vendas_por_semana(df_filtered).to_pandas()
fig_semana = px.line(df_semana, x="semana", y="venda_total", markers=True, title="Total de Vendas por Semana")
st.plotly_chart(fig_semana, use_container_width=True)

# Gráfico de Vendas por Filial
st.subheader("🏢 Distribuição de Vendas por Filial")

df_filial = df_filtered.group_by("nmFilial").agg(
    pl.col("vlVenda").sum().alias("venda_total")
).to_pandas()


fig_filial = px.bar(df_filial, x="nmFilial", y="venda_total", title="Vendas Totais por Filial")
st.plotly_chart(fig_filial, use_container_width=True)

# Gráfico de pizza para cada filial
st.subheader("📊 Distribuição de Vendas por Mês em Cada Filial")

# Agregação das vendas totais por mês e filial
df_filial_mes = df_filtered.group_by(["nmFilial", "Mes"]).agg(
    pl.col("vlVenda").sum().alias("venda_total")
).to_pandas()

# Gráfico de pizza para cada mês
fig_pizza_filial_mes = px.pie(df_filial_mes, 
                               names="nmFilial", 
                               values="venda_total", 
                               color="Mes", 
                               title="Distribuição de Vendas por Mês em Cada Filial",
                               color_discrete_sequence=px.colors.qualitative.Set3)

st.plotly_chart(fig_pizza_filial_mes, use_container_width=True)

st.subheader("📅 Vendas por Dia da Semana em Cada Filial")

# Adiciona a coluna com o dia da semana
df_filtered = df_filtered.with_columns(
    pl.col("dtVenda").dt.weekday().alias("dia_da_semana")
)

# Agrupa por filial e dia da semana e soma as vendas
df_dia_semana_filial = df_filtered.group_by(["nmFilial", "dia_da_semana"]).agg(
    pl.col("vlVenda").sum().alias("venda_total")
).sort(["nmFilial", "dia_da_semana"])

# Converte para pandas para usar com plotly
df_dia_semana_filial = df_dia_semana_filial.to_pandas()

# Mapeia o número do dia da semana para o nome do dia
dias_da_semana = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 
    4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
}
df_dia_semana_filial["dia_da_semana"] = df_dia_semana_filial["dia_da_semana"].map(dias_da_semana)

# Gráfico de barras
fig_dia_semana_filial = px.bar(
    df_dia_semana_filial, 
    x="dia_da_semana", 
    y="venda_total", 
    color="nmFilial", 
    title="Vendas Totais por Dia da Semana em Cada Filial", 
    labels={"dia_da_semana": "Dia da Semana", "venda_total": "Total de Vendas"},
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(fig_dia_semana_filial, use_container_width=True)



# Obter coordenadas das filiais filtradas
filiais_coords = get_filiais_coordinates(selected_filiais)

# Renderizar o mapa com essas coordenadas
render_filiais_map(filiais_coords)
