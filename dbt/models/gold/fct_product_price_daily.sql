{{ config(
    materialized='incremental',
    unique_key='price_observation_id',
    incremental_strategy='delete+insert'
) }}

WITH ranked_prices AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY
                s.normalised_name,
                s.platform,
                s.observed_date
            ORDER BY s.crawled_at DESC, s.raw_id DESC
        ) AS row_num
    FROM {{ ref('int_product_normalisation') }} s
    WHERE s.price > 0
    AND COALESCE(s.data_source, 'unknown') <> 'synthetic'
),

latest_prices AS (
    SELECT *
    FROM ranked_prices
    WHERE row_num = 1
)

SELECT
    MD5(
        p.product_id || '|' ||
        pl.platform_id || '|' ||
        TO_CHAR(s.observed_date, 'YYYYMMDD')
    ) AS price_observation_id,
    p.product_id,
    pl.platform_id,
    d.date_id,
    s.price,
    s.original_price,
    s.discount_pct,
    s.currency,
    s.crawled_at,
    s.raw_id
FROM latest_prices s
INNER JOIN {{ ref('dim_product_master') }} p
    ON s.normalised_name = p.product_matching_key
INNER JOIN {{ ref('dim_platform') }} pl
    ON s.platform = pl.platform_name
INNER JOIN {{ ref('dim_date') }} d
    ON s.observed_date = d.full_date