"""API integration tests for tax calculation and taxpayer endpoints."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.token import create_access_token
from app.database.dependencies import get_db
from app.main import app
from app.models.tax_calculation import TaxCalculation
from app.models.user import User

client = TestClient(app)


@pytest.fixture(autouse=True)
def authenticated_test_client() -> Generator[None]:
    """Provide an isolated database and a valid user token for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TaxCalculation.metadata.create_all(engine)
    test_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    with test_session_factory() as db:
        user = User(
            name="API Test User",
            email="api-test@example.com",
            hashed_password="not-used",
        )
        db.add(user)
        db.commit()
        access_token = create_access_token(user.id)

    def override_get_db() -> Generator[Session]:
        with test_session_factory() as db:
            yield db

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    client.headers["Authorization"] = f"Bearer {access_token}"

    try:
        yield
    finally:
        client.headers.pop("Authorization", None)
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def test_calculate_tax_requires_authentication() -> None:
    """Reject tax calculation requests without a bearer token."""
    unauthenticated_client = TestClient(app)

    response = unauthenticated_client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 401


def test_calculate_tax_endpoint():
    """Verify a manual old-regime calculation response."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "is_metro_city": True,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["gross_salary"] == 1100000
    assert result["taxable_income"] == 830000
    assert result["tax_before_cess"] == 78500
    assert result["cess_amount"] == 3140
    assert result["total_tax"] == 81640


def test_calculate_tax_with_negative_salary():
    """Reject a tax calculation with a negative salary."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": -600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "is_metro_city": True,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 422


def test_calculate_tax_with_invalid_regime():
    """Reject a tax calculation with an unsupported regime."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "invalid",
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "is_metro_city": True,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 422


def test_automatic_regime_comparison_endpoint():
    """Return both regimes and a recommendation when none is selected."""

    response = client.post(
        "/tax/calculate",
        json={
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 200

    result = response.json()
    comparison = result["comparison"]

    assert "old_regime" in comparison
    assert "new_regime" in comparison

    old_tax = comparison["old_regime"]["total_tax"]
    new_tax = comparison["new_regime"]["total_tax"]

    assert comparison["recommended_regime"] in [
        "old",
        "new",
        "both",
    ]

    assert comparison["tax_saving"] == abs(old_tax - new_tax)


def test_manual_regime_selection():
    """Return only the selected old-regime calculation."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["tax_regime"] == "old"
    assert "total_tax" in result
    assert "comparison" not in result


def test_manual_new_regime_selection():
    """Apply new-regime deduction rules for a manual selection."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "new",
            "basic_salary": 600000,
            "hra_received": 240000,
            "special_allowance": 160000,
            "bonus": 100000,
            "rent_paid": 180000,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["tax_regime"] == "new"
    assert result["hra_exemption"] == 0
    assert result["80c_deduction"] == 0
    assert "total_tax" in result
    assert "comparison" not in result


def test_zero_income_calculation():
    """Calculate zero tax for zero income under the new regime."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "new",
            "basic_salary": 0,
            "hra_received": 0,
            "special_allowance": 0,
            "bonus": 0,
            "rent_paid": 0,
            "eligible_investments": 0,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["gross_salary"] == 0
    assert result["taxable_income"] == 0
    assert result["total_tax"] == 0


def test_negative_investments_validation():
    """Reject negative eligible investment amounts."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": 150000,
            "eligible_investments": -10000,
        },
    )

    assert response.status_code == 422


def test_negative_rent_validation():
    """Reject negative rent amounts."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": -5000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_negative_basic_salary_validation():
    """Reject a negative basic salary."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": -10000,
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": 150000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_missing_basic_salary_validation():
    """Reject a calculation request without a basic salary."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": 150000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_negative_hra_validation():
    """Reject a negative HRA amount."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": -10000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": 150000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_negative_bonus_validation():
    """Reject a negative bonus amount."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": -5000,
            "rent_paid": 150000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_negative_special_allowance_validation():
    """Reject a negative special allowance."""

    response = client.post(
        "/tax/calculate",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 200000,
            "special_allowance": -10000,
            "bonus": 50000,
            "rent_paid": 150000,
            "eligible_investments": 50000,
        },
    )

    assert response.status_code == 422


def test_home_endpoint():
    """Return a welcome message from the API root."""

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Income Tax Calculator API"}


def test_health_endpoint():
    """Return the healthy status from the health endpoint."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_taxpayer_endpoint():
    """Accept taxpayer details and return the normalized response."""

    response = client.post(
        "/taxpayer",
        json={
            "name": "Rahul",
            "age": 30,
            "tax_regime": "old",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["message"] == "Taxpayer details received successfully"
    assert result["taxpayer"]["name"] == "Rahul"
    assert result["taxpayer"]["age"] == 30
    assert result["taxpayer"]["tax_regime"] == "old"


def test_calculate_salary_endpoint():
    """Return the gross salary and its component amounts."""

    response = client.post(
        "/salary/calculate",
        json={
            "basic_salary": 600000,
            "hra": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["basic_salary"] == 600000
    assert result["hra"] == 200000
    assert result["special_allowance"] == 100000
    assert result["bonus"] == 50000
    assert result["gross_salary"] == 950000


def test_calculate_hra_exemption_endpoint():
    """Return HRA exemption details for a valid request."""

    response = client.post(
        "/salary/hra-exemption",
        json={
            "basic_salary": 600000,
            "hra_received": 200000,
            "rent_paid": 300000,
            "dearness_allowance": 0,
            "turnover_commission": 0,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["actual_hra"] == 200000
    assert result["rent_excess"] == 240000
    assert result["salary_limit"] == 240000
    assert result["hra_exemption"] == 200000
    assert result["taxable_hra"] == 0


def test_standard_deduction_endpoint():
    """Return the standard deduction for the old regime."""

    response = client.get("/deductions/standard/old")

    assert response.status_code == 200
    assert response.json() == {
        "tax_regime": "old",
        "standard_deduction": 50000,
    }


def test_new_regime_standard_deduction_endpoint():
    """Return the standard deduction for the new regime."""

    response = client.get("/deductions/standard/new")

    assert response.status_code == 200
    assert response.json() == {
        "tax_regime": "new",
        "standard_deduction": 75000,
    }


def test_80c_deduction_endpoint():
    """Return the allowed section 80C deduction."""

    response = client.post(
        "/deductions/80c",
        json={
            "tax_regime": "old",
            "eligible_investments": 200000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["eligible_investments"] == 200000
    assert result["allowed_deduction"] == 150000
    assert result["tax_regime"] == "old"


def test_calculate_taxable_income_endpoint():
    """Return taxable income and deductions for the old regime."""

    response = client.post(
        "/tax/calculate-taxable-income",
        json={
            "tax_regime": "old",
            "basic_salary": 600000,
            "hra_received": 200000,
            "special_allowance": 100000,
            "bonus": 50000,
            "rent_paid": 300000,
            "eligible_investments": 100000,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["gross_salary"] == 950000
    assert result["hra_exemption"] == 200000
    assert result["standard_deduction"] == 50000
    assert result["80c_deduction"] == 100000
    assert result["taxable_income"] == 600000


def test_calculate_cess_endpoint():
    """Return the cess amount and total tax for a valid amount."""

    response = client.post(
        "/tax/calculate-cess",
        params={"tax_amount": 100000},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["tax_before_cess"] == 100000
    assert result["cess_rate"] == "4%"
    assert result["cess_amount"] == 4000
    assert result["total_tax"] == 104000
