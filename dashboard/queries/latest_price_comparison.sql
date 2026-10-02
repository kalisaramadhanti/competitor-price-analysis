SELECT
    canonical_product_name,
    platform_name,
    full_date,
    price
FROM gold.price_competitiveness_analysis
WHERE platform_name <> 'mock_store'
  AND full_date = (
      SELECT MAX(full_date)
      FROM gold.price_competitiveness_analysis
      WHERE platform_name <> 'mock_store'
  )
ORDER BY
    canonical_product_name,
    platform_name;