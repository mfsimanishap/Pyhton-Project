"""Service for house rent allowance exemption calculations."""

from app.schemas.hra import HRADetails


class HRAService:
    """Calculate the exempt and taxable HRA amounts."""

    def calculate_hra_exemption(self, hra: HRADetails) -> dict[str, float]:
        """Calculate HRA exemption using salary, rent, and HRA limits.

        Args:
            hra: Annual salary, HRA, rent, and related allowance details.

        Returns:
            Actual HRA, each limiting amount, exemption, and taxable HRA.
        """

        salary = hra.basic_salary + hra.dearness_allowance + hra.turnover_commission

        actual_hra = hra.hra_received

        rent_excess = max(hra.rent_paid - (salary * 0.10), 0)

        salary_limit = salary * 0.40

        exemption = min(actual_hra, rent_excess, salary_limit)

        return {
            "actual_hra": actual_hra,
            "rent_excess": rent_excess,
            "salary_limit": salary_limit,
            "hra_exemption": exemption,
            "taxable_hra": actual_hra - exemption,
        }
