SELECT
    MAX(ingested_at) AS latest_ingested_at,
    MAX(crawled_at) AS latest_crawled_at,
    MAX(observed_date) AS latest_observation_date,
    COUNT(*) AS total_records
FROM {{ ref('stg_competitor_products') }}