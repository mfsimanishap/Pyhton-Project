"""Authentication and application configuration values."""

import os

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key-change-this-before-production",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
