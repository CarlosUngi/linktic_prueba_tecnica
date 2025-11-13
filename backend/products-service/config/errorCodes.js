const errorCodes = {
    INVALID_INPUT_DATA: 'INVALID_INPUT_DATA',
    RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
    UNAUTHORIZED_ACCESS: 'UNAUTHORIZED_ACCESS', // Usado en authApiKey.js
    DB_ERROR: 'DATABASE_ERROR'
};

// Clases de error personalizadas para la capa de Servicio
class CustomError extends Error {
    constructor(message, code, details = []) {
        super(message);
        this.code = code;
        this.details = details;
        this.name = this.constructor.name;
    }
}
class InvalidInputError extends CustomError { constructor(message, details) { super(message, errorCodes.INVALID_INPUT_DATA, details); } }
class ResourceNotFoundError extends CustomError { constructor(message) { super(message, errorCodes.RESOURCE_NOT_FOUND); } }

module.exports = { errorCodes, InvalidInputError, ResourceNotFoundError, CustomError };
