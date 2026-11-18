"""Logging setup for the application."""

import logging

from app.config.env_config import LOG_LEVEL


def configure_logging() -> None:
    """Configure standard application logging to the console."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
