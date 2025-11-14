import os
import pymysql.cursors
from typing import Any, Dict
from dbutils.pooled_db import PooledDB

# Constantes de conexión

MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

class DBConnection:
    """
    Gestión de un Pool de Conexiones a MySQL usando DBUtils.
    Esta clase sigue el patrón Singleton para asegurar una única instancia del pool.
    """
    _pool = None

    @classmethod
    def get_pool(cls) -> PooledDB:
        """Retorna la instancia del pool, creándola si no existe."""
        if cls._pool is None:
            if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
                raise EnvironmentError("Variables de entorno de DB faltantes.")
            try:
                cls._pool = PooledDB(
                    creator=pymysql,
                    maxconnections=10,  # Número máximo de conexiones en el pool
                    mincached=2,      # Número mínimo de conexiones inactivas
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False,
                    blocking=True     # Esperar si no hay conexiones disponibles
                )
            except pymysql.Error as e:
                print(f"CRITICAL DB ERROR: No se pudo inicializar el pool de conexiones. {e}")
                raise
        return cls._pool

    def get_connection(self) -> pymysql.connections.Connection:
        """Obtiene una conexión del pool."""
        pool = self.get_pool()
        return pool.connection()
