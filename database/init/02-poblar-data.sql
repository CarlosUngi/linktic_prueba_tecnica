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
(105, '3m USB-C Cable', 'High-resistance braided cable with fast charging support.', 9.99, 0), -- Inactive product
(106, 'Gaming Laptop', '15-inch laptop with RTX 3060 and 16GB RAM.', 1200.00, 1),
(107, 'Bluetooth Headphones', 'Over-ear headphones with noise cancellation.', 150.00, 1),
(108, '4TB External SSD', 'Portable SSD with USB-C connection.', 350.00, 1),
(109, 'Ergonomic Chair', 'Office chair with lumbar support.', 250.00, 1),
(110, 'Docking Station', 'USB-C hub with multiple ports for peripherals.', 89.99, 1),
(111, 'Smartwatch', 'Fitness tracker with heart rate monitor.', 199.99, 1),
(112, 'VR Headset', 'Virtual reality headset for immersive gaming.', 399.00, 1),
(113, '4K Projector', 'Home theater projector with 3000 lumens.', 800.00, 1),
(114, 'Mechanical Pencil Set', 'Set of professional mechanical pencils.', 15.50, 1),
(115, 'LED Desk Lamp', 'Adjustable desk lamp with wireless charging.', 45.00, 0); -- Inactive product

-- 2. Insert data into the 'inventory' table
INSERT INTO `inventory` (`product_id`, `available_stock`, `location`) VALUES
(101, 150, 'Warehouse 01 - Shelf A'),
(102, 45, 'Warehouse 02 - Zone B'),
(103, 320, 'Warehouse 01 - Shelf C'),
(104, 80, 'Warehouse 02 - Zone D'),
(105, 0, 'Warehouse 03 - Archived'), -- Stock 0 and inactive product
(106, 25, 'Warehouse 01 - Shelf B'),
(107, 200, 'Warehouse 02 - Zone A'),
(108, 75, 'Warehouse 01 - Shelf D'),
(109, 50, 'Warehouse 03 - Zone C'),
(110, 120, 'Warehouse 02 - Shelf E'),
(111, 300, 'Warehouse 01 - Zone F'),
(112, 40, 'Warehouse 03 - Shelf G'),
(113, 15, 'Warehouse 02 - Zone H'),
(114, 500, 'Warehouse 01 - Shelf I'),
(115, 10, 'Warehouse 03 - Archived'); -- Inactive product

-- Restore foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Note: You can use the following SQL command to verify the inserted data:
-- SELECT * FROM products;
-- SELECT * FROM inventory;
