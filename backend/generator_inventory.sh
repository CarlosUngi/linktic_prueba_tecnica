#!/bin/bash

# Este script inicializa la estructura de carpetas y archivos
# para el microservicio 'inventory-service' en Python (Flask),
# siguiendo la arquitectura propuesta (Clean Architecture / Patrones de Servicio/Repositorio).

PROJECT_ROOT="inventory-service"

echo "Creando la estructura del proyecto $PROJECT_ROOT..."

# 1. Crear directorios principales
mkdir -p $PROJECT_ROOT/{config,db,middleware,models,logic,routes,tests/{unit,integration},exceptions,logs,test_results}

# 2. Crear archivos de configuración y raíz
touch $PROJECT_ROOT/{app.py,requirements.txt,.env.example}
touch $PROJECT_ROOT/config/{settings.py,error_codes.json,__init__.py}
touch $PROJECT_ROOT/db/__init__.py
touch $PROJECT_ROOT/exceptions/__init__.py
touch $PROJECT_ROOT/tests/__init__.py
touch $PROJECT_ROOT/tests/unit/__init__.py
touch $PROJECT_ROOT/tests/integration/__init__.py
touch $PROJECT_ROOT/middleware/__init__.py
touch $PROJECT_ROOT/models/__init__.py
touch $PROJECT_ROOT/logic/__init__.py
touch $PROJECT_ROOT/routes/__init__.py

# 3. Creación de archivos Python clave con contenido básico y tipado

# app.py (Punto de entrada)
echo "#!/usr/bin/env python3
# app.py

import os
from flask import Flask
from middleware.error_handler import register_error_handlers
from exceptions.api_exceptions import APIException
# Importar otras rutas y middleware aquí

def create_app() -> Flask:
    """Función de factoría para crear y configurar la aplicación Flask."""
    
    # Cargar FLASK_ENV desde .env o usar 'development' por defecto
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    
    # Configuración de Flask (ajustar según el entorno)
    app.config['ENV'] = FLASK_ENV

    # Registrar manejadores de errores (CRÍTICO para JSON API y Logging)
    register_error_handlers(app)

    # TODO: Registrar Blueprint de rutas aquí (e.g., app.register_blueprint(inventory_bp))

    return app

if __name__ == '__main__':
    # Se recomienda usar Docker, pero esto es para desarrollo local
    from dotenv import load_dotenv
    load_dotenv()
    
    app = create_app()
    port = int(os.environ.get('INVENTORY_SERVICE_PORT_HOST', 8000))
    app.run(debug=True, port=port)
" > $PROJECT_ROOT/app.py

# requirements.txt (Dependencias)
echo "# Requerimientos del Microservicio de Inventario (Python)

# Framework
Flask
python-dotenv
# Base de Datos
PyMySQL
# Logging Estructurado
structlog
# Cliente HTTP Resiliente
requests
# Serialización y Validación (JSON API)
marshmallow
# Pruebas (80% de cobertura)
pytest
pytest-cov
" > $PROJECT_ROOT/requirements.txt

# .env.example (Variables de Entorno Mínimas)
echo "# Variables de Entorno del Proyecto - INVENTORY-SERVICE
# NOTA: Usar el nombre del servicio Docker como HOSTNAME en el ambiente de contenedor

# 1. CONFIGURACIÓN DE BASE DE DATOS (MYSQL)
MYSQL_HOST=mysql_db
MYSQL_PORT=3306
MYSQL_DATABASE=linktick_db
MYSQL_USER=linktick_user
MYSQL_PASSWORD=user_password

# 2. CONFIGURACIÓN DE PUERTOS Y URLS
INVENTORY_SERVICE_PORT_HOST=8000
PRODUCTS_SERVICE_URL_INTERNAL=http://products-service:3000

# 3. AUTENTICACIÓN (API KEYS)
PRODUCTS_API_KEY=my-secure-key-for-products-access

# 4. CONFIGURACIÓN ESPECÍFICA DE ENTORNOS
FLASK_ENV=development # production
" > $PROJECT_ROOT/.env.example

# db/db_connection.py (Gestión del Pool de Conexiones - con tipado)
echo "import os
import pymysql.cursors
from typing import Any, Dict

# Constantes de conexión
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql_db')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

class DBConnection:
    \"\"\"Gestión del Pool de Conexiones a MySQL para el Patrón Repositorio.\"\"\"

    def __init__(self) -> None:
        if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]):
            raise EnvironmentError(\"Variables de entorno de DB faltantes.\")

    def get_connection(self) -> pymysql.connections.Connection:
        \"\"\"Establece y retorna una nueva conexión.\"\"\"
        try:
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor, # Retorna resultados como diccionarios
                autocommit=False # Desactivar autocommit para manejo explícito de transacciones
            )
        except pymysql.Error as e:
            # CRITICAL LOGGING: Fallo en la conexión a la BD
            print(f\"CRITICAL DB ERROR: No se pudo conectar a la base de datos. {e}\")
            raise

    @staticmethod
    def execute_query(sql: str, params: tuple = ()) -> Dict[str, Any]:
        \"\"\"Método estático para ejecutar queries (requiere lógica de pool en la implementación real).\"\"\"
        # Nota: La implementación completa del Pool de Conexiones puede ser compleja.
        # Por simplicidad y para la prueba, se puede inicializar una conexión por request
        # o implementar un patrón Singleton de Pool, pero se recomienda usar un ORM 
        # para manejar el Pool de forma nativa en producción.
        print(f\"Executing: {sql} with params: {params}\")
        return {\"affected_rows\": 0, \"last_id\": None, \"results\": []}
" > $PROJECT_ROOT/db/db_connection.py

# exceptions/api_exceptions.py (Excepciones tipadas)
echo "from typing import Optional, Any

# Excepción base para todos los errores que deben ser formateados como JSON API
class APIException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str, detail: Optional[str] = None) -> None:
        super().__init__(message)
        self.status_code: int = status_code
        self.error_code: str = error_code
        self.detail: str = detail if detail is not None else message

# 503 Service Unavailable (Para fallos de resiliencia inter-servicio)
class ServiceUnavailableError(APIException):
    def __init__(self, message: str = \"Servicio Dependiente No Disponible.\", detail: Optional[str] = None) -> None:
        super().__init__(
            message=message, 
            status_code=503, 
            error_code=\"SERVICE_UNAVAILABLE\", 
            detail=detail
        )

# 404 Not Found (Para manejar IDs no encontrados)
class NotFoundError(APIException):
    def __init__(self, resource_type: str, resource_id: Any) -> None:
        message = f\"Recurso no encontrado: {resource_type} con ID {resource_id}\"
        super().__init__(
            message=message,
            status_code=404,
            error_code=\"RESOURCE_NOT_FOUND\",
            detail=message
        )
" > $PROJECT_ROOT/exceptions/api_exceptions.py


# middleware/error_handler.py (Logeo Estructurado y JSON API - con tipado)
echo "import datetime
import requests.exceptions
from typing import Any, Dict, Tuple
from flask import Flask, jsonify, request, Response
from exceptions.api_exceptions import APIException, ServiceUnavailableError

# ----------------- CONFIGURACIÓN DEL LOGGING ESTRUCTURADO -----------------

def write_structured_log(log_data: Dict[str, Any]) -> None:
    \"\"\"Serializa el log estructurado al formato de texto plano y lo escribe a logs/\"\"\"
    
    # Mapeo de campos basado en la Sección III del documento de Estrategia de Logging
    # Usar get() para evitar KeyError si falta algún campo (aunque no debería ocurrir)
    timestamp_str: str = log_data.get(\"timestamp\", \"\").replace('Z', '')
    
    fecha: str = timestamp_str.split(\"T\")[0] if \"T\" in timestamp_str else str(datetime.date.today())
    hora: str = timestamp_str.split(\"T\")[1].split(\".\")[0] if \"T\" in timestamp_str and \".\" in timestamp_str else str(datetime.datetime.now().time()).split(\".\")[0]
    
    servicio: str = log_data.get(\"service\", \"inventory-service\")
    codigo_error: str = log_data.get(\"error_code\", \"UNKNOWN_ERROR\")
    api_url: str = log_data.get(\"api_url\", \"N/A\")
    mensaje_error: str = log_data.get(\"message\", \"Error sin detalle.\")
    
    # Formato de salida solicitado (Ej: 2025-11-12 19:00:00 products-service INVALID_INPUT_DATA /api/v1/products El precio...)
    log_line: str = f\"{fecha} {hora} {servicio} {codigo_error} {api_url} {mensaje_error}\\n\"

    # 4. Escritura a Disco (Asumiendo que el volumen /logs está montado en Docker)
    log_file_path: str = f\"logs/{fecha}.log\" # YYYY-MM-DD.log
    try:
        with open(log_file_path, \"a\") as f:
            f.write(log_line)
    except Exception as e:
        # En caso de que no se pueda escribir al disco montado
        print(f\"CRITICAL LOGGING ERROR: No se pudo escribir a {log_file_path}. Detalle: {e}\")


# ----------------- MANEJADOR DE EXCEPCIONES CENTRAL -----------------

def build_json_api_error(status_code: int, error_code: str, title: str, detail: str) -> Dict[str, Any]:
    \"\"\"Helper para construir la respuesta JSON API de error.\"\"\"
    return {
        \"errors\": [{
            \"status\": str(status_code),
            \"code\": error_code,
            \"title\": title,
            \"detail\": detail
        }]
    }

def register_error_handlers(app: Flask) -> None:
    \"\"\"Registra los manejadores de errores para la aplicación Flask.\"\"\"
    
    # Manjeador de Errores Generales (Internos o no controlados)
    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception) -> Tuple[Response, int]:
        \"\"\"Captura todas las excepciones no APIException, incluyendo fallos de Requests.\"\"\"
        
        status_code: int = 500
        error_code: str = \"INTERNAL_SERVER_ERROR\"
        detail_message: str = str(error)
        
        # Caso específico: Fallo en la comunicación inter-servicio (resiliencia)
        if isinstance(error, requests.exceptions.RequestException):
            status_code = 503
            error_code = \"SERVICE_UNAVAILABLE\" 
            detail_message = f\"Fallo de comunicación inter-servicio. Detalle: {str(error)}\"
        
        # Construir y loguear el objeto JSON estructurado
        log_entry: Dict[str, Any] = {
            \"timestamp\": datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
            \"level\": \"CRITICAL\" if status_code >= 500 else \"ERROR\", 
            \"service\": \"inventory-service\",
            \"http_method\": request.method if request else \"N/A\",
            \"api_url\": request.path if request else \"N/A\",
            \"error_code\": error_code,
            \"message\": detail_message,
        }
        write_structured_log(log_entry)
        
        # Formatear la respuesta JSON API
        response_body = build_json_api_error(
            status_code=status_code,
            error_code=error_code,
            title=\"Error Interno del Servidor\",
            detail=detail_message
        )
        return jsonify(response_body), status_code

    # Manjeador de Errores de API (Errores controlados por el desarrollador)
    @app.errorhandler(APIException)
    def handle_api_exception(error: APIException) -> Tuple[Response, int]:
        \"\"\"Captura las excepciones personalizadas que ya tienen formato y código.\"\"\"
        
        # 1. Construir y loguear el objeto JSON estructurado 
        log_entry: Dict[str, Any] = {
            \"timestamp\": datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
            \"level\": \"ERROR\" if error.status_code < 500 else \"CRITICAL\",
            \"service\": \"inventory-service\",
            \"http_method\": request.method if request else \"N/A\",
            \"api_url\": request.path if request else \"N/A\",
            \"error_code\": error.error_code,
            \"message\": error.detail,
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
" > $PROJECT_ROOT/middleware/error_handler.py


# config/error_codes.json (Estandarización de errores)
echo "{
  \"INVALID_INPUT_DATA\": {
    \"status\": 400,
    \"title\": \"Datos de entrada inválidos\",
    \"detail\": \"Uno o más campos en la solicitud tienen un formato o valor incorrecto.\"
  },
  \"UNAUTHORIZED_ACCESS\": {
    \"status\": 401,
    \"title\": \"Acceso No Autorizado\",
    \"detail\": \"La API Key proporcionada es incorrecta o falta el header X-API-Key.\"
  },
  \"RESOURCE_NOT_FOUND\": {
    \"status\": 404,
    \"title\": \"Recurso No Encontrado\",
    \"detail\": \"El ID de inventario o producto no existe.\"
  },
  \"INVENTORY_NOT_AVAILABLE\": {
    \"status\": 409,
    \"title\": \"Stock Insuficiente\",
    \"detail\": \"La cantidad solicitada supera la cantidad disponible en el inventario.\"
  },
  \"SERVICE_UNAVAILABLE\": {
    \"status\": 503,
    \"title\": \"Servicio Dependiente No Disponible\",
    \"detail\": \"El Products Service no respondió o falló después de múltiples reintentos.\"
  },
  \"INTERNAL_SERVER_ERROR\": {
    \"status\": 500,
    \"title\": \"Error Interno del Servidor\",
    \"detail\": \"Ocurrió un error inesperado. El incidente ha sido registrado.\"
  }
}" > $PROJECT_ROOT/config/error_codes.json


echo "Estructura de $PROJECT_ROOT creada y archivos base inicializados."
echo "--------------------------------------------------------"

# 4. Creación del README.md con instrucciones
echo "
# Microservicio de Inventario (\`inventory-service\`)

Este microservicio, desarrollado en **Python (Flask)**, gestiona la información de stock y la cantidad disponible de los productos, cumpliendo con los estándares de la prueba técnica de Líder.

Implementa los patrones de **Servicio** y **Repositorio**, usa **tipado estricto** en Python y asegura la **resiliencia** en la comunicación con el Products Service.

## 🚀 1. Estructura y Arquitectura

Sigue una estructura de Clean Architecture adaptada a microservicios:
- \`exceptions/\`: Definición de excepciones personalizadas y tipadas para manejar errores JSON API (e.g., \`NotFoundError\`).
- \`middleware/\`: Contiene \`error_handler.py\` para el **Logging Estructurado** y el mapeo de errores a **JSON API**.
- \`db/\`: Gestión del Pool de Conexiones a MySQL.
- \`models/\`: Patrón Repositorio (lógica de consultas SQL a la tabla \`inventarios\`).
- \`logic/\`: Patrón de Servicio (lógica de negocio, validaciones y el **Cliente HTTP Resiliente** para Products Service).

## 🛠️ 2. Configuración e Instalación

### 2.1. Requisitos
- Python 3.9+

### 2.2. Entorno Virtual (\`venv\`)

Es **obligatorio** usar un entorno virtual para aislar las dependencias:

1.  **Crear y Activar \`venv\`** (ejecutar desde la raíz del proyecto \`inventory-service/\`):
    \`\`\`bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # o: venv\\Scripts\\activate  # Windows
    \`\`\`

2.  **Instalar Dependencias** (con \`(venv)\` activo):
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`
    *(Las dependencias están definidas en \`requirements.txt\` e incluyen Flask, PyMySQL, requests, y pytest/coverage).*

### 2.3. Variables de Entorno

Copie el archivo de ejemplo para configurar sus variables locales. **NUNCA** suba \`.env\` al control de versiones.

\`\`\`bash
cp .env.example .env
# Luego, edite el archivo .env con sus credenciales y API Keys
\`\`\`

## ▶️ 3. Ejecución Local

Con el entorno virtual activo y las dependencias instaladas:

\`\`\`bash
# Establecer el entorno de desarrollo
export FLASK_ENV=development 
# Ejecutar el servidor (normalmente en el puerto 8000 o el definido en .env)
python app.py
\`\`\`

## 🧪 4. Ejecución de Pruebas y Cobertura

El objetivo es alcanzar el **80% de Cobertura** del Backend.

\`\`\`bash
# Ejecutar Pytest y generar el reporte HTML de cobertura
pytest --cov=. --cov-report html:test_results/inventory-coverage
\`\`\`

El reporte detallado se encontrará en el directorio \`test_results/inventory-coverage/index.html\`." > $PROJECT_ROOT/README.md

echo "Se ha generado el README.md en $PROJECT_ROOT/"
echo "--------------------------------------------------------"
echo "Para usar, primero haz el script ejecutable:"
echo "chmod +x setup_inventory_service.sh"
echo "Luego, ejecútalo:"
echo "./setup_inventory_service.sh"