WITH prices AS (
    SELECT
        f.date_id,
        d.full_date,
        f.product_id,
        p.canonical_product_name,
        p.brand,
        p.category,
        p.pack_size_raw,
        f.platform_id,
        pl.platform_name,
        f.price,
        f.original_price,
        f.discount_pct,
        f.currency
    FROM {{ ref('fct_product_price_daily') }} f

    INNER JOIN {{ ref('dim_product_master') }} p
        ON f.product_id = p.product_id

    INNER JOIN {{ ref('dim_platform') }} pl
        ON f.platform_id = pl.platform_id

    INNER JOIN {{ ref('dim_date') }} d
        ON f.date_id = d.date_id
),

analysis AS (
    SELECT
        *,
        AVG(price) OVER (
            PARTITION BY product_id, date_id
        ) AS competitor_avg_price,

        MIN(price) OVER (
            PARTITION BY product_id, date_id
        ) AS competitor_min_price,

        MAX(price) OVER (
            PARTITION BY product_id, date_id
        ) AS competitor_max_price

    FROM prices
)

SELECT
    *,
    price - competitor_avg_price AS price_vs_avg,
    competitor_max_price - competitor_min_price AS price_dispersion,

    CASE
        WHEN competitor_avg_price > 0
        THEN ROUND(
            ((price - competitor_avg_price)
            / competitor_avg_price) * 100,
            2
        )
    END AS price_vs_avg_pct

FROM analysis