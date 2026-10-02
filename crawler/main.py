import argparse
import hashlib
import json
import logging

from crawler.fetcher import fetch_html
from crawler.parser import parse_products
from crawler.storage import save_jsonl
from crawler.postgres_storage import save_postgres
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def run_ingestion(
    source,
    platform,
    base_url,
    output,
    storage_backend="jsonl",
    crawled_at_override=None,
):
    logger.info(
        "Starting ingestion: platform=%s source=%s",
        platform,
        source,
    )

    html = fetch_html(source)
    html_hash = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    result = parse_products(
        html=html,
        platform=platform,
        base_url=base_url,
    )
    
    if crawled_at_override:
        for product in result.products:
            product.crawled_at = crawled_at_override

    logger.info(
        "Parsing complete: total=%d valid=%d "
        "failed=%d success_rate=%.2f",
        result.total_cards,
        len(result.products),
        result.failed_cards,
        result.success_rate,
    )

    # Fail closed: don't publish results from an unhealthy
    # extraction, including an unrecognised page.
    if not result.healthy:
        raise RuntimeError(
            "Parsing health check failed. "
            f"Success rate: {result.success_rate:.0%}"
        )

    if storage_backend == "postgres":
        inserted = save_postgres(
            products=result.products,
            html_hash=html_hash,
        )
    elif storage_backend == "jsonl":
        inserted = save_jsonl(
            products=result.products,
            html_hash=html_hash,
            output_path=output,
        )
    else:
        raise ValueError(
            f"Unsupported storage backend: {storage_backend}"
        )

    logger.info(
        "Ingestion completed: inserted=%d",
        inserted,
    )

    return {
        "total_cards": result.total_cards,
        "valid_products": len(result.products),
        "inserted": inserted,
        "success_rate": result.success_rate,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
    "--crawled-at",
    type=str,
    default=None,
    help="Optional ISO timestamp override for synthetic historical fixtures only.",
    )

    parser.add_argument("--source", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument(
        "--output",
        default="data/raw_products.jsonl",
    )
    parser.add_argument(
    "--storage",
    choices=["jsonl", "postgres"],
    default="jsonl",
    )

    args = parser.parse_args()

    crawled_at_override = None
    if args.crawled_at:
        crawled_at_override = datetime.fromisoformat(args.crawled_at)

    summary = run_ingestion(
        source=args.source,
        platform=args.platform,
        base_url=args.base_url,
        output=args.output,
        storage_backend=args.storage,
        crawled_at_override=crawled_at_override,
    )
    print(json.dumps(summary, indent=2))