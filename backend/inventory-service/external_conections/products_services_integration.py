import os
import requests
from typing import Dict, Any, Tuple

from exceptions.api_exceptions import ServiceUnavailableError

def get_products_from_service(page: int = 1, limit: int = 10) -> Tuple[Dict[str, Any], int]:
    """
    Obtiene la lista de productos desde el servicio de productos.

    Args:
        page (int): El número de página a solicitar.
        limit (int): El número de productos por página.

    Returns:
        Tuple[Dict[str, Any], int]: Una tupla con los datos de la respuesta y el código de estado.

    Lanza:
        ServiceUnavailableError: Si el servicio de productos no está disponible o responde con un error.
    """
    base_url = os.environ.get("PRODUCTS_SERVICE_URL_INTERNAL")
    if not base_url:
        raise ServiceUnavailableError("La URL del servicio de productos no está configurada.")
    products_api_key = os.environ.get("PRODUCTS_API_KEY")
    if not products_api_key:
        raise ServiceUnavailableError("La API key del servicio de productos no está configurada.")

    url = f"{base_url}/api/v1/productos"
    params = {"page": page, "limit": limit}
    headers = {"X-API-KEY": products_api_key}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx/5xx
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        # Engloba cualquier error de `requests` en una excepción personalizada
        raise ServiceUnavailableError(f"No se pudo conectar con el servicio de productos: {e}")
