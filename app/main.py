"""FastAPI application and tax calculation endpoints."""

from typing import Any

from fastapi import Depends, FastAPI
from app.routers.auth import router as auth_router
from app.schemas.deduction import Deduction80CRequest
from app.schemas.hra import HRADetails
from app.schemas.salary import SalaryDetails
from app.schemas.tax_calculation import TaxCalculationRequest
from app.schemas.taxpayer import TaxpayerDetails
from app.services.cess_service import CessService
from app.services.deduction_80c_service import Deduction80CService
from app.services.deduction_service import DeductionService, StandardDeductionResult
from app.services.hra_service import HRAService
from app.services.salary_service import SalaryService
from app.services.tax_calculator_service import TaxCalculatorService
from app.services.taxpayer_service import TaxpayerService
from app.core.dependencies import get_current_user
from app.models.user import User

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.tax_history_service import save_tax_calculation

from sqlalchemy import select
from app.models.tax_calculation import TaxCalculation

app = FastAPI(
    title="Income Tax Calculator API",
    description="API for calculating and comparing Indian income tax.",
    version="1.0.0",
)

app.include_router(auth_router)

taxpayer_service = TaxpayerService()
salary_service = SalaryService()
hra_service = HRAService()
deduction_service = DeductionService()
deduction_80c_service = Deduction80CService()
tax_calculator_service = TaxCalculatorService()
cess_service = CessService()


@app.get("/")
def home() -> dict[str, Any]:
    """Return a welcome message for the API root.

    Returns:
        A message describing the API.
    """
    return {"message": "Welcome to the Income Tax Calculator API"}


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Report that the API is healthy.

    Returns:
        The service health status.
    """
    return {"status": "healthy"}


@app.post("/taxpayer")
def create_taxpayer(taxpayer: TaxpayerDetails) -> dict[str, Any]:
    """Validate and return the submitted taxpayer details.

    Args:
        taxpayer: Validated taxpayer information.

    Returns:
        A success message and the normalized taxpayer details.
    """
    result = taxpayer_service.create_taxpayer(taxpayer)

    return {"message": "Taxpayer details received successfully", "taxpayer": result}


@app.post("/salary/calculate")
def calculate_salary(salary: SalaryDetails) -> dict[str, Any]:
    """Calculate gross salary from its components.

    Args:
        salary: Validated salary components.

    Returns:
        The salary components and calculated gross salary.
    """
    return salary_service.calculate_gross_salary(salary)


@app.post("/salary/hra-exemption")
def calculate_hra_exemption(hra: HRADetails) -> dict[str, Any]:
    """Calculate the exempt and taxable portions of HRA.

    Args:
        hra: Salary, HRA, and rent details.

    Returns:
        The HRA exemption calculation.
    """
    return hra_service.calculate_hra_exemption(hra)


@app.get("/deductions/standard/{tax_regime}")
def calculate_standard_deduction(tax_regime: str) -> StandardDeductionResult:
    """Return the standard deduction for a tax regime.

    Args:
        tax_regime: Tax regime identifier, either ``old`` or ``new``.

    Returns:
        The regime and its standard deduction.
    """
    return deduction_service.calculate_standard_deduction(tax_regime)


@app.post("/deductions/80c")
def calculate_80c(request: Deduction80CRequest) -> dict[str, Any]:
    """Calculate the eligible section 80C deduction.

    Args:
        request: Tax regime and eligible investment amount.

    Returns:
        The eligible investments and allowed deduction.
    """
    return deduction_80c_service.calculate_80c(request)


@app.post("/tax/calculate-taxable-income")
def calculate_taxable_income(request: TaxCalculationRequest) -> dict[str, Any]:
    """Calculate taxable income for a selected tax regime.

    Args:
        request: Salary, deduction, and tax regime details.

    Returns:
        The income and deduction breakdown.
    """
    return tax_calculator_service.calculate_taxable_income(request)


@app.post("/tax/calculate-cess")
def calculate_cess(tax_amount: float) -> dict[str, Any]:
    """Calculate cess and total tax for an amount of tax.

    Args:
        tax_amount: Income tax before cess.

    Returns:
        The tax before cess, cess amount, and total tax.
    """
    return cess_service.calculate_cess(tax_amount)


@app.post("/tax/calculate")
def calculate_tax(
    request: TaxCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Calculate tax and save the result for the authenticated user.

    Args:
        request: Salary, deduction, and optional tax regime details.
        current_user: Authenticated user making the request.
        db: Database session used to persist the calculation.

    Returns:
        The tax calculation or regime comparison result.
    """
    result = tax_calculator_service.calculate_final_tax(request)

    save_tax_calculation(
        db=db,
        user_id=current_user.id,
        request_data=request.model_dump(mode="json"),
        result_data=result,
    )

    return result


@app.get("/tax/history")
def get_tax_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return saved tax calculations for the authenticated user.

    Args:
        current_user: Authenticated user whose history is requested.
        db: Database session used to query calculation history.

    Returns:
        The user's calculations in reverse chronological order.
    """
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
