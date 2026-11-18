"""Tests for validated, immutable tax constants."""

import pytest
from pydantic import BaseModel, ValidationError

from app.constants.tax_constants import STANDARD_DEDUCTION
from app.constants.tax_slabs import TAX_SLABS


def test_tax_constants_are_immutable_pydantic_models():
    """Expose tax constants as immutable Pydantic model instances."""
    assert isinstance(STANDARD_DEDUCTION, BaseModel)
    assert isinstance(TAX_SLABS, BaseModel)

    with pytest.raises(ValidationError):
        STANDARD_DEDUCTION.old = 0

    with pytest.raises(ValidationError):
        TAX_SLABS.new = ()


def test_tax_slab_constants_use_immutable_sequences():
    """Keep slab definitions and their individual entries immutable."""
    assert isinstance(TAX_SLABS.old, tuple)
    assert isinstance(TAX_SLABS.old[0], tuple)
