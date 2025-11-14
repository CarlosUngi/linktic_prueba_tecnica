import sys
import os
import pytest
import pymysql.connections
import pymysql.err
from unittest.mock import MagicMock, patch
from typing import Any, Dict

from models.inventory_table import InventoryRepository
from db.db_connection import DBConnection
# Asumo que las excepciones básicas de Python como Exception y pymysql.err.IntegrityError son manejadas en el Repositorio

# -------------------- DATOS Y FIXTURES --------------------

MOCK_INVENTARIO_RECORD: Dict[str, Any] = {
    'id': 1,
    'product_id': 101,
    'available_stock': 50,
    'location': 'A1',
    'ultima_actualizacion_inv': '2025-11-13 10:00:00'
}

@pytest.fixture
def mock_db_connection():
    """Mockea la conexión completa de la BD, el cursor, y parchea la dependencia."""
    # 1. Mock de la Conexión (Connection)
    mock_conn = MagicMock(spec=pymysql.connections.Connection)
    # 2. Mock del Cursor (DictCursor)
    mock_cursor = MagicMock(spec=pymysql.cursors.DictCursor)
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # 3. Mockear el objeto DBConnection para que retorne la conexión mockeada
    mock_db_conn_instance = MagicMock(spec=DBConnection)
    mock_db_conn_instance.get_connection.return_value = mock_conn
    
    yield mock_db_conn_instance, mock_conn, mock_cursor

@pytest.fixture
def repository(mock_db_connection):
    """Retorna una instancia del Repositorio con la conexión mockeada."""
    mock_db_conn_instance, _, _ = mock_db_connection
    return InventoryRepository(mock_db_conn_instance)

# -------------------- PRUEBAS DEL REPOSITORIO --------------------

def test_get_inventory_by_product_id_success(repository, mock_db_connection):
    """Verifica la obtención de inventario y el cierre de conexión."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Configuración del Mock: Simular que la BD devuelve un registro
    mock_cursor.fetchone.return_value = MOCK_INVENTARIO_RECORD
    
    inventario = repository.get_inventory_by_product_id(product_id=101)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    sql_executed = mock_cursor.execute.call_args[0][0]
    assert 'SELECT * FROM inventory' in sql_executed

    # 2. Validación de Cierre de Conexión
    mock_conn.close.assert_called_once()
    
    # 3. Validación de Resultado
    assert inventario['product_id'] == 101

def test_get_inventory_by_product_id_not_found(repository, mock_db_connection):
    """Verifica que se retorna None si el inventario no existe."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Configuración del Mock: Simular que la BD no devuelve nada
    mock_cursor.fetchone.return_value = None
    
    inventario = repository.get_inventory_by_product_id(product_id=999)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once_with("SELECT * FROM inventory WHERE product_id = %s", (999,))
    
    # 2. Validación de Cierre de Conexión
    mock_conn.close.assert_called_once()
    
    assert inventario is None

def test_get_inventory_by_product_id_db_error(repository, mock_db_connection):
    """Verifica el manejo de excepciones genéricas en la lectura."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular un error genérico de BD
    mock_cursor.execute.side_effect = Exception("DB connection lost")
    
    with pytest.raises(Exception, match="DB connection lost"):
        repository.get_inventory_by_product_id(product_id=101)
    
    # Asegurar que la conexión se cierre incluso si hay un error
    mock_conn.close.assert_called_once()

def test_get_inventory_by_product_id_connection_error(repository, mock_db_connection):
    """Verifica el manejo de error si la conexión a la BD falla."""
    mock_db_conn_instance, _, mock_cursor = mock_db_connection
    
    # Simular un error al obtener la conexión
    mock_db_conn_instance.get_connection.side_effect = Exception("Failed to connect")
    
    with pytest.raises(Exception, match="Failed to connect"):
        repository.get_inventory_by_product_id(product_id=101)
    
    mock_cursor.execute.assert_not_called()

def test_create_inventory_success(repository, mock_db_connection):
    """Verifica la creación y el commit."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    mock_cursor.lastrowid = 5 
    
    inventory_id = repository.create_inventory(product_id=102, available_stock=10, location='B2')
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    sql_executed = mock_cursor.execute.call_args[0][0]
    assert 'INSERT INTO inventory' in sql_executed
    
    # 2. Validación de Transacción
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()
    mock_conn.close.assert_called_once()
    
    assert inventory_id == 5

def test_create_inventory_integrity_error(repository, mock_db_connection):
    """Verifica el rollback en caso de error de BD (ej. Clave Duplicada)."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular un error de integridad (ej. producto_id duplicado)
    mock_cursor.execute.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")
    
    with pytest.raises(pymysql.err.IntegrityError):
        repository.create_inventory(product_id=102, available_stock=10, location='B2')
    
    # 1. Validación de Transacción: Debe hacer rollback
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_create_inventory_connection_error(repository, mock_db_connection):
    """Verifica el manejo de error si la conexión a la BD falla en la creación."""
    mock_db_conn_instance, _, mock_cursor = mock_db_connection
    
    # Simular un error al obtener la conexión
    mock_db_conn_instance.get_connection.side_effect = Exception("Failed to connect")
    
    with pytest.raises(Exception, match="Failed to connect"):
        repository.create_inventory(product_id=102, available_stock=10)
        
    mock_cursor.execute.assert_not_called()

def test_create_inventory_cursor_error(repository, mock_db_connection):
    """Verifica el rollback si obtener el cursor falla."""
    _, mock_conn, _ = mock_db_connection
    
    # Simular un error al obtener el cursor
    mock_conn.cursor.side_effect = Exception("Cursor creation failed")
    
    with pytest.raises(Exception, match="Cursor creation failed"):
        repository.create_inventory(product_id=102, available_stock=10)
    
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


def test_update_inventory_stock_success(repository, mock_db_connection):
    """Verifica la actualización de stock y el commit."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular 1 fila afectada
    mock_cursor.rowcount = 1 
    
    rows_affected = repository.update_inventory_stock(product_id=101, new_stock=40)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    sql_executed = mock_cursor.execute.call_args[0][0]
    assert 'UPDATE inventory' in sql_executed
    assert 'SET available_stock' in sql_executed
    
    # 2. Validación de Transacción
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    assert rows_affected == 1

def test_update_inventory_stock_not_found(repository, mock_db_connection):
    """Verifica que la actualización retorna 0 si el producto no existe."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular 0 filas afectadas
    mock_cursor.rowcount = 0
    
    rows_affected = repository.update_inventory_stock(product_id=999, new_stock=40)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    
    # 2. Validación de Transacción
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    assert rows_affected == 0

def test_update_inventory_stock_db_error(repository, mock_db_connection):
    """Verifica el rollback en caso de error en la actualización."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular un error genérico de BD
    mock_cursor.execute.side_effect = Exception("DB connection lost")
    
    with pytest.raises(Exception, match="DB connection lost"):
        repository.update_inventory_stock(product_id=101, new_stock=40)
    
    # Validación de Transacción: Debe hacer rollback
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_update_inventory_stock_connection_error(repository, mock_db_connection):
    """Verifica el manejo de error si la conexión a la BD falla en la actualización."""
    mock_db_conn_instance, _, mock_cursor = mock_db_connection
    
    # Simular un error al obtener la conexión
    mock_db_conn_instance.get_connection.side_effect = Exception("Failed to connect")
    
    with pytest.raises(Exception, match="Failed to connect"):
        repository.update_inventory_stock(product_id=101, new_stock=40)
        
    mock_cursor.execute.assert_not_called()

def test_update_inventory_stock_cursor_error(repository, mock_db_connection):
    """Verifica el rollback si obtener el cursor falla en la actualización."""
    _, mock_conn, _ = mock_db_connection
    
    # Simular un error al obtener el cursor
    mock_conn.cursor.side_effect = Exception("Cursor creation failed")
    
    with pytest.raises(Exception, match="Cursor creation failed"):
        repository.update_inventory_stock(product_id=101, new_stock=40)
    
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_delete_inventory_success(repository, mock_db_connection):
    """Verifica la eliminación y el commit."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular 1 fila afectada
    mock_cursor.rowcount = 1 
    
    rows_affected = repository.delete_inventory(product_id=101)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    sql_executed = mock_cursor.execute.call_args[0][0]
    assert 'DELETE FROM inventory' in sql_executed
    
    # 2. Validación de Transacción
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    assert rows_affected == 1

def test_delete_inventory_not_found(repository, mock_db_connection):
    """Verifica que la eliminación retorna 0 si el producto no existe."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular 0 filas afectadas
    mock_cursor.rowcount = 0
    
    rows_affected = repository.delete_inventory(product_id=999)
    
    # 1. Validación de SQL
    mock_cursor.execute.assert_called_once()
    
    # 2. Validación de Transacción
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    assert rows_affected == 0

def test_delete_inventory_db_error(repository, mock_db_connection):
    """Verifica el rollback en caso de error en la eliminación."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    # Simular un error genérico de BD
    mock_cursor.execute.side_effect = Exception("DB connection lost")
    
    with pytest.raises(Exception, match="DB connection lost"):
        repository.delete_inventory(product_id=101)
    
    # Validación de Transacción: Debe hacer rollback
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()

def test_delete_inventory_connection_error(repository, mock_db_connection):
    """Verifica el manejo de error si la conexión a la BD falla en la eliminación."""
    mock_db_conn_instance, _, mock_cursor = mock_db_connection
    
    # Simular un error al obtener la conexión
    mock_db_conn_instance.get_connection.side_effect = Exception("Failed to connect")
    
    with pytest.raises(Exception, match="Failed to connect"):
        repository.delete_inventory(product_id=101)
        
    mock_cursor.execute.assert_not_called()

def test_delete_inventory_cursor_error(repository, mock_db_connection):
    """Verifica el rollback si obtener el cursor falla en la eliminación."""
    _, mock_conn, _ = mock_db_connection
    
    # Simular un error al obtener el cursor
    mock_conn.cursor.side_effect = Exception("Cursor creation failed")
    
    with pytest.raises(Exception, match="Cursor creation failed"):
        repository.delete_inventory(product_id=101)
    
    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()