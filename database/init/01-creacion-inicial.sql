-- Archivo DDL: 01_create_tables.sql
-- Propósito: Creación de la base de datos para los microservicios de Productos e Inventario.
-- Tecnología: MySQL (Motor InnoDB para transacciones y FKs)

-- Establecer el conjunto de caracteres y el motor de almacenamiento
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------------------
-- TABLA: productos (Microservicio Productos)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del producto (PK)',
  `nombre` VARCHAR(255) NOT NULL COMMENT 'Nombre del producto',
  `descripcion` TEXT COMMENT 'Descripción detallada del producto',
  `precio` DECIMAL(10, 2) NOT NULL COMMENT 'Precio unitario (mayor a 0)',
  `activo` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Estado del producto (1=Activo, 0=Inactivo - Soft Delete)',
  `creado_en` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del registro',
  `actualizado_en` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de la última actualización',

  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_nombre` (`nombre`), -- Previene productos con el mismo nombre
  KEY `idx_activo` (`activo`),             -- Optimiza la paginación de productos activos

  -- Restricción para asegurar que el precio sea un valor positivo
  CONSTRAINT `chk_precio_positivo` CHECK (`precio` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Gestiona la información base de los productos.';


-- --------------------------------------------------------
-- TABLA: inventarios (Microservicio Inventario)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `inventarios`;
CREATE TABLE `inventarios` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del registro de inventario (PK)',
  `producto_id` BIGINT UNSIGNED NOT NULL COMMENT 'ID del producto al que pertenece este inventario (FK)',
  `cantidad_disponible` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Cantidad de stock disponible',
  `ubicacion` VARCHAR(100) COMMENT 'Ubicación física del stock (ej: Almacén A)',
  `ultima_actualizacion_inv` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Marca de tiempo para el evento de cambio de stock',

  PRIMARY KEY (`id`),
  -- UNIQUE KEY: Esta restricción fuerza la relación 1:1 (un solo registro de inventario por producto)
  UNIQUE KEY `idx_unique_producto_id` (`producto_id`),
  
  -- Clave Foránea: Vincula el inventario al producto
  CONSTRAINT `fk_inventarios_producto` 
    FOREIGN KEY (`producto_id`) 
    REFERENCES `productos` (`id`) 
    ON DELETE CASCADE  -- Si se borra el producto, se borra su inventario
    ON UPDATE CASCADE, -- Si se actualiza el ID del producto, se actualiza en el inventario
    
  -- Restricción para asegurar que el stock no sea negativo
  CONSTRAINT `chk_cantidad_no_negativa` CHECK (`cantidad_disponible` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Gestiona el stock y la cantidad disponible de productos.';

-- Restaurar el chequeo de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;