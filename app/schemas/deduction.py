"""Request schemas for tax deductions."""

from pydantic import BaseModel, Field

from app.schemas.taxpayer import TaxRegime


class Deduction80CRequest(BaseModel):
    """Inputs for calculating the section 80C deduction.

    Attributes:
        tax_regime: Regime under which the deduction is calculated.
        eligible_investments: Amount of eligible investments.
    """

    tax_regime: TaxRegime
    eligible_investments: float = Field(ge=0)
