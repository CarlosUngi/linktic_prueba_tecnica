
# Microservicio de Inventario (`inventory-service`)

Este microservicio, desarrollado en **Python (Flask)**, gestiona la información de stock y la cantidad disponible de los productos, cumpliendo con los estándares de la prueba técnica de Líder.

Implementa los patrones de **Servicio** y **Repositorio**, usa **tipado estricto** en Python y asegura la **resiliencia** en la comunicación con el Products Service.

## 🚀 1. Estructura y Arquitectura

Sigue una estructura de Clean Architecture adaptada a microservicios:
- `exceptions/`: Definición de excepciones personalizadas y tipadas para manejar errores JSON API (e.g., `NotFoundError`).
- `middleware/`: Contiene `error_handler.py` para el **Logging Estructurado** y el mapeo de errores a **JSON API**.
- `db/`: Gestión del Pool de Conexiones a MySQL.
- `models/`: Patrón Repositorio (lógica de consultas SQL a la tabla `inventarios`).
- `logic/`: Patrón de Servicio (lógica de negocio, validaciones y el **Cliente HTTP Resiliente** para Products Service).

## 🛠️ 2. Configuración e Instalación

### 2.1. Requisitos
- Python 3.9+

### 2.2. Entorno Virtual (`venv`)

Es **obligatorio** usar un entorno virtual para aislar las dependencias:

1.  **Crear y Activar `venv`** (ejecutar desde la raíz del proyecto `inventory-service/`):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # o: venv\Scripts\activate  # Windows
    ```

2.  **Instalar Dependencias** (con `(venv)` activo):
    ```bash
    pip install -r requirements.txt
    ```
    *(Las dependencias están definidas en `requirements.txt` e incluyen Flask, PyMySQL, requests, y pytest/coverage).*

### 2.3. Variables de Entorno

Copie el archivo de ejemplo para configurar sus variables locales. **NUNCA** suba `.env` al control de versiones.

```bash
cp .env.example .env
# Luego, edite el archivo .env con sus credenciales y API Keys
```

## ▶️ 3. Ejecución Local

Con el entorno virtual activo y las dependencias instaladas:

```bash
# Establecer el entorno de desarrollo
export FLASK_ENV=development 
# Ejecutar el servidor (normalmente en el puerto 8000 o el definido en .env)
python app.py
```

## 🧪 4. Ejecución de Pruebas y Cobertura

El objetivo es alcanzar el **80% de Cobertura** del Backend.

```bash
# Ejecutar Pytest y generar el reporte HTML de cobertura
pytest --cov=. --cov-report html:test_results/inventory-coverage
```

El reporte detallado se encontrará en el directorio `test_results/inventory-coverage/index.html`.
