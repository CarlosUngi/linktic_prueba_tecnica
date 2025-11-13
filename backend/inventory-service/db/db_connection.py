import os
import pymysql.cursors
from typing import Any, Dict

# Constantes de conexión

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql_db')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

class DBConnection:
    """Gestión del Pool de Conexiones a MySQL para el Patrón Repositorio."""

    def __init__(self) -> None:
        if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
            raise EnvironmentError("Variables de entorno de DB faltantes.")

    def get_connection(self) -> pymysql.connections.Connection:
        """Establece y retorna una nueva conexión."""
        try:
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor, # Retorna resultados como diccionarios
                autocommit=False # Desactivar autocommit para manejo explícito de transacciones
            )
        except pymysql.Error as e:
            # CRITICAL LOGGING: Fallo en la conexión a la BD
            print(f"CRITICAL DB ERROR: No se pudo conectar a la base de datos. {e}")
            raise

    @staticmethod
    def execute_query(sql: str, params: tuple = ()) -> Dict[str, Any]:
        """Método estático para ejecutar queries (requiere lógica de pool en la implementación real)."""
        print(f"Executing: {sql} with params: {params}")
        return {"affected_rows": 0, "last_id": None, "results": []}

