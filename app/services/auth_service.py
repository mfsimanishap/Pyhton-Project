"""Database operations for user registration and authentication."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """Find a user by their email address.

    Args:
        db: Database session used for the query.
        email: Email address to look up.

    Returns:
        The matching user, or ``None`` if no account exists.
    """
    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    """Create and persist a user account.

    Args:
        db: Database session used to persist the account.
        user_data: Validated registration details.

    Returns:
        The newly created user.

    Raises:
        ValueError: If the email address is already registered.
    """
    existing_user = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        raise ValueError("Email is already registered.")

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """Authenticate credentials against a registered account.

    Args:
        db: Database session used to find the account.
        email: Email address submitted by the user.
        password: Plaintext password submitted by the user.

    Returns:
        The matching user if the credentials are valid; otherwise ``None``.
    """
    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
