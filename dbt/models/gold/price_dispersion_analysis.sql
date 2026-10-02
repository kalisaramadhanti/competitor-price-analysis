{{ config(materialized='table') }}

WITH product_prices AS (

    SELECT
        f.product_id,
        f.date_id,
        d.full_date,
        p.canonical_product_name,
        p.brand,
        p.category,
        p.pack_size_raw,
        f.platform_id,
        f.price

    FROM {{ ref('fct_product_price_daily') }} f

    INNER JOIN {{ ref('dim_product_master') }} p
        ON f.product_id = p.product_id

    INNER JOIN {{ ref('dim_date') }} d
        ON f.date_id = d.date_id
),

aggregated AS (

    SELECT
        product_id,
        date_id,
        full_date,
        canonical_product_name,
        brand,
        category,
        pack_size_raw,

        COUNT(DISTINCT platform_id) AS platform_count,

        MIN(price) AS min_price,
        MAX(price) AS max_price,
        ROUND(AVG(price), 2) AS avg_price,

        MAX(price) - MIN(price) AS price_dispersion,

        ROUND(
            100.0 * (MAX(price) - MIN(price))
            / NULLIF(AVG(price), 0),
            2
        ) AS price_dispersion_pct

    FROM product_prices

    GROUP BY
        product_id,
        date_id,
        full_date,
        canonical_product_name,
        brand,
        category,
        pack_size_raw
)

SELECT
    *,
    CASE
        WHEN platform_count >= 2 THEN TRUE
        ELSE FALSE
    END AS has_cross_platform_comparison

FROM aggregated