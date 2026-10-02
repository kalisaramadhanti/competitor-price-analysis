import pytest
from pydantic import ValidationError

from crawler.models import ProductRecord


def test_valid_product():
    product = ProductRecord(
        platform="mock_store",
        product_name="Example Shampoo 170 ml",
        price_raw="Rp 25.000",
        source_url="https://example.com/product/1"
    )

    assert product.product_name == "Example Shampoo 170 ml"
    assert product.price_raw == "Rp 25.000"


def test_missing_price():
    with pytest.raises(ValidationError):
        ProductRecord(
            platform="mock_store",
            product_name="Example Shampoo",
            source_url="https://example.com/product/1"
        )


def test_optional_discount():
    product = ProductRecord(
        platform="mock_store",
        product_name="Example Shampoo",
        price_raw="Rp 25.000",
        source_url="https://example.com/product/1"
    )

    assert product.discount_raw is None