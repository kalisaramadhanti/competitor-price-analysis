WITH comparable_prices AS (

    SELECT
        product_id,
        date_id,
        platform_id,
        price,

        COUNT(*) OVER (
            PARTITION BY product_id, date_id
        ) AS platform_count,

        AVG(price) OVER (
            PARTITION BY product_id, date_id
        ) AS market_avg_price

    FROM {{ ref('fct_product_price_daily') }}
),

indexed AS (

    SELECT
        product_id,
        date_id,
        platform_id,
        price,
        market_avg_price,

        100.0 * price / NULLIF(market_avg_price, 0) AS price_index

    FROM comparable_prices
    WHERE platform_count >= 2
)

SELECT
    p.platform_name,
    COUNT(*) AS comparable_observations,
    ROUND(AVG(i.price_index), 2) AS price_index

FROM indexed i

JOIN {{ ref('dim_platform') }} p
    ON i.platform_id = p.platform_id

GROUP BY p.platform_name