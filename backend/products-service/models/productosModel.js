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
