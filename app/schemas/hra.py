"""Request schema for house rent allowance calculations."""

from pydantic import BaseModel, Field


class HRADetails(BaseModel):
    """Salary and rent inputs used to calculate HRA exemption.

    Attributes:
        basic_salary: Annual basic salary.
        hra_received: Annual HRA received.
        rent_paid: Annual rent paid.
        dearness_allowance: Annual dearness allowance, if applicable.
        turnover_commission: Annual turnover-based commission, if applicable.
    """

    basic_salary: float = Field(ge=0)
    hra_received: float = Field(ge=0)
    rent_paid: float = Field(ge=0)
    dearness_allowance: float = Field(default=0, ge=0)
    turnover_commission: float = Field(default=0, ge=0)
