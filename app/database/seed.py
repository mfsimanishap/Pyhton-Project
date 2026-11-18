"""Optional dummy-data seeding for local development and test environments."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.tax_calculation import TaxCalculation
from app.models.user import User


DUMMY_USERS = (
    {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@123",
    },
    {
        "name": "Demo User",
        "email": "demo@example.com",
        "password": "Demo@123",
    },
)


DUMMY_TAX_REQUEST = {
    "tax_regime": "old",
    "basic_salary": 600000,
    "hra_received": 240000,
    "special_allowance": 160000,
    "bonus": 100000,
    "rent_paid": 180000,
    "is_metro_city": True,
    "eligible_investments": 100000,
}


def seed_dummy_data(db: Session) -> list[User]:
    """Insert repeatable dummy users and a sample calculation if absent."""
    users: list[User] = []

    for data in DUMMY_USERS:
        user = db.scalar(select(User).where(User.email == data["email"]))

        if user is None:
            user = User(
                name=data["name"],
                email=data["email"],
                hashed_password=hash_password(data["password"]),
            )
            db.add(user)
            db.flush()

        users.append(user)

    test_user = users[0]
    existing_calculation = db.scalar(
        select(TaxCalculation).where(TaxCalculation.user_id == test_user.id).limit(1)
    )

    if existing_calculation is None:
        db.add(
            TaxCalculation(
                user_id=test_user.id,
                request_data=DUMMY_TAX_REQUEST,
                result_data={
                    "gross_salary": 1100000,
                    "taxable_income": 830000,
                    "tax_before_cess": 78500,
                    "cess_amount": 3140,
                    "total_tax": 81640,
                },
            )
        )

    db.commit()
    return users
