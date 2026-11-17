"""Request schema for income tax calculations."""

from pydantic import BaseModel, Field

from app.schemas.taxpayer import TaxRegime


class TaxCalculationRequest(BaseModel):
    """Income and deduction inputs for a tax calculation.

    Attributes:
        tax_regime: Regime to calculate, or ``None`` to compare both regimes.
        basic_salary: Annual basic salary.
        hra_received: Annual HRA received.
        special_allowance: Annual special allowance.
        bonus: Annual bonus.
        rent_paid: Annual rent paid.
        eligible_investments: Eligible annual section 80C investments.
    """

    tax_regime: TaxRegime | None = None
    basic_salary: float = Field(ge=0)
    hra_received: float = Field(ge=0)
    special_allowance: float = Field(ge=0)
    bonus: float = Field(ge=0)
    rent_paid: float = Field(ge=0)
    eligible_investments: float = Field(ge=0)
