"""Unit tests for gross salary calculations."""

from app.schemas.salary import SalaryDetails
from app.services.salary_service import SalaryService


def test_calculate_gross_salary():
    """Sum the salary components into the gross salary."""

    service = SalaryService()

    salary = SalaryDetails(
        basic_salary=600000,
        hra=200000,
        special_allowance=100000,
        bonus=50000,
    )

    result = service.calculate_gross_salary(salary)

    assert result["basic_salary"] == 600000
    assert result["hra"] == 200000
    assert result["special_allowance"] == 100000
    assert result["bonus"] == 50000
    assert result["gross_salary"] == 950000
