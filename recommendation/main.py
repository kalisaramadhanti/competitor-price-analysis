import os
from datetime import datetime, timezone

import psycopg2


MODEL_VERSION = "rule_v1"
RECOMMENDATION_RULE = "95% of competitor median"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "competitor_prices"),
        user=os.getenv("POSTGRES_USER", "analyst"),
        password=os.getenv("POSTGRES_PASSWORD", "analyst"),
    )


def run_recommendation_batch():
    run_timestamp = datetime.now(timezone.utc)

    query = """
        WITH aggregated AS (
            SELECT
                product_id,
                date_id,
                COUNT(DISTINCT platform_id) AS platform_count,
                PERCENTILE_CONT(0.5)
                    WITHIN GROUP (ORDER BY price)
                    AS competitor_median_price
            FROM gold.fct_product_price_daily
            GROUP BY product_id, date_id
        )

        SELECT
            product_id,
            date_id,
            platform_count,
            ROUND(competitor_median_price::NUMERIC, 2)
                AS competitor_median_price,

            CASE
                WHEN platform_count >= 2
                THEN ROUND(
                    (competitor_median_price * 0.95)::NUMERIC,
                    2
                )
            END AS recommended_price,

            CASE
                WHEN platform_count >= 2
                THEN %s
                ELSE 'insufficient cross-platform coverage'
            END AS recommendation_rule

        FROM aggregated
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (RECOMMENDATION_RULE,))
            recommendations = cur.fetchall()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gold.fct_price_recommendation (
                    product_id TEXT NOT NULL,
                    date_id INTEGER NOT NULL,
                    platform_count INTEGER NOT NULL,
                    competitor_median_price NUMERIC(18,2),
                    recommended_price NUMERIC(18,2),
                    recommendation_rule TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    run_timestamp TIMESTAMPTZ NOT NULL,
                    PRIMARY KEY (product_id, date_id)
                )
            """)

            for row in recommendations:
                (
                    product_id,
                    date_id,
                    platform_count,
                    median_price,
                    recommended_price,
                    recommendation_rule,
                ) = row

                cur.execute("""
                    INSERT INTO gold.fct_price_recommendation (
                        product_id,
                        date_id,
                        platform_count,
                        competitor_median_price,
                        recommended_price,
                        recommendation_rule,
                        model_version,
                        run_timestamp
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

                    ON CONFLICT (product_id, date_id)
                    DO UPDATE SET
                        platform_count = EXCLUDED.platform_count,
                        competitor_median_price =
                            EXCLUDED.competitor_median_price,
                        recommended_price =
                            EXCLUDED.recommended_price,
                        recommendation_rule =
                            EXCLUDED.recommendation_rule,
                        model_version =
                            EXCLUDED.model_version,
                        run_timestamp =
                            EXCLUDED.run_timestamp
                """, (
                    product_id,
                    date_id,
                    platform_count,
                    median_price,
                    recommended_price,
                    recommendation_rule,
                    MODEL_VERSION,
                    run_timestamp,
                ))

    print(
        f"Recommendation batch complete: "
        f"{len(recommendations)} products processed "
        f"with model={MODEL_VERSION}"
    )


if __name__ == "__main__":
    run_recommendation_batch()