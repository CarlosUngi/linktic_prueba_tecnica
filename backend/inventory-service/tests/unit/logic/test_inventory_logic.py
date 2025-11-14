import pytest
from unittest.mock import patch, MagicMock
from logic.inventory_logic import InventoryService
from exceptions.api_exceptions import ServiceUnavailableError

# Fixture para el mock del repositorio de inventario
@pytest.fixture
def mock_inventory_repository():
    return MagicMock()

# Fixture para el servicio de inventario con el repositorio mockeado
@pytest.fixture
def inventory_service(mock_inventory_repository):
    return InventoryService(inventory_repository=mock_inventory_repository)

# Mock de la respuesta del servicio de productos
MOCK_PRODUCTS_RESPONSE = {
    "data": [
        {"id": "101", "attributes": {"name": "Product A"}},
        {"id": "102", "attributes": {"name": "Product B"}},
    ],
    "meta": {"total": 2, "limite": 10, "offset": 0}
}

# Mock de la respuesta del repositorio de inventario
MOCK_INVENTORY_LIST = [
    {"product_id": 101, "available_stock": 50},
    {"product_id": 102, "available_stock": 15},
]

@patch('logic.inventory_logic.get_products_from_service')
def test_get_products_with_stock_success(mock_get_products, inventory_service, mock_inventory_repository):
    """
    Prueba que el servicio enriquece correctamente los productos con el stock.
    """
    # Configurar mocks
    mock_get_products.return_value = (MOCK_PRODUCTS_RESPONSE, 200)
    mock_inventory_repository.get_inventory_by_product_ids.return_value = MOCK_INVENTORY_LIST

    # Llamar al método
    result = inventory_service.get_products_with_stock(page=1, limit=10)

    # Verificar llamadas a los mocks
    mock_get_products.assert_called_once_with(1, 10)
    mock_inventory_repository.get_inventory_by_product_ids.assert_called_once_with([101, 102])

    # Verificar el resultado
    assert len(result["data"]) == 2
    assert result["data"][0]["attributes"]["available_stock"] == 50
    assert result["data"][1]["attributes"]["available_stock"] == 15

@patch('logic.inventory_logic.get_products_from_service')
def test_get_products_with_stock_product_service_unavailable(mock_get_products, inventory_service):
    """
    Prueba que se maneja correctamente un error del servicio de productos.
    """
    # Configurar mock para que lance una excepción
    mock_get_products.side_effect = ServiceUnavailableError("Service down")

    # Verificar que la excepción se propaga
    with pytest.raises(ServiceUnavailableError):
        inventory_service.get_products_with_stock(page=1, limit=10)

@patch('logic.inventory_logic.get_products_from_service')
def test_get_products_with_stock_no_products_found(mock_get_products, inventory_service, mock_inventory_repository):
    """
    Prueba el caso en que el servicio de productos no devuelve productos.
    """
    # Configurar mock para que no devuelva productos
    mock_get_products.return_value = ({"data": [], "meta": {}}, 200)

    # Llamar al método
    result = inventory_service.get_products_with_stock(page=1, limit=10)

    # Verificar que no se llama al repositorio de inventario
    mock_inventory_repository.get_inventory_by_product_ids.assert_not_called()

    # Verificar el resultado
    assert result["data"] == []

@patch('logic.inventory_logic.get_products_from_service')
def test_get_products_with_stock_some_products_without_inventory(mock_get_products, inventory_service, mock_inventory_repository):
    """
    Prueba que a los productos sin inventario se les asigna un stock de 0.
    """
    # Configurar mocks
    mock_products = {
        "data": [
            {"id": "101", "attributes": {"name": "Product A"}},
            {"id": "103", "attributes": {"name": "Product C"}}, # Sin inventario
        ],
        "meta": {"total": 2, "limite": 10, "offset": 0}
    }
    mock_get_products.return_value = (mock_products, 200)
    
    # Solo el producto 101 tiene inventario
    mock_inventory_repository.get_inventory_by_product_ids.return_value = [
        {"product_id": 101, "available_stock": 50}
    ]

    # Llamar al método
    result = inventory_service.get_products_with_stock(page=1, limit=10)

    # Verificar el resultado
    assert len(result["data"]) == 2
    assert result["data"][0]["attributes"]["available_stock"] == 50
    assert result["data"][1]["attributes"]["available_stock"] == 0 # Stock por defecto
