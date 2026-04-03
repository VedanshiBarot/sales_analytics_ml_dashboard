-- Check for NULL officeCode values (should return 0 rows)
SELECT *
FROM offices
WHERE officeCode IS NULL;
-- Find duplicate officeCode values
SELECT
    officeCode,
    COUNT(*) AS cnt
FROM offices
GROUP BY officeCode
HAVING COUNT(*) > 1;
-- Employees whose officeCode does not exist in offices table
SELECT DISTINCT e.officeCode
FROM employees e
LEFT JOIN offices o
    ON e.officeCode = o.officeCode
WHERE o.officeCode IS NULL;
-- Offices that currently have no employees
SELECT o.officeCode
FROM offices o
LEFT JOIN employees e
    ON o.officeCode = e.officeCode
WHERE e.officeCode IS NULL;
-- Same officeCode associated with multiple cities (data inconsistency)
SELECT
    officeCode,
    COUNT(DISTINCT city) AS city_count
FROM offices
GROUP BY officeCode
HAVING COUNT(DISTINCT city) > 1;
-- Quick look at officeCode with location
SELECT
    officeCode,
    city,
    country,
    territory
FROM offices
ORDER BY officeCode;
-- Check if addressLine1 has NULL values
SELECT 
    COUNT(*) AS null_address_count
FROM offices
WHERE addressLine1 IS NULL;
-- Check for empty or whitespace-only address values
SELECT 
    officeCode,
    addressLine1
FROM offices
WHERE TRIM(addressLine1) = '';
-- Identify unusually short address values (possible junk)
SELECT 
    officeCode,
    addressLine1,
    LENGTH(addressLine1) AS address_length
FROM offices
WHERE LENGTH(addressLine1) < 5;
-- add line 1 foramt and null checked --
-- Check how many NULL values exist in state column
SELECT 
    COUNT(*) AS null_state_count
FROM offices
WHERE state IS NULL;
-- See which countries have NULL states
SELECT 
    country,
    COUNT(*) AS rows_with_null_state
FROM offices
WHERE state IS NULL
GROUP BY country
ORDER BY rows_with_null_state DESC;
-- List distinct state values to visually inspect inconsistencies
SELECT DISTINCT state
FROM offices
ORDER BY state;
-- Inspect US state values separately
SELECT DISTINCT state
FROM offices
WHERE country = 'USA'
ORDER BY state;
-- Check if same state exists in multiple letter cases
SELECT 
    state,
    COUNT(*) AS count
FROM offices
GROUP BY state
HAVING COUNT(DISTINCT BINARY state) > 1;
-- Check if same state exists in multiple letter cases
SELECT 
    state,
    COUNT(*) AS count
FROM offices
GROUP BY state
HAVING COUNT(DISTINCT BINARY state) > 1;
-- Create derived column for BI usage
SELECT
    officeCode,
    city,
    country,
    COALESCE(state, 'Unknown') AS state_cleaned
FROM offices;
-- Check for NULL country values (should ideally be 0)
SELECT 
    COUNT(*) AS null_country_count
FROM offices
WHERE country IS NULL;
-- Check country–territory mapping
SELECT DISTINCT
    country,
    territory
FROM offices
ORDER BY territory, country;
-- Cleaning Decision:
-- Country is a high-level geographic attribute
-- Used in executive dashboards and regional comparisons
-- Country names will be standardized (spelling, casing)
-- No records will be dropped

-- Count NULL postal codes
SELECT 
    COUNT(*) AS null_postalcode_count
FROM offices
WHERE postalCode IS NULL;
-- Inspect postal code formats by country
SELECT DISTINCT
    country,
    postalCode
FROM offices
ORDER BY country, postalCode;
-- Cleaning Decision:
-- postalCode has no analytical or ML relevance
-- NULLs and format differences are acceptable
-- Column will be left unchanged

-- Check for NULL territory values
SELECT 
    COUNT(*) AS null_territory_count
FROM offices
WHERE territory IS NULL;
-- Validate logical mapping between country and territory
SELECT
    country,
    territory,
    COUNT(*) AS office_count
FROM offices
GROUP BY country, territory
ORDER BY territory, country;
-- Detect countries mapped to multiple territories
SELECT
    country,
    COUNT(DISTINCT territory) AS territory_count
FROM offices
GROUP BY country
HAVING COUNT(DISTINCT territory) > 1;
-- Cleaning Decision:
-- Territory is a business-defined region
-- Critical for regional sales analysis
-- Values will be standardized and validated
-- NULL or mismatched values must be corrected
