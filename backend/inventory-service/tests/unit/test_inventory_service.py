import pymysql
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from exceptions.api_exceptions import NotFoundError, ConflictError, InvalidInputError
from logic.inventory_logic import InventoryService

# -------------------- FIXTURES DE MOCKING --------------------

# Mockear el repositorio para AISLAR la lógica de negocio
@pytest.fixture
def mock_inventory_repository():
    with patch('logic.inventory_logic.InventoryRepository') as MockRepo:
        repo_instance = MockRepo.return_value
        # Aseguramos que la instancia pasada a InventoryService sea el mock
        yield repo_instance

@pytest.fixture
def mock_products_client():
    """Mockea el cliente HTTP para el Products Service (asumiendo que existe)."""
    with patch('logic.inventory_logic.ProductsClient') as MockClient:
        client_instance = MockClient.return_value
        yield client_instance

@pytest.fixture
def inventory_service(mock_inventory_repository):
    """Instancia del servicio con sus dependencias mockeadas."""
    # Pasamos el mock del repositorio al constructor del servicio
    return InventoryService(inventory_repository=mock_inventory_repository)

# -------------------- DATOS MOCK --------------------
MOCK_INVENTORY_DATA: Dict[str, Any] = {
    'id': 1,
    'product_id': 101,
    'available_stock': 50,
    'location': 'A1',
    'ultima_actualizacion_inv': '2025-11-13 10:00:00'
}

# -------------------- PRUEBAS DE CREACIÓN --------------------

def test_create_new_inventory_success(inventory_service, mock_inventory_repository):
    """Verifica la creación exitosa y el formato de respuesta."""
    
    mock_inventory_repository.create_inventory.return_value = 5 # Simular ID insertado
    
    resultado = inventory_service.create_new_inventory(product_id=200, available_stock=100)
    
    mock_inventory_repository.create_inventory.assert_called_once()
    assert resultado['id'] == 5
    assert resultado['available_stock'] == 100

def test_create_new_inventory_negative_stock(inventory_service, mock_inventory_repository):
    """Verifica la Validación de Negocio: Stock negativo debe lanzar InvalidInputError."""
    
    with pytest.raises(InvalidInputError) as excinfo:
        inventory_service.create_new_inventory(product_id=200, available_stock=-10)
        
    assert 'no puede ser negativo' in excinfo.value.detail
    # CRÍTICO: Asegurar que el repositorio NO fue llamado
    mock_inventory_repository.create_inventory.assert_not_called()

def test_create_new_inventory_conflict_error(inventory_service, mock_inventory_repository):
    """Verifica el mapeo de error de BD (IntegrityError 1062) a ConflictError."""
    
    # Mockear un error de BD específico (ej. Unique Key Constraint)
    mock_inventory_repository.create_inventory.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")
    
    with pytest.raises(ConflictError) as excinfo:
        inventory_service.create_new_inventory(product_id=200, available_stock=10)
        
    assert 'Ya existe un inventario para el producto' in excinfo.value.detail

# -------------------- PRUEBAS DE CONSULTA/ACTUALIZACIÓN --------------------

def test_get_inventory_for_product_success(inventory_service, mock_inventory_repository):
    """Verifica la obtención exitosa de un inventario."""
    
    # Simular que la BD devuelve el registro de inventario
    mock_inventory_repository.get_inventory_by_product_id.return_value = MOCK_INVENTORY_DATA
    
    resultado = inventory_service.get_inventory_for_product(product_id=101)
    
    # Verificar que se llamó al método correcto del repositorio
    mock_inventory_repository.get_inventory_by_product_id.assert_called_once_with(101)
    # Verificar que el resultado es el esperado
    assert resultado == MOCK_INVENTORY_DATA

def test_get_inventory_for_product_not_found(inventory_service, mock_inventory_repository):
    """Verifica que si la BD retorna None, se lanza NotFoundError."""
    
    mock_inventory_repository.get_inventory_by_product_id.return_value = None
    
    with pytest.raises(NotFoundError) as excinfo:
        inventory_service.get_inventory_for_product(product_id=999)
        
    assert 'inventario' in str(excinfo.value) and '999' in str(excinfo.value)

def test_update_stock_for_product_not_found(inventory_service, mock_inventory_repository):
    """Verifica el manejo de NotFoundError antes de la actualización."""
    
    # Simular que la consulta de existencia del producto devuelve None.
    mock_inventory_repository.get_inventory_by_product_id.return_value = None
    
    with pytest.raises(NotFoundError):
        inventory_service.update_stock_for_product(product_id=999, new_stock=10)
    # CRÍTICO: La actualización (update_inventory_stock) no debe llamarse
    mock_inventory_repository.update_inventory_stock.assert_not_called()

def test_update_stock_for_product_negative_stock(inventory_service, mock_inventory_repository):
    """Verifica la Validación de Negocio: Nuevo stock negativo debe lanzar InvalidInputError."""
    
    with pytest.raises(InvalidInputError) as excinfo:
        inventory_service.update_stock_for_product(product_id=101, new_stock=-5)
        
    assert 'no puede ser negativo' in excinfo.value.detail
    mock_inventory_repository.update_inventory_stock.assert_not_called()
    
# -------------------- PRUEBAS DE ELIMINACIÓN --------------------

def test_delete_inventory_for_product_success(inventory_service, mock_inventory_repository):
    """Verifica la eliminación exitosa."""
    
    # Simular 1 fila afectada
    mock_inventory_repository.delete_inventory.return_value = 1 
    
    inventory_service.delete_inventory_for_product(product_id=101)
    
    mock_inventory_repository.delete_inventory.assert_called_once_with(101)

def test_delete_inventory_for_product_not_found(inventory_service, mock_inventory_repository):
    """Verifica que 0 filas afectadas lanza NotFoundError."""
    
    # Simular 0 filas afectadas
    mock_inventory_repository.delete_inventory.return_value = 0 
    
    with pytest.raises(NotFoundError) as excinfo:
        inventory_service.delete_inventory_for_product(product_id=999)
        
    assert 'inventario' in str(excinfo.value)