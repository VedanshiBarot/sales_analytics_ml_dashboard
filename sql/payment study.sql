/* ============================================================
   PAYMENTS TABLE STUDY + CLEAN DATE + INSIGHTS (CORRECT VERSION)
   Schema: sales_analytics_internship
   Notes:
   - payments has NO orderNumber, so "order-level payment matching" is not possible.
   - All payment-to-order logic is CUSTOMER-level or APPROXIMATE ship→pay matching.
   ============================================================ */

USE sales_analytics_internship;

-- ------------------------------------------------------------
-- 0) Sanity: tables
-- ------------------------------------------------------------
SHOW TABLES;

-- ------------------------------------------------------------
-- 1) payments.customerNumber (FK) checks
-- ------------------------------------------------------------

/* 1A) NULL customerNumber check
   Expected: 0 rows
*/
SELECT *
FROM payments
WHERE customerNumber IS NULL;

/* 1B) Orphan payments check against COMPLETE customer master
   Use vw_customers_all (should include customers + customers_missing)
   Expected: ideally 0 rows; if >0 => master data gap
*/
SELECT
    p.customerNumber,
    COUNT(*) AS payment_count
FROM payments p
LEFT JOIN vw_customers_all c
    ON p.customerNumber = c.customerNumber
WHERE c.customerNumber IS NULL
GROUP BY p.customerNumber
ORDER BY payment_count DESC;

/* 1C) Multiple payments per customer (expected)
   Expected: many rows
*/
SELECT
    customerNumber,
    COUNT(*) AS total_payments
FROM payments
GROUP BY customerNumber
HAVING COUNT(*) > 1
ORDER BY total_payments DESC;

/* 1D) Overall coverage (sanity)
   Expected: summary counts
*/
SELECT
    COUNT(DISTINCT customerNumber) AS unique_customers,
    COUNT(*) AS total_payments
FROM payments;

-- Cleaning decision (document)
-- customerNumber is mandatory, many payments per customer allowed,
-- do not modify; flag missing master customers (if any).

-- ------------------------------------------------------------
-- 2) payments.checkNumber (payment identifier) checks
-- ------------------------------------------------------------

/* 2A) NULL checkNumber check
   Expected: 0 rows
*/
SELECT *
FROM payments
WHERE checkNumber IS NULL;

/* 2B) Uniqueness of checkNumber
   Expected: 0 rows
*/
SELECT
    checkNumber,
    COUNT(*) AS occurrence_count
FROM payments
GROUP BY checkNumber
HAVING COUNT(*) > 1;

/* 2C) checkNumber length (inspection)
*/
SELECT
    checkNumber,
    LENGTH(checkNumber) AS char_length
FROM payments
ORDER BY char_length DESC
LIMIT 10;

/* 2D) Suspicious characters (non-alphanumeric)
   Expected: 0 rows (usually)
*/
SELECT DISTINCT checkNumber
FROM payments
WHERE checkNumber REGEXP '[^A-Za-z0-9]';

/* 2E) payments count vs distinct checkNumbers
   Expected: equal numbers
*/
SELECT
    COUNT(*) AS total_payments,
    COUNT(DISTINCT checkNumber) AS distinct_check_numbers
FROM payments;

-- Cleaning decision (document)
-- checkNumber is mandatory + unique; keep for audit only (not ML feature).

-- ------------------------------------------------------------
-- 3) payments.paymentDate (TEXT) → paymentDate_clean (DATE)
-- ------------------------------------------------------------

/* 3A) NULL/blank paymentDate check
   Expected: ideally 0
*/
SELECT
    SUM(paymentDate IS NULL) AS null_paymentDate,
    SUM(paymentDate IS NOT NULL AND TRIM(paymentDate)='') AS blank_paymentDate
FROM payments;

/* 3B) Inspect raw values (sample)
*/
SELECT paymentDate
FROM payments
WHERE paymentDate IS NOT NULL
LIMIT 20;

/* 3C) Detect formats (pattern counts)
*/
SELECT
  SUM(TRIM(paymentDate) REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$') AS fmt_yyyy_mm_dd,
  SUM(TRIM(paymentDate) REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$') AS fmt_dd_mm_yyyy,
  SUM(TRIM(paymentDate) REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$') AS fmt_dd_mm_yyyy_slash,
  SUM(TRIM(paymentDate) REGEXP '^[0-9]{4}/[0-9]{2}/[0-9]{2}$') AS fmt_yyyy_mm_dd_slash,
  SUM(paymentDate IS NULL OR TRIM(paymentDate)='') AS blank_or_null
FROM payments;

/* 3D) Ensure paymentDate_clean exists
*/
-- Create column only if it doesn't exist (safe approach)
SELECT COUNT(*) AS col_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'sales_analytics_internship'
  AND TABLE_NAME = 'payments'
  AND COLUMN_NAME = 'paymentDate_clean';


SHOW FULL COLUMNS FROM payments LIKE 'paymentDate_clean';
/* 3E) Populate paymentDate_clean using multi-format parsing (robust)
   NOTE: This overwrites only when NULL to be safe
*/
SET SQL_SAFE_UPDATES = 0;

UPDATE payments
SET paymentDate_clean =
  CASE
    WHEN paymentDate IS NULL OR TRIM(paymentDate) = '' THEN NULL

    -- YYYY-MM-DD
    WHEN TRIM(paymentDate) REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
      THEN STR_TO_DATE(TRIM(paymentDate), '%Y-%m-%d')

    -- DD-MM-YYYY
    WHEN TRIM(paymentDate) REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
      THEN STR_TO_DATE(TRIM(paymentDate), '%d-%m-%Y')

    -- DD/MM/YYYY
    WHEN TRIM(paymentDate) REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
      THEN STR_TO_DATE(TRIM(paymentDate), '%d/%m/%Y')

    -- YYYY/MM/DD
    WHEN TRIM(paymentDate) REGEXP '^[0-9]{4}/[0-9]{2}/[0-9]{2}$'
      THEN STR_TO_DATE(TRIM(paymentDate), '%Y/%m/%d')

    ELSE NULL
  END
WHERE paymentDate_clean IS NULL;

/* 3F) Verify population
*/
SELECT
    COUNT(*) AS total_rows,
    SUM(paymentDate_clean IS NOT NULL) AS populated_rows,
    SUM(paymentDate_clean IS NULL) AS null_rows
FROM payments;

/* 3G) Show any values that still failed parsing (should be 0)
*/
SELECT paymentDate
FROM payments
WHERE (paymentDate IS NOT NULL AND TRIM(paymentDate) <> '')
  AND paymentDate_clean IS NULL
LIMIT 50;

/* 3H) Confirm datatype
   Expected: DATE
*/
SHOW FULL COLUMNS FROM payments LIKE 'paymentDate_clean';

/* 3I) Future dates check (should be 0 rows)
*/
SELECT
    customerNumber,
    checkNumber,
    paymentDate_clean,
    amount
FROM payments
WHERE paymentDate_clean > CURDATE()
ORDER BY paymentDate_clean DESC;

-- ------------------------------------------------------------
-- 4) Timeline alignment with orders (CUSTOMER-LEVEL checks)
-- ------------------------------------------------------------

/* 4A) First payment earlier than first order date (suspicious)
   Expected: ideally 0 rows or very few
*/
SELECT
    p.customerNumber,
    MIN(p.paymentDate_clean) AS first_payment_date,
    MIN(o.orderDate) AS first_order_date
FROM payments p
JOIN orders o
    ON p.customerNumber = o.customerNumber
WHERE p.paymentDate_clean IS NOT NULL
GROUP BY p.customerNumber
HAVING MIN(p.paymentDate_clean) < MIN(o.orderDate);

/* 4B) Last payment after last order date (payment lag; not invalid)
   Shows top 20 customers by lag after last order
*/
SELECT
    p.customerNumber,
    MAX(o.orderDate) AS last_order_date,
    MAX(p.paymentDate_clean) AS last_payment_date,
    DATEDIFF(MAX(p.paymentDate_clean), MAX(o.orderDate)) AS days_after_last_order
FROM payments p
JOIN orders o
    ON p.customerNumber = o.customerNumber
WHERE p.paymentDate_clean IS NOT NULL
GROUP BY p.customerNumber
ORDER BY days_after_last_order DESC
LIMIT 20;

-- ------------------------------------------------------------
-- 5) Cash inflow trend + seasonality
-- ------------------------------------------------------------

/* 5A) Monthly cash inflow trend */
SELECT
    DATE_FORMAT(paymentDate_clean, '%Y-%m') AS payment_month,
    SUM(amount) AS total_revenue,
    COUNT(*) AS total_payments
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY payment_month
ORDER BY payment_month;

/* 5B) Seasonality (month-of-year) */
SELECT
    MONTH(paymentDate_clean) AS month_num,
    SUM(amount) AS total_revenue
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY month_num
ORDER BY month_num;

-- ------------------------------------------------------------
-- 6) Customer payment behavior snapshot (BI + ML feature base)
-- ------------------------------------------------------------

SELECT
    customerNumber,
    MAX(paymentDate_clean) AS last_payment_date,
    DATEDIFF(CURDATE(), MAX(paymentDate_clean)) AS recency_days,
    COUNT(*) AS payment_count,
    SUM(amount) AS total_amount_paid,
    AVG(amount) AS avg_payment_amount
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY customerNumber;

-- ------------------------------------------------------------
-- 7) Ship → Pay lag (APPROXIMATE, payment-level)
-- ------------------------------------------------------------

/* For each payment, match the latest shippedDate <= paymentDate_clean
   for that customer (if exists), then compute ship_to_pay_days.
   Expected: ship_to_pay_days >= 0 (NULL if no shippedDate exists <= payment)
*/
SELECT
    p.customerNumber,
    p.checkNumber,
    p.paymentDate_clean,
    p.amount,
    m.matched_shipped_date,
    DATEDIFF(p.paymentDate_clean, m.matched_shipped_date) AS ship_to_pay_days
FROM payments p
JOIN (
    SELECT
        p2.customerNumber,
        p2.checkNumber,
        MAX(o.shippedDate) AS matched_shipped_date
    FROM payments p2
    JOIN orders o
      ON o.customerNumber = p2.customerNumber
     AND o.shippedDate IS NOT NULL
     AND p2.paymentDate_clean IS NOT NULL
     AND o.shippedDate <= p2.paymentDate_clean
    GROUP BY p2.customerNumber, p2.checkNumber
) m
  ON m.customerNumber = p.customerNumber
 AND m.checkNumber = p.checkNumber
ORDER BY ship_to_pay_days DESC
LIMIT 50;

-- ------------------------------------------------------------
-- 8) Top / low paying customers + recency risk
-- ------------------------------------------------------------

/* 8A) Top paying customers */
SELECT
    customerNumber,
    SUM(amount) AS total_amount_paid
FROM payments
GROUP BY customerNumber
ORDER BY total_amount_paid DESC
LIMIT 10;

/* 8B) Lowest paying customers (who have paid > 0) */
SELECT
    customerNumber,
    SUM(amount) AS total_amount_paid
FROM payments
GROUP BY customerNumber
HAVING SUM(amount) > 0
ORDER BY total_amount_paid ASC
LIMIT 10;

/* 8C) One-time low-value payers */
SELECT
    customerNumber,
    COUNT(*) AS payment_count,
    SUM(amount) AS total_amount_paid
FROM payments
GROUP BY customerNumber
HAVING COUNT(*) = 1
ORDER BY total_amount_paid ASC
LIMIT 10;

/* 8D) High-value but inactive (not paid recently) */
SELECT
    customerNumber,
    SUM(amount) AS total_amount_paid,
    MAX(paymentDate_clean) AS last_payment_date,
    DATEDIFF(CURDATE(), MAX(paymentDate_clean)) AS recency_days
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY customerNumber
HAVING recency_days > 90
ORDER BY total_amount_paid DESC
LIMIT 10;

-- ------------------------------------------------------------
-- 9) Customers who have orders but no payments (CUSTOMER-LEVEL gap)
-- ------------------------------------------------------------

/* 9A) List customers with orders but no payments at all */
SELECT
    o.customerNumber,
    COUNT(DISTINCT o.orderNumber) AS total_orders,
    MIN(o.orderDate) AS first_order_date,
    MAX(o.orderDate) AS last_order_date
FROM orders o
LEFT JOIN payments p
    ON o.customerNumber = p.customerNumber
WHERE p.customerNumber IS NULL
GROUP BY o.customerNumber
ORDER BY total_orders DESC;

/* 9B) Count of such customers */
SELECT
    COUNT(DISTINCT o.customerNumber) AS customers_without_payments
FROM orders o
LEFT JOIN payments p
    ON o.customerNumber = p.customerNumber
WHERE p.customerNumber IS NULL;


