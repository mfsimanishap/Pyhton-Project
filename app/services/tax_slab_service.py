"""Service for calculating progressive tax across income slabs."""

from typing import Any

from app.constants.tax_slabs import TAX_SLABS


class TaxSlabService:
    """Calculate tax and slab-level breakdowns."""

    def calculate_tax(self, taxable_income: float, tax_regime: str) -> dict[str, Any]:
        """Calculate progressive tax for a regime and taxable income.

        Args:
            taxable_income: Income amount to tax.
            tax_regime: Tax regime identifier, either ``old`` or ``new``.

        Returns:
            Taxable income, regime, total tax before cess, and slab breakdown.

        Raises:
            ValueError: If ``tax_regime`` is not supported.
        """
        if tax_regime == "old":
            slabs = TAX_SLABS.old
        elif tax_regime == "new":
            slabs = TAX_SLABS.new
        else:
            raise ValueError("Invalid tax regime")

        previous_limit: float = 0.0
        total_tax: float = 0.0
        breakdown = []

        for upper_limit, rate in slabs:
            if taxable_income <= previous_limit:
                break

            amount: float = min(taxable_income, upper_limit) - previous_limit
            tax = amount * rate
            total_tax += tax

            breakdown.append(
                {
                    "slab_rate": f"{rate * 100:.0f}%",
                    "taxable_amount": amount,
                    "tax": tax,
                }
            )

            previous_limit = upper_limit

        return {
            "taxable_income": taxable_income,
            "tax_regime": tax_regime,
            "tax_before_cess": total_tax,
            "breakdown": breakdown,
        }
