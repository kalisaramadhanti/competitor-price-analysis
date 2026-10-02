import json
from pathlib import Path

import pytest

from crawler.main import run_ingestion


ROOT = Path(__file__).resolve().parents[1]


def test_ingestion_is_idempotent(tmp_path):
    output = tmp_path / "products.jsonl"

    kwargs = {
        "source": str(
            ROOT / "synthetic_mock_store/v1/index.html"
        ),
        "platform": "mock_store",
        "base_url": "https://example.com",
        "output": str(output),
    }

    first = run_ingestion(**kwargs)
    second = run_ingestion(**kwargs)

    assert first["inserted"] == 1
    assert second["inserted"] == 0

    records = [
        json.loads(line)
        for line in output.read_text().splitlines()
    ]

    assert len(records) == 1
    assert records[0]["html_hash"]
    assert records[0]["raw_id"]


def test_v2_does_not_duplicate_v1(tmp_path):
    output = tmp_path / "products.jsonl"

    common = {
        "platform": "mock_store",
        "base_url": "https://example.com",
        "output": str(output),
    }

    first = run_ingestion(
        source=str(
            ROOT / "synthetic_mock_store/v1/index.html"
        ),
        **common,
    )

    second = run_ingestion(
        source=str(
            ROOT / "synthetic_mock_store/v2/index.html"
        ),
        **common,
    )

    assert first["inserted"] == 1
    assert second["inserted"] == 0


def test_ingestion_rejects_broken_html(tmp_path):
    source = tmp_path / "broken.html"
    output = tmp_path / "products.jsonl"

    source.write_text(
        "<html><body>Unexpected layout</body></html>"
    )

    with pytest.raises(RuntimeError):
        run_ingestion(
            source=str(source),
            platform="mock_store",
            base_url="https://example.com",
            output=str(output),
        )

    assert not output.exists()