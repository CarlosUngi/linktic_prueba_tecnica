import pymysql.connections
from typing import Any, Dict, List, Optional
from db.db_connection import DBConnection

class InventoryRepository:
    """
    Repositorio para la gestión de operaciones CRUD en la tabla `inventory`.
    """

    def __init__(self, db_connection: DBConnection) -> None:
        self.db_connection = db_connection

    def create_inventory(self, product_id: int, available_stock: int, location: Optional[str] = None) -> int:
        """
        Crea un nuevo registro de inventario para un producto.
        Retorna el ID del nuevo registro de inventario.
        """
        sql = """
            INSERT INTO inventory (product_id, available_stock, location)
            VALUES (%s, %s, %s)
        """
        conn: Optional[pymysql.connections.Connection] = None
        try:
            conn = self.db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (product_id, available_stock, location))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def get_inventory_by_product_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro de inventario por su product_id.
        Retorna el registro de inventario como un diccionario o None si no se encuentra.
        """
        sql = "SELECT * FROM inventory WHERE product_id = %s"
        conn: Optional[pymysql.connections.Connection] = None
        try:
            conn = self.db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (product_id,))
                return cursor.fetchone()
        finally:
            if conn:
                conn.close()

    def update_inventory_stock(self, product_id: int, new_stock: int) -> int:
        """
        Actualiza la cantidad de stock disponible para un producto.
        Retorna el número de filas afectadas.
        """
        sql = """
            UPDATE inventory
            SET available_stock = %s
            WHERE product_id = %s
        """
        conn: Optional[pymysql.connections.Connection] = None
        try:
            conn = self.db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (new_stock, product_id))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def delete_inventory(self, product_id: int) -> int:
        """
        Elimina un registro de inventario por su product_id.
        Retorna el número de filas afectadas.
        """
        sql = "DELETE FROM inventory WHERE product_id = %s"
        conn: Optional[pymysql.connections.Connection] = None
        try:
            conn = self.db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (product_id,))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def get_inventory_by_product_ids(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Obtiene los registros de inventario para una lista de product_ids.
        Retorna una lista de registros de inventario.
        """
        if not product_ids:
            return []
        
        # Prepara la consulta de forma segura para evitar SQL Injection
        placeholders = ', '.join(['%s'] * len(product_ids))
        sql = f"SELECT * FROM inventory WHERE product_id IN ({placeholders})"
        
        conn: Optional[pymysql.connections.Connection] = None
        try:
            conn = self.db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(product_ids))
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()