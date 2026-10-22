from pathlib import Path
from urllib.parse import urlparse

import requests
from pathlib import Path
from urllib.parse import urlparse

import requests


class SourceBlockedError(RuntimeError):
    """Raised when a source rejects crawler access."""
    pass


def fetch_html(source: str, render_js: bool = False) -> str:
    parsed = urlparse(source)

    if parsed.scheme in ("http", "https"):
        if render_js:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                try:
                    page = browser.new_page()
                    page.goto(
                        source,
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )
                    try:
                        if "tokopedia.com" in parsed.netloc.lower():
                            page.wait_for_function(
                                """() => Array.from(
                                    document.querySelectorAll('a[href]')
                                ).some(a =>
                                    /^https?:\/\/(?:www\.)?tokopedia\.com\/[^/]+\/[^/?#]+-\d{10,}/.test(
                                        a.href
                                    ) &&
                                    /Rp\s*[\d.,]+/.test(a.innerText)
                                )""",
                                timeout=30000,
                            )
                        elif "klikindomaret.com" in parsed.netloc.lower():
                            page.locator(
                                "div.card-product .wrp-price .price"
                            ).first.wait_for(
                                state="visible",
                                timeout=30000,
                            )
                        else:
                            page.locator(
                                "a.elf-product-card[href*='/p/']"
                            ).first.wait_for(
                                state="attached",
                                timeout=30000,
                            )

                    except Exception:
                        print("DEBUG URL:", page.url)
                        print("DEBUG TITLE:", page.title())
                        print(
                            "DEBUG PRODUCT LINKS:",
                            page.locator("a[href*='/p/']").count(),
                        )
                        print(
                            "DEBUG BODY:",
                            page.locator("body").inner_text()[:500],
                        )
                        raise

                    return page.content()
                finally:
                    browser.close()

        response = requests.get(
            source,
            timeout=20,
            headers={
                "User-Agent": "CompetitorPriceResearch/1.0"
            },
        )
        response.raise_for_status()
        return response.text

    if parsed.scheme not in ("", "file"):
        raise ValueError("Unsupported source scheme")

    path = Path(
        parsed.path if parsed.scheme == "file" else source
    )
    return path.read_text(encoding="utf-8")

def fetch_blibli_pages(source: str, max_pages: int = 3):
    from playwright.sync_api import sync_playwright

    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    card_selector = "a.elf-product-card[href*='/p/']"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        try:
            page = browser.new_page()
            page.goto(
                source,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            for page_number in range(1, max_pages + 1):
                cards = page.locator(card_selector)
                cards.first.wait_for(
                    state="attached",
                    timeout=30000,
                )

                # Wait for product list to settle.
                # Scroll to trigger lazy-loaded products.
                previous_count = -1
                stable_rounds = 0

                for _ in range(15):
                    page.mouse.wheel(0, 1200)
                    page.wait_for_timeout(1000)

                    current_count = cards.count()

                    if current_count == previous_count and current_count > 0:
                        stable_rounds += 1
                    else:
                        stable_rounds = 0

                    previous_count = current_count

                    if stable_rounds >= 3:
                        break

                product_urls = set(
                    cards.evaluate_all(
                        "(cards) => cards.map(card => card.href)"
                    )
                )

                print(
                    f"Page {page_number}: "
                    f"{len(product_urls)} unique products"
                )

                yield {
                    "page_number": page_number,
                    "url": page.url,
                    "html": page.content(),
                }

                if page_number == max_pages:
                    break

                next_page = page_number + 1

                # Click the real pagination button.
                page.locator(
                    "button.blu-pagination__button"
                ).get_by_text(
                    str(next_page),
                    exact=True,
                ).click(timeout=15000)

                # Wait until the active page changes.
                page.wait_for_function(
                    """(expected) => {
                        const active = document.querySelector(
                            'button.blu-pagination__button.b-active'
                        );
                        return active?.textContent?.trim() === expected;
                    }""",
                    arg=str(next_page),
                    timeout=30000,
                )

                # Wait for a new product to appear.
                page.wait_for_function(
                    """(previousUrls) => {
                        const cards = Array.from(
                            document.querySelectorAll(
                                'a.elf-product-card[href*="/p/"]'
                            )
                        );

                        return cards.length > 0 &&
                            cards.some(
                                card => !previousUrls.includes(card.href)
                            );
                    }""",
                    arg=list(product_urls),
                    timeout=30000,
                )

        finally:
            browser.close()

def fetch_tokopedia_pages(source: str, max_pages: int = 10):
    from playwright.sync_api import sync_playwright

    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    next_selector = '[data-testid="btnShopProductPageNext"]'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 900}
            )
            page.goto(
                source,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            visited_urls = set()

            for page_number in range(1, max_pages + 1):
                if page.url in visited_urls:
                    print("Stopping: repeated page URL")
                    break

                visited_urls.add(page.url)

                # Allow initial product loading.
                page.wait_for_timeout(3000)

                # Scroll to load the complete product list.
                previous_count = -1
                stable_rounds = 0

                for _ in range(25):
                    page.mouse.wheel(0, 1200)
                    page.wait_for_timeout(1000)

                    from crawler.parser import parse_products

                    result = parse_products(
                        html=page.content(),
                        platform="tokopedia",
                        base_url="https://www.tokopedia.com",
                    )

                    count = len(result.products)

                    if count == previous_count and count > 0:
                        stable_rounds += 1
                    else:
                        stable_rounds = 0

                    previous_count = count

                    if stable_rounds >= 3 and count >= 80:
                        break

                from crawler.parser import parse_products

                html = page.content()
                result = parse_products(
                    html=html,
                    platform="tokopedia",
                    base_url="https://www.tokopedia.com",
                )

                print(
                    f"Tokopedia page {page_number}: "
                    f"{len(result.products)} products | "
                    f"healthy={result.healthy}"
                )

                if not result.healthy or not result.products:
                    raise RuntimeError(
                        f"Tokopedia page {page_number} "
                        "failed parser health check"
                    )

                yield {
                    "page_number": page_number,
                    "url": page.url,
                    "html": html,
                }

                if page_number == max_pages:
                    break

                next_link = page.locator(next_selector).first

                if next_link.count() == 0:
                    print("Tokopedia: last page reached")
                    break

                next_href = next_link.get_attribute("href")

                if not next_href:
                    print("Tokopedia: no next page URL")
                    break

                from urllib.parse import urljoin

                next_url = urljoin(page.url, next_href)

                if next_url in visited_urls:
                    print("Stopping: next URL already visited")
                    break

                page.goto(
                    next_url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

        finally:
            browser.close()
