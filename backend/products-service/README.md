# 📦 Microservicio: Products-Service (Node.js/Express)

## 1. Introducción y Justificación de la Arquitectura

Este microservicio es el módulo central CRUD para la entidad **Producto**. Siguiendo la guía de arquitectura, se implementa en **Node.js/Express** debido a su simplicidad y alto rendimiento en APIs de I/O intensiva, siendo la opción ideal para un servicio con lógica de negocio previsiblemente baja.

La estructura se adhiere a una **Clean Architecture adaptada a microservicios**, asegurando el máximo desacoplamiento y escalabilidad:

| Capa/Directorio | Patrón Implementado | Responsabilidad |
| :--- | :--- | :--- |
| `models/` | **Patrón Repositorio** | Abstracción de la base de datos MySQL (SQL queries). Facilita el mocking en pruebas. |
| `logic/` | **Patrón de Servicio** | Concentra la lógica de negocio, las validaciones de entrada (`Joi`) y la coordinación. |
| `middleware/` | - | Funciones de pre-procesamiento como Autenticación (`authApiKey`). |
| `routes/` | **Versionado por URI** | Mapeo de endpoints (`/api/v1/productos`) y formateo de la respuesta final a **JSON API**. |
| `db/` | - | Gestión del Pool de Conexiones (`mysql2`). |

## 2. Requisitos Previos

Asegúrate de tener instalado Node.js (v18+) y npm. Para la base de datos, se requiere una instancia de MySQL con las credenciales definidas en el `.env`.

## 3. Instalación y Ejecución

### A. Estructura de Directorios

La estructura fue generada usando el script `generar_estructura.sh`:

```
products-service/
├── config/           # Constantes y códigos de error
├── db/               # Conexión a MySQL (Pool)
├── middleware/       # Autenticación (authApiKey.js)
├── models/           # Repositorio (productosModel.js)
├── logic/            # Servicio (productosService.js)
├── routes/           # Mapeo de URLs (productosRoutes.js)
├── test/             # Pruebas Unitarias y de Integración
├── .env              # Variables de entorno
├── package.json
├── server.js         # Archivo de inicio
└── swagger.yaml      # Documentación OpenAPI/Swagger
```

### B. Pasos de Inicio

1.  **Instalar dependencias:**

    ```bash
    cd backend/products-service
    npm install
    ```

2.  **Configurar Variables de Entorno (`.env`):**
    Crea el archivo `.env` y define las variables de entorno, usando el siguiente *template*:

    ```env
    # ------------------------------------
    # CONFIGURACIÓN DE BASE DE DATOS
    # ------------------------------------
    MYSQL_HOST=mysql_db
    MYSQL_PORT=3306
    MYSQL_DATABASE=linktick_db
    MYSQL_USER=linktick_user
    MYSQL_PASSWORD=user_password

    # ------------------------------------
    # CONFIGURACIÓN DE PUERTOS Y SEGURIDAD
    # ------------------------------------
    PRODUCTS_SERVICE_PORT_HOST=8001 # Puerto de exposición (Host)
    PRODUCTS_API_KEY=my-secure-key-for-products-access # Clave para autenticación inter-servicios
    NODE_ENV=development
    ```

3.  **Ejecutar el Servicio:**

    ```bash
    npm run dev
    # O para producción:
    # npm start
    ```

    El servicio estará disponible en `http://localhost:8001`.

## 4. Documentación de la API (Swagger/OpenAPI)

La especificación de la API se encuentra en `swagger.yaml`. Una vez que el servicio esté corriendo (puerto `8001`), la documentación interactiva estará accesible en:

  * **`http://localhost:8001/api-docs`**

## 5. Estrategia de Pruebas (80% Cobertura)

Se utilizará **Jest** para las pruebas, apuntando a un **80% de Cobertura** en las capas de *Backend*.

### A. Enfoque de Pruebas

| Tipo de Prueba | Ubicación | Objetivo |
| :--- | :--- | :--- |
| **Unitaria - Repositorio** | `test/unit/models/` | Probar que `productosModel.js` genere el SQL correcto (Mocking del Pool de Conexiones). |
| **Unitaria - Servicio** | `test/unit/logic/` | Probar **el 100% de la lógica de negocio** y validaciones (`Joi`), mockeando el Repositorio. |
| **Integración** | `test/integration/` | Flujo completo: **Ruta -> Servicio -> MySQL de prueba**. Validar la respuesta JSON API, el `authApiKey` y el manejo de errores de BD (ej. `ER_DUP_ENTRY`). |

### B. Ejecución de Pruebas

Para generar la cobertura y el reporte `lcov`:

```bash
npm test
```

El reporte HTML de cobertura se guardará en `test_results/` (siguiendo la **Estrategia de Pruebas** definida).
