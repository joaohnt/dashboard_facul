import polars as pl
from db.db_connection import get_connection

def load_sales_data() -> pl.DataFrame:
    query = """
    SELECT idVendas, nrCNPJ, nmFilial, dtVenda, vlVenda, txMeta
    FROM tbVendasDashboard
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)


    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    data = [dict(zip(columns, row)) for row in rows]

  
    df = pl.DataFrame(data).with_columns([
        pl.col("dtVenda").cast(pl.Date),
        pl.col("vlVenda").cast(pl.Float64),
        pl.col("txMeta").cast(pl.Float64)
    ])

    return df

def vendas_por_mes(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns(pl.col("dtVenda").dt.truncate("1mo").alias("mes"))
          .group_by("mes")
          .agg([
              pl.col("vlVenda").sum().alias("venda_total"),
              pl.col("txMeta").mean().alias("media_meta")
          ])
          .sort("mes")
    )

def vendas_por_semana(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns(pl.col("dtVenda").dt.truncate("1w").alias("semana"))
          .group_by("semana")
          .agg([
              pl.col("vlVenda").sum().alias("venda_total"),
              pl.col("txMeta").mean().alias("media_meta")
          ])
          .sort("semana")
    )


def vendas_por_dia_semana(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.with_columns([
            pl.col("dtVenda").dt.strftime("%A").alias("dia_semana")  
        ])
        .select([
            "dia_semana",  
            "vlVenda"
        ])
        .groupby_dynamic(
            by="dia_semana",  
            every="1d",  
            sort_by="dia_semana" 
        )
        .agg([
            pl.col("vlVenda").sum().alias("venda_total") 
        ])
    )
