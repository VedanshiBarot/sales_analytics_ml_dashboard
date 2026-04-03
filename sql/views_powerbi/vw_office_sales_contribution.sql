CREATE OR REPLACE VIEW vw_office_sales_contribution AS
SELECT
    ofc.officeCode,
    ofc.city AS office_city,
    UPPER(TRIM(ofc.country))   AS office_country,
    UPPER(TRIM(ofc.territory)) AS territory,

    COUNT(DISTINCT o.orderNumber)      AS total_orders,
    COUNT(DISTINCT c.customerNumber)   AS total_customers,

    COALESCE(
        ROUND(SUM(od.quantityOrdered * od.priceEach), 2),
        0
    ) AS total_revenue

FROM offices ofc
LEFT JOIN employees e
    ON ofc.officeCode = e.officeCode
LEFT JOIN customers c
    ON e.employeeNumber = c.salesRepEmployeeNumber
LEFT JOIN orders o
    ON c.customerNumber = o.customerNumber
LEFT JOIN orderdetails od
    ON o.orderNumber = od.orderNumber
-- Optional filter (uncomment if needed)
-- WHERE UPPER(TRIM(o.status)) <> 'CANCELLED'
GROUP BY
    ofc.officeCode, ofc.city, UPPER(TRIM(ofc.country)), UPPER(TRIM(ofc.territory));
