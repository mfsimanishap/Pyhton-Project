"""Unit tests for taxpayer detail normalization."""

from app.schemas.taxpayer import TaxpayerDetails, TaxRegime
from app.services.taxpayer_service import TaxpayerService


def test_create_taxpayer():
    """Return the normalized taxpayer name, age, and regime."""

    service = TaxpayerService()

    taxpayer = TaxpayerDetails(
        name="Rahul",
        age=30,
        tax_regime=TaxRegime.OLD,
    )

    result = service.create_taxpayer(taxpayer)

    assert result["name"] == "Rahul"
    assert result["age"] == 30
    assert result["tax_regime"] == "old"
