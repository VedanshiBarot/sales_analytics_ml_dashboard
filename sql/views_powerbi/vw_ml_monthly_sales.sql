CREATE OR REPLACE VIEW vw_ml_monthly_sales AS
SELECT
    DATE_FORMAT(orderDate, '%Y-%m-01') AS month_start,
    YEAR(orderDate) AS year,
    MONTH(orderDate) AS month_num,

    COUNT(DISTINCT orderNumber) AS total_orders,
    COUNT(DISTINCT customerNumber) AS total_customers,

    SUM(quantityOrdered) AS units_sold,
    SUM(line_revenue) AS revenue,

    AVG(priceEach) AS avg_price_each
FROM vw_sales_fact
WHERE orderDate IS NOT NULL
GROUP BY 1,2,3
ORDER BY month_start;
SELECT COUNT(*) FROM vw_ml_monthly_sales;
SELECT * FROM vw_ml_monthly_sales LIMIT 10;
SELECT MIN(month_start), MAX(month_start)
FROM vw_ml_monthly_sales;