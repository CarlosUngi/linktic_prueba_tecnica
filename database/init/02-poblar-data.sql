-- DML File: 02_seed_data.sql
-- Purpose: Insertion of initial data (seed data) for the products and inventory tables.
-- Note: Insertion is performed in the correct order to respect the foreign key constraint.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Insert data into the 'products' table
INSERT INTO `products` (`id`, `name`, `description`, `price`, `is_active`) VALUES
(101, 'RGB Mechanical Keyboard', 'High-performance keyboard with Brown switches, ideal for programmers.', 79.99, 1),
(102, '34-inch Ultrawide Monitor', 'Curved 4K screen with a 144Hz refresh rate. Perfect for gaming and design.', 499.50, 1),
(103, 'Wireless Ergonomic Mouse', 'Rechargeable vertical mouse with Bluetooth connection and adjustable DPI.', 25.00, 1),
(104, 'Full HD 1080p Webcam', 'Camera with autofocus and dual microphone. Ideal for video calls.', 35.75, 1),
(105, '3m USB-C Cable', 'High-resistance braided cable with fast charging support.', 9.99, 0); -- Inactive product to test pagination/filtering

-- 2. Insert data into the 'inventory' table
-- Assuming the automatically generated product IDs are 101, 102, 103, 104, and 105.
INSERT INTO `inventory` (`product_id`, `available_stock`, `location`) VALUES
(101, 150, 'Warehouse 01 - Shelf A'),
(102, 45, 'Warehouse 02 - Zone B'),
(103, 320, 'Warehouse 01 - Shelf C'),
(104, 80, 'Warehouse 02 - Zone D'),
(105, 0, 'Warehouse 03 - Archived'); -- Stock 0 and inactive product

-- Restore foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Note: You can use the following SQL command to verify the inserted data:
-- SELECT * FROM products;
-- SELECT * FROM inventory;