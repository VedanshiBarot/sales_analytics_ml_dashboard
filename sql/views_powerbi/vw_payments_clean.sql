CREATE OR REPLACE VIEW vw_payments_clean AS
SELECT
    p.customerNumber,
    p.checkNumber,
    p.amount,
    p.paymentDate_clean,
    DATE_FORMAT(p.paymentDate_clean, '%Y-%m') AS payment_month,
    YEAR(p.paymentDate_clean)  AS payment_year,
    MONTH(p.paymentDate_clean) AS payment_month_num
FROM payments p
WHERE p.paymentDate_clean IS NOT NULL
  AND p.amount IS NOT NULL
  AND p.amount > 0
  AND p.customerNumber IS NOT NULL
  AND p.checkNumber IS NOT NULL;