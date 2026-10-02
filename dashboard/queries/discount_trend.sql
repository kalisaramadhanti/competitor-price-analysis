SELECT
    d.full_date,
    pl.platform_name,
    ROUND(AVG(f.discount_pct), 2) AS avg_discount_pct
FROM gold.fct_product_price_daily f
INNER JOIN gold.dim_date d
    ON f.date_id = d.date_id
INNER JOIN gold.dim_platform pl
    ON f.platform_id = pl.platform_id
WHERE pl.platform_name <> 'mock_store'
  AND f.discount_pct IS NOT NULL
GROUP BY
    d.full_date,
    pl.platform_name
ORDER BY
    d.full_date,
    pl.platform_name;