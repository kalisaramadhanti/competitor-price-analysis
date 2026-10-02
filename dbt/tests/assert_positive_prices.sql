SELECT *
FROM {{ ref('stg_competitor_products') }}
WHERE price <= 0