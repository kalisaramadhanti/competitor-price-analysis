import os

from fastapi import Depends, FastAPI, Query

from api.database import get_connection

from typing import Optional

from datetime import date

from api.auth import require_admin, require_reader

from recommendation.main import run_recommendation_batch


app = FastAPI(
    title="Competitor Price Analysis API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

    return {
        "status": "healthy",
        "database": "connected",
    }

@app.get("/products")
def get_products(
    brand: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    role: str = Depends(require_reader),
):
    query = """
        SELECT
            product_id,
            canonical_product_name,
            brand,
            category,
            pack_size_raw,
            platform_count
        FROM gold.dim_product_master
        WHERE (%s IS NULL OR LOWER(brand) = LOWER(%s))
          AND (%s IS NULL OR LOWER(category) = LOWER(%s))
        ORDER BY canonical_product_name
        LIMIT %s
        OFFSET %s
    """

    params = (
        brand, brand,
        category, category,
        limit, offset,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            products = cur.fetchall()

    return {
        "count": len(products),
        "limit": limit,
        "offset": offset,
        "data": products,
    }

@app.get("/prices")
def get_prices(
    product_id: Optional[str] = None,
    platform: Optional[str] = None,
    observation_date: Optional[date] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    role: str = Depends(require_reader),
):
    query = """
        SELECT
            f.product_id,
            p.canonical_product_name,
            pl.platform_name,
            d.full_date,
            f.price,
            f.original_price,
            f.discount_pct,
            f.currency
        FROM gold.fct_product_price_daily f
        INNER JOIN gold.dim_product_master p
            ON f.product_id = p.product_id
        INNER JOIN gold.dim_platform pl
            ON f.platform_id = pl.platform_id
        INNER JOIN gold.dim_date d
            ON f.date_id = d.date_id
        WHERE (%s IS NULL OR f.product_id = %s)
          AND (%s IS NULL OR LOWER(pl.platform_name) = LOWER(%s))
          AND (%s IS NULL OR d.full_date = %s)
        ORDER BY
            d.full_date DESC,
            p.canonical_product_name,
            pl.platform_name
        LIMIT %s
        OFFSET %s
    """

    params = (
        product_id, product_id,
        platform, platform,
        observation_date, observation_date,
        limit, offset,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            prices = cur.fetchall()

    return {
        "count": len(prices),
        "limit": limit,
        "offset": offset,
        "data": prices,
    }

@app.get("/recommendations")
def get_recommendations(
    product_id: Optional[str] = None,
    recommendation_date: Optional[date] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    role: str = Depends(require_reader),
):
    query = """
        SELECT
            r.product_id,
            p.canonical_product_name,
            d.full_date,
            r.platform_count,
            r.competitor_median_price,
            r.recommended_price,
            r.recommendation_rule,
            r.model_version,
            r.run_timestamp
        FROM gold.fct_price_recommendation r
        INNER JOIN gold.dim_product_master p
            ON r.product_id = p.product_id
        INNER JOIN gold.dim_date d
            ON r.date_id = d.date_id
        WHERE (%s IS NULL OR r.product_id = %s)
          AND (%s IS NULL OR d.full_date = %s)
        ORDER BY
            d.full_date DESC,
            p.canonical_product_name
        LIMIT %s
        OFFSET %s
    """

    params = (
        product_id, product_id,
        recommendation_date, recommendation_date,
        limit, offset,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            recommendations = cur.fetchall()

    return {
        "count": len(recommendations),
        "limit": limit,
        "offset": offset,
        "data": recommendations,
    }

@app.post("/recommendations/run")
def trigger_recommendation_batch(
    role: str = Depends(require_admin),
):
    run_recommendation_batch()

    return {
        "status": "success",
        "message": "Recommendation batch completed",
    }