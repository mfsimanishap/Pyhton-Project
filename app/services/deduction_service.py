"""Service for standard deduction calculations."""

from typing import TypedDict

from app.constants.tax_constants import STANDARD_DEDUCTION


class StandardDeductionResult(TypedDict):
    """Standard deduction result for a tax regime.

    Attributes:
        tax_regime: Identifier of the selected tax regime.
        standard_deduction: Standard deduction amount for the regime.
    """

    tax_regime: str
    standard_deduction: float


class DeductionService:
    """Look up standard deductions by tax regime."""

    def calculate_standard_deduction(self, tax_regime: str) -> StandardDeductionResult:
        """Return the standard deduction allowed for a regime.

        Args:
            tax_regime: Tax regime identifier, either ``old`` or ``new``.

        Returns:
            The regime and its standard deduction amount.

        Raises:
            ValueError: If ``tax_regime`` is not supported.
        """

        deduction = STANDARD_DEDUCTION.get(tax_regime)

        if deduction is None:
            raise ValueError("Invalid tax regime")

        return {
            "tax_regime": tax_regime,
            "standard_deduction": float(deduction),
        }
