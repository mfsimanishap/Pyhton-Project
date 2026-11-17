"""Request schema for gross salary calculations."""

from pydantic import BaseModel, Field


class SalaryDetails(BaseModel):
    """Salary components used to calculate gross salary.

    Attributes:
        basic_salary: Annual basic salary.
        hra: Annual house rent allowance.
        special_allowance: Annual special allowance.
        bonus: Annual bonus.
    """

    basic_salary: float = Field(ge=0)
    hra: float = Field(ge=0)
    special_allowance: float = Field(ge=0)
    bonus: float = Field(ge=0)
