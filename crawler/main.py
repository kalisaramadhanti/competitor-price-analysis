import argparse
import hashlib
import json
import logging

from crawler.fetcher import (
    fetch_html,
    fetch_blibli_pages,
    fetch_tokopedia_pages,
)
from crawler.parser import parse_products
from crawler.storage import save_jsonl
from crawler.postgres_storage import save_postgres
from crawler.config import BLIBLI_SELECTORS
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
    render_js=False,
):
    logger.info(
        "Starting ingestion: platform=%s source=%s",
        platform,
        source,
    )

    html = fetch_html(source, render_js=render_js)

    from bs4 import BeautifulSoup

    debug_soup = BeautifulSoup(html, "html.parser")

    print("DEBUG HTML LENGTH:", len(html))
    print(
        "DEBUG BLIBLI CARDS:",
        len(debug_soup.select("a.elf-product-card[href*='/p/']")),
    )
    print(
        "DEBUG PRODUCT LINKS:",
        len(debug_soup.select("a[href*='/p/']")),
    )
    print(
        "DEBUG PRODUCT TITLES:",
        len(debug_soup.select(".els-product__title")),
    )
    print(
        "DEBUG SELECTOR MODE:",
        "blibli" if platform.lower() == "blibli" and render_js else "synthetic",
    )

    html_hash = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    result = parse_products(
        html=html,
        platform=platform,
        base_url=base_url,
        selectors=(
            BLIBLI_SELECTORS
            if platform.lower() == "blibli" and render_js
            else None
        ),
    )

    if platform.lower() == "klikindomaret" and not render_js:
        for product in result.products:
            product.data_source = "synthetic"
    
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

def run_paginated_ingestion(
    source,
    platform,
    base_url,
    output,
    storage_backend="jsonl",
    max_pages=3,
):
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    platform_key = platform.lower()

    if platform_key == "blibli":
        page_iterator = fetch_blibli_pages(
            source, max_pages=max_pages
        )
        selectors = BLIBLI_SELECTORS

    elif platform_key == "tokopedia":
        page_iterator = fetch_tokopedia_pages(
            source, max_pages=max_pages
        )
        selectors = None

    else:
        raise ValueError(
            f"Pagination not supported for platform: {platform}"
        )

    summary = {
        "pages_processed": 0,
        "total_cards": 0,
        "valid_products": 0,
        "inserted": 0,
    }

    for page_data in page_iterator:
        print("DEBUG PAGINATION:", platform, page_data["page_number"], page_data["url"])
        page_number = page_data["page_number"]
        html = page_data["html"]

        html_hash = hashlib.sha256(
            html.encode("utf-8")
        ).hexdigest()

        result = parse_products(
            html=html,
            platform=platform,
            base_url=base_url,
            selectors=selectors,
        )

        logger.info(
            "Page %d: total=%d valid=%d failed=%d success_rate=%.2f",
            page_number,
            result.total_cards,
            len(result.products),
            result.failed_cards,
            result.success_rate,
        )

        if not result.healthy:
            raise RuntimeError(
                f"Page {page_number} failed parsing health check: "
                f"{result.success_rate:.0%}"
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

        summary["pages_processed"] += 1
        summary["total_cards"] += result.total_cards
        summary["valid_products"] += len(result.products)
        summary["inserted"] += inserted

        logger.info(
            "Page %d saved: inserted=%d",
            page_number,
            inserted,
        )

    return summary


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
    parser.add_argument(
    "--render-js",
    action="store_true",
    help="Render live website using Playwright.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Number of Blibli pages to crawl. Default: 1.",
    )

    args = parser.parse_args()

    crawled_at_override = None
    if args.crawled_at:
        crawled_at_override = datetime.fromisoformat(args.crawled_at)

    if args.max_pages > 1:
        if not args.render_js:
            parser.error("--max-pages requires --render-js")

        if args.crawled_at:
            parser.error("--max-pages does not support --crawled-at")

        summary = run_paginated_ingestion(
            source=args.source,
            platform=args.platform,
            base_url=args.base_url,
            output=args.output,
            storage_backend=args.storage,
            max_pages=args.max_pages,
        )
    else:
        summary = run_ingestion(
            source=args.source,
            platform=args.platform,
            base_url=args.base_url,
            output=args.output,
            storage_backend=args.storage,
            crawled_at_override=crawled_at_override,
            render_js=args.render_js,
        )

    print(json.dumps(summary, indent=2))