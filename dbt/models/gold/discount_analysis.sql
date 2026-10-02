{{ config(materialized='table') }}

WITH base AS (

    SELECT
        f.product_id,
        f.platform_id,
        f.date_id,
        p.category,
        pl.platform_name,
        f.price,
        f.original_price,
        f.discount_pct

    FROM {{ ref('fct_product_price_daily') }} f

    INNER JOIN {{ ref('dim_product_master') }} p
        ON f.product_id = p.product_id

    INNER JOIN {{ ref('dim_platform') }} pl
        ON f.platform_id = pl.platform_id
),

aggregated AS (

    SELECT
        category,
        platform_name,

        COUNT(*) AS total_observations,

        COUNT(*) FILTER (
            WHERE discount_pct > 0
        ) AS discounted_observations,

        COUNT(*) FILTER (
            WHERE discount_pct IS NOT NULL
        ) AS observations_with_discount_data,

        ROUND(
            100.0
            * COUNT(*) FILTER (WHERE discount_pct > 0)
            / NULLIF(
                COUNT(*) FILTER (WHERE discount_pct IS NOT NULL),
                0
            ),
            2
        ) AS discount_frequency_pct,

        ROUND(
            AVG(discount_pct) FILTER (WHERE discount_pct > 0),
            2
        ) AS avg_discount_depth_pct,

        MAX(discount_pct) AS max_discount_depth_pct

    FROM base

    GROUP BY
        category,
        platform_name
)

SELECT *
FROM aggregated