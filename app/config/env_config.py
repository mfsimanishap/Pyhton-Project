"""Environment-backed application settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-key-change-this-before-production",
)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

_database_path = Path(
    os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "tax_calculator.db"))
)
DATABASE_PATH = (
    _database_path if _database_path.is_absolute() else PROJECT_ROOT / _database_path
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
    raise ValueError(f"Invalid LOG_LEVEL: {LOG_LEVEL}")

DUMMY_DATA_ENABLED = os.getenv("DUMMY_DATA_ENABLED", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
