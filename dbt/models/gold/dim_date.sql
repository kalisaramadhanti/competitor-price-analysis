WITH dates AS (
    SELECT DISTINCT observed_date
    FROM {{ ref('stg_competitor_products') }}
    WHERE observed_date IS NOT NULL
)

SELECT
    TO_CHAR(observed_date, 'YYYYMMDD')::INTEGER AS date_id,
    observed_date AS full_date,
    EXTRACT(YEAR FROM observed_date)::INTEGER AS year,
    EXTRACT(MONTH FROM observed_date)::INTEGER AS month,
    EXTRACT(DAY FROM observed_date)::INTEGER AS day,
    EXTRACT(ISODOW FROM observed_date)::INTEGER AS day_of_week,
    TRIM(TO_CHAR(observed_date, 'Day')) AS day_name
FROM dates