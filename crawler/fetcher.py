from pathlib import Path
from urllib.parse import urlparse

import requests


def fetch_html(source: str) -> str:
    parsed = urlparse(source)

    if parsed.scheme in ("http", "https"):
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

    path = Path(parsed.path if parsed.scheme == "file" else source)
    return path.read_text(encoding="utf-8")