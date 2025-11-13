#!/bin/bash

# Script de inicialización para el Microservicio Products-Service
# Autor: Desarrollador JavaScript (Tu Asistente)
# Objetivo: Crear la estructura de directorios según el patrón Clean Architecture
# adaptada a microservicios (Lider Técnico).

# ----------------------------------------------------
# 1. Variables y Directorios
# ----------------------------------------------------

# Directorio base del servicio
SERVICE_DIR="products-service"
# Directorios requeridos por la arquitectura
DIRECTORIES=(
    "$SERVICE_DIR/config"
    "$SERVICE_DIR/db"
    "$SERVICE_DIR/middleware"
    "$SERVICE_DIR/models"
    "$SERVICE_DIR/logic"
    "$SERVICE_DIR/routes"
    "$SERVICE_DIR/test"
    "$SERVICE_DIR/test/unit/logic"
    "$SERVICE_DIR/test/unit/models"
    "$SERVICE_DIR/test/integration"
)

echo "Iniciando la generación de la estructura del products-service..."

# Crear directorios
for DIR in "${DIRECTORIES[@]}"; do
    mkdir -p "$DIR"
    echo "  -> Creado directorio: $DIR"
done

# ----------------------------------------------------
# 2. Creación de Archivos Base y Documentación Interna
# ----------------------------------------------------

# Archivos principales y de configuración
touch "$SERVICE_DIR/.env"
echo "constante_api_key: String = process.env.PRODUCTS_API_KEY;" > "$SERVICE_DIR/config/constants.js"

# server.js (Incluye soporte para Swagger)
cat > "$SERVICE_DIR/server.js" << EOF
// server.js - Archivo principal del microservicio Products-Service
const express = require('express');
const dotenv = require('dotenv');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const path = require('path');

dotenv.config(); // Carga las variables del .env

const app = express();
const port = process.env.PRODUCTS_SERVICE_PORT_HOST || 3000;

// Middlewares
app.use(express.json()); // Para parsear el body de las peticiones JSON
// TODO: Implementar Middleware de Logging Global y Manejo de Errores

// Rutas (Versionadas por URI: /api/v1)
app.use('/api/v1', require('./routes/productosRoutes'));

// Documentación Swagger/OpenAPI (Disponible en http://localhost:8001/api-docs)
const swaggerDocument = YAML.load(path.join(__dirname, 'swagger.yaml'));
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Puerto de Escucha
app.listen(port, () => console.log(\`Products Service corriendo en puerto \${port} y Swagger en /api-docs\`));
EOF

# package.json (Agrega swagger-ui-express y yamljs)
cat > "$SERVICE_DIR/package.json" << EOF
{
  "name": "products-service",
  "version": "1.0.0",
  "description": "Microservicio de Productos (CRUD simple).",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "NODE_ENV=development node server.js",
    "test": "jest --coverage"
  },
  "keywords": ["node", "express", "jsonapi", "products", "swagger"],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "mysql2": "^3.9.1",
    "joi": "^17.9.2",
    "swagger-ui-express": "^5.0.0",
    "yamljs": "^0.3.0"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^6.3.3"
  }
}
EOF

# Archivos de la capa DB (Conexión)
cat > "$SERVICE_DIR/db/conexionPool.js" << EOF
// db/conexionPool.js - Gestión del Pool de Conexiones
// Propósito: Inicializar el Pool de MySQL usando mysql2 con soporte de Promises.
// Patrón de diseño: Singleton (exportar una instancia única del Pool).
const mysql = require('mysql2/promise');

async function crearPool() {
    console.log('Inicializando pool de MySQL...');
    try {
        const pool = await mysql.createPool({
            host: process.env.MYSQL_HOST,
            user: process.env.MYSQL_USER,
            password: process.env.MYSQL_PASSWORD,
            database: process.env.MYSQL_DATABASE,
            waitForConnections: true,
            connectionLimit: 10,
            queueLimit: 0
        });
        console.log('Pool de MySQL creado exitosamente.');
        return pool;
    } catch (error) {
        console.error('Error al crear el pool de conexiones:', error);
        // CRÍTICO: El servicio no debe iniciar sin conexión a DB.
        process.exit(1);
    }
}

module.exports = crearPool(); // Se exporta la promesa del Pool para ser awaited en models/
EOF

# Archivos de la capa Middleware
cat > "$SERVICE_DIR/middleware/authApiKey.js" << EOF
// middleware/authApiKey.js - Autenticación Inter-Servicios
// Propósito: Validar el header X-API-Key contra la variable de entorno PRODUCTS_API_KEY.
// Flujo: 1. Leer PRODUCTS_API_KEY. 2. Verificar X-API-Key en request. 3. En caso de fallo,
// retornar 401 UNAUTHORIZED_ACCESS (Patrón de seguridad).
function authApiKey(req, res, next) {
    const expectedKey = process.env.PRODUCTS_API_KEY;
    const incomingKey = req.headers['x-api-key'];

    if (!incomingKey || incomingKey !== expectedKey) {
        // Formato JSON API para error 401
        return res.status(401).json({
            "errors": [{
                "status": "401",
                "code": "UNAUTHORIZED_ACCESS",
                "title": "Acceso No Autorizado",
                "detail": "La API Key proporcionada es incorrecta o falta el header X-API-Key."
            }]
        });
    }
    // Clave válida, continuar al siguiente middleware/ruta
    next();
}

module.exports = authApiKey;
EOF

# Archivos de la capa Repositorio (Patrón Repositorio)
cat > "$SERVICE_DIR/models/productosModel.js" << EOF
// models/productosModel.js - Implementación del Patrón Repositorio
// Propósito: Abstraer el acceso a la tabla 'productos' (SQL).
const poolPromise = require('../db/conexionPool');

class ProductosModel {

    // Método 1: obtenerPorId(id)
    // Tarea: Buscar un producto por su PK.
    async obtenerPorId(id) {
        const pool = await poolPromise;
        const query = 'SELECT * FROM productos WHERE id = ? AND activo = 1;';
        const [rows] = await pool.query(query, [id]);
        return rows[0] || null;
    }

    // Método 2: listarProductos(paginacion)
    // Tarea: Obtener lista paginada de productos activos.
    async listarProductos({ limite, offset }) {
        const pool = await poolPromise;
        // Importante: No usar ORDER BY aquí para evitar errores de índice (firestore instruction).
        // Se recomienda ordenar en JS si es necesario.
        const query = 'SELECT * FROM productos WHERE activo = 1 LIMIT ? OFFSET ?;';
        const [rows] = await pool.query(query, [limite, offset]);

        const countQuery = 'SELECT COUNT(*) as total FROM productos WHERE activo = 1;';
        const [countRows] = await pool.query(countQuery);
        const total = countRows[0].total;

        return { data: rows, meta: { total, limite, offset } };
    }

    // Método 3: crearProducto(datos)
    // Tarea: Insertar un nuevo producto.
    async crearProducto({ nombre, descripcion, precio }) {
        const pool = await poolPromise;
        const query = 'INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?);';
        const [result] = await pool.query(query, [nombre, descripcion, precio]);
        return result.insertId;
    }

    // Método 4: eliminarProducto(id) - Soft Delete
    // Tarea: Actualizar el campo 'activo' a 0.
    async eliminarProducto(id) {
        const pool = await poolPromise;
        const query = 'UPDATE productos SET activo = 0 WHERE id = ?;';
        const [result] = await pool.query(query, [id]);
        return result.affectedRows; // Retorna 1 si se eliminó (soft delete)
    }

    // Tarea Pendiente: implementar actualizarProducto(id, datos)

}

module.exports = new ProductosModel();
EOF

# Archivos de la capa de Servicio (Patrón de Servicio)
cat > "$SERVICE_DIR/logic/productosService.js" << EOF
// logic/productosService.js - Implementación del Patrón de Servicio
// Propósito: Contener la lógica de negocio, validaciones (Joi) y coordinación.
const productosModel = require('../models/productosModel');
const Joi = require('joi');
// Código de error estandarizado para manejo de errores
const { InvalidInputError, ResourceNotFoundError } = require('../config/errorCodes');

// Esquema de validación Joi para crear/actualizar (Principio de validación en la capa de negocio)
const productoSchema = Joi.object({
    nombre: Joi.string().min(3).max(255).required().messages({
        'string.min': 'El nombre debe tener al menos 3 caracteres.',
        'any.required': 'El nombre es un campo obligatorio.'
    }),
    descripcion: Joi.string().allow(null, '').optional(),
    precio: Joi.number().precision(2).positive().required().messages({
        'number.positive': 'El precio debe ser un valor positivo (chk_precio_positivo).',
        'any.required': 'El precio es un campo obligatorio.'
    }),
});

class ProductosService {

    // Tarea: Validar la entrada y orquestar la creación
    async crearNuevoProducto(datos) {
        const { error } = productoSchema.validate(datos, { abortEarly: false });
        if (error) {
            // Lanza error de negocio estándar (InvalidInputError)
            throw new InvalidInputError("Datos de producto inválidos.", error.details);
        }

        try {
            const id = await productosModel.crearProducto(datos);
            return { id, ...datos };
        } catch (dbError) {
            // Manejo de error de DB (ej. nombre duplicado)
            if (dbError.code === 'ER_DUP_ENTRY') { // MySQL error code
                 throw new InvalidInputError("El nombre del producto ya existe.");
            }
            throw dbError; // Relanzar otros errores de DB
        }
    }

    // Tarea: Obtener producto, verificar existencia
    async obtenerProducto(id) {
        const producto = await productosModel.obtenerPorId(id);
        if (!producto) {
            throw new ResourceNotFoundError(\`Producto con ID \${id} no encontrado.\`);
        }
        return producto;
    }

    // Tarea: Listar con paginación
    async listarProductos(pagina = 1, limite = 10) {
        const offset = (pagina - 1) * limite;
        return productosModel.listarProductos({ limite, offset });
    }

    // Tarea Pendiente: implementar actualizarProducto y eliminarProducto
}

module.exports = new ProductosService();
EOF

# Archivos de la capa de Rutas
cat > "$SERVICE_DIR/routes/productosRoutes.js" << EOF
// routes/productosRoutes.js - Mapeo de URL
// Propósito: Definir las rutas con Versionado por URI (/api/v1) y aplicar Middlewares.
const express = require('express');
const router = express.Router();
const productosService = require('../logic/productosService');
const authApiKey = require('../middleware/authApiKey');
// TODO: Importar middleware de manejo de errores global (errorHandlerMiddleware)

// 1. Crear un producto (POST /api/v1/productos)
// Protegida por authApiKey (solo Inventory/Admin puede crear)
router.post('/productos', authApiKey, async (req, res, next) => {
    try {
        const nuevoProducto = await productosService.crearNuevoProducto(req.body);
        // Formato JSON API (data.attributes)
        res.status(201).json({
            data: {
                type: 'productos',
                id: nuevoProducto.id.toString(),
                attributes: nuevoProducto
            }
        });
    } catch (error) {
        next(error); // Pasar el error al middleware de manejo de errores
    }
});

// 2. Listar todos los productos con paginación (GET /api/v1/productos)
router.get('/productos', async (req, res, next) => {
    try {
        const { page = 1, limit = 10 } = req.query;
        const result = await productosService.listarProductos(parseInt(page), parseInt(limit));

        // Formato JSON API (arreglo de recursos)
        res.status(200).json({
            data: result.data.map(p => ({
                type: 'productos',
                id: p.id.toString(),
                attributes: p
            })),
            meta: result.meta
        });
    } catch (error) {
        next(error);
    }
});

// 3. Obtener un producto por ID (GET /api/v1/productos/:id)
router.get('/productos/:id', async (req, res, next) => {
    try {
        const producto = await productosService.obtenerProducto(req.params.id);

        // Formato JSON API (recurso único)
        res.status(200).json({
            data: {
                type: 'productos',
                id: producto.id.toString(),
                attributes: producto
            }
        });
    } catch (error) {
        next(error);
    }
});

// 4. Eliminar un producto por ID (DELETE /api/v1/productos/:id) - Soft Delete
// Protegida por authApiKey
router.delete('/productos/:id', authApiKey, async (req, res, next) => {
    try {
        const affectedRows = await productosService.eliminarProducto(req.params.id);
        if (affectedRows === 0) {
            throw new ResourceNotFoundError(\`Producto con ID \${req.params.id} no encontrado para eliminar.\`);
        }
        res.status(204).send(); // HTTP 204 No Content
    } catch (error) {
        next(error);
    }
});

// Tarea Pendiente: Implementar PUT/PATCH /productos/:id

module.exports = router;
EOF

# Archivos de pruebas (placeholders)
echo "// Test Unitario para la lógica de negocio (Patrón de Servicio)" > "$SERVICE_DIR/test/unit/logic/productosService.test.js"
echo "// Test Unitario para la abstracción de SQL (Patrón Repositorio)" > "$SERVICE_DIR/test/unit/models/productosModel.test.js"
echo "// Test de Integración: Asegura el flujo Route -> Logic -> DB" > "$SERVICE_DIR/test/integration/productosFlujo.test.js"

# config/errorCodes.js (Estandarización de errores para JSON API)
cat > "$SERVICE_DIR/config/errorCodes.js" << EOF
const errorCodes = {
    INVALID_INPUT_DATA: 'INVALID_INPUT_DATA',
    RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
    UNAUTHORIZED_ACCESS: 'UNAUTHORIZED_ACCESS', // Usado en authApiKey.js
    DB_ERROR: 'DATABASE_ERROR'
};

// Clases de error personalizadas para la capa de Servicio
class CustomError extends Error {
    constructor(message, code, details = []) {
        super(message);
        this.code = code;
        this.details = details;
        this.name = this.constructor.name;
    }
}
class InvalidInputError extends CustomError { constructor(message, details) { super(message, errorCodes.INVALID_INPUT_DATA, details); } }
class ResourceNotFoundError extends CustomError { constructor(message) { super(message, errorCodes.RESOURCE_NOT_FOUND); } }

module.exports = { errorCodes, InvalidInputError, ResourceNotFoundError, CustomError };
EOF

# Documentación Swagger (placeholder)
cat > "$SERVICE_DIR/swagger.yaml" << EOF
# Documentación OpenAPI 3.0 para Products-Service
# Versión: /api/v1

openapi: 3.0.0
info:
  title: Products Service API
  version: 1.0.0
  description: CRUD simple para la gestión de la información base de productos, siguiendo el estándar JSON API.
  contact:
    name: Líder Técnico - [Tu Nombre]

servers:
  - url: http://localhost:8001/api/v1
    description: URL principal del microservicio

security:
  - ApiKeyAuth: []

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key # Header requerido para Inventory-Service

  schemas:
    ProductoResource:
      type: object
      properties:
        id:
          type: string
          description: ID único del producto.
        type:
          type: string
          example: productos
        attributes:
          type: object
          properties:
            nombre:
              type: string
            descripcion:
              type: string
            precio:
              type: number
              format: float
              minimum: 0.01

paths:
  /productos:
    get:
      summary: Lista productos con paginación.
      parameters:
        - name: page
          in: query
          required: false
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Lista de recursos de productos.
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/ProductoResource'
                  meta:
                    type: object
                    properties:
                      total:
                        type: integer
                      limit:
                        type: integer
                      offset:
                        type: integer
        '500':
          description: Error interno del servidor.

    post:
      summary: Crea un nuevo producto.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nombre:
                  type: string
                  example: Camisa Polo Roja
                precio:
                  type: number
                  example: 25.99
                descripcion:
                  type: string
      responses:
        '201':
          description: Producto creado exitosamente.
        '401':
          description: Acceso no autorizado (API Key inválida/faltante).
        '422':
          description: Error de validación (JSON API).

  /productos/{id}:
    get:
      summary: Obtiene un producto por su ID.
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Recurso de producto individual.
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    $ref: '#/components/schemas/ProductoResource'
        '404':
          description: Producto no encontrado.
        '401':
          description: Acceso no autorizado (API Key inválida/faltante).

    delete:
      summary: Elimina (Soft Delete) un producto por su ID.
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: Eliminación exitosa (No Content).
        '404':
          description: Producto no encontrado.
        '401':
          description: Acceso no autorizado (API Key inválida/faltante).
EOF

# Se añade el README para completar la documentación base
cat > "$SERVICE_DIR/README.md" << EOF
# 📦 Microservicio: Products-Service (Node.js/Express)

## 1. Introducción y Justificación de la Arquitectura

Este microservicio es el módulo central CRUD para la entidad **Producto**. Siguiendo la guía de arquitectura, se implementa en **Node.js/Express** debido a su simplicidad y alto rendimiento en APIs de I/O intensiva, siendo la opción ideal para un servicio con lógica de negocio previsiblemente baja.

La estructura se adhiere a una **Clean Architecture adaptada a microservicios**, asegurando el máximo desacoplamiento y escalabilidad:

| Capa/Directorio | Patrón Implementado | Responsabilidad |
| :--- | :--- | :--- |
| \`models/\` | **Patrón Repositorio** | Abstracción de la base de datos MySQL (SQL queries). Facilita el mocking en pruebas. |
| \`logic/\` | **Patrón de Servicio** | Concentra la lógica de negocio, las validaciones de entrada (\`Joi\`) y la coordinación. |
| \`middleware/\` | - | Funciones de pre-procesamiento como Autenticación (\`authApiKey\`). |
| \`routes/\` | **Versionado por URI** | Mapeo de endpoints (\`/api/v1/productos\`) y formateo de la respuesta final a **JSON API**. |
| \`db/\` | - | Gestión del Pool de Conexiones (\`mysql2\`). |

## 2. Requisitos Previos

Asegúrate de tener instalado Node.js (v18+) y npm. Para la base de datos, se requiere una instancia de MySQL con las credenciales definidas en el \`.env\`.

## 3. Instalación y Ejecución

### A. Estructura de Directorios

La estructura fue generada usando el script \`generar_estructura.sh\`:

\`\`\`
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
\`\`\`

### B. Pasos de Inicio

1.  **Instalar dependencias:**

    \`\`\`bash
    cd backend/products-service
    npm install
    \`\`\`

2.  **Configurar Variables de Entorno (\`.env\`):**
    Crea el archivo \`.env\` y define las variables de entorno, usando el siguiente *template*:

    \`\`\`env
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
    \`\`\`

3.  **Ejecutar el Servicio:**

    \`\`\`bash
    npm run dev
    # O para producción:
    # npm start
    \`\`\`

    El servicio estará disponible en \`http://localhost:8001\`.

## 4. Documentación de la API (Swagger/OpenAPI)

La especificación de la API se encuentra en \`swagger.yaml\`. Una vez que el servicio esté corriendo (puerto \`8001\`), la documentación interactiva estará accesible en:

  * **\`http://localhost:8001/api-docs\`**

## 5. Estrategia de Pruebas (80% Cobertura)

Se utilizará **Jest** para las pruebas, apuntando a un **80% de Cobertura** en las capas de *Backend*.

### A. Enfoque de Pruebas

| Tipo de Prueba | Ubicación | Objetivo |
| :--- | :--- | :--- |
| **Unitaria - Repositorio** | \`test/unit/models/\` | Probar que \`productosModel.js\` genere el SQL correcto (Mocking del Pool de Conexiones). |
| **Unitaria - Servicio** | \`test/unit/logic/\` | Probar **el 100% de la lógica de negocio** y validaciones (\`Joi\`), mockeando el Repositorio. |
| **Integración** | \`test/integration/\` | Flujo completo: **Ruta -> Servicio -> MySQL de prueba**. Validar la respuesta JSON API, el \`authApiKey\` y el manejo de errores de BD (ej. \`ER_DUP_ENTRY\`). |

### B. Ejecución de Pruebas

Para generar la cobertura y el reporte \`lcov\`:

\`\`\`bash
npm test
\`\`\`

El reporte HTML de cobertura se guardará en \`test_results/\` (siguiendo la **Estrategia de Pruebas** definida).
EOF

echo "Archivos base y placeholders creados. Estructura lista."
echo "----------------------------------------------------"
echo "Para ejecutar el script:"
echo "1. Navega al directorio raiz de tu proyecto."
echo "2. Otorga permisos de ejecución: chmod +x generar_estructura.sh"
echo "3. Ejecuta: ./generar_estructura.sh"