"""Service for calculating section 80C deductions."""

from typing import Any

from app.schemas.deduction import Deduction80CRequest


class Deduction80CService:
    """Calculate the allowed section 80C deduction."""

    MAX_DEDUCTION = 150000

    def calculate_80c(self, request: Deduction80CRequest) -> dict[str, Any]:
        """Calculate the allowed deduction for a tax regime.

        Args:
            request: Tax regime and eligible investment amount.

        Returns:
            Eligible investments, allowed deduction, and regime.
        """

        if request.tax_regime.value == "new":
            allowed_deduction: float = 0.0
        else:
            allowed_deduction = min(request.eligible_investments, self.MAX_DEDUCTION)

        return {
            "eligible_investments": request.eligible_investments,
            "allowed_deduction": allowed_deduction,
            "tax_regime": request.tax_regime.value,
        }
