// test/unit/logic/productosService.test.js
const productosService = require('../../../logic/productosService');
const productosModel = require('../../../models/productosModel');
const { InvalidInputError, ResourceNotFoundError } = require('../../../config/errorCodes');

// Mock del Modelo
jest.mock('../../../models/productosModel', () => ({
    crearProducto: jest.fn(),
    obtenerPorId: jest.fn(),
    listarProductos: jest.fn(),
    actualizarProducto: jest.fn(),
    eliminarProducto: jest.fn(),
}));

describe('ProductosService', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    // Tests para crearNuevoProducto
    describe('crearNuevoProducto', () => {
        it('debe crear un producto si los datos son válidos', async () => {
            const datos = { name: 'Producto Test', price: 10 };
            productosModel.crearProducto.mockResolvedValue(1);

            const result = await productosService.crearNuevoProducto(datos);

            expect(productosModel.crearProducto).toHaveBeenCalledWith(datos);
            expect(result).toEqual({ id: 1, ...datos });
        });

        it('debe lanzar InvalidInputError si los datos son inválidos', async () => {
            const datos = { name: 'P' }; // Nombre muy corto
            await expect(productosService.crearNuevoProducto(datos)).rejects.toThrow(InvalidInputError);
        });

        it('debe lanzar InvalidInputError si el nombre del producto ya existe', async () => {
            const datos = { name: 'Producto Existente', price: 20 };
            productosModel.crearProducto.mockRejectedValue({ code: 'ER_DUP_ENTRY' });

            await expect(productosService.crearNuevoProducto(datos)).rejects.toThrow(InvalidInputError);
            await expect(productosService.crearNuevoProducto(datos)).rejects.toThrow("El nombre del producto ya existe.");
        });
    });

    // Tests para obtenerProducto
    describe('obtenerProducto', () => {
        it('debe devolver un producto si existe', async () => {
            const mockProducto = { id: 1, name: 'Test' };
            productosModel.obtenerPorId.mockResolvedValue(mockProducto);

            const result = await productosService.obtenerProducto(1);

            expect(productosModel.obtenerPorId).toHaveBeenCalledWith(1);
            expect(result).toEqual(mockProducto);
        });

        it('debe lanzar ResourceNotFoundError si el producto no existe', async () => {
            productosModel.obtenerPorId.mockResolvedValue(null);
            await expect(productosService.obtenerProducto(99)).rejects.toThrow(ResourceNotFoundError);
        });
    });

    // Tests para actualizarProducto
    describe('actualizarProducto', () => {
        it('debe actualizar el producto y devolverlo', async () => {
            const datosUpdate = { price: 150 };
            const productoActualizado = { id: 1, name: 'Test', price: 150 };
            productosModel.actualizarProducto.mockResolvedValue(1); // affectedRows = 1
            productosModel.obtenerPorId.mockResolvedValue(productoActualizado);

            const result = await productosService.actualizarProducto(1, datosUpdate);

            expect(productosModel.actualizarProducto).toHaveBeenCalledWith(1, datosUpdate);
            expect(result).toEqual(productoActualizado);
        });

        it('debe lanzar InvalidInputError si no se proporcionan datos', async () => {
            await expect(productosService.actualizarProducto(1, {})).rejects.toThrow(InvalidInputError);
        });

        it('debe lanzar ResourceNotFoundError si el producto a actualizar no se encuentra', async () => {
            productosModel.actualizarProducto.mockResolvedValue(0); // affectedRows = 0
            await expect(productosService.actualizarProducto(99, { price: 100 })).rejects.toThrow(ResourceNotFoundError);
        });
    });

    // Tests para eliminarProducto
    describe('eliminarProducto', () => {
        it('debe llamar al modelo para eliminar', async () => {
            productosModel.eliminarProducto.mockResolvedValue(1); // affectedRows = 1
            await productosService.eliminarProducto(1);
            expect(productosModel.eliminarProducto).toHaveBeenCalledWith(1);
        });

        it('debe lanzar ResourceNotFoundError si el producto a eliminar no se encuentra', async () => {
            productosModel.eliminarProducto.mockResolvedValue(0); // affectedRows = 0
            await expect(productosService.eliminarProducto(99)).rejects.toThrow(ResourceNotFoundError);
        });
    });
});