import streamlit as st
import plotly.express as px
import polars as pl

def get_filiais_coordinates(selected_filiais=None) -> pl.DataFrame:
    """
    Retorna um DataFrame contendo nome das filiais e suas coordenadas (latitude e longitude).
    Se uma lista de filiais for passada, retorna apenas essas filiais.
    """

    filiais_data = {
        "nmFilial": [
            "FILIAL CURITIBA", "FILIAL RIO DE JANEIRO", "FILIAL FORTALEZA", "FILIAL SALVADOR",
            "FILIAL CAMPINAS", "FILIAL SÃO LUÍS", "FILIAL BRASÍLIA", "FILIAL BELÉM",
            "FILIAL SÃO PAULO", "FILIAL GOIÂNIA", "FILIAL RECIFE", "FILIAL GUARULHOS",
            "FILIAL SÃO GONÇALO", "FILIAL BELO HORIZONTE"
        ],
        "latitude": [
            -25.4284, -22.9068, -3.7319, -12.9777,
            -22.9056, -2.5307, -15.8267, -1.4558,
            -23.5505, -16.6869, -8.0476, -23.4576,
            -22.8268, -19.9167
        ],
        "longitude": [
            -49.2733, -43.1729, -38.5267, -38.5016,
            -47.0608, -44.3028, -47.9218, -48.4902,
            -46.6333, -49.2643, -34.8770, -46.5333,
            -43.0634, -43.9345
        ]
    }
    
 
    df_filiais = pl.DataFrame(filiais_data)
    

    if selected_filiais:
        df_filiais = df_filiais.filter(df_filiais["nmFilial"].is_in(selected_filiais))
    
    return df_filiais


def render_filiais_map(df_filiais: pl.DataFrame):
    """
    Renderiza o mapa com as filiais marcadas com pins e nomes visíveis diretamente.
    """
    df_mapa = df_filiais.to_pandas()

    fig = px.scatter_mapbox(
        df_mapa,
        lat="latitude",
        lon="longitude",
        hover_name="nmFilial",
        text="nmFilial",  
        zoom=4.5,
        height=550
    )

    fig.update_traces(
        marker=dict(size=12, color="#FF5733"),
        textposition="top right"  
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.subheader("📍 Filiais no Mapa")
    st.plotly_chart(fig, use_container_width=True)

