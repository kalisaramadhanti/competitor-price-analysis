SELECT
    CASE
        WHEN latest_observation_date >= CURRENT_DATE - INTERVAL '2 days'
            THEN 'Healthy'
        ELSE 'Stale'
    END AS pipeline_status,
    latest_observation_date AS latest_data_date,
    latest_crawled_at AS last_crawl,
    latest_ingested_at AS last_ingestion,
    total_records
FROM gold.pipeline_health;