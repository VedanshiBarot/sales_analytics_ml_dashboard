-- Set the active schema (database)
USE sales_analytics_internship;
SHOW TABLES;
RENAME TABLE `order details` TO orderdetails;
SHOW TABLES;

DESCRIBE orderdetails;
DESCRIBE orderdetails;
SHOW CREATE TABLE orderdetails;
SELECT COUNT(*) FROM orderdetails;
SELECT * FROM orderdetails LIMIT 10;
-- Count how many line items exist per order
SELECT 
    orderNumber,
    COUNT(*) AS line_item_count
FROM orderdetails
GROUP BY orderNumber
ORDER BY line_item_count DESC;
-- Check if orderNumber is unique (it should NOT be)
SELECT 
    COUNT(DISTINCT orderNumber) AS distinct_orders,
    COUNT(*) AS total_rows
FROM orderdetails;
-- Find orderNumbers in orderdetails that do NOT exist in orders
SELECT DISTINCT od.orderNumber
FROM orderdetails od
LEFT JOIN orders o
    ON od.orderNumber = o.orderNumber
WHERE o.orderNumber IS NULL;
-- Orders that exist but have no line items
SELECT o.orderNumber
FROM orders o
LEFT JOIN orderdetails od
    ON o.orderNumber = od.orderNumber
WHERE od.orderNumber IS NULL;
-- Check duplicate product entries within the same order
SELECT 
    orderNumber,
    productCode,
    COUNT(*) AS duplicate_count
FROM orderdetails
GROUP BY orderNumber, productCode
HAVING COUNT(*) > 1;
-- Sample few orders with multiple products
SELECT *
FROM orderdetails
WHERE orderNumber IN (
    SELECT orderNumber
    FROM orderdetails
    GROUP BY orderNumber
    HAVING COUNT(*) > 3
)
LIMIT 20;