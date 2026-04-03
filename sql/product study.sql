-- Check for NULL productCode values
-- Expected output: 0 rows
SELECT *
FROM products
WHERE productCode IS NULL;
-- Check for duplicate productCodes
-- Expected output: EMPTY SET
SELECT
    productCode,
    COUNT(*) AS cnt
FROM products
GROUP BY productCode
HAVING COUNT(*) > 1;
-- Find productCodes used in orders but missing in products table
-- Expected output: EMPTY SET
SELECT DISTINCT
    od.productCode
FROM orderdetails od
LEFT JOIN products p
    ON od.productCode = p.productCode
WHERE p.productCode IS NULL;
-- Products that have never appeared in orderdetails
-- This is NOT an error; useful business insight
SELECT
    p.productCode,
    p.productName
FROM products p
LEFT JOIN orderdetails od
    ON p.productCode = od.productCode
WHERE od.productCode IS NULL;
-- productCode cleaning decision
-- ----------------------------
-- 1) productCode must be NON-NULL and UNIQUE
-- 2) Validated no duplicate productCodes
-- 3) Referential integrity validated against orderdetails.productCode
-- 4) Products with no sales are allowed and retained for analysis
-- 5) No transformations required

-- Check for NULL product names
-- Expected output: 0 rows
SELECT productCode, productName
FROM products
WHERE productName IS NULL;
-- Check for NULL product names
-- Expected output: 0 rows
SELECT productCode, productName
FROM products
WHERE productName IS NULL;
-- Check for leading or trailing spaces in productName
-- Expected output: EMPTY SET
SELECT productCode, productName
FROM products
WHERE productName <> TRIM(productName);
-- Find duplicate product names mapped to multiple productCodes
-- Expected: some rows may appear (this is allowed)
SELECT
    productName,
    COUNT(DISTINCT productCode) AS product_code_count
FROM products
GROUP BY productName
HAVING COUNT(DISTINCT productCode) > 1;
-- Identify product names with non-alphanumeric or unusual characters
-- This is a sanity check, not necessarily an error
SELECT productCode, productName
FROM products
WHERE productName REGEXP '[^a-zA-Z0-9 .,()-]';
-- Find duplicate product names mapped to multiple productCodes
-- Expected: some rows may appear (this is allowed)
SELECT
    productName,
    COUNT(DISTINCT productCode) AS product_code_count
FROM products
GROUP BY productName
HAVING COUNT(DISTINCT productCode) > 1;
-- Distribution of productName usage
SELECT
    productName,
    COUNT(*) AS occurrences
FROM products
GROUP BY productName
ORDER BY occurrences DESC;
-- productName cleaning decision
-- -----------------------------
-- 1) productName must be NON-NULL                   
-- 2) Leading/trailing spaces checked; trim if needed
-- 3) Special characters reviewed; retained as-is    
-- 4) Duplicate names across productCodes are allowed
-- 5) productName is descriptive only; not a key 

-- Check for NULL quantityInStock (❌ not allowed)
-- Expected output: 0 rows
SELECT productCode, productName, quantityInStock
FROM products
WHERE quantityInStock IS NULL;
-- Check for negative stock values (invalid)
-- Expected output: EMPTY SET
SELECT productCode, productName, quantityInStock
FROM products
WHERE quantityInStock < 0;
-- Quick range overview
SELECT
    MIN(quantityInStock) AS min_stock,
    MAX(quantityInStock) AS max_stock,
    AVG(quantityInStock) AS avg_stock
FROM products;
-- Flag low-stock products (threshold can be tuned)
SELECT productCode, productName, quantityInStock
FROM products
WHERE quantityInStock <= 100
ORDER BY quantityInStock ASC;
-- Flag high-stock products (possible overstock)
SELECT productCode, productName, quantityInStock
FROM products
ORDER BY quantityInStock DESC
LIMIT 20;
-- Flag outliers using z-score (|z| > 3)
SELECT
    p.productCode,
    p.productName,
    p.quantityInStock,
    ROUND((p.quantityInStock - s.avg_stock) / NULLIF(s.std_stock, 0), 2) AS z_score
FROM products p
CROSS JOIN (
    SELECT
        AVG(quantityInStock) AS avg_stock,
        STDDEV_POP(quantityInStock) AS std_stock
    FROM products
) s
WHERE s.std_stock > 0
  AND ABS((p.quantityInStock - s.avg_stock) / s.std_stock) > 3
ORDER BY ABS((p.quantityInStock - s.avg_stock) / s.std_stock) DESC;
-- Approximate IQR outliers using NTILE (MySQL 8+)
WITH ranked AS (
    SELECT
        quantityInStock,
        NTILE(4) OVER (ORDER BY quantityInStock) AS quartile
    FROM products
),
iqr_vals AS (
    SELECT
        MAX(CASE WHEN quartile = 1 THEN quantityInStock END) AS q1,
        MAX(CASE WHEN quartile = 3 THEN quantityInStock END) AS q3
    FROM ranked
)
SELECT
    p.productCode,
    p.productName,
    p.quantityInStock,
    v.q1,
    v.q3,
    (v.q3 - v.q1) AS iqr
FROM products p
CROSS JOIN iqr_vals v
WHERE p.quantityInStock < (v.q1 - 1.5 * (v.q3 - v.q1))
   OR p.quantityInStock > (v.q3 + 1.5 * (v.q3 - v.q1))
ORDER BY p.quantityInStock DESC;
-- buyPrice NULL check
-- Expected output: 0 rows
SELECT productCode, productName, buyPrice
FROM products
WHERE buyPrice IS NULL;
-- Invalid buyPrice check (<= 0)
-- Expected output: EMPTY SET
SELECT productCode, productName, buyPrice
FROM products
WHERE buyPrice <= 0;
-- Pricing logic check: buyPrice > MSRP (invalid)
-- Expected output: EMPTY SET
SELECT productCode, productName, buyPrice, MSRP
FROM products
WHERE buyPrice > MSRP;
-- MSRP NULL check
-- Expected output: 0 rows
SELECT productCode, productName, MSRP
FROM products
WHERE MSRP IS NULL;
-- Invalid MSRP check (<= 0)
-- Expected output: EMPTY SET
SELECT productCode, productName, MSRP
FROM products
WHERE MSRP <= 0;
-- Derived: margin and margin percentage
SELECT
    productCode,
    productName,
    buyPrice,
    MSRP,
    (MSRP - buyPrice) AS margin,
    ROUND(((MSRP - buyPrice) / NULLIF(MSRP, 0)) * 100, 2) AS margin_pct
FROM products
ORDER BY margin DESC;
-- Derived: inventory value based on buyPrice
SELECT
    productCode,
    productName,
    quantityInStock,
    buyPrice,
    (quantityInStock * buyPrice) AS inventory_value
FROM products
ORDER BY inventory_value DESC
LIMIT 20;
-- Derived: stock status flag (dashboard-friendly)
SELECT
    productCode,
    productName,
    quantityInStock,
    CASE
        WHEN quantityInStock <= 50 THEN 'LOW'
        WHEN quantityInStock BETWEEN 51 AND 200 THEN 'NORMAL'
        ELSE 'HIGH'
    END AS stock_status
FROM products
ORDER BY quantityInStock ASC;
-- Pricing cleaning decision (buyPrice / MSRP)
-- ------------------------------------------
-- 1) buyPrice and MSRP should be NON-NULL and > 0
-- 2) buyPrice must be <= MSRP (pricing logic validation)
-- 3) Any violations are flagged (not deleted) for review
-- 4) Derived fields for BI/ML: margin, margin_pct, inventory_value, stock_status
-- Top vendors by total units sold (highest selling)
SELECT
    p.productVendor,
    SUM(od.quantityOrdered) AS units_sold
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY units_sold DESC;
-- Top vendors by total revenue (priceEach * quantity)
SELECT
    p.productVendor,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_revenue
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY total_revenue DESC;
-- Vendors with highest frequency of sales (most order lines)
SELECT
    p.productVendor,
    COUNT(*) AS order_line_count
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY order_line_count DESC;
-- Vendors whose products appear in the most distinct orders
SELECT
    p.productVendor,
    COUNT(DISTINCT od.orderNumber) AS distinct_orders
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY distinct_orders DESC;
-- Least purchased vendors (lowest total units sold)
SELECT
    p.productVendor,
    SUM(od.quantityOrdered) AS units_sold
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY units_sold ASC;
-- Vendors by estimated gross profit
-- Profit proxy = (selling priceEach - buyPrice) * quantityOrdered
SELECT
    p.productVendor,
    ROUND(SUM((od.priceEach - p.buyPrice) * od.quantityOrdered), 2) AS est_gross_profit
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY est_gross_profit DESC;
-- Vendors with negative estimated profit (loss)
SELECT
    p.productVendor,
    ROUND(SUM((od.priceEach - p.buyPrice) * od.quantityOrdered), 2) AS est_gross_profit
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
HAVING est_gross_profit < 0
ORDER BY est_gross_profit ASC;
-- Vendor profit margin % = profit / revenue
SELECT
    p.productVendor,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS revenue,
    ROUND(SUM((od.priceEach - p.buyPrice) * od.quantityOrdered), 2) AS est_profit,
    ROUND(
        (SUM((od.priceEach - p.buyPrice) * od.quantityOrdered) / NULLIF(SUM(od.quantityOrdered * od.priceEach), 0)) * 100
    , 2) AS profit_margin_pct
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor
ORDER BY profit_margin_pct DESC;
-- Example filter: include only shipped orders
SELECT
    p.productVendor,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_revenue
FROM orderdetails od
JOIN products p ON od.productCode = p.productCode
JOIN orders o ON od.orderNumber = o.orderNumber
WHERE o.status = 'Shipped'
GROUP BY p.productVendor
ORDER BY total_revenue DESC;
-- Show sold products with vendor name (proof mapping works)
SELECT
    od.orderNumber,
    od.productCode,
    p.productName,
    p.productVendor,
    od.quantityOrdered,
    od.priceEach
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
LIMIT 20;
-- Vendor sales with order info (complete join path)
SELECT
    o.orderNumber,
    o.orderDate,
    p.productVendor,
    SUM(od.quantityOrdered) AS units_sold,
    SUM(od.quantityOrdered * od.priceEach) AS revenue
FROM orders o
JOIN orderdetails od
    ON o.orderNumber = od.orderNumber
JOIN products p
    ON od.productCode = p.productCode
GROUP BY o.orderNumber, o.orderDate, p.productVendor;