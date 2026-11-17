"""Unit tests for cess calculations."""

import pytest

from app.services.cess_service import CessService


def test_calculate_cess_rejects_negative_tax():
    """Reject a negative tax amount when calculating cess."""

    service = CessService()

    with pytest.raises(ValueError, match="Tax amount cannot be negative"):
        service.calculate_cess(-1000)
