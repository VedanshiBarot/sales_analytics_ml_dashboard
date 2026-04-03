USE sales_analytics_internship;
SHOW TABLES;
DESCRIBE customers;
SELECT * 
FROM customers
LIMIT 10;
-- check null 
SELECT  
    SUM(customerNumber IS NULL) AS customerNumber_nulls,
    SUM(customerName IS NULL) AS customerName_nulls,
    SUM(phone IS NULL) AS phone_nulls,
    SUM(addressLine2 IS NULL) AS addressLine2_nulls,
    SUM(state IS NULL) AS state_nulls
FROM customers;
-- check duplicates
SELECT customerNumber, COUNT(*) AS cnt 
FROM customers
GROUP BY customerNumber
HAVING cnt > 1;
SELECT customerName, COUNT(*) AS cnt 
FROM customers
GROUP BY customerName
HAVING cnt > 1;
SELECT contactLastName, COUNT(*) AS cnt 
FROM customers
GROUP BY contactLastName
HAVING cnt > 1;
SELECT contactFirstName, COUNT(*) AS cnt 
FROM customers
GROUP BY contactFirstName
HAVING cnt > 1;
SELECT COUNT(*) 
FROM customers
WHERE phone IS NULL OR phone = '';
-- count country and order them
SELECT country, COUNT(*) 
FROM customers
GROUP BY country
ORDER BY COUNT(*) DESC;
SELECT 
    MIN(creditLimit), 
    MAX(creditLimit), 
    AVG(creditLimit)
FROM customers;
SELECT *
FROM customers
WHERE creditLimit <= 0;
SELECT contactFirstName, contactLastName, COUNT(*) AS cnt
FROM customers
GROUP BY contactFirstName, contactLastName
HAVING cnt > 1
ORDER BY cnt DESC;
-- check that everone is having phone number
SELECT
    customerNumber,
    CASE
        WHEN phone IS NULL OR phone = '' THEN 0
        ELSE 1
    END AS has_phone
FROM customers; 
DROP VIEW vw_customers_clean;
SELECT @@hostname, @@port;