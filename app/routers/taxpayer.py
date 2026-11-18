"""Taxpayer endpoints."""

from typing import Any

from fastapi import APIRouter

from app.schemas.taxpayer import TaxpayerDetails
from app.services.taxpayer_service import TaxpayerService

router = APIRouter(tags=["Taxpayer"])
taxpayer_service = TaxpayerService()


@router.post("/taxpayer")
def create_taxpayer(taxpayer: TaxpayerDetails) -> dict[str, Any]:
    """Validate and return the submitted taxpayer details."""
    result = taxpayer_service.create_taxpayer(taxpayer)
    return {"message": "Taxpayer details received successfully", "taxpayer": result}
