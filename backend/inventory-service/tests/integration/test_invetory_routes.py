import pytest
from unittest.mock import patch
import json

from app import create_app
from db.db_connection import DBConnection
from models.inventory_table import InventoryRepository

# Fixture para crear una instancia de la aplicación Flask para pruebas
@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

# Fixture para el cliente de pruebas de Flask
@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

# Fixture para limpiar y poblar la base de datos de prueba
@pytest.fixture(scope='function')
def setup_database():
    db_connection = DBConnection()
    inventory_repo = InventoryRepository(db_connection)

    product_ids = [101, 102, 103, 104]
    # Limpiar datos antes de la prueba
    for pid in product_ids:
        try:
            inventory_repo.delete_inventory(pid)
        except Exception:
            pass

    # Poblar con datos de prueba
    inventory_repo.create_inventory(product_id=101, available_stock=150)
    inventory_repo.create_inventory(product_id=102, available_stock=45)
    inventory_repo.create_inventory(product_id=103, available_stock=320)
    inventory_repo.create_inventory(product_id=104, available_stock=80)

    yield

    # Limpiar después de la prueba
    for pid in product_ids:
        inventory_repo.delete_inventory(pid)


# Mock de la respuesta del servicio de productos
MOCK_PRODUCTS_RESPONSE = {
    "data": [
        {
            "type": "productos",
            "id": "101",
            "attributes": {
                "id": 101,
                "name": "RGB Mechanical Keyboard",
                "description": "High-performance keyboard with Brown switches, ideal for programmers.",
                "price": "79.99",
                "is_active": 1,
                "created_at": "2025-11-14T17:42:59.000Z",
                "updated_at": "2025-11-14T17:42:59.000Z"
            }
        },
        {
            "type": "productos",
            "id": "102",
            "attributes": {
                "id": 102,
                "name": "34-inch Ultrawide Monitor",
                "description": "Curved 4K screen with a 144Hz refresh rate. Perfect for gaming and design.",
                "price": "499.50",
                "is_active": 1,
                "created_at": "2025-11-14T17:42:59.000Z",
                "updated_at": "2025-11-14T17:42:59.000Z"
            }
        },
        {
            "type": "productos",
            "id": "103",
            "attributes": {
                "id": 103,
                "name": "Wireless Ergonomic Mouse",
                "description": "Rechargeable vertical mouse with Bluetooth connection and adjustable DPI.",
                "price": "25.00",
                "is_active": 1,
                "created_at": "2025-11-14T17:42:59.000Z",
                "updated_at": "2025-11-14T17:42:59.000Z"
            }
        },
        {
            "type": "productos",
            "id": "104",
            "attributes": {
                "id": 104,
                "name": "Full HD 1080p Webcam",
                "description": "Camera with autofocus and dual microphone. Ideal for video calls.",
                "price": "35.75",
                "is_active": 1,
                "created_at": "2025-11-14T17:42:59.000Z",
                "updated_at": "2025-11-14T17:42:59.000Z"
            }
        }
    ],
    "meta": {"total": 4, "limite": 10, "offset": 0}
}

@patch('logic.inventory_logic.get_products_from_service')
def test_get_products_with_stock(mock_get_products, test_client, setup_database):
    """
    Prueba de integración para el endpoint GET /api/v1/inventory/products-with-stock
    """
    # Configurar el mock para que devuelva la respuesta esperada
    mock_get_products.return_value = (MOCK_PRODUCTS_RESPONSE, 200)

    # Realizar la solicitud al endpoint
    response = test_client.get('/api/v1/inventory/products-with-stock?page=1&limit=10')

    # Verificar el código de estado
    assert response.status_code == 200

    # Verificar el contenido de la respuesta
    data = json.loads(response.data)
    
    assert "data" in data
    assert "meta" in data
    assert len(data["data"]) == 4

    # Verificar que el stock se haya añadido correctamente
    product_101 = next((p for p in data["data"] if p["id"] == "101"), None)
    product_102 = next((p for p in data["data"] if p["id"] == "102"), None)
    product_103 = next((p for p in data["data"] if p["id"] == "103"), None)
    product_104 = next((p for p in data["data"] if p["id"] == "104"), None)

    assert product_101 is not None
    assert product_101["attributes"]["available_stock"] == 150

    assert product_102 is not None
    assert product_102["attributes"]["available_stock"] == 45

    assert product_103 is not None
    assert product_103["attributes"]["available_stock"] == 320
    
    assert product_104 is not None
    assert product_104["attributes"]["available_stock"] == 80
