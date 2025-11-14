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
        await productosService.eliminarProducto(req.params.id);
        res.status(204).send(); // HTTP 204 No Content
    } catch (error) {
        next(error);
    }
});

// 5. Actualizar un producto por ID (PUT /api/v1/productos/:id)
// Protegida por authApiKey
router.put('/productos/:id', authApiKey, async (req, res, next) => {
    try {
        const productoActualizado = await productosService.actualizarProducto(req.params.id, req.body);
        res.status(200).json({
            data: {
                type: 'productos',
                id: productoActualizado.id.toString(),
                attributes: productoActualizado
            }
        });
    } catch (error) {
        next(error);
    }
});


module.exports = router;
