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
