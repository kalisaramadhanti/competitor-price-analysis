from pathlib import Path

OUTPUT_DIR = Path("synthetic_mock_store/historical")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

observations = [
    # date, product, blibli price, blibli original, blibli discount,
    #       tokopedia price, tokopedia original, tokopedia discount

    ("2026-04-30", "Dove Shampoo 170ml", 25000, 30000, 17, 27000, 32000, 16),
    ("2026-05-31", "Dove Shampoo 170ml", 25000, 30000, 17, 27000, 32000, 16),
    ("2026-06-30", "Dove Shampoo 170ml", 25000, 30000, 17, 26500, 32000, 17),
    ("2026-07-31", "Dove Shampoo 170ml", 26000, 30000, 13, 26500, 32000, 17),
    ("2026-08-31", "Dove Shampoo 170ml", 26000, 30000, 13, 27000, 32000, 16),

    ("2026-04-30", "Dove Shampoo 340ml", 45000, 50000, 10, 47000, 52000, 10),
    ("2026-05-31", "Dove Shampoo 340ml", 45000, 50000, 10, 47000, 52000, 10),
    ("2026-06-30", "Dove Shampoo 340ml", 45000, 50000, 10, 47000, 52000, 10),
    ("2026-07-31", "Dove Shampoo 340ml", 46000, 50000, 8, 47000, 52000, 10),
    ("2026-08-31", "Dove Shampoo 340ml", 46000, 50000, 8, 48000, 52000, 8),

    ("2026-04-30", "Lifebuoy Body Wash 500ml", 42000, 45000, 7, 40000, 45000, 11),
    ("2026-05-31", "Lifebuoy Body Wash 500ml", 42000, 45000, 7, 40000, 45000, 11),
    ("2026-06-30", "Lifebuoy Body Wash 500ml", 41000, 45000, 9, 40000, 45000, 11),
    ("2026-07-31", "Lifebuoy Body Wash 500ml", 41000, 45000, 9, 39000, 45000, 13),
    ("2026-08-31", "Lifebuoy Body Wash 500ml", 42000, 45000, 7, 39000, 45000, 13),

    ("2026-04-30", "Sunsilk Shampoo 170ml", 24000, 27000, 11, 25000, 28000, 11),
    ("2026-05-31", "Sunsilk Shampoo 170ml", 24000, 27000, 11, 25000, 28000, 11),
    ("2026-06-30", "Sunsilk Shampoo 170ml", 23000, 27000, 15, 25000, 28000, 11),
    ("2026-07-31", "Sunsilk Shampoo 170ml", 23000, 27000, 15, 24500, 28000, 13),
    ("2026-08-31", "Sunsilk Shampoo 170ml", 24000, 27000, 11, 24500, 28000, 13),
]


def make_card(product, price, original, discount):
    return f"""
    <div class="product-card">
        <div class="product-name">{product}</div>
        <div class="selling-price">Rp{price:,}</div>
        <div class="original-price">Rp{original:,}</div>
        <div class="discount">{discount}%</div>
        <div class="product-detail">{product}</div>
        <a class="product-link" href="/synthetic/{product.lower().replace(' ', '-')}">
            View
        </a>
    </div>
    """


grouped = {}

for (
    date,
    product,
    blibli_price,
    blibli_original,
    blibli_discount,
    tokopedia_price,
    tokopedia_original,
    tokopedia_discount,
) in observations:

    grouped.setdefault((date, "blibli"), []).append(
        make_card(
            product,
            blibli_price,
            blibli_original,
            blibli_discount,
        )
    )

    grouped.setdefault((date, "tokopedia"), []).append(
        make_card(
            product,
            tokopedia_price,
            tokopedia_original,
            tokopedia_discount,
        )
    )


for (date, platform), cards in grouped.items():
    html = f"""
    <html>
        <body>
            {''.join(cards)}
        </body>
    </html>
    """

    path = OUTPUT_DIR / f"{date}_{platform}.html"
    path.write_text(html, encoding="utf-8")

    print(f"Created {path}")