"""Validated standard deduction amounts for supported tax regimes."""

from pydantic import BaseModel, ConfigDict


class StandardDeductionConstants(BaseModel):
    """Standard deduction amounts for the old and new tax regimes."""

    model_config = ConfigDict(frozen=True)

    old: float = 50000
    new: float = 75000


STANDARD_DEDUCTION = StandardDeductionConstants()
