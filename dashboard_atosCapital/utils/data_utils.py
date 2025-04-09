import polars as pl
import pyodbc
from db.db_connection import get_connection

def load_sales_data():
    query = """
    SELECT idVendas, nrCNPJ, nmFilial, dtVenda, vlVenda, txMeta
    FROM tbVendasDashboard
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    # Extrair nomes das colunas
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Converte para lista de dicionários para evitar problemas de schema
    data = [dict(zip(columns, row)) for row in rows]

    # Cria DataFrame de forma segura
    df = pl.DataFrame(data)

    # Conversão de tipos
    df = df.with_columns([
        pl.col("dtVenda").cast(pl.Date),
        pl.col("vlVenda").cast(pl.Float64),
        pl.col("txMeta").cast(pl.Float64)
    ])

    return df
