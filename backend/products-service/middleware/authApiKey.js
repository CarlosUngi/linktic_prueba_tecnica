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
