CREATE OR REPLACE VIEW vw_employee_sales_performance AS
SELECT
    e.employeeNumber,
    CONCAT(e.firstName, ' ', e.lastName) AS employeeName,
    e.jobTitle,
    e.officeCode,
    COUNT(DISTINCT c.customerNumber) AS customers_managed,
    COUNT(DISTINCT o.orderNumber) AS total_orders,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_revenue
FROM employees e
LEFT JOIN customers c
    ON e.employeeNumber = c.salesRepEmployeeNumber
LEFT JOIN orders o
    ON c.customerNumber = o.customerNumber
LEFT JOIN orderdetails od
    ON o.orderNumber = od.orderNumber
GROUP BY
    e.employeeNumber, employeeName, e.jobTitle, e.officeCode;