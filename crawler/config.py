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

BLIBLI_SELECTORS = {
    "product_card": [
        "a.elf-product-card[href*='/p/']",
    ],
    "product_name": [
        ".els-product__title",
    ],
    "price": [
        ".els-product__fixed-price",
    ],
    "original_price": [
        ".els-product__discount-price",
    ],
    "discount": [
        ".els-promo-label__text",
    ],
    "detail": [
        ".els-product__seller-name",
    ],
    "product_link": [
        "a[href*='/p/']",
    ],
}

MIN_PARSE_SUCCESS_RATE = 0.80