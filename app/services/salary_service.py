"""Service for gross salary calculations."""

from app.schemas.salary import SalaryDetails


class SalaryService:
    """Calculate gross salary from its component amounts."""

    def calculate_gross_salary(self, salary: SalaryDetails) -> dict[str, float]:
        """Sum the salary components into a gross annual salary.

        Args:
            salary: Annual basic salary, HRA, allowance, and bonus.

        Returns:
            Each salary component and the gross salary total.
        """

        gross_salary = (
            salary.basic_salary + salary.hra + salary.special_allowance + salary.bonus
        )

        return {
            "basic_salary": salary.basic_salary,
            "hra": salary.hra,
            "special_allowance": salary.special_allowance,
            "bonus": salary.bonus,
            "gross_salary": gross_salary,
        }
