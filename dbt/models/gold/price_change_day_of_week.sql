{{ config(materialized='table') }}

SELECT
    day_name,

    COUNT(*) FILTER (
        WHERE previous_price IS NOT NULL
    ) AS comparable_observations,

    COUNT(*) FILTER (
        WHERE price_changed = TRUE
    ) AS price_change_count,

    ROUND(
        100.0
        * COUNT(*) FILTER (WHERE price_changed = TRUE)
        / NULLIF(
            COUNT(*) FILTER (WHERE previous_price IS NOT NULL),
            0
        ),
        2
    ) AS price_change_frequency_pct,

    ROUND(
        AVG(ABS(price_change_pct))
            FILTER (WHERE price_changed = TRUE),
        2
    ) AS avg_absolute_price_change_pct

FROM {{ ref('price_change_analysis') }}

GROUP BY day_name