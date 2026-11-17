"""FastAPI dependencies for database sessions."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request.

    Yields:
        A SQLAlchemy session bound to the application database.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
