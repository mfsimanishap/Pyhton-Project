"""Backward-compatible imports for application environment settings."""

from app.config.env_config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)

__all__ = ["ACCESS_TOKEN_EXPIRE_MINUTES", "ALGORITHM", "SECRET_KEY"]
