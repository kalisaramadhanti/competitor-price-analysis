from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ProductRecord(BaseModel):
    platform: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    price_raw: str = Field(min_length=1)

    original_price_raw: Optional[str] = None
    discount_raw: Optional[str] = None
    detail_raw: Optional[str] = None

    source_url: str = Field(min_length=1)

    crawled_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    crawler_version: str = "1.0.0"