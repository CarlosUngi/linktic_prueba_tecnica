-- DDL File: 01_create_tables.sql
-- Purpose: Database schema creation for Products and Inventory microservices.
-- Technology: MySQL (InnoDB Engine for transactions and FKs)

-- Set character set and storage engine
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------------------------
-- TABLE: products (Managed by Products Microservice)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique product identifier (PK)',
  `name` VARCHAR(255) NOT NULL COMMENT 'Product name',
  `description` TEXT COMMENT 'Detailed product description',
  `price` DECIMAL(10, 2) NOT NULL COMMENT 'Unit price (must be greater than 0)',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Product status (1=Active, 0=Inactive - Soft Delete)',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation date',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Date of the last update',

  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_name` (`name`), -- Prevents products with the same name
  KEY `idx_is_active` (`is_active`),     -- Optimizes active product listing/pagination

  -- Constraint to ensure price is a positive value
  CONSTRAINT `chk_price_positive` CHECK (`price` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Manages the core product information.';


-- --------------------------------------------------------
-- TABLE: inventory (Managed by Inventory Microservice)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `inventory`;
CREATE TABLE `inventory` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Unique inventory record identifier (PK)',
  `product_id` BIGINT UNSIGNED NOT NULL COMMENT 'ID of the product this inventory belongs to (FK)',
  `available_stock` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Available stock quantity',
  `location` VARCHAR(100) COMMENT 'Physical stock location (e.g., Warehouse A)',
  `last_inventory_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp for stock change event emission',

  PRIMARY KEY (`id`),
  -- UNIQUE KEY: This constraint enforces the 1:1 relationship (only one inventory record per product)
  UNIQUE KEY `idx_unique_product_id` (`product_id`),
  
  -- Foreign Key: Links inventory to the product
  CONSTRAINT `fk_inventory_product` 
    FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) 
    ON DELETE CASCADE  -- If the product is deleted, its inventory record is also deleted
    ON UPDATE CASCADE, -- If the product ID is updated, it is updated in the inventory
    
  -- Constraint to ensure stock is non-negative
  CONSTRAINT `chk_stock_non_negative` CHECK (`available_stock` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Manages product stock and available quantity.';

-- Restore foreign key checks
SET FOREIGN_KEY_CHECKS = 1;