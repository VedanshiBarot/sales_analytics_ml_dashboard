-- Check for NULL orderNumber values (should return 0)
SELECT *
FROM orders
WHERE orderNumber IS NULL;
-- Check for duplicate orderNumber values in orders table
SELECT
    orderNumber,
    COUNT(*) AS cnt
FROM orders
GROUP BY orderNumber
HAVING COUNT(*) > 1;
-- Orders that do not have any associated order details
SELECT o.orderNumber
FROM orders o
LEFT JOIN orderdetails od
    ON o.orderNumber = od.orderNumber
WHERE od.orderNumber IS NULL;
-- Order details referencing missing orders
SELECT DISTINCT od.orderNumber
FROM orderdetails od
LEFT JOIN orders o
    ON od.orderNumber = o.orderNumber
WHERE o.orderNumber IS NULL;
-- Check if orderNumber maps to more than one orderDate (should not)
SELECT
    orderNumber,
    COUNT(DISTINCT orderDate) AS date_count
FROM orders
GROUP BY orderNumber
HAVING COUNT(DISTINCT orderDate) > 1;
-- Check consistency of customerNumber per order
SELECT
    orderNumber,
    COUNT(DISTINCT customerNumber) AS customer_count
FROM orders
GROUP BY orderNumber
HAVING COUNT(DISTINCT customerNumber) > 1;
-- orderNumber validated as primary key
-- No NULLs or duplicates found
-- Referential integrity with orderdetails verified
-- Suitable for fact table joins and aggregations

-- Check for NULL orderDate values (should return 0)
SELECT *
FROM orders
WHERE orderDate IS NULL;
-- Check if orderDate can be parsed as a valid DATE
-- If this returns rows, format issues exist
SELECT
    orderNumber,
    orderDate
FROM orders
WHERE orderDate IS NOT NULL
  AND STR_TO_DATE(orderDate, '%Y-%m-%d') IS NULL;
-- Identify orders with orderDate in the future
SELECT
    orderNumber,
    orderDate
FROM orders
WHERE orderDate > CURRENT_DATE();
-- Check if orderDate is later than requiredDate
SELECT
    orderNumber,
    orderDate,
    requiredDate
FROM orders
WHERE requiredDate IS NOT NULL
  AND orderDate > requiredDate;
-- Check if orderDate is later than shippedDate
SELECT
    orderNumber,
    orderDate,
    shippedDate
FROM orders
WHERE shippedDate IS NOT NULL
  AND orderDate > shippedDate;
-- Check if orderDate is later than shippedDate
SELECT
    orderNumber,
    orderDate,
    shippedDate
FROM orders
WHERE shippedDate IS NOT NULL
  AND orderDate > shippedDate;
-- Identify orders with unusually large delivery gaps (>60 days)- comaprison between order date and ship date - unusual delivery gap 
SELECT
    orderNumber,
    DATEDIFF(shippedDate, orderDate) AS delivery_days
FROM orders
WHERE shippedDate IS NOT NULL
  AND DATEDIFF(shippedDate, orderDate) > 60
ORDER BY delivery_days DESC;
-- Identify orders shipped after the required delivery date - comaprison between ship date and require date
SELECT
    orderNumber,
    requiredDate,
    shippedDate,
    DATEDIFF(shippedDate, requiredDate) AS delay_days
FROM orders
WHERE shippedDate IS NOT NULL
  AND requiredDate IS NOT NULL
  AND shippedDate > requiredDate
ORDER BY delay_days DESC;
-- Orders delivered on or before required date
SELECT
    orderNumber,
    requiredDate,
    shippedDate,
    DATEDIFF(shippedDate, requiredDate) AS delay_days
FROM orders
WHERE shippedDate IS NOT NULL
  AND requiredDate IS NOT NULL
  AND shippedDate <= requiredDate;
-- Orders pending shipment (delay unknown yet)
SELECT
    orderNumber,
    requiredDate,
    shippedDate,
    status
FROM orders
WHERE shippedDate IS NULL;
-- Cleaning Decision:
-- orderDate is a critical time dimension
-- No NULLs or invalid formats allowed
-- Future dates are invalid and must be corrected
-- Logical ordering with requiredDate and shippedDate must be maintained
-- Column will be standardized to DATE format

-- Check for NULL orderDate values (should return 0)
SELECT *
FROM orders
WHERE orderDate IS NULL;
-- Check if orderDate can be parsed as a valid DATE
-- If this returns rows, format issues exist
SELECT
    orderNumber,
    orderDate
FROM orders
WHERE orderDate IS NOT NULL
  AND STR_TO_DATE(orderDate, '%Y-%m-%d') IS NULL;
-- Identify orders with orderDate in the future
SELECT
    orderNumber,
    orderDate
FROM orders
WHERE orderDate > CURRENT_DATE();
-- Check if requiredDate is later than shippedDate - indicate early order 
SELECT
    orderNumber,
    requiredDate,
    shippedDate
FROM orders
WHERE requiredDate IS NOT NULL
  AND shippedDate IS NOT NULL
  AND requiredDate > shippedDate;
  -- Flag invalid or suspicious requiredDate values
SELECT
    orderNumber,
    orderDate,
    requiredDate,
    CASE
        WHEN requiredDate IS NULL THEN 'MISSING'
        WHEN requiredDate < orderDate THEN 'INVALID_BEFORE_ORDER'
        WHEN DATEDIFF(requiredDate, orderDate) > 60 THEN 'UNREALISTIC_LONG'
        WHEN DATEDIFF(requiredDate, orderDate) <= 1 THEN 'VERY_SHORT'
        ELSE 'VALID'
    END AS requiredDate_quality_flag
FROM orders;

-- Cleaning Decision:
-- orderDate is a critical time dimension
-- No NULLs or invalid formats allowed
-- Future dates are invalid and must be corrected
-- Logical ordering with requiredDate and shippedDate must be maintained
-- Column will be standardized to DATE format

-- Count shipped vs non-shipped orders
SELECT
    status,
    COUNT(*) AS order_count,
    SUM(CASE WHEN shippedDate IS NULL THEN 1 ELSE 0 END) AS null_shippedDate
FROM orders
GROUP BY status;

-- Total cancelled orders
SELECT COUNT(*) AS total_cancelled
FROM orders
WHERE status = 'Cancelled';
-- Cancelled orders that still have shippedDate
SELECT
    orderNumber,
    orderDate,
    requiredDate,
    shippedDate,
    status
FROM orders
WHERE status = 'Cancelled'
  AND shippedDate IS NOT NULL;
  -- Cancelled orders not shipped
SELECT
    orderNumber,
    orderDate,
    requiredDate,
    shippedDate,
    status
FROM orders
WHERE status = 'Cancelled'
  AND shippedDate IS NULL;

-- shippedDate before orderDate (invalid)
SELECT
    orderNumber,
    orderDate,
    shippedDate
FROM orders
WHERE shippedDate IS NOT NULL
  AND shippedDate < orderDate;
-- Shipped orders without shippedDate (invalid)
SELECT
    orderNumber,
    status,
    shippedDate
FROM orders
WHERE status = 'Shipped'
  AND shippedDate IS NULL;

-- shippedDate quality flag -- valid/invalid/not shipped 
SELECT
    orderNumber,
    status,
    orderDate,
    shippedDate,
    CASE
        WHEN status = 'Shipped' AND shippedDate IS NULL THEN 'MISSING_SHIPPED_DATE'
        WHEN shippedDate < orderDate THEN 'INVALID_DATE_ORDER'
        WHEN shippedDate IS NULL THEN 'NOT_SHIPPED_YET'
        ELSE 'VALID'
    END AS shippedDate_quality_flag
FROM orders;
-- List all distinct status values
SELECT DISTINCT status
FROM orders
ORDER BY status;
-- Normalize status text - standardize
SELECT
    orderNumber,
    status,
    UPPER(TRIM(status)) AS standardized_status
FROM orders;
-- Identify invalid status values -- all get covered
SELECT DISTINCT status
FROM orders
WHERE UPPER(TRIM(status)) NOT IN (
    'SHIPPED',
    'CANCELLED',
    'IN PROCESS',
    'DISPUTED',
    'RESOLVED',
    'ON HOLD'
);
-- shippedDate present but status not 'Shipped' - on hold and progress are haing null shipped date so not in output
SELECT
    orderNumber,
    status,
    shippedDate
FROM orders
WHERE shippedDate IS NOT NULL
  AND UPPER(TRIM(status)) <> 'SHIPPED';
-- Map order status to lifecycle stage
SELECT
    orderNumber,
    status,
    CASE
        WHEN UPPER(TRIM(status)) = 'SHIPPED' THEN 'FULFILLED'
        WHEN UPPER(TRIM(status)) = 'CANCELLED' THEN 'CANCELLED'
        WHEN UPPER(TRIM(status)) IN ('IN PROCESS', 'DISPUTED') THEN 'OPEN'
        WHEN UPPER(TRIM(status)) = 'RESOLVED' THEN 'CLOSED'
        ELSE 'UNKNOWN'
    END AS order_lifecycle_stage
FROM orders;
-- On-time vs late shipments
SELECT
    CASE
        WHEN DATEDIFF(shippedDate, requiredDate) <= 0 THEN 'ON_TIME'
        ELSE 'LATE'
    END AS delivery_status,
    COUNT(*) AS order_count
FROM orders
WHERE shippedDate IS NOT NULL
GROUP BY delivery_status;
SELECT
    orderNumber,
    requiredDate,
    shippedDate,
    CASE
        WHEN DATEDIFF(shippedDate, requiredDate) <= 0 THEN 'ON_TIME'
        ELSE 'LATE'
    END AS delivery_status,
    CASE
        WHEN DATEDIFF(shippedDate, requiredDate) > 0
             THEN DATEDIFF(shippedDate, requiredDate)
        ELSE 0
    END AS delivery_delay_days
FROM orders
WHERE shippedDate IS NOT NULL;
SELECT
    CASE
        WHEN DATEDIFF(shippedDate, requiredDate) <= 0 THEN 'ON_TIME'
        ELSE 'LATE'
    END AS delivery_status,
    COUNT(*) AS order_count,
    AVG(
        CASE
            WHEN DATEDIFF(shippedDate, requiredDate) > 0
                 THEN DATEDIFF(shippedDate, requiredDate)
            ELSE NULL
        END
    ) AS avg_delay_days
FROM orders
WHERE shippedDate IS NOT NULL
GROUP BY delivery_status;
-- Count total rows vs rows with comments
SELECT
    COUNT(*) AS total_orders,
    COUNT(comments) AS orders_with_comments,
    COUNT(*) - COUNT(comments) AS orders_without_comments
FROM orders;
-- View sample comments to check relevance / sensitivity
SELECT
    orderNumber,
    comments
FROM orders
WHERE comments IS NOT NULL
LIMIT 10;
-- Orders per customer
SELECT
    customerNumber,
    COUNT(*) AS order_count
FROM orders
GROUP BY customerNumber
HAVING COUNT(*) > 1
ORDER BY order_count DESC;
-- Basic customer coverage
SELECT
    COUNT(DISTINCT customerNumber) AS unique_customers,
    COUNT(*) AS total_orders
FROM orders;
SELECT COUNT(DISTINCT customerNumber)
FROM orders;
SELECT COUNT(*)
FROM customers c
LEFT JOIN orders o
    ON c.customerNumber = o.customerNumber
WHERE o.customerNumber IS NULL;
-- Find orphan orders (orders without matching customer)
SELECT
    o.orderNumber,
    o.customerNumber
FROM orders o
LEFT JOIN customers c
    ON o.customerNumber = c.customerNumber
WHERE c.customerNumber IS NULL;



/*
========================================
ORDERS TABLE – DATA STUDY & OBSERVATIONS
========================================

Table Purpose:
--------------
Stores order-level transactional data.
Each row represents one customer order.

Key Findings (Exploratory Study):
--------------------------------
1. orderNumber
   - Always present (NOT NULL)
   - Unique per order (acts as Primary Key)
   - Maps correctly to orderdetails.orderNumber
   - One order can have multiple orderDetails (expected)

2. orderDate
   - Present for all orders
   - Date format consistent
   - Used for time-based analysis (monthly, yearly trends)
   - Acts as base date for delivery calculations

3. requiredDate
   - Always present
   - Generally greater than or equal to orderDate
   - Used to measure delivery commitment (SLA)

4. shippedDate
   - Can be NULL for non-shipped orders (expected)
   - Used to calculate actual delivery delay
   - Logical order: orderDate ≤ shippedDate (validated)

5. status
   - Controlled set of values:
     Shipped, Cancelled, In Process, Disputed, Resolved
   - Some cancelled orders may have shippedDate (data quality issue)
   - Status values are standardized for BI usage

6. comments
   - Mostly NULL
   - Free-text, not used in core analytics
   - Retained for completeness

7. customerNumber
   - Present for all orders
   - Some customerNumbers do not exist in customers master table
   - Identified as data quality gap (orphan customers)
   - No corrective action taken at this stage
   - Orders retained to avoid data loss

Sanity Checks:
--------------
- Total orders: 326
- Distinct customers in orders: 98
- Customers in master table: 123
- Indicates presence of inactive customers and missing customer references

Conclusion:
-----------
Orders table is analytically usable.
Known data gaps are documented and acknowledged.
No rows deleted or modified during study phase.
Cleaning and feature engineering to be handled in later stages.
========================================
*/
