CREATE OR REPLACE VIEW vw_vendor_performance AS
SELECT
    p.productVendor,
    SUM(od.quantityOrdered) AS units_sold,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_revenue,
    ROUND(SUM((od.priceEach - p.buyPrice) * od.quantityOrdered), 2) AS est_gross_profit,
    ROUND(
        (SUM((od.priceEach - p.buyPrice) * od.quantityOrdered) / NULLIF(SUM(od.quantityOrdered * od.priceEach), 0)) * 100
    , 2) AS est_profit_margin_pct
FROM orderdetails od
JOIN products p
    ON od.productCode = p.productCode
GROUP BY p.productVendor;