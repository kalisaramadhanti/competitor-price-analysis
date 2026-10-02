WITH products AS (
    SELECT
        normalised_name,
        MIN(product_name) AS canonical_product_name,
        COUNT(DISTINCT platform) AS platform_count
    FROM {{ ref('int_product_normalisation') }}
    GROUP BY normalised_name
),

attributes AS (
    SELECT
        normalised_name,
        brand,
        pack_size_raw
    FROM {{ ref('int_product_attributes') }}
),

categories AS (
    SELECT
        product_matching_key,
        category
    FROM {{ ref('product_category_mapping') }}
)

SELECT
    MD5(p.normalised_name) AS product_id,
    p.normalised_name AS product_matching_key,
    p.canonical_product_name,
    a.brand,
    a.pack_size_raw,
    COALESCE(c.category, 'Unmapped') AS category,
    p.platform_count
FROM products p
LEFT JOIN attributes a
    ON p.normalised_name = a.normalised_name
LEFT JOIN categories c
    ON p.normalised_name = c.product_matching_key