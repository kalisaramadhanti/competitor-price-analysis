from pathlib import Path

from crawler.parser import parse_products


ROOT = Path(__file__).resolve().parents[1]


def load_fixture(version):
    return (
        ROOT / "synthetic_mock_store" / version / "index.html"
    ).read_text(encoding="utf-8")


def test_parser_supports_v1():
    result = parse_products(
        html=load_fixture("v1"),
        platform="mock_store",
        base_url="https://example.com",
    )

    assert result.healthy
    assert result.total_cards == 1
    assert len(result.products) == 1
    assert result.products[0].price_raw == "Rp 25.000"


def test_parser_survives_v2():
    result = parse_products(
        html=load_fixture("v2"),
        platform="mock_store",
        base_url="https://example.com",
    )

    assert result.healthy
    assert result.total_cards == 1
    assert len(result.products) == 1
    assert (
        result.products[0].product_name
        == "Example Shampoo 170 ml"
    )


def test_parser_detects_broken_structure():
    broken_html = """
    <html>
        <body>
            <div class="unknown-product-layout">
                Something changed!
            </div>
        </body>
    </html>
    """

    result = parse_products(
        html=broken_html,
        platform="mock_store",
        base_url="https://example.com",
    )

    assert result.total_cards == 0
    assert result.success_rate == 0
    assert not result.healthy


def test_parser_rejects_missing_price():
    html = """
    <div class="product-card">
        <h2 class="product-name">Example Shampoo</h2>
    </div>
    """

    result = parse_products(
        html=html,
        platform="mock_store",
        base_url="https://example.com",
    )

    assert result.total_cards == 1
    assert result.failed_cards == 1
    assert not result.healthy