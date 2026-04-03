CREATE OR REPLACE VIEW vw_products_features AS
SELECT
    p.productCode,
    p.productName,
    p.productLine,
    p.productVendor,
    p.quantityInStock,
    p.buyPrice,
    p.MSRP,

    -- Pricing features
    (p.MSRP - p.buyPrice) AS margin,
    ROUND(((p.MSRP - p.buyPrice) / NULLIF(p.MSRP, 0)) * 100, 2) AS margin_pct,

    -- Inventory feature
    (p.quantityInStock * p.buyPrice) AS inventory_value,

    -- Stock status bucket (dashboard-friendly)
    CASE
        WHEN p.quantityInStock <= 50 THEN 'LOW'
        WHEN p.quantityInStock BETWEEN 51 AND 200 THEN 'NORMAL'
        ELSE 'HIGH'
    END AS stock_status

FROM products p
WHERE p.productCode IS NOT NULL
  AND p.productName IS NOT NULL
  AND p.quantityInStock IS NOT NULL
  AND p.quantityInStock >= 0
  AND p.buyPrice IS NOT NULL
  AND p.buyPrice > 0
  AND p.MSRP IS NOT NULL
  AND p.MSRP > 0;