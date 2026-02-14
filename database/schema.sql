-- Create database
CREATE DATABASE IF NOT EXISTS customs_calculator;
USE customs_calculator;

-- Table 1: Customs Rules
CREATE TABLE IF NOT EXISTS customs_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origin_country VARCHAR(50) NOT NULL,
    destination_country VARCHAR(50) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    hs_code VARCHAR(20) NOT NULL,
    base_duty_rate DECIMAL(5, 4) NOT NULL,
    gst_rate DECIMAL(5, 4) NOT NULL,
    regulation_reference TEXT,
    effective_from DATE DEFAULT (CURRENT_DATE),
    effective_until DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_route_category (origin_country, destination_country, product_category)
);

-- Table 2: Additional Fees
CREATE TABLE IF NOT EXISTS additional_fees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(50) NOT NULL,
    fee_name VARCHAR(100) NOT NULL,
    calculation_method VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    regulation_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country)
);

-- Table 3: Calculation Audit Log
CREATE TABLE IF NOT EXISTS calculation_audit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    product_description TEXT,
    origin_country VARCHAR(50),
    destination_country VARCHAR(50),
    classified_category VARCHAR(50),
    hs_code VARCHAR(20),
    classification_confidence DECIMAL(5, 4),
    base_price_usd DECIMAL(10, 2),
    total_charges_inr DECIMAL(10, 2),
    calculation_details JSON,
    INDEX idx_order_id (order_id),
    INDEX idx_timestamp (timestamp)
);

-- Insert initial customs rules
INSERT INTO customs_rules 
(origin_country, destination_country, product_category, hs_code, base_duty_rate, gst_rate, regulation_reference, notes)
VALUES
-- USA to India
('USA', 'India', 'Electronics', '8518.30.00', 0.1500, 0.1800, 'India Customs Tariff Act 2024, Schedule II, Item 8518', 'Audio equipment including headphones'),
('USA', 'India', 'Clothing', '6109.10.00', 0.1200, 0.1200, 'India Customs Tariff Act 2024, Schedule VII, Item 6109', 'Cotton clothing'),
('USA', 'India', 'Books', '4901.99.00', 0.0000, 0.0000, 'India Customs Tariff Act 2024, Schedule IX (Duty-free)', 'Books are duty-free'),
('USA', 'India', 'Toys', '9503.00.00', 0.1000, 0.1800, 'India Customs Tariff Act 2024, Schedule XII, Item 9503', 'Toys and games'),

-- China to India (higher rates)
('China', 'India', 'Electronics', '8518.30.00', 0.2000, 0.1800, 'India Customs Tariff Act 2024 + China Surcharge (5%)', 'Higher duty for China electronics'),
('China', 'India', 'Clothing', '6109.10.00', 0.1500, 0.1200, 'India Customs Tariff Act 2024 + China Surcharge (3%)', 'Higher duty for China clothing'),
('China', 'India', 'Books', '4901.99.00', 0.0500, 0.0000, 'India Customs Tariff Act 2024, Reduced rate', 'Small duty on books from China'),
('China', 'India', 'Toys', '9503.00.00', 0.1200, 0.1800, 'India Customs Tariff Act 2024 + China Surcharge (2%)', 'Higher duty for China toys');

-- Insert fees
INSERT INTO additional_fees 
(country, fee_name, calculation_method, amount, regulation_reference)
VALUES
('India', 'Customs Handling Fee', 'flat', 500.00, 'CBIC Circular 15/2024'),
('India', 'Port Handling Charges', 'per_kg', 50.00, 'Port Trust Act 2023'),
('India', 'Documentation Fee', 'flat', 200.00, 'CBIC Circular 08/2024');