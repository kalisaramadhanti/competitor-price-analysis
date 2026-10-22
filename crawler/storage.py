import hashlib
import json
from datetime import timezone
from pathlib import Path


def prepare_observation(product, html_hash):
    payload = product.model_dump(mode="json")

    # One observation per product, source and UTC crawl date.
    # Repeated ingestion of the same values on the same date
    # produces the same identifier.
    observed_date = (
        product.crawled_at.astimezone(timezone.utc)
        .date()
        .isoformat()
    )

    identity = {
        "platform": product.platform,
        "source_url": product.source_url,
        "observed_date": observed_date,
        "product_name": product.product_name,
        "price_raw": product.price_raw,
        "original_price_raw": product.original_price_raw,
        "discount_raw": product.discount_raw,
        "detail_raw": product.detail_raw,
        "seller_name": product.seller_name,
    }

    encoded = json.dumps(
        identity,
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")

    payload["raw_id"] = hashlib.sha256(encoded).hexdigest()
    payload["html_hash"] = html_hash

    return payload


def save_jsonl(products, html_hash, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing_ids = set()

    if path.exists():
        with path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    existing_ids.add(
                        json.loads(line)["raw_id"]
                    )

    inserted = 0

    with path.open("a", encoding="utf-8") as file:
        for product in products:
            observation = prepare_observation(
                product,
                html_hash,
            )

            if observation["raw_id"] in existing_ids:
                continue

            file.write(
                json.dumps(
                    observation,
                    ensure_ascii=False,
                ) + "\n"
            )

            existing_ids.add(observation["raw_id"])
            inserted += 1

    return inserted