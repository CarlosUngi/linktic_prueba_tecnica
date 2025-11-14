// test/integration/productosFlujo.test.js
const request = require('supertest');
const { app, server } = require('../../server');
const poolPromise = require('../../db/conexionPool');

// API Key de prueba (debe coincidir con la del .env de prueba)
const API_KEY = process.env.API_KEY || 'test-api-key';

describe('Flujo de Integración de Productos API', () => {
    let pool;
    let productoId; // Para almacenar el ID del producto creado

    beforeAll(async () => {
        pool = await poolPromise;
    });

    afterAll(async () => {
        // Limpieza: eliminar el producto creado durante la prueba
        if (productoId) {
            await pool.query('DELETE FROM productos WHERE id = ?', [productoId]);
        }
        server.close(); // Cierra el servidor
        await pool.end(); // Cierra el pool de conexiones
    });

    // 1. Test para POST /productos (Crear)
    describe('POST /api/v1/productos', () => {
        it('debe crear un nuevo producto y devolver 201', async () => {
            const res = await request(app)
                .post('/api/v1/productos')
                .set('x-api-key', API_KEY)
                .send({
                    nombre: 'Producto de Integración',
                    descripcion: 'Creado desde test',
                    precio: 199.99
                });

            expect(res.statusCode).toEqual(201);
            expect(res.body.data.attributes).toHaveProperty('id');
            expect(res.body.data.attributes.nombre).toBe('Producto de Integración');
            
            // Guardar el ID para usarlo en otras pruebas y para la limpieza
            productoId = res.body.data.attributes.id;
        });

        it('debe devolver 401 si no se proporciona API Key', async () => {
            const res = await request(app)
                .post('/api/v1/productos')
                .send({ nombre: 'Test', precio: 10 });
            
            expect(res.statusCode).toEqual(401);
        });

        it('debe devolver 400 por datos inválidos', async () => {
            const res = await request(app)
                .post('/api/v1/productos')
                .set('x-api-key', API_KEY)
                .send({ nombre: 'N' }); // Nombre corto
            
            expect(res.statusCode).toEqual(400);
        });
    });

    // 2. Test para GET /productos (Listar)
    describe('GET /api/v1/productos', () => {
        it('debe devolver una lista de productos y 200', async () => {
            const res = await request(app).get('/api/v1/productos');
            expect(res.statusCode).toEqual(200);
            expect(Array.isArray(res.body.data)).toBe(true);
            expect(res.body.data.length).toBeGreaterThan(0);
        });
    });

    // 3. Test para GET /productos/:id (Obtener)
    describe('GET /api/v1/productos/:id', () => {
        it('debe devolver un producto por su ID y 200', async () => {
            const res = await request(app).get(`/api/v1/productos/${productoId}`);
            expect(res.statusCode).toEqual(200);
            expect(res.body.data.id).toBe(productoId.toString());
        });

        it('debe devolver 404 si el producto no existe', async () => {
            const res = await request(app).get('/api/v1/productos/99999');
            expect(res.statusCode).toEqual(404);
        });
    });

    // 4. Test para PUT /productos/:id (Actualizar)
    describe('PUT /api/v1/productos/:id', () => {
        it('debe actualizar un producto y devolver 200', async () => {
            const res = await request(app)
                .put(`/api/v1/productos/${productoId}`)
                .set('x-api-key', API_KEY)
                .send({ precio: 250.50 });

            expect(res.statusCode).toEqual(200);
            expect(res.body.data.attributes.precio).toBe('250.50');
        });

        it('debe devolver 404 si el producto a actualizar no existe', async () => {
            const res = await request(app)
                .put('/api/v1/productos/99999')
                .set('x-api-key', API_KEY)
                .send({ precio: 100 });
            
            expect(res.statusCode).toEqual(404);
        });
    });

    // 5. Test para DELETE /productos/:id (Eliminar)
    describe('DELETE /api/v1/productos/:id', () => {
        it('debe eliminar (soft delete) un producto y devolver 204', async () => {
            const res = await request(app)
                .delete(`/api/v1/productos/${productoId}`)
                .set('x-api-key', API_KEY);
            
            expect(res.statusCode).toEqual(204);

            // Verificar que ya no se puede obtener (porque está inactivo)
            const getRes = await request(app).get(`/api/v1/productos/${productoId}`);
            expect(getRes.statusCode).toEqual(404);
        });

        it('debe devolver 404 si el producto a eliminar no existe', async () => {
            const res = await request(app)
                .delete('/api/v1/productos/99999')
                .set('x-api-key', API_KEY);
            
            expect(res.statusCode).toEqual(404);
        });
    });
});