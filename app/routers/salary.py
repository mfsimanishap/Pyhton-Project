"""Salary and HRA endpoints."""

from typing import Any

from fastapi import APIRouter

from app.schemas.hra import HRADetails
from app.schemas.salary import SalaryDetails
from app.services.hra_service import HRAService
from app.services.salary_service import SalaryService

router = APIRouter(tags=["Salary"])
salary_service = SalaryService()
hra_service = HRAService()


@router.post("/salary/calculate")
def calculate_salary(salary: SalaryDetails) -> dict[str, Any]:
    """Calculate gross salary from its components."""
    return salary_service.calculate_gross_salary(salary)


@router.post("/salary/hra-exemption")
def calculate_hra_exemption(hra: HRADetails) -> dict[str, Any]:
    """Calculate the exempt and taxable portions of HRA."""
    return hra_service.calculate_hra_exemption(hra)
