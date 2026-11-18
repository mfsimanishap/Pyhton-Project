"""Tests for optional dummy-data seeding."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed import DUMMY_USERS, seed_dummy_data
from app.models.tax_calculation import TaxCalculation
from app.models.user import User


def test_seed_dummy_data_is_repeatable(db: Session) -> None:
    """Seed users and sample tax data without creating duplicates."""
    users = seed_dummy_data(db)

    assert len(users) == len(DUMMY_USERS)
    assert db.scalar(select(User).where(User.email == DUMMY_USERS[0]["email"])) is not None

    calculations = db.scalars(select(TaxCalculation)).all()
    assert len(calculations) == 1

    users_again = seed_dummy_data(db)
    assert [user.id for user in users_again] == [user.id for user in users]
    assert len(db.scalars(select(TaxCalculation)).all()) == 1
