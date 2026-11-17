"""Service for normalizing taxpayer details."""

from app.schemas.taxpayer import TaxpayerDetails


class TaxpayerService:
    """Convert validated taxpayer details into response data."""

    def create_taxpayer(self, taxpayer: TaxpayerDetails) -> dict[str, str | int]:
        """Return the taxpayer's normalized details.

        Args:
            taxpayer: Validated taxpayer identity and regime details.

        Returns:
            A dictionary containing the taxpayer's name, age, and regime.
        """
        return {
            "name": taxpayer.name,
            "age": taxpayer.age,
            "tax_regime": taxpayer.tax_regime.value,
        }
