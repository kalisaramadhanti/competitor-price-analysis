SELECT *
FROM {{ ref('stg_competitor_products') }}
WHERE original_price IS NOT NULL
  AND original_price < price