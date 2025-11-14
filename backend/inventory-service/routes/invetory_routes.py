from flask import Blueprint, jsonify, request, Response

from db.db_connection import DBConnection
from models.inventory_table import InventoryRepository
from logic.inventory_logic import InventoryService
from exceptions.api_exceptions import InvalidInputError

# ----------------- INYECCIÓN DE DEPENDENCIAS -----------------
# Se instancian las dependencias que se inyectarán en las rutas.
# En una aplicación más grande, esto se manejaría con un contenedor de inyección de dependencias.
db_connection = DBConnection()
inventory_repository = InventoryRepository(db_connection)
inventory_service = InventoryService(inventory_repository)

# ----------------- CREACIÓN DEL BLUEPRINT -----------------
inventory_bp = Blueprint(
    'inventory_api', 
    __name__, 
    url_prefix='/api/v1/inventory'
)

# ----------------- DEFINICIÓN DE RUTAS -----------------

@inventory_bp.route('/', methods=['POST'])
def create_inventory_route():
    """
    Endpoint para crear un nuevo registro de inventario.
    Espera un JSON con 'product_id' y 'available_stock'.
    """
    data = request.get_json()
    if not data or 'product_id' not in data or 'available_stock' not in data:
        raise InvalidInputError("El cuerpo de la solicitud debe contener 'product_id' y 'available_stock'.")

    product_id = data.get('product_id')
    available_stock = data.get('available_stock')
    location = data.get('location') # Opcional

    new_inventory = inventory_service.create_new_inventory(product_id, available_stock, location)
    
    return jsonify({
        "data": {
            "type": "inventory",
            "id": str(new_inventory.get("id")),
            "attributes": new_inventory
        }
    }), 201


@inventory_bp.route('/<int:product_id>', methods=['GET'])
def get_inventory_route(product_id: int):
    """
    Endpoint para obtener el inventario de un producto por su ID.
    """
    inventory = inventory_service.get_inventory_for_product(product_id)
    return jsonify({
        "data": {
            "type": "inventory",
            "id": str(inventory.get("id")),
            "attributes": inventory
        }
    }), 200


@inventory_bp.route('/<int:product_id>/stock', methods=['PUT'])
def update_stock_route(product_id: int):
    """
    Endpoint para actualizar el stock de un producto.
    Espera un JSON con 'new_stock'.
    """
    data = request.get_json()
    if not data or 'new_stock' not in data:
        raise InvalidInputError("El cuerpo de la solicitud debe contener 'new_stock'.")

    new_stock = data.get('new_stock')
    
    updated_inventory = inventory_service.update_stock_for_product(product_id, new_stock)
    
    return jsonify({"data": updated_inventory}), 200


@inventory_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_inventory_route(product_id: int):
    """
    Endpoint para eliminar el inventario de un producto.
    """
    inventory_service.delete_inventory_for_product(product_id)
    return Response(status=204)