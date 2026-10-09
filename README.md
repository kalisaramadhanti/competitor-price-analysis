# Competitor Price Analysis

An end-to-end data engineering system for competitor price analysis across Indonesian e-commerce platforms.

The project demonstrates the full data lifecycle:

**Ingestion → Raw → dbt Silver → dbt Gold → Recommendation Model → API → Dashboard**

The repository includes synthetic historical fixtures so the entire system can be reproduced without depending on live marketplace availability or anti-bot behaviour.

> **Data disclaimer:** The included historical prices are synthetic and are used only to demonstrate pipeline behaviour, transformations, analytics, and dashboard functionality. They should not be interpreted as actual historical prices from Blibli or Tokopedia.

---

## 1. Architecture

```text
Synthetic / Store HTML
        │
        ▼
┌─────────────────────┐
│ Python Crawler      │
│ BeautifulSoup       │
│ Pydantic validation │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ PostgreSQL          │
│ RAW                 │
│ competitor_products │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ dbt SILVER          │
│                     │
│ Cleaning            │
│ IDR parsing         │
│ Unit normalization  │
│ Product matching    │
│ Deduplication       │
└──────────┬──────────┘
           │
           ▼
┌────────────────────────────┐
│ dbt GOLD                   │
│                            │
│ Dimensions                 │
│ Fact tables                │
│ Analytical models          │
│ Pipeline health            │
└─────────────┬──────────────┘
              │
        ┌─────┴──────────┐
        ▼                ▼
┌───────────────┐   ┌───────────────┐
│ Recommendation│   │ Metabase      │
│ Python batch  │   │ Dashboard     │
└───────┬───────┘   └───────────────┘
        │
        ▼
┌───────────────────┐
│ FastAPI           │
│ API-key RBAC      │
│ Gold layer only   │
└───────────────────┘
```

### Technology

- Python 3.11
- BeautifulSoup
- Pydantic
- PostgreSQL 16
- dbt Core + dbt-postgres
- FastAPI
- Metabase
- Docker Compose
- pytest

---

## 2. Quick Start

### Prerequisites

- Docker Desktop
- Docker Compose

Clone the repository and run:

```bash
docker compose up --build
```

The command will:

1. Start PostgreSQL.
2. Ingest the bundled synthetic pricing fixtures.
3. Build and test the dbt project.
4. Generate price recommendations.
5. Start the FastAPI service.
6. Start Metabase.

The pipeline is implemented as a one-shot container. A successful run therefore appears as:

```text
competitor_pipeline   Exited (0)
competitor_postgres   Up (healthy)
competitor_api        Up
competitor_metabase   Up
```

During final validation, the project successfully bootstrapped against an empty PostgreSQL database with:

```text
dbt:            PASS=52 WARN=0 ERROR=0
recommendation: 24 rows processed
pipeline:       Exited (0)
```

### Services

| Service | URL |
|---|---|
| FastAPI | `http://localhost:8000` |
| Swagger / OpenAPI | `http://localhost:8000/docs` |
| Metabase | `http://localhost:3000` |

Development API keys:

```text
Reader: dev-reader-key
Admin:  dev-admin-key
```

These keys are provided only for local demonstration and should be replaced with secret-managed credentials in a production environment.

---

## 3. Running Components Individually

A Makefile provides shortcuts for common development workflows.

```bash
make test
make build
make ingest
make dbt
make recommend
make api
make docs
```

For commands executed locally rather than inside Docker, configure the database password first:

```bash
export POSTGRES_PASSWORD=analyst
```

Python tests use:

```bash
python -m pytest -q
```

---

## 4. Data Ingestion

The crawler is implemented under `crawler/`.

Each observation captures:

- platform
- product name
- displayed price
- original price
- discount
- product detail
- source URL
- crawl timestamp
- crawler version
- raw payload
- HTML hash

Raw observations are stored in:

```text
raw.competitor_products
```

The crawler automatically creates the Raw schema and table when they do not exist, allowing the application to bootstrap against an empty PostgreSQL database.

### Idempotency

Each raw observation receives a deterministic identifier based on its observation attributes.

PostgreSQL ingestion uses:

```sql
ON CONFLICT (raw_id) DO NOTHING
```

This makes repeated fixture ingestion safe and prevents duplicate raw observations.

---

## 5. Crawler Resilience

Selectors are configured as ordered fallback lists rather than being hard-coded into parsing logic.

For example, the parser can try both a primary selector and a fallback selector for:

- product card
- product name
- price
- original price
- discount
- product detail
- product link

The parser also calculates a parse success rate. If the success rate falls below the configured threshold, ingestion is stopped rather than silently loading heavily corrupted data.

### Synthetic resilience fixtures

The assignment references a provided `mock_store/` fixture. The hiring team later clarified that this fixture was not supplied.

Therefore, independent fixtures were created under:

```text
synthetic_mock_store/
```

These fixtures simulate structural HTML changes and are used to test:

- fallback selectors
- parsing validation
- parser health checks
- ingestion behaviour

These tests demonstrate resilience to the simulated structural changes only; they do not guarantee compatibility with every future marketplace HTML change.

---

## 6. Historical Fixture Data

To make time-based transformations and dashboard functionality reproducible, the repository contains synthetic observations across six dates for:

- Blibli
- Tokopedia

The reproducible dataset contains:

```text
4 products
× 2 platforms
× 6 observation dates
= 48 price observations
```

The products represented are:

- Dove Shampoo 170ml
- Dove Shampoo 340ml
- Lifebuoy Body Wash 500ml
- Sunsilk Shampoo 170ml

A `--crawled-at` CLI option is used only to assign deterministic observation timestamps to historical synthetic fixtures.

Live crawling continues to use the actual crawl timestamp.

---

## 7. dbt Transformation Layers

### Raw

The Raw layer preserves crawler output with minimal modification.

Primary source:

```text
raw.competitor_products
```

Source freshness is configured using `ingested_at`.

### Silver

The Silver layer handles data cleaning and standardisation, including:

- platform standardisation
- IDR price parsing
- numeric discount parsing
- product-name normalisation
- pack-size extraction
- unit normalisation
- product matching
- deduplication

For IDR prices, punctuation is treated as thousands formatting in the context of this dataset. For example:

```text
Rp25.000
Rp25,000
```

are normalised to:

```text
25000
```

Pack sizes are normalised to common units:

```text
L  → ml
kg → g
```

### Product Matching

Product matching uses a deterministic normalised product key derived from product name and pack size.

Examples:

```text
Dove Shampoo 170 ML
Dove Shampoo 170ml
```

map to:

```text
dove shampoo 170ml
```

This approach is intentionally simple and explainable.

#### Limitations

The current matching strategy may not correctly resolve:

- spelling errors
- substantially different product titles
- bundles or multipacks
- variant descriptions not represented in the title
- ambiguous products with similar names and pack sizes

A production implementation could introduce a curated product master, barcode/GTIN matching, or confidence-scored fuzzy matching.

---

## 8. Gold Data Model

The primary Gold models include:

```text
dim_product_master
dim_platform
dim_date
fct_product_price_daily
fct_price_recommendation
```

Additional analytical models include:

```text
platform_price_index
discount_analysis
price_dispersion_analysis
price_change_analysis
price_change_day_of_week
price_competitiveness_analysis
pipeline_health
```

### ERD

```text
                 ┌────────────────────┐
                 │ dim_product_master │
                 │ PK product_id      │
                 └─────────┬──────────┘
                           │
                           │
┌──────────────┐           │           ┌──────────────┐
│ dim_platform │           │           │   dim_date   │
│ PK platform_id           │           │ PK date_id   │
└──────┬───────┘           │           └──────┬───────┘
       │                   │                  │
       └──────────┐        │        ┌─────────┘
                  ▼        ▼        ▼
              ┌─────────────────────────┐
              │ fct_product_price_daily │
              │ FK product_id           │
              │ FK platform_id          │
              │ FK date_id              │
              └─────────────────────────┘

                 ┌──────────────────────────┐
                 │ fct_price_recommendation│
                 │ FK product_id            │
                 │ FK date_id               │
                 └──────────────────────────┘
```

## Mapping to a Production Lakehouse

This take-home uses PostgreSQL to keep the local environment simple and reproducible. The same Raw → Silver → Gold architecture could be mapped to a production lakehouse without changing the logical data flow.

- **Raw:** crawler outputs would be written to object storage such as Amazon S3 in an append-only format, preserving the original payload and ingestion metadata.
- **Silver:** dbt would transform Raw data into cleaned and conformed Iceberg or Delta tables, including price parsing, unit normalisation, deduplication, and product matching.
- **Gold:** dimensional models and analytical tables would also be stored as managed Iceberg or Delta tables and exposed to the dashboard, recommendation process, and API through a query engine or warehouse.

PostgreSQL schemas in this project therefore represent the logical lakehouse layers:

`raw schema → silver schema → gold schema`

In a production implementation, I would also add partitioning by observation date, catalogue/version management, automated data-quality monitoring, and orchestration around ingestion and transformation.

### Fact Grains

`fct_product_price_daily`

> One row per matched product, platform, and observation date, using the latest crawl when multiple observations exist on the same day.

`fct_price_recommendation`

> One row per product and observation date.

---

## 9. Incremental Processing and History

`fct_product_price_daily` is implemented as an incremental dbt model.

Product-master history is tracked using a dbt snapshot with SCD Type 2 behaviour. Changes to attributes such as category or canonical product information therefore preserve historical versions rather than overwriting history.

---

## 10. Data Quality

Data quality checks exist across the transformation layers.

They include standard dbt tests such as:

- `not_null`
- `unique`
- `relationships`

Custom tests validate business/data assumptions such as valid positive prices.

Crawler behaviour is additionally tested with pytest, including:

- parsing
- ingestion
- fallback selectors
- resilience to changed HTML structures

Run the Python suite with:

```bash
make test
```

Run the complete dbt build and test workflow with:

```bash
make dbt
```

---

## 11. Analytical Questions

The Gold layer contains models designed to answer the required business questions.

### Platform price index

`platform_price_index` compares each platform's product price with the cross-platform market average for the same product and date.

An index of:

```text
100
```

represents the cross-platform benchmark.

Values below 100 indicate prices below the benchmark, while values above 100 indicate prices above the benchmark.

Only product-date observations with cross-platform coverage are included.

### Discount behaviour

`discount_analysis` measures:

- discount frequency
- average discount depth
- maximum discount depth

by platform and category.

### Price dispersion

`price_dispersion_analysis` identifies product-date combinations with the largest cross-platform price differences.

### Price changes

`price_change_analysis` compares each observation with the previous available observation for the same product and platform.

`price_change_day_of_week` provides a day-of-week aggregation.

Because the bundled historical dataset is synthetic and sparsely sampled, particularly around month-end dates, it should **not** be used to infer real-world weekday pricing behaviour.

---

## 12. Recommendation Model

The recommendation process is implemented in:

```text
recommendation/main.py
```

The current rule is intentionally transparent:

```text
recommended price = 95% × cross-platform competitor median
```

A recommendation is generated only when the product has sufficient cross-platform coverage.

Each recommendation stores:

- product
- observation date
- platform coverage
- competitor median price
- recommended price
- rule
- model version
- run timestamp

Current model version:

```text
rule_v1
```

### Limitations

The rule is a demonstration model rather than a production pricing strategy.

It does not incorporate:

- product cost
- margin constraints
- demand elasticity
- inventory
- customer segmentation
- promotional strategy
- commercial pricing rules

---

## 13. API

FastAPI exposes Gold-layer data only.

### Read endpoints

```text
GET /products
GET /prices
GET /recommendations
```

The endpoints support filtering and pagination where applicable.

Example:

```bash
curl \
  -H "X-API-Key: dev-reader-key" \
  "http://localhost:8000/products?limit=10"
```

### Recommendation trigger

```text
POST /recommendations/run
```

This endpoint requires the admin role.

Example:

```bash
curl -X POST \
  -H "X-API-Key: dev-admin-key" \
  "http://localhost:8000/recommendations/run"
```

### Authorization

Two API-key roles are implemented:

| Role | Read Gold data | Trigger recommendation |
|---|---:|---:|
| Reader | Yes | No |
| Admin | Yes | Yes |

Invalid keys return `401 Unauthorized`.

A Reader attempting an Admin operation returns `403 Forbidden`.

OpenAPI documentation is available at:

```text
http://localhost:8000/docs
```

---

## 14. Dashboard

Metabase is available at:

```text
http://localhost:3000
```

The dashboard contains four primary views:

1. Latest Competitor Price Comparison
2. Discount Trend Over Time by Platform
3. Recommended Price vs Competitor Median
4. Pipeline Health

Dashboard SQL and reproduction instructions are stored under:

```text
dashboard/
├── README.md
├── queries/
└── screenshots/
```

The dashboard reads from the Gold layer only.

---

### Dashboard Preview

The Metabase dashboard provides four views:
- Competitor price comparison by product and platform
- Discount trends across historical observation dates
- Recommended prices versus competitor median prices
- Pipeline health and data freshness

![Competitor Price Analysis Dashboard](dashboard/screenshots/competitor_price_dashboard.png)

The dashboard uses synthetic historical observations for
demonstration purposes. Results should not be interpreted
as actual historical competitor pricing.

### dbt Lineage

The dbt lineage graph illustrates how raw competitor observations
flow through Silver staging and normalisation into Gold
dimensions, facts, and analytical models.

![dbt Lineage Graph](docs/dbt_lineage.png)

The recommendation batch is implemented in Python and writes
to `gold.fct_price_recommendation` outside dbt.

### Business Analysis

See [Business Summary](business_summary.md) for the four
analytical questions, findings, recommendations, and
limitations of the synthetic dataset.


## 15. Pipeline Health

`gold.pipeline_health` exposes:

- latest ingestion timestamp
- latest crawl timestamp
- latest observation date
- total record count

The Metabase health card applies a two-day observation freshness threshold for demonstration purposes.

Because the included fixtures use deterministic historical dates, the synthetic dataset may correctly appear as `Stale` when the project is run at a later date.

---

## 16. Design Decisions and Trade-offs

### PostgreSQL as both operational and analytical storage

For the scale of this take-home exercise, PostgreSQL keeps the system reproducible and easy to run locally.

At larger scale, Raw data could be persisted in object storage and transformations executed in a cloud analytical warehouse.

### Deterministic matching over fuzzy matching

The project prioritises an explainable normalisation-based matching rule.

This reduces hidden matching behaviour but provides less coverage than a production entity-resolution system.

### Synthetic fallback data

Marketplace crawling can be affected by anti-bot controls and changing frontend structures.

The system therefore separates crawler logic from deterministic synthetic fixtures so that the complete downstream architecture can still be evaluated reproducibly.

### Simple recommendation model

The recommendation rule is deliberately simple so its assumptions are visible and testable.

The purpose is to demonstrate integration between analytical data and a batch model rather than claim production-grade pricing optimisation.

---

## 17. Project Structure

```text
.
├── api/                    # FastAPI application
├── crawler/                # ingestion and parsing
├── dashboard/              # Metabase queries and setup
├── dbt/                    # dbt project
│   ├── models/
│   ├── seeds/
│   └── snapshots/
├── recommendation/         # recommendation batch
├── scripts/                # pipeline/fixture scripts
├── synthetic_mock_store/   # deterministic synthetic HTML fixtures
├── tests/                  # crawler tests
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── README.md
```

---

## 18. Known Limitations

- Historical marketplace observations included in this repository are synthetic.
- HTML fixtures cover selected structural changes rather than every possible live-site change.
- Product matching is deterministic rather than probabilistic.
- The synthetic historical sample is too small and temporally biased to support real-world weekday pricing conclusions.
- The recommendation model does not account for internal commercial constraints.
- Development API keys are intentionally simple and are not production authentication.
- The local architecture prioritises reproducibility over distributed scalability.

---

## 19. AI Assistance

AI coding assistance was used during development for debugging support and documentation refinement.

All generated or suggested code was reviewed, tested, and adapted before inclusion.