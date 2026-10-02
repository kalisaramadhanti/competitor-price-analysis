WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'competitor_products') }}

),

cleaned AS (

    SELECT
        raw_id,
        LOWER(TRIM(platform)) AS platform,
        TRIM(product_name) AS product_name,

        price_raw,
        original_price_raw,
        discount_raw,
        detail_raw,
        
        CASE
            WHEN price_raw ~* '^\s*Rp' THEN 'IDR'
            ELSE NULL
        END AS currency,

        CASE
            WHEN price_raw ~* '^\s*Rp\s*[0-9][0-9.,]*\s*$' THEN NULLIF(REGEXP_REPLACE(price_raw, '[^0-9]', '', 'g'),'')::NUMERIC(18,2)
            ELSE NULL
        END AS price,

        NULLIF(
            REGEXP_REPLACE(original_price_raw, '[^0-9]', '', 'g'),
            ''
        )::NUMERIC AS original_price,

        NULLIF(
            REGEXP_REPLACE(discount_raw, '[^0-9.]', '', 'g'),
            ''
        )::NUMERIC AS discount_pct,

        source_url,
        crawled_at,
        crawled_at::DATE AS observed_date,
        crawler_version,
        html_hash,
        ingested_at

    FROM source_data

)

SELECT *
FROM cleaned