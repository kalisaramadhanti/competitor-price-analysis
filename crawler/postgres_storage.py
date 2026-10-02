import json
import os

import psycopg2
from psycopg2.extras import Json, execute_values

from crawler.storage import prepare_observation

INIT_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.competitor_products (
    raw_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price_raw TEXT NOT NULL,
    original_price_raw TEXT,
    discount_raw TEXT,
    detail_raw TEXT,
    source_url TEXT NOT NULL,
    crawled_at TIMESTAMPTZ NOT NULL,
    crawler_version TEXT NOT NULL,
    raw_payload JSONB NOT NULL,
    html_hash TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_competitor_products_crawled_at
    ON raw.competitor_products (crawled_at);
"""

INSERT_SQL = """
    INSERT INTO raw.competitor_products (
        raw_id,
        platform,
        product_name,
        price_raw,
        original_price_raw,
        discount_raw,
        detail_raw,
        source_url,
        crawled_at,
        crawler_version,
        raw_payload,
        html_hash
    )
    VALUES %s
    ON CONFLICT (raw_id) DO NOTHING
    RETURNING raw_id
"""


def save_postgres(products, html_hash):
    observations = [
        prepare_observation(product, html_hash)
        for product in products
    ]

    if not observations:
        return 0

    rows = [
        (
            obs["raw_id"],
            obs["platform"],
            obs["product_name"],
            obs["price_raw"],
            obs["original_price_raw"],
            obs["discount_raw"],
            obs["detail_raw"],
            obs["source_url"],
            obs["crawled_at"],
            obs["crawler_version"],
            Json(obs),
            obs["html_hash"],
        )
        for obs in observations
    ]

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv(
            "POSTGRES_DB", "competitor_prices"
        ),
        user=os.getenv("POSTGRES_USER", "analyst"),
        password=os.environ["POSTGRES_PASSWORD"],
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INIT_SQL)

                inserted = execute_values(
                    cursor,
                    INSERT_SQL,
                    rows,
                    fetch=True,
            )

        return len(inserted)
    finally:
        connection.close()