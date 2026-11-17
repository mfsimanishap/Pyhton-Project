"""Service coordinating deductions, tax slabs, and regime comparisons."""

from typing import Any

from app.schemas.deduction import Deduction80CRequest
from app.schemas.hra import HRADetails
from app.schemas.tax_calculation import TaxCalculationRequest
from app.schemas.taxpayer import TaxRegime
from app.services.cess_service import CessService
from app.services.deduction_80c_service import Deduction80CService
from app.services.deduction_service import DeductionService
from app.services.hra_service import HRAService
from app.services.tax_slab_service import TaxSlabService


class TaxCalculatorService:
    """Calculate taxable income, final tax, and regime comparisons."""

    def __init__(self) -> None:
        """Initialize the services used in tax calculations."""
        self.hra_service = HRAService()
        self.deduction_service = DeductionService()
        self.deduction_80c_service = Deduction80CService()
        self.tax_slab_service = TaxSlabService()
        self.cess_service = CessService()

    def calculate_taxable_income(
        self, request: TaxCalculationRequest
    ) -> dict[str, Any]:
        """Calculate taxable income for one explicitly selected regime.

        Args:
            request: Salary, deduction, and selected regime details.

        Returns:
            Gross salary, allowable deductions, and taxable income.

        Raises:
            ValueError: If no tax regime is selected.
        """

        if request.tax_regime is None:
            raise ValueError("Tax regime is required for individual calculation")

        gross_salary = (
            request.basic_salary
            + request.hra_received
            + request.special_allowance
            + request.bonus
        )

        if request.tax_regime == TaxRegime.OLD:
            hra_request = HRADetails(
                basic_salary=request.basic_salary,
                hra_received=request.hra_received,
                rent_paid=request.rent_paid,
            )

            hra_result = self.hra_service.calculate_hra_exemption(hra_request)
            hra_exemption = hra_result["hra_exemption"]

        else:
            hra_exemption = 0

        standard_result = self.deduction_service.calculate_standard_deduction(
            request.tax_regime.value
        )

        investment_request = Deduction80CRequest(
            tax_regime=request.tax_regime,
            eligible_investments=request.eligible_investments,
        )

        investment_result = self.deduction_80c_service.calculate_80c(investment_request)

        taxable_income = (
            gross_salary
            - hra_exemption
            - standard_result["standard_deduction"]
            - investment_result["allowed_deduction"]
        )

        return {
            "gross_salary": gross_salary,
            "hra_exemption": hra_exemption,
            "standard_deduction": standard_result["standard_deduction"],
            "80c_deduction": investment_result["allowed_deduction"],
            "taxable_income": max(taxable_income, 0),
        }

    def calculate_final_tax(self, request: TaxCalculationRequest) -> dict[str, Any]:
        """Calculate final tax or compare both tax regimes.

        Args:
            request: Salary, deduction, and optional regime details.

        Returns:
            The final tax breakdown for one regime, or both regimes with a
            recommendation when no regime was selected.
        """

        if request.tax_regime is None:
            return self.compare_regimes(request)

        income_result = self.calculate_taxable_income(request)

        taxable_income = income_result["taxable_income"]

        tax_result = self.tax_slab_service.calculate_tax(
            taxable_income, request.tax_regime.value
        )

        tax_before_cess = tax_result["tax_before_cess"]

        cess_result = self.cess_service.calculate_cess(tax_before_cess)

        return {
            **income_result,
            "tax_regime": request.tax_regime.value,
            "tax_before_cess": tax_before_cess,
            "tax_slab_breakdown": tax_result["breakdown"],
            "cess_amount": cess_result["cess_amount"],
            "total_tax": cess_result["total_tax"],
        }

    def compare_regimes(self, request: TaxCalculationRequest) -> dict[str, Any]:
        """Calculate and compare tax under the old and new regimes.

        Args:
            request: Salary and deduction details to evaluate in both regimes.

        Returns:
            Both regime results, the recommended regime, and the tax saving.
        """

        old_request = request.model_copy(update={"tax_regime": TaxRegime.OLD})

        new_request = request.model_copy(update={"tax_regime": TaxRegime.NEW})

        old_result = self.calculate_final_tax(old_request)
        new_result = self.calculate_final_tax(new_request)

        old_tax = old_result["total_tax"]
        new_tax = new_result["total_tax"]

        if old_tax < new_tax:
            recommended_regime = "old"
            tax_saving = new_tax - old_tax

        elif new_tax < old_tax:
            recommended_regime = "new"
            tax_saving = old_tax - new_tax

        else:
            recommended_regime = "both"
            tax_saving = 0

        return {
            "comparison": {
                "old_regime": old_result,
                "new_regime": new_result,
                "recommended_regime": recommended_regime,
                "tax_saving": tax_saving,
            }
        }
