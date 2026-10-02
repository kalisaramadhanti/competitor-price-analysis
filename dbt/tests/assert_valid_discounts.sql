SELECT *
FROM {{ ref('stg_competitor_products') }}
WHERE discount_pct < 0
   OR discount_pct > 100