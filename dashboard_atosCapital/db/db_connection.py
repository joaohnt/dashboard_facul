import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=aquidaba.infonet.com.br;'
        'DATABASE=dbproinfo;'
        'UID=leituraVendas;'
        'PWD=KRphDP65BM;'
    )
    return conn

