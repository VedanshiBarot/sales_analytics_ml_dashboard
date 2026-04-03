USE sales_analytics_internship;
SHOW TABLES;
DESCRIBE employees;
-- NULL check
SELECT *
FROM employees
WHERE employeeNumber IS NULL;

-- Duplicate check
SELECT employeeNumber, COUNT(*) AS cnt
FROM employees
GROUP BY employeeNumber
HAVING COUNT(*) > 1;
-- emp name null check
SELECT *
FROM employees
WHERE firstName IS NULL
   OR lastName IS NULL;
   -- format validation
SELECT *
FROM employees
WHERE email NOT LIKE '%@%.%';
-- extension null check 
SELECT *
FROM employees
WHERE extension IS NULL;
-- office code null and validity check 
SELECT DISTINCT e.officeCode
FROM employees e
LEFT JOIN offices o
ON e.officeCode = o.officeCode
WHERE o.officeCode IS NULL;
-- report to null check 
SELECT DISTINCT reportsTo
FROM employees
WHERE reportsTo IS NOT NULL
  AND reportsTo NOT IN (
      SELECT employeeNumber FROM employees
  );
  -- counting jobtitle
SELECT jobTitle, COUNT(*) 
FROM employees
GROUP BY jobTitle;
SELECT customerNumber, customerName
FROM customers
WHERE customerName != TRIM(customerName);
SELECT customerNumber, customerName
FROM customers
WHERE customerName REGEXP '  +';
SELECT customerNumber, customerName
FROM customers
WHERE customerName REGEXP '[^A-Za-z0-9 .&-]';
SELECT customerName
FROM customers
WHERE customerName = UPPER(customerName)
   OR customerName = LOWER(customerName);
-- Check sample extension values to understand format
SELECT DISTINCT extension
FROM employees
LIMIT 10;
-- Check length of extension values
SELECT 
    MIN(LENGTH(extension)) AS min_length,
    MAX(LENGTH(extension)) AS max_length
FROM employees;
-- Check how many employees do not have extension
SELECT 
    COUNT(*) AS total_employees,
    COUNT(extension) AS employees_with_extension,
    COUNT(*) - COUNT(extension) AS missing_extension
FROM employees;
-- Check if extension correlates with job roles
SELECT jobTitle, COUNT(extension) AS ext_count
FROM employees
GROUP BY jobTitle;
-- Check if any employees have NULL email
SELECT 
    COUNT(*) AS total_employees,
    COUNT(email) AS employees_with_email,
    COUNT(*) - COUNT(email) AS missing_email
FROM employees;
-- Check for duplicate email addresses
SELECT 
    email,
    COUNT(*) AS email_count
FROM employees
GROUP BY email
HAVING COUNT(*) > 1;
-- Find emails missing '@' or '.'
SELECT email
FROM employees
WHERE email NOT LIKE '%@%'
   OR email NOT LIKE '%.%';
-- Count employees per office to confirm valid joins
SELECT 
    o.officeCode,
    o.city,
    o.country,
    COUNT(e.employeeNumber) AS employee_count
FROM offices o
LEFT JOIN employees e
    ON o.officeCode = e.officeCode
GROUP BY o.officeCode, o.city, o.country
ORDER BY employee_count DESC;

-- Insight:
-- Shows distribution of employees across offices
-- Useful later for dashboards 





