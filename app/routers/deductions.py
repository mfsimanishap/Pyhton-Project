"""Deduction endpoints."""

from typing import Any

from fastapi import APIRouter

from app.schemas.deduction import Deduction80CRequest
from app.services.deduction_80c_service import Deduction80CService
from app.services.deduction_service import DeductionService, StandardDeductionResult

router = APIRouter(tags=["Deductions"])
deduction_service = DeductionService()
deduction_80c_service = Deduction80CService()


@router.get("/deductions/standard/{tax_regime}")
def calculate_standard_deduction(tax_regime: str) -> StandardDeductionResult:
    """Return the standard deduction for a tax regime."""
    return deduction_service.calculate_standard_deduction(tax_regime)


@router.post("/deductions/80c")
def calculate_80c(request: Deduction80CRequest) -> dict[str, Any]:
    """Calculate the eligible section 80C deduction."""
    return deduction_80c_service.calculate_80c(request)
