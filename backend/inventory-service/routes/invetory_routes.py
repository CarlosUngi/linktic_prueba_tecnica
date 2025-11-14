from flask import Blueprint, jsonify, request, Response

from db.db_connection import DBConnection
from models.inventory_table import InventoryRepository
from logic.inventory_logic import InventoryService
from exceptions.api_exceptions import InvalidInputError

# ----------------- INYECCIÓN DE DEPENDENCIAS -----------------
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
    Create a new inventory item.
    ---
    tags:
      - Inventory
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryItem'
    responses:
      201:
        description: Inventory item created successfully.
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Invalid input.
        schema:
          $ref: '#/definitions/Error'
    """
    data = request.get_json()
    if not data or 'product_id' not in data or 'available_stock' not in data:
        raise InvalidInputError("El cuerpo de la solicitud debe contener 'product_id' y 'available_stock'.")

    product_id = data.get('product_id')
    available_stock = data.get('available_stock')
    location = data.get('location')

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
    Get inventory by product ID.
    ---
    tags:
      - Inventory
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The ID of the product to retrieve inventory for.
    responses:
      200:
        description: Inventory item found.
        schema:
          $ref: '#/definitions/InventoryItem'
      404:
        description: Inventory not found.
        schema:
          $ref: '#/definitions/Error'
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
    Update stock for a product.
    ---
    tags:
      - Inventory
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The ID of the product to update stock for.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            new_stock:
              type: integer
              description: The new stock quantity.
    responses:
      200:
        description: Stock updated successfully.
        schema:
          $ref: '#/definitions/InventoryItem'
      400:
        description: Invalid input.
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Inventory not found.
        schema:
          $ref: '#/definitions/Error'
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
    Delete inventory for a product.
    ---
    tags:
      - Inventory
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The ID of the product to delete inventory for.
    responses:
      204:
        description: Inventory deleted successfully.
      404:
        description: Inventory not found.
        schema:
          $ref: '#/definitions/Error'
    """
    inventory_service.delete_inventory_for_product(product_id)
    return Response(status=204)


@inventory_bp.route('/products-with-stock', methods=['GET'])
def get_products_with_stock_route():
    """
    Get a paginated list of products with their stock.
    ---
    tags:
      - Inventory
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: The page number to retrieve.
      - in: query
        name: limit
        type: integer
        default: 10
        description: The number of items per page.
    responses:
      200:
        description: A paginated list of products with stock information.
      503:
        description: The product service is unavailable.
        schema:
          $ref: '#/definitions/Error'
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except (TypeError, ValueError):
        raise InvalidInputError("Los parámetros 'page' y 'limit' deben ser números enteros.")

    products_with_stock = inventory_service.get_products_with_stock(page, limit)
    
    return jsonify(products_with_stock), 200