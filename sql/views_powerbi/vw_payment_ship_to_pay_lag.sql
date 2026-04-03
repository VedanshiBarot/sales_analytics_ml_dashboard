CREATE OR REPLACE VIEW vw_payment_ship_to_pay_lag AS
SELECT
    p.customerNumber,
    p.checkNumber,
    p.paymentDate_clean,
    p.amount,
    (
      SELECT MAX(o.shippedDate)
      FROM orders o
      WHERE o.customerNumber = p.customerNumber
        AND o.shippedDate IS NOT NULL
        AND o.shippedDate <= p.paymentDate_clean
    ) AS matched_shipped_date,
    DATEDIFF(
      p.paymentDate_clean,
      (
        SELECT MAX(o.shippedDate)
        FROM orders o
        WHERE o.customerNumber = p.customerNumber
          AND o.shippedDate IS NOT NULL
          AND o.shippedDate <= p.paymentDate_clean
      )
    ) AS ship_to_pay_days
FROM payments p
WHERE p.paymentDate_clean IS NOT NULL;  