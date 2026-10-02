import os

from fastapi import Header, HTTPException, status


READER_API_KEY = os.getenv("READER_API_KEY", "dev-reader-key")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key")


def require_reader(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    if x_api_key == ADMIN_API_KEY:
        return "admin"

    if x_api_key == READER_API_KEY:
        return "reader"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


def require_admin(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    if x_api_key == ADMIN_API_KEY:
        return "admin"

    if x_api_key == READER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )