// test/unit/models/productosModel.test.js
const productosModel = require('../../../models/productosModel');
const poolPromise = require('../../../db/conexionPool');

// Mock del pool de MySQL
jest.mock('../../../db/conexionPool', () => {
    const mPool = {
        query: jest.fn(),
    };
    return Promise.resolve(mPool);
});

describe('ProductosModel', () => {
    let pool;
    beforeEach(async () => {
        pool = await poolPromise;
        pool.query.mockClear();
    });

    // Test para crearProducto
    test('crearProducto debe insertar un producto y devolver el ID', async () => {
        const mockProducto = { nombre: 'Test Producto', descripcion: 'Descripción', precio: 100 };
        const mockResult = { insertId: 1 };
        pool.query.mockResolvedValue([mockResult]);

        const id = await productosModel.crearProducto(mockProducto);

        expect(pool.query).toHaveBeenCalledWith(
            'INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?);',
            [mockProducto.nombre, mockProducto.descripcion, mockProducto.precio]
        );
        expect(id).toBe(1);
    });

    // Test para obtenerPorId
    test('obtenerPorId debe devolver un producto si lo encuentra', async () => {
        const mockProducto = { id: 1, nombre: 'Test', is_active: 1 };
        pool.query.mockResolvedValue([[mockProducto]]);

        const producto = await productosModel.obtenerPorId(1);

        expect(pool.query).toHaveBeenCalledWith('SELECT * FROM productos WHERE id = ? AND is_active = 1;', [1]);
        expect(producto).toEqual(mockProducto);
    });

    test('obtenerPorId debe devolver null si no encuentra el producto', async () => {
        pool.query.mockResolvedValue([[]]);
        const producto = await productosModel.obtenerPorId(99);
        expect(producto).toBeNull();
    });

    // Test para listarProductos
    test('listarProductos debe devolver una lista paginada de productos', async () => {
        const mockProductos = [{ id: 1, nombre: 'P1' }, { id: 2, nombre: 'P2' }];
        const mockCount = { total: 10 };
        pool.query
            .mockResolvedValueOnce([mockProductos]) // Para la query de datos
            .mockResolvedValueOnce([[mockCount]]);   // Para la query de conteo

        const result = await productosModel.listarProductos({ limite: 5, offset: 0 });

        expect(pool.query).toHaveBeenCalledWith('SELECT * FROM productos WHERE is_active = 1 LIMIT ? OFFSET ?;', [5, 0]);
        expect(pool.query).toHaveBeenCalledWith('SELECT COUNT(*) as total FROM productos WHERE is_active = 1;');
        expect(result.data).toEqual(mockProductos);
        expect(result.meta.total).toBe(10);
    });

    // Test para actualizarProducto
    test('actualizarProducto debe ejecutar UPDATE y devolver affectedRows', async () => {
        const datosUpdate = { nombre: 'Nuevo Nombre', precio: 150 };
        const mockResult = { affectedRows: 1 };
        pool.query.mockResolvedValue([mockResult]);

        const affectedRows = await productosModel.actualizarProducto(1, datosUpdate);

        expect(pool.query).toHaveBeenCalledWith(
            'UPDATE productos SET nombre = ?, precio = ? WHERE id = ?;',
            ['Nuevo Nombre', 150, 1]
        );
        expect(affectedRows).toBe(1);
    });

    // Test para eliminarProducto (Soft Delete)
    test('eliminarProducto debe ejecutar UPDATE para hacer soft delete', async () => {
        const mockResult = { affectedRows: 1 };
        pool.query.mockResolvedValue([mockResult]);

        const affectedRows = await productosModel.eliminarProducto(1);

        expect(pool.query).toHaveBeenCalledWith('UPDATE productos SET is_active = 0 WHERE id = ?;', [1]);
        expect(affectedRows).toBe(1);
    });
});