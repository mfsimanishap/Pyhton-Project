"""Tax calculation and history endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.tax_calculation import TaxCalculation
from app.models.user import User
from app.schemas.tax_calculation import TaxCalculationRequest
from app.services.cess_service import CessService
from app.services.tax_calculator_service import TaxCalculatorService
from app.services.tax_history_service import save_tax_calculation

router = APIRouter(tags=["Tax"])
tax_calculator_service = TaxCalculatorService()
cess_service = CessService()


@router.post("/tax/calculate-taxable-income")
def calculate_taxable_income(request: TaxCalculationRequest) -> dict[str, Any]:
    """Calculate taxable income for a selected tax regime."""
    return tax_calculator_service.calculate_taxable_income(request)


@router.post("/tax/calculate-cess")
def calculate_cess(tax_amount: float) -> dict[str, Any]:
    """Calculate cess and total tax for an amount of tax."""
    return cess_service.calculate_cess(tax_amount)


@router.post("/tax/calculate")
def calculate_tax(
    request: TaxCalculationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Calculate tax and save the result for the authenticated user."""
    result = tax_calculator_service.calculate_final_tax(request)

    save_tax_calculation(
        db=db,
        user_id=current_user.id,
        request_data=request.model_dump(mode="json"),
        result_data=result,
    )

    return result


@router.get("/tax/history")
def get_tax_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, Any]]:
    """Return saved tax calculations for the authenticated user."""
    statement = (
        select(TaxCalculation)
        .where(TaxCalculation.user_id == current_user.id)
        .order_by(TaxCalculation.created_at.desc())
    )
    calculations = db.scalars(statement).all()

    return [
        {
            "id": calculation.id,
            "user_id": calculation.user_id,
            "request": calculation.request_data,
            "result": calculation.result_data,
            "created_at": calculation.created_at.isoformat(),
        }
        for calculation in calculations
    ]
