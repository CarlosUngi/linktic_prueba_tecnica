-- Archivo DML: 02_seed_data.sql
-- Propósito: Inserción de datos iniciales (seed data) para las tablas productos e inventarios.
-- Nota: La inserción se realiza en el orden correcto para respetar la clave foránea.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Insertar datos en la tabla 'productos'
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `activo`) VALUES
(101, 'Teclado Mecánico RGB', 'Teclado de alto rendimiento con switches Brown, ideal para programadores.', 79.99, 1),
(102, 'Monitor Ultrawide 34"', 'Pantalla curva 4K con tasa de refresco de 144Hz. Perfecto para gaming y diseño.', 499.50, 1),
(103, 'Mouse Ergonómico Inalámbrico', 'Mouse vertical recargable con conexión Bluetooth y DPI ajustable.', 25.00, 1),
(104, 'Webcam Full HD 1080p', 'Cámara con enfoque automático y micrófono dual. Ideal para videollamadas.', 35.75, 1),
(105, 'Cable USB-C de 3m', 'Cable trenzado de alta resistencia con soporte de carga rápida.', 9.99, 0); -- Producto inactivo para probar la paginación/filtrado

-- 2. Insertar datos en la tabla 'inventarios'
-- Se asume que los IDs de producto generados automáticamente son 101, 102, 103, 104 y 105.
-- La tabla inventarios depende de estos IDs.
INSERT INTO `inventarios` (`producto_id`, `cantidad_disponible`, `ubicacion`) VALUES
(101, 150, 'Almacén 01 - Estante A'),
(102, 45, 'Almacén 02 - Zona B'),
(103, 320, 'Almacén 01 - Estante C'),
(104, 80, 'Almacén 02 - Zona D'),
(105, 0, 'Almacén 03 - Archivado'); -- Stock 0 y producto inactivo

-- Restaurar el chequeo de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- Nota: Puedes usar el siguiente comando SQL para verificar los datos insertados:
-- SELECT * FROM productos;
-- SELECT * FROM inventarios;