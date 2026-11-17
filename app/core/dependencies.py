"""FastAPI dependencies for authenticated requests."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.database.dependencies import get_db
from app.models.user import User

oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a bearer token.

    Args:
        credentials: Bearer credentials supplied with the request.
        db: Database session used to load the user.

    Returns:
        The user identified by the token.

    Raises:
        HTTPException: If the token is invalid or its user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        parsed_user_id = int(user_id)

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception from None

    user = db.get(User, parsed_user_id)

    if user is None:
        raise credentials_exception

    return user
