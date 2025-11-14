// middleware/errorHandler.js
const { InvalidInputError, ResourceNotFoundError, UnauthorizedError } = require('../config/errorCodes');

/**
 * Middleware de manejo de errores global.
 * Captura las excepciones y las formatea en una respuesta JSON:API estandarizada.
 */
const errorHandler = (err, req, res, next) => {
    let statusCode = 500;
    let errorCode = 'INTERNAL_SERVER_ERROR';
    let title = 'Error Interno del Servidor';
    let detail = 'Ocurrió un error inesperado. El incidente ha sido registrado.';

    if (err instanceof InvalidInputError) {
        statusCode = 400;
        errorCode = 'INVALID_INPUT_DATA';
        title = 'Datos de entrada inválidos';
        detail = err.message;
    } else if (err instanceof ResourceNotFoundError) {
        statusCode = 404;
        errorCode = 'RESOURCE_NOT_FOUND';
        title = 'Recurso No Encontrado';
        detail = err.message;
    } else if (err instanceof UnauthorizedError) {
        statusCode = 401;
        errorCode = 'UNAUTHORIZED_ACCESS';
        title = 'Acceso No Autorizado';
        detail = err.message;
    }

    // TODO: Implementar logging estructurado aquí para registrar el error.

    res.status(statusCode).json({
        errors: [{
            status: statusCode.toString(),
            code: errorCode,
            title: title,
            detail: detail
        }]
    });
};

module.exports = errorHandler;