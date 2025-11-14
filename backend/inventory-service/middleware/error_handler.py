import datetime
import requests.exceptions
from typing import Any, Dict, Tuple
from flask import Flask, jsonify, request, Response
from exceptions.api_exceptions import APIException, ServiceUnavailableError

# ----------------- CONFIGURACIÓN DEL LOGGING ESTRUCTURADO -----------------

def write_structured_log(log_data: Dict[str, Any]) -> None:
    """Serializa el log estructurado al formato de texto plano y lo escribe a logs/"""
    
    # Mapeo de campos basado en la Sección III del documento de Estrategia de Logging
    # Usar get() para evitar KeyError si falta algún campo (aunque no debería ocurrir)
    timestamp_str: str = log_data.get("timestamp", "").replace('Z', '')
    
    fecha: str = timestamp_str.split("T")[0] if "T" in timestamp_str else str(datetime.date.today())
    hora: str = timestamp_str.split("T")[1].split(".")[0] if "T" in timestamp_str and "." in timestamp_str else str(datetime.datetime.now().time()).split(".")[0]
    
    servicio: str = log_data.get("service", "inventory-service")
    codigo_error: str = log_data.get("error_code", "UNKNOWN_ERROR")
    api_url: str = log_data.get("api_url", "N/A")
    mensaje_error: str = log_data.get("message", "Error sin detalle.")
    
    # Formato de salida solicitado (Ej: 2025-11-12 19:00:00 products-service INVALID_INPUT_DATA /api/v1/products El precio...)
    log_line: str = f"{fecha} {hora} {servicio} {codigo_error} {api_url} {mensaje_error}\n"

    # 4. Escritura a Disco (Asumiendo que el volumen /logs está montado en Docker)
    log_file_path: str = f"logs/{fecha}.log" # YYYY-MM-DD.log
    try:
        with open(log_file_path, "a") as f:
            f.write(log_line)
    except Exception as e:
        # En caso de que no se pueda escribir al disco montado
        print(f"CRITICAL LOGGING ERROR: No se pudo escribir a {log_file_path}. Detalle: {e}")


# ----------------- MANEJADOR DE EXCEPCIONES CENTRAL -----------------

def build_json_api_error(status_code: int, error_code: str, title: str, detail: str) -> Dict[str, Any]:
    """Helper para construir la respuesta JSON API de error."""
    return {
        "errors": [{
            "status": str(status_code),
            "code": error_code,
            "title": title,
            "detail": detail
        }]
    }

def register_error_handlers(app: Flask) -> None:
    """Registra los manejadores de errores para la aplicación Flask."""
    
    # Manjeador de Errores Generales (Internos o no controlados)
    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception) -> Tuple[Response, int]:
        """Captura todas las excepciones no APIException, incluyendo fallos de Requests."""
        
        status_code: int = 500
        error_code: str = "INTERNAL_SERVER_ERROR"
        detail_message: str = str(error)
        
        # Caso específico: Fallo en la comunicación inter-servicio (resiliencia)
        if isinstance(error, requests.exceptions.RequestException):
            status_code = 503
            error_code = "SERVICE_UNAVAILABLE" 
            detail_message = f"Fallo de comunicación inter-servicio. Detalle: {str(error)}"
        
        # Construir y loguear el objeto JSON estructurado
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
            "level": "CRITICAL" if status_code >= 500 else "ERROR", 
            "service": "inventory-service",
            "http_method": request.method if request else "N/A",
            "api_url": request.path if request else "N/A",
            "error_code": error_code,
            "message": detail_message,
        }
        write_structured_log(log_entry)
        
        # Formatear la respuesta JSON API
        response_body = build_json_api_error(
            status_code=status_code,
            error_code=error_code,
            title="Error Interno del Servidor",
            detail=detail_message
        )
        return jsonify(response_body), status_code

    # Manjeador de Errores de API (Errores controlados por el desarrollador)
    @app.errorhandler(APIException)
    def handle_api_exception(error: APIException) -> Tuple[Response, int]:
        """Captura las excepciones personalizadas que ya tienen formato y código."""
        
        # 1. Construir y loguear el objeto JSON estructurado 
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
            "level": "ERROR" if error.status_code < 500 else "CRITICAL",
            "service": "inventory-service",
            "http_method": request.method if request else "N/A",
            "api_url": request.path if request else "N/A",
            "error_code": error.error_code,
            "message": error.detail,
        }
        write_structured_log(log_entry)

        # 2. Formato de respuesta JSON API
        response_body = build_json_api_error(
            status_code=error.status_code,
            error_code=error.error_code,
            title=error.message,
            detail=error.detail
        )
        return jsonify(response_body), error.status_code
