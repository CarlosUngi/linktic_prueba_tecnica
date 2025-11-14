// models/productosModel.js - Implementación del Patrón Repositorio
// Propósito: Abstraer el acceso a la tabla 'productos' (SQL).
const poolPromise = require('../db/conexionPool');

class ProductosModel {

    // Método 1: obtenerPorId(id)
    // Tarea: Buscar un producto por su PK.
    async obtenerPorId(id) {
        const pool = await poolPromise;
        const query = 'SELECT * FROM products WHERE id = ? AND is_active = 1;';
        const [rows] = await pool.query(query, [id]);
        return rows[0] || null;
    }

    // Método 2: listarProductos(paginacion)
    // Tarea: Obtener lista paginada de productos activos.
    async listarProductos({ limite, offset }) {
        const pool = await poolPromise;
        // Importante: No usar ORDER BY aquí para evitar errores de índice (firestore instruction).
        // Se recomienda ordenar en JS si es necesario.
        const query = 'SELECT * FROM products WHERE is_active = 1 LIMIT ? OFFSET ?;';
        const [rows] = await pool.query(query, [limite, offset]);

        const countQuery = 'SELECT COUNT(*) as total FROM products WHERE is_active = 1;';
        const [countRows] = await pool.query(countQuery);
        const total = countRows[0].total;

        return { data: rows, meta: { total, limite, offset } };
    }

    // Método 3: crearProducto(datos)
    // Tarea: Insertar un nuevo producto.
    async crearProducto({ name, description, price }) {
        const pool = await poolPromise;
        const query = 'INSERT INTO products (name, description, price) VALUES (?, ?, ?);';
        const [result] = await pool.query(query, [name, description, price]);
        return result.insertId;
    }

    // Método 4: eliminarProducto(id) - Soft Delete
    // Tarea: Actualizar el campo 'activo' a 0.
    async eliminarProducto(id) {
        const pool = await poolPromise;
        const query = 'UPDATE products SET is_active = 0 WHERE id = ?;';
        const [result] = await pool.query(query, [id]);
        return result.affectedRows; // Retorna 1 si se eliminó (soft delete)
    }

    // Tarea Pendiente: implementar actualizarProducto(id, datos)
    async actualizarProducto(id, datos) {
        const pool = await poolPromise;
        
        const fields = Object.keys(datos);
        const values = Object.values(datos);
        
        if (fields.length === 0) {
            return 0; // No hay nada que actualizar
        }

        const setClause = fields.map(field => `${field} = ?`).join(', ');
        
        const query = `UPDATE products SET ${setClause} WHERE id = ?;`;
        
        const [result] = await pool.query(query, [...values, id]);
        return result.affectedRows;
    }

}

module.exports = new ProductosModel();
