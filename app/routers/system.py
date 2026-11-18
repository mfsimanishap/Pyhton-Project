"""Application health and root endpoints."""

from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/")
def home() -> dict[str, Any]:
    """Return a welcome message for the API root."""
    return {"message": "Welcome to the Income Tax Calculator API"}


@router.get("/health")
def health_check() -> dict[str, Any]:
    """Report that the API is healthy."""
    return {"status": "healthy"}
