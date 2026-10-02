import os

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "competitor_prices"),
        user=os.getenv("POSTGRES_USER", "analyst"),
        password=os.getenv("POSTGRES_PASSWORD", "analyst"),
        cursor_factory=RealDictCursor,
    )