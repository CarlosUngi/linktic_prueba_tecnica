// logic/productosService.js - Implementación del Patrón de Servicio
// Propósito: Contener la lógica de negocio, validaciones (Joi) y coordinación.
const productosModel = require('../models/productosModel');
const Joi = require('joi');
// Código de error estandarizado para manejo de errores
const { InvalidInputError, ResourceNotFoundError } = require('../config/errorCodes');

// Esquema de validación Joi para crear/actualizar (Principio de validación en la capa de negocio)
const productoSchema = Joi.object({
    name: Joi.string().min(3).max(255).required().messages({
        'string.min': 'El nombre debe tener al menos 3 caracteres.',
        'any.required': 'El nombre es un campo obligatorio.'
    }),
    description: Joi.string().allow(null, '').optional(),
    price: Joi.number().precision(2).positive().required().messages({
        'number.positive': 'El precio debe ser un valor positivo (chk_price_positive).',
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
            throw new ResourceNotFoundError(`Producto con ID ${id} no encontrado.`);
        }
        return producto;
    }

    // Tarea: Listar con paginación
    async listarProductos(pagina = 1, limite = 10) {
        const offset = (pagina - 1) * limite;
        return productosModel.listarProductos({ limite, offset });
    }

    async actualizarProducto(id, datos) {
        // Esquema para actualización (al menos un campo es requerido)
        const productoUpdateSchema = Joi.object({
            name: Joi.string().min(3).max(255).optional(),
            description: Joi.string().allow(null, '').optional(),
            price: Joi.number().precision(2).positive().optional(),
            is_active: Joi.boolean().optional()
        }).min(1).messages({
            'object.min': 'Debe proporcionar al menos un campo para actualizar.'
        });

        const { error } = productoUpdateSchema.validate(datos, { abortEarly: false });
        if (error) {
            throw new InvalidInputError("Datos de actualización inválidos.", error.details);
        }

        const affectedRows = await productosModel.actualizarProducto(id, datos);
        if (affectedRows === 0) {
            throw new ResourceNotFoundError(`Producto con ID ${id} no encontrado para actualizar.`);
        }
        return this.obtenerProducto(id);
    }

    async eliminarProducto(id) {
        const affectedRows = await productosModel.eliminarProducto(id);
        if (affectedRows === 0) {
            throw new ResourceNotFoundError(`Producto con ID ${id} no encontrado para eliminar.`);
        }
        return affectedRows;
    }
}

module.exports = new ProductosService();
