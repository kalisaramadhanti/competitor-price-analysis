SELECT
    p.canonical_product_name,
    d.full_date,
    r.competitor_median_price,
    r.recommended_price
FROM gold.fct_price_recommendation r
INNER JOIN gold.dim_product_master p
    ON r.product_id = p.product_id
INNER JOIN gold.dim_date d
    ON r.date_id = d.date_id
WHERE r.recommended_price IS NOT NULL
  AND d.full_date = (
      SELECT MAX(d2.full_date)
      FROM gold.fct_price_recommendation r2
      INNER JOIN gold.dim_date d2
          ON r2.date_id = d2.date_id
      WHERE r2.recommended_price IS NOT NULL
  )
ORDER BY p.canonical_product_name;