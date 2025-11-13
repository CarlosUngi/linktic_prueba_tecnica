from typing import Optional, Any

# Excepción base para todos los errores que deben ser formateados como JSON API
class APIException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str, detail: Optional[str] = None) -> None:
        super().__init__(message)
        self.status_code: int = status_code
        self.error_code: str = error_code
        self.detail: str = detail if detail is not None else message

# 503 Service Unavailable (Para fallos de resiliencia inter-servicio)
class ServiceUnavailableError(APIException):
    def __init__(self, message: str = "Servicio Dependiente No Disponible.", detail: Optional[str] = None) -> None:
        super().__init__(
            message=message, 
            status_code=503, 
            error_code="SERVICE_UNAVAILABLE", 
            detail=detail
        )

# 404 Not Found (Para manejar IDs no encontrados)
class NotFoundError(APIException):
    def __init__(self, resource_type: str, resource_id: Any) -> None:
        message = f"Recurso no encontrado: {resource_type} con ID {resource_id}"
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            detail=message
        )

# 400 Bad Request (Para validaciones de entrada fallidas)
class InvalidInputError(APIException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            message="Datos de entrada inválidos",
            status_code=400,
            error_code="INVALID_INPUT_DATA",
            detail=detail
        )

# 409 Conflict (Para recursos que ya existen)
class ConflictError(APIException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            message="Conflicto de Recurso",
            status_code=409,
            error_code="RESOURCE_CONFLICT",
            detail=detail
        )
