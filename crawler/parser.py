import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pydantic import ValidationError

from crawler.config import (
    MIN_PARSE_SUCCESS_RATE,
    SELECTORS,
    BLIBLI_SELECTORS,
)
from crawler.models import ProductRecord


logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    products: list[ProductRecord] = field(default_factory=list)
    total_cards: int = 0
    failed_cards: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_cards == 0:
            return 0.0

        return len(self.products) / self.total_cards

    @property
    def healthy(self) -> bool:
        return (
            self.total_cards > 0
            and self.success_rate >= MIN_PARSE_SUCCESS_RATE
        )


def select_first(element, selectors):
    """Return the first element matching any configured selector."""
    for selector in selectors:
        match = element.select_one(selector)
        if match is not None:
            return match

    return None


def extract_text(element, selectors):
    match = select_first(element, selectors)

    if match is None:
        return None

    return match.get_text(" ", strip=True) or None

def extract_blibli_seller(card):
    """Extract merchant name from Blibli product card."""
    elements = card.select(".els-product__seller-name")

    names = [
        element.get_text(" ", strip=True)
        for element in elements
    ]

    names = [name for name in names if name]
    # Known fulfilment labels are not merchant names.
    for name in names:
        if name.lower().startswith("disediakan "):
            continue

        if name.lower().startswith(("kota ", "kabupaten ", "kab. ")):
            continue

        return name

    return None

def parse_tokopedia_products(
    html: str,
    platform: str,
    base_url: str,
) -> ParseResult:
    """Extract products from rendered Tokopedia store HTML."""
    soup = BeautifulSoup(html, "html.parser")
    result = ParseResult()
    seen_urls = set()

    for link in soup.select("a[href]"):
        href = link.get("href", "")
        parts = urlsplit(urljoin(base_url, href))
        path_parts = parts.path.strip("/").split("/")

        if parts.netloc not in ("www.tokopedia.com", "tokopedia.com"):
            continue

        if len(path_parts) != 2:
            continue

        if not re.search(r"-\d{10,}(?:-\d{10,})?$", path_parts[1]):
            continue

        prices = [
            node.get_text(" ", strip=True)
            for node in link.find_all(["div", "span"])
            if not node.find(["div", "span"])
            and re.fullmatch(
                r"Rp\s*[\d.,]+",
                node.get_text(" ", strip=True),
            )
        ]

        if not prices:
            continue

        canonical_url = urlunsplit((
            parts.scheme,
            parts.netloc,
            parts.path,
            "",
            "",
        ))

        if canonical_url in seen_urls:
            continue

        seen_urls.add(canonical_url)
        result.total_cards += 1

        full_text = link.get_text(" ", strip=True)
        product_name = full_text.split(prices[0], 1)[0]

        product_name = re.sub(
            r"^\s*>?\s*\d+(?:[.,]\d+)?%\s*",
            "",
            product_name,
        ).strip()

        try:
            product = ProductRecord(
                platform=platform,
                product_name=product_name,
                price_raw=prices[0],
                original_price_raw=(
                    prices[1] if len(prices) > 1 else None
                ),
                discount_raw=None,
                detail_raw=None,
                seller_name=path_parts[0],
                source_url=canonical_url,
            )
            result.products.append(product)

        except ValidationError as exc:
            result.failed_cards += 1
            error = f"Tokopedia card: {exc}"
            result.errors.append(error)
            logger.warning(error)

    return result

def parse_products(
    html: str,
    platform: str,
    base_url: str,
    selectors=None,
) -> ParseResult:
    if platform.lower() == "tokopedia":
        return parse_tokopedia_products(
            html=html,
            platform=platform,
            base_url=base_url,
        )

    selectors = selectors if selectors is not None else SELECTORS
    soup = BeautifulSoup(html, "html.parser")
    result = ParseResult()

    cards = []
    seen = set()

    for selector in selectors["product_card"]:
        for card in soup.select(selector):
            if id(card) not in seen:
                seen.add(id(card))
                cards.append(card)

    result.total_cards = len(cards)

    for index, card in enumerate(cards, start=1):
        try:
            link = (
                card
                if card.name == "a" and card.get("href")
                else select_first(card, selectors["product_link"])
            )

            source_url = (
                urljoin(base_url, link.get("href"))
                if link and link.get("href")
                else base_url
            )

            if platform.lower() == "blibli":
                parts = urlsplit(source_url)

                source_url = urlunsplit((
                    parts.scheme,
                    parts.netloc,
                    parts.path,
                    "",
                    "",
                ))

            product = ProductRecord(
                platform=platform,
                product_name=extract_text(
                    card, selectors["product_name"]
                ),
                price_raw=extract_text(
                    card, selectors["price"]
                ),
                original_price_raw=extract_text(
                    card, selectors["original_price"]
                ),
                discount_raw=extract_text(
                    card, selectors["discount"]
                ),
                detail_raw=extract_text(
                    card, selectors["detail"]
                ),
                seller_name=(
                    extract_blibli_seller(card)
                    if platform.lower() == "blibli"
                    else None
                ),
                source_url=source_url,
            )

            result.products.append(product)

        except ValidationError as exc:
            result.failed_cards += 1

            error = f"Card {index}: {exc}"
            result.errors.append(error)
            logger.warning(error)

    if not result.healthy:
        logger.error(
            "Parsing health check failed: "
            "platform=%s success_rate=%.2f "
            "total_cards=%d",
            platform,
            result.success_rate,
            result.total_cards,
        )

    return result
