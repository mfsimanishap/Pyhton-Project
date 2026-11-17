"""JWT access-token creation helpers."""

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


def create_access_token(
    user_id: int,
) -> str:
    """Create a signed access token for a user.

    Args:
        user_id: Identifier of the user the token represents.

    Returns:
        A signed JWT containing the user identifier and expiry time.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
