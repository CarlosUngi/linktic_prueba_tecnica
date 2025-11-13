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
app.listen(port, () => console.log(`Products Service corriendo en puerto ${port} y Swagger en /api-docs`));
