import logging
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic import ValidationError

from crawler.config import MIN_PARSE_SUCCESS_RATE, SELECTORS
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


def parse_products(
    html: str,
    platform: str,
    base_url: str,
) -> ParseResult:
    soup = BeautifulSoup(html, "html.parser")
    result = ParseResult()

    # Collect all matching cards without counting duplicates.
    cards = []
    seen = set()

    for selector in SELECTORS["product_card"]:
        for card in soup.select(selector):
            if id(card) not in seen:
                seen.add(id(card))
                cards.append(card)

    result.total_cards = len(cards)

    for index, card in enumerate(cards, start=1):
        try:
            link = select_first(
                card,
                SELECTORS["product_link"],
            )

            source_url = (
                urljoin(base_url, link.get("href"))
                if link and link.get("href")
                else base_url
            )

            product = ProductRecord(
                platform=platform,
                product_name=extract_text(
                    card, SELECTORS["product_name"]
                ),
                price_raw=extract_text(
                    card, SELECTORS["price"]
                ),
                original_price_raw=extract_text(
                    card, SELECTORS["original_price"]
                ),
                discount_raw=extract_text(
                    card, SELECTORS["discount"]
                ),
                detail_raw=extract_text(
                    card, SELECTORS["detail"]
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