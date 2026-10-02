{{ config(materialized='table') }}

WITH price_history AS (

    SELECT
        f.product_id,
        p.canonical_product_name,
        p.category,
        f.platform_id,
        pl.platform_name,
        d.full_date,
        d.day_name,
        f.price,

        LAG(f.price) OVER (
            PARTITION BY f.product_id, f.platform_id
            ORDER BY d.full_date
        ) AS previous_price

    FROM {{ ref('fct_product_price_daily') }} f

    INNER JOIN {{ ref('dim_product_master') }} p
        ON f.product_id = p.product_id

    INNER JOIN {{ ref('dim_platform') }} pl
        ON f.platform_id = pl.platform_id

    INNER JOIN {{ ref('dim_date') }} d
        ON f.date_id = d.date_id
),

changes AS (

    SELECT
        *,

        CASE
            WHEN previous_price IS NULL THEN NULL
            WHEN price <> previous_price THEN TRUE
            ELSE FALSE
        END AS price_changed,

        CASE
            WHEN previous_price IS NOT NULL
            THEN price - previous_price
        END AS price_change_amount,

        CASE
            WHEN previous_price > 0
            THEN ROUND(
                100.0 * (price - previous_price) / previous_price,
                2
            )
        END AS price_change_pct

    FROM price_history
)

SELECT *
FROM changes