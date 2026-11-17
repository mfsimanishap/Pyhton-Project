"""Taxpayer details and supported tax regime schema."""

from enum import StrEnum

from pydantic import BaseModel, Field


class TaxRegime(StrEnum):
    """Supported Indian income tax regimes."""

    OLD = "old"
    NEW = "new"


class TaxpayerDetails(BaseModel):
    """Identity and regime preferences for a taxpayer.

    Attributes:
        name: Taxpayer's name.
        age: Taxpayer's age in years.
        tax_regime: Selected tax regime.
    """

    name: str = Field(min_length=2, max_length=100)
    age: int = Field(gt=0, lt=120)
    tax_regime: TaxRegime
