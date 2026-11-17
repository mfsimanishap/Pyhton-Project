"""ORM model for saved tax calculations."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TaxCalculation(Base):
    """A tax calculation request and its result.

    Attributes:
        id: Primary key of the calculation.
        user_id: Identifier of the user who owns the calculation.
        request_data: JSON-serializable input used for the calculation.
        result_data: JSON-serializable calculation output.
        created_at: UTC time when the calculation was saved.
    """

    __tablename__ = "tax_calculations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    request_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    result_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
