"""Service for calculating health and education cess."""


class CessService:
    """Calculate cess on income tax."""

    CESS_RATE = 0.04

    def calculate_cess(self, tax_amount: float) -> dict[str, float | str]:
        """Add cess to tax before cess.

        Args:
            tax_amount: Income tax amount before cess.

        Returns:
            Tax before cess, the rate, cess amount, and total tax.

        Raises:
            ValueError: If ``tax_amount`` is negative.
        """
        if tax_amount < 0:
            raise ValueError("Tax amount cannot be negative")

        cess = tax_amount * self.CESS_RATE
        total_tax = tax_amount + cess

        return {
            "tax_before_cess": tax_amount,
            "cess_rate": "4%",
            "cess_amount": cess,
            "total_tax": total_tax,
        }
