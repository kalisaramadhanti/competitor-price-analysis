# Metabase Dashboard

The dashboard reads only from the Gold layer.

## Start Metabase

Run:

    docker compose up --build

Then open Metabase at:

    http://localhost:3000

Connect Metabase to PostgreSQL using:

- Host: `postgres`
- Port: `5432`
- Database: `competitor_prices`
- Username: `analyst`
- Password: `analyst`

When Metabase runs inside Docker, use `postgres` as the database host rather than `localhost`.

## Dashboard

Create a dashboard named:

`Competitor Price Analysis Dashboard`

The SQL definitions used by the dashboard are stored under `dashboard/queries/`.

### 1. Latest Competitor Price Comparison

Query:
`queries/latest_price_comparison.sql`

Recommended visualization:
- Bar chart
- Category: canonical product name
- Value: price
- Series: platform

### 2. Discount Trend Over Time by Platform

Query:
`queries/discount_trend.sql`

Recommended visualization:
- Line chart
- X-axis: full date
- Y-axis: average discount %
- Series: platform

### 3. Recommended Price vs Competitor Median

Query:
`queries/recommendation_comparison.sql`

Recommended visualization:
- Bar chart
- Category: canonical product name
- Values: competitor median price and recommended price

### 4. Pipeline Health

Query:
`queries/pipeline_health.sql`

Recommended visualization:
- Table

The health status uses a two-day observation freshness threshold for demonstration purposes.

## Data Note

The included historical pricing data is synthetic and is intended to demonstrate pipeline, analytical, and dashboard functionality. It should not be interpreted as actual historical pricing behaviour on Blibli or Tokopedia or any brand mentioned in the data.

The `mock_store` fixture is used for crawler resilience testing and is excluded from business-facing dashboard queries.