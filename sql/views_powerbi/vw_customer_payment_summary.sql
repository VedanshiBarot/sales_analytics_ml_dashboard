CREATE OR REPLACE VIEW vw_customer_payment_summary AS
SELECT
    customerNumber,
    MAX(paymentDate_clean) AS last_payment_date,
    DATEDIFF(CURDATE(), MAX(paymentDate_clean)) AS recency_days,
    COUNT(*) AS payment_count,
    SUM(amount) AS total_amount_paid,
    AVG(amount) AS avg_payment_amount
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY customerNumber;      