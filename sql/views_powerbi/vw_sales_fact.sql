CREATE OR REPLACE VIEW vw_sales_fact AS
SELECT
    o.orderNumber,
    o.orderDate,
    o.requiredDate,
    o.shippedDate,
    UPPER(TRIM(o.status)) AS status,
    o.customerNumber,

    od.productCode,
    od.orderLineNumber,
    od.quantityOrdered,
    od.priceEach,

    ROUND(od.quantityOrdered * od.priceEach, 2) AS line_revenue,

    -- Delivery analytics
    CASE
        WHEN o.shippedDate IS NULL THEN NULL
        ELSE DATEDIFF(o.shippedDate, o.orderDate)
    END AS delivery_days,

    CASE
        WHEN o.shippedDate IS NULL OR o.requiredDate IS NULL THEN NULL
        ELSE DATEDIFF(o.shippedDate, o.requiredDate)
    END AS delay_days,

    CASE
        WHEN o.shippedDate IS NULL OR o.requiredDate IS NULL THEN NULL
        WHEN DATEDIFF(o.shippedDate, o.requiredDate) <= 0 THEN 'ON_TIME'
        ELSE 'LATE'
    END AS delivery_status,

    CASE
        WHEN UPPER(TRIM(o.status)) = 'SHIPPED' THEN 'FULFILLED'
        WHEN UPPER(TRIM(o.status)) = 'CANCELLED' THEN 'CANCELLED'
        WHEN UPPER(TRIM(o.status)) IN ('IN PROCESS', 'DISPUTED', 'ON HOLD') THEN 'OPEN'
        WHEN UPPER(TRIM(o.status)) = 'RESOLVED' THEN 'CLOSED'
        ELSE 'UNKNOWN'
    END AS order_lifecycle_stage

FROM orders o
LEFT JOIN orderdetails od
    ON o.orderNumber = od.orderNumber;