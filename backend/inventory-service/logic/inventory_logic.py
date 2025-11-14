import pymysql
from typing import Any, Dict, Optional, List

from models.inventory_table import InventoryRepository
from db.db_connection import DBConnection
from exceptions.api_exceptions import NotFoundError, InvalidInputError, ConflictError
from external_conections.products_services_integration import get_products_from_service

class InventoryService:
    """
    Capa de servicio que contiene la lógica de negocio para la gestión del inventario.
    Orquesta las operaciones del repositorio y aplica las validaciones de negocio.
    """

    def __init__(self, inventory_repository: Optional[InventoryRepository] = None) -> None:
        """
        Inicializa el servicio con una instancia del repositorio de inventario.
        Si no se proporciona un repositorio, crea uno por defecto.
        """
        if inventory_repository is None:
            db_connection = DBConnection()
            self.inventory_repository = InventoryRepository(db_connection)
        else:
            self.inventory_repository = inventory_repository


    def create_new_inventory(self, product_id: int, available_stock: int, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida y crea un nuevo registro de inventario para un producto.

        Lanza:
            - InvalidInputError: Si el stock es negativo.
            - ConflictError: Si ya existe un inventario para el producto_id.
        """
        if available_stock < 0:
            raise InvalidInputError("El stock disponible ('available_stock') no puede ser negativo.")

        try:
            inventory_id = self.inventory_repository.create_inventory(product_id, available_stock, location)
            return {
                "id": inventory_id,
                "product_id": product_id,
                "available_stock": available_stock,
                "location": location
            }
        except pymysql.err.IntegrityError as e:
            # Captura el error de clave única para 'product_id'
            if e.args[0] == 1062: # Código de error para 'Duplicate entry'
                raise ConflictError(f"Ya existe un inventario para el producto con ID {product_id}.")
            # Relanza otros errores de integridad (ej. FK no encontrada)
            raise InvalidInputError(f"No se pudo crear el inventario. Verifique que el producto con ID {product_id} exista.")

    def get_inventory_for_product(self, product_id: int) -> Dict[str, Any]:
        """
        Obtiene el inventario de un producto específico.

        Lanza:
            - NotFoundError: Si no se encuentra un inventario para el producto_id.
        """
        inventory = self.inventory_repository.get_inventory_by_product_id(product_id)
        if not inventory:
            raise NotFoundError("inventario", product_id)
        return inventory

    def update_stock_for_product(self, product_id: int, new_stock: int) -> Dict[str, Any]:
        """
        Valida y actualiza el stock de un producto.

        Lanza:
            - InvalidInputError: Si el nuevo stock es negativo.
            - NotFoundError: Si no se encuentra un inventario para el producto_id.
        """
        if new_stock < 0:
            raise InvalidInputError("El nuevo stock ('new_stock') no puede ser negativo.")

        # Primero, verificamos que el inventario exista para dar un error 404 claro.
        self.get_inventory_for_product(product_id)

        affected_rows = self.inventory_repository.update_inventory_stock(product_id, new_stock)
        
        # Esta comprobación es una salvaguarda, aunque get_inventory_for_product ya lo valida.
        if affected_rows == 0:
            raise NotFoundError("inventario", product_id)

        return {
            "product_id": product_id,
            "available_stock": new_stock,
            "message": "Stock actualizado correctamente."
        }

    def delete_inventory_for_product(self, product_id: int) -> None:
        """
        Elimina el registro de inventario de un producto.

        Lanza:
            - NotFoundError: Si no se encuentra un inventario para el producto_id a eliminar.
        """
        affected_rows = self.inventory_repository.delete_inventory(product_id)
        if affected_rows == 0:
            raise NotFoundError("inventario", product_id)

    def get_products_with_stock(self, page: int, limit: int) -> Dict[str, Any]:
        """
        Obtiene una lista paginada de productos desde el servicio de productos
        y la enriquece con la información de stock del inventario.

        Args:
            page (int): Número de página a solicitar.
            limit (int): Límite de productos por página.

        Returns:
            Dict[str, Any]: Un diccionario con la lista de productos enriquecida y metadatos de paginación.
        """
        # 1. Obtener productos del servicio externo
        products_data, _ = get_products_from_service(page, limit)
        print(products_data)
        print('salio del servicio externo')
        
        products = products_data.get("data", [])
        if not products:
            return {"data": [], "meta": products_data.get("meta", {})}

        # 2. Extraer IDs de productos
        product_ids = [int(p["id"]) for p in products]

        # 3. Obtener el inventario para esos IDs
        inventory_list = self.inventory_repository.get_inventory_by_product_ids(product_ids)
        
        print('salio de la consulta de inventario')
        # 4. Crear un mapa de stock para búsqueda rápida
        stock_map = {item["product_id"]: item["available_stock"] for item in inventory_list}


        # 5. Enriquecer los productos con la información de stock
        for product in products:
            product_id = int(product["id"])
            # Asignar stock si existe, de lo contrario, 0
            product["attributes"]["available_stock"] = stock_map.get(product_id, 0)

        return products_data