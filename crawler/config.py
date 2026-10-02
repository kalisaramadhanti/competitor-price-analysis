SELECTORS = {
    "product_card": [
        ".product-card",
        "article[data-product-id]",
    ],
    "product_name": [
        ".product-name",
        "[data-testid='product-title']",
    ],
    "price": [
        ".selling-price",
        "[data-testid='selling-price']",
    ],
    "original_price": [
        ".original-price",
        "[data-testid='original-price']",
    ],
    "discount": [
        ".discount",
        "[data-testid='discount']",
    ],
    "detail": [
        ".product-detail",
        "[data-testid='product-detail']",
    ],
    "product_link": [
        "a.product-link",
        "a[href]",
    ],
}

MIN_PARSE_SUCCESS_RATE = 0.80