CREATE OR REPLACE VIEW vw_customers_all AS
SELECT
    c.customerNumber,
    c.customerName,
    c.contactLastName,
    c.contactFirstName,
    c.phone,
    c.addressLine1,
    c.addressLine2,
    c.city,
    c.state,
    c.postalCode,
    c.country,
    c.salesRepEmployeeNumber,
    c.creditLimit,

    /* Derived flags (BI/ML friendly) */
    CASE
        WHEN c.phone IS NULL OR TRIM(c.phone) = '' THEN 0
        ELSE 1
    END AS has_phone,

    CASE
        WHEN c.addressLine1 IS NULL OR TRIM(c.addressLine1) = ''
          OR c.city IS NULL OR TRIM(c.city) = ''
          OR c.country IS NULL OR TRIM(c.country) = ''
        THEN 0
        ELSE 1
    END AS has_min_address,

    CASE
        WHEN c.state IS NULL OR TRIM(c.state) = '' THEN 0
        ELSE 1
    END AS has_state,

    CASE
        WHEN c.addressLine2 IS NULL OR TRIM(c.addressLine2) = '' THEN 0
        ELSE 1
    END AS has_addressLine2,

    CASE
        WHEN c.creditLimit IS NULL THEN NULL
        WHEN c.creditLimit > 0 THEN 1
        ELSE 0
    END AS is_valid_creditLimit

FROM customers c
WHERE c.customerNumber IS NOT NULL
  AND c.customerName IS NOT NULL;