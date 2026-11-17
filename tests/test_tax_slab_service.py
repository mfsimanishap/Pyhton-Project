"""Unit tests for tax slab calculations."""

import pytest

from app.services.tax_slab_service import TaxSlabService


def test_calculate_tax_rejects_invalid_regime():
    """Reject an unsupported regime when calculating slab tax."""

    service = TaxSlabService()

    with pytest.raises(ValueError, match="Invalid tax regime"):
        service.calculate_tax(100000, "invalid")
