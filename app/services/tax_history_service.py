"""Persistence helpers for tax calculation history."""

from typing import Any

from sqlalchemy.orm import Session

from app.models.tax_calculation import TaxCalculation


def save_tax_calculation(
    db: Session,
    user_id: int,
    request_data: dict[str, Any],
    result_data: dict[str, Any],
) -> TaxCalculation:
    """Save a tax calculation and return its persisted database record.

    Args:
        db: Database session used to persist the calculation.
        user_id: Identifier of the user who owns the calculation.
        request_data: JSON-serializable input used for the calculation.
        result_data: JSON-serializable result of the calculation.

    Returns:
        The refreshed tax calculation record.
    """
    calculation = TaxCalculation(
        user_id=user_id,
        request_data=request_data,
        result_data=result_data,
    )

    try:
        db.add(calculation)
        db.commit()
        db.refresh(calculation)

    except Exception:
        db.rollback()
        raise

    return calculation
