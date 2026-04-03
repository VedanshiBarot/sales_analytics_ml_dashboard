CREATE OR REPLACE VIEW vw_payments_monthly_revenue AS
SELECT
    DATE_FORMAT(paymentDate_clean, '%Y-%m') AS payment_month,
    SUM(amount) AS total_revenue,
    COUNT(*) AS total_payments
FROM payments
WHERE paymentDate_clean IS NOT NULL
GROUP BY DATE_FORMAT(paymentDate_clean, '%Y-%m');