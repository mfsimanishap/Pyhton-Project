"""Unit tests for HRA exemption calculations."""

from app.schemas.hra import HRADetails
from app.services.hra_service import HRAService


def test_hra_exemption_limited_by_actual_hra():
    """Limit the exemption to the HRA actually received."""

    service = HRAService()

    hra = HRADetails(
        basic_salary=600000,
        hra_received=100000,
        rent_paid=300000,
    )

    result = service.calculate_hra_exemption(hra)

    assert result["hra_exemption"] == 100000


def test_hra_exemption_limited_by_rent_paid():
    """Limit the exemption to rent paid above ten percent of salary."""

    service = HRAService()

    hra = HRADetails(
        basic_salary=600000,
        hra_received=300000,
        rent_paid=200000,
    )

    result = service.calculate_hra_exemption(hra)

    assert result["hra_exemption"] == 140000


def test_hra_exemption_limited_by_salary_percentage():
    """Limit the exemption to the applicable salary percentage."""

    service = HRAService()

    hra = HRADetails(
        basic_salary=600000,
        hra_received=300000,
        rent_paid=500000,
    )

    result = service.calculate_hra_exemption(hra)

    assert result["hra_exemption"] == 240000


def test_hra_exemption_when_rent_is_zero():
    """Allow no HRA exemption when no rent has been paid."""

    service = HRAService()

    hra = HRADetails(
        basic_salary=600000,
        hra_received=200000,
        rent_paid=0,
    )

    result = service.calculate_hra_exemption(hra)

    assert result["hra_exemption"] == 0
    assert result["taxable_hra"] == 200000
