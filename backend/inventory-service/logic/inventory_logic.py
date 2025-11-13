import pymysql
from typing import Any, Dict, Optional

from models.inventory_table import InventoryRepository
from exceptions.api_exceptions import NotFoundError, InvalidInputError, ConflictError

class InventoryService:
    """
    Capa de servicio que contiene la lógica de negocio para la gestión del inventario.
    Orquesta las operaciones del repositorio y aplica las validaciones de negocio.
    """

    def __init__(self, inventory_repository: InventoryRepository) -> None:
        """
        Inicializa el servicio con una instancia del repositorio de inventario.
        """
        if not isinstance(inventory_repository, InventoryRepository):
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
        print('2')
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