import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Enciende y devuelve una conexión activa a MySQL."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3307)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "base_inegi_correccion_final"),
        charset="utf8mb4",
        use_unicode=True,
    )


def desconectar(conn, cursor=None):
    """Apaga de forma segura el cursor y la conexión a MySQL."""
    if cursor is not None:
        try:
            cursor.close()
        except Error:
            pass
    if conn is not None and conn.is_connected():
        conn.close()
