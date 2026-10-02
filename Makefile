.PHONY: up down build test ingest dbt recommend api docs

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

test:
	python -m pytest -q

ingest:
	./scripts/run_ingestion.sh

dbt:
	dbt build --project-dir dbt --profiles-dir dbt

recommend:
	python -m recommendation.main

api:
	uvicorn api.main:app --reload --port 8000

docs:
	dbt docs generate --project-dir dbt --profiles-dir dbt
	dbt docs serve --project-dir dbt --profiles-dir dbt --port 8081