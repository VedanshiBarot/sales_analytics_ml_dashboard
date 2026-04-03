CREATE OR REPLACE VIEW vw_customers_orders_no_payments AS
SELECT
    o.customerNumber,
    COUNT(DISTINCT o.orderNumber) AS total_orders,
    MIN(o.orderDate) AS first_order_date,
    MAX(o.orderDate) AS last_order_date
FROM orders o
LEFT JOIN payments p
  ON p.customerNumber = o.customerNumber
  AND p.paymentDate_clean IS NOT NULL
WHERE p.customerNumber IS NULL
GROUP BY o.customerNumber;