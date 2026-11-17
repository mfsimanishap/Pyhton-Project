"""Unit tests for deductions, tax calculation, and regime comparison."""

import pytest

from app.schemas.deduction import Deduction80CRequest
from app.schemas.tax_calculation import TaxCalculationRequest
from app.schemas.taxpayer import TaxRegime
from app.services.deduction_80c_service import Deduction80CService
from app.services.deduction_service import DeductionService
from app.services.tax_calculator_service import TaxCalculatorService
from app.services.tax_slab_service import TaxSlabService


def test_calculate_final_tax():
    """Calculate taxable income, tax, cess, and total tax for the old regime."""

    service = TaxCalculatorService()

    request = TaxCalculationRequest(
        tax_regime=TaxRegime.OLD,
        basic_salary=600000,
        hra_received=240000,
        special_allowance=160000,
        bonus=100000,
        rent_paid=180000,
        is_metro_city=True,
        eligible_investments=100000,
    )

    result = service.calculate_final_tax(request)

    assert result["gross_salary"] == 1100000
    assert result["hra_exemption"] == 120000
    assert result["standard_deduction"] == 50000
    assert result["80c_deduction"] == 100000
    assert result["taxable_income"] == 830000
    assert result["tax_before_cess"] == 78500
    assert result["cess_amount"] == 3140
    assert result["total_tax"] == 81640


def test_80c_deduction_limit():
    """Cap the old-regime section 80C deduction at its maximum."""

    service = Deduction80CService()

    request = Deduction80CRequest(tax_regime=TaxRegime.OLD, eligible_investments=200000)

    result = service.calculate_80c(request)

    assert result["eligible_investments"] == 200000
    assert result["allowed_deduction"] == 150000


def test_80c_deduction_new_regime():
    """Disallow the section 80C deduction under the new regime."""

    service = Deduction80CService()

    request = Deduction80CRequest(tax_regime=TaxRegime.NEW, eligible_investments=150000)

    result = service.calculate_80c(request)

    assert result["eligible_investments"] == 150000
    assert result["allowed_deduction"] == 0


def test_old_regime_tax_slab():
    """Calculate tax across the applicable old-regime slabs."""

    service = TaxSlabService()

    result = service.calculate_tax(taxable_income=780000, tax_regime="old")

    assert result["tax_before_cess"] == 68500
    assert len(result["breakdown"]) == 3


def test_automatic_regime_comparison():
    """Compare old and new regime tax and report the recommended option."""

    service = TaxCalculatorService()

    request = TaxCalculationRequest(
        tax_regime=None,
        basic_salary=600000,
        hra_received=240000,
        special_allowance=160000,
        bonus=100000,
        rent_paid=180000,
        is_metro_city=True,
        eligible_investments=100000,
    )

    result = service.calculate_final_tax(request)

    comparison = result["comparison"]

    assert "old_regime" in comparison
    assert "new_regime" in comparison

    old_tax = comparison["old_regime"]["total_tax"]
    new_tax = comparison["new_regime"]["total_tax"]

    assert comparison["recommended_regime"] in ["old", "new", "both"]
    assert comparison["tax_saving"] == abs(old_tax - new_tax)


def test_zero_80c_investments():
    """Return no section 80C deduction when investments are zero."""

    service = Deduction80CService()

    request = Deduction80CRequest(
        tax_regime=TaxRegime.OLD,
        eligible_investments=0,
    )

    result = service.calculate_80c(request)

    assert result["eligible_investments"] == 0
    assert result["allowed_deduction"] == 0


def test_invalid_tax_regime_standard_deduction():
    """Reject an unsupported regime when looking up standard deduction."""

    service = DeductionService()

    with pytest.raises(ValueError, match="Invalid tax regime"):
        service.calculate_standard_deduction("invalid")


def test_calculate_taxable_income_without_regime():
    """Require a selected regime for an individual income calculation."""

    service = TaxCalculatorService()

    request = TaxCalculationRequest(
        tax_regime=None,
        basic_salary=600000,
        hra_received=200000,
        special_allowance=100000,
        bonus=50000,
        rent_paid=150000,
        eligible_investments=50000,
    )

    with pytest.raises(
        ValueError, match="Tax regime is required for individual calculation"
    ):
        service.calculate_taxable_income(request)


def test_old_regime_recommended():
    """Recommend the old regime when its tax is lower."""

    service = TaxCalculatorService()

    request = TaxCalculationRequest(
        tax_regime=None,
        basic_salary=300000,
        hra_received=150000,
        special_allowance=150000,
        bonus=0,
        rent_paid=150000,
        eligible_investments=150000,
    )

    result = service.calculate_final_tax(request)

    comparison = result["comparison"]

    assert comparison["recommended_regime"] == "old"
    assert comparison["old_regime"]["total_tax"] < comparison["new_regime"]["total_tax"]
    assert comparison["tax_saving"] > 0


def test_both_regimes_recommended_when_tax_is_equal():
    """Recommend both regimes when their calculated tax is equal."""

    service = TaxCalculatorService()

    request = TaxCalculationRequest(
        tax_regime=None,
        basic_salary=0,
        hra_received=0,
        special_allowance=0,
        bonus=0,
        rent_paid=0,
        eligible_investments=0,
    )

    result = service.calculate_final_tax(request)

    comparison = result["comparison"]

    assert comparison["old_regime"]["total_tax"] == 0
    assert comparison["new_regime"]["total_tax"] == 0
    assert comparison["recommended_regime"] == "both"
    assert comparison["tax_saving"] == 0
