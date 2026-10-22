import re
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup


PRICE_PATTERN = re.compile(r"^Rp\s*[\d.]+$")
DISCOUNT_PATTERN = re.compile(r"^\d{1,2}%$")


def parse_tokopedia_products(html: str):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    seen_urls = set()

    for anchor in soup.select(
        'a[href^="https://www.tokopedia.com/unilever-official-store/"]'
    ):
        href = anchor.get("href", "")
        clean_url = urlunsplit(
            (*urlsplit(href)[:3], "", "")
        )

        # Skip store navigation, duplicate cards, and non-products.
        if clean_url in seen_urls:
            continue

        prices = [
            tag.get_text(" ", strip=True)
            for tag in anchor.find_all(["div", "span"])
            if PRICE_PATTERN.fullmatch(
                tag.get_text(" ", strip=True)
            )
        ]

        # Nested div/span elements can repeat the same price.
        prices = list(dict.fromkeys(prices))

        if not prices:
            continue

        # Product title appears inside a text span, before prices.
        title_candidates = [
            tag.get_text(" ", strip=True)
            for tag in anchor.find_all("span")
            if len(tag.get_text(" ", strip=True)) > 15
            and "Rp" not in tag.get_text(" ", strip=True)
            and "Hemat" not in tag.get_text(" ", strip=True)
        ]

        if not title_candidates:
            continue

        discount_candidates = [
            tag.get_text(" ", strip=True)
            for tag in anchor.find_all(["div", "span"])
            if DISCOUNT_PATTERN.fullmatch(
                tag.get_text(" ", strip=True)
            )
        ]

        product = {
            "platform": "tokopedia",
            "seller_name": "Unilever Official Store",
            "product_name": title_candidates[0],
            "price_raw": prices[0],
            "original_price_raw": (
                prices[1] if len(prices) > 1 else None
            ),
            "discount_raw": (
                discount_candidates[0]
                if discount_candidates
                else None
            ),
            "source_url": clean_url,
        }

        products.append(product)
        seen_urls.add(clean_url)

    return products
