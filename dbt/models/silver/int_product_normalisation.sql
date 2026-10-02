WITH products AS (
    SELECT *
    FROM {{ ref('stg_competitor_products') }}
),

normalised AS (
    SELECT
        *,
        LOWER(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    TRIM(product_name),
                    '([0-9])\s+(ml|g|kg|l)\y',
                    '\1\2',
                    'gi'
                ),
                '\s+',
                ' ',
                'g'
            )
        ) AS normalised_name
    FROM products
)

SELECT *
FROM normalised