"""Authentication endpoints for registration and login."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.token import create_access_token
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Register a user account.

    Args:
        user_data: Validated name, email, and password for the new user.
        db: Database session used to create the account.

    Returns:
        The public representation of the newly registered user.

    Raises:
        HTTPException: If the email address is already registered.
    """
    try:
        user = create_user(db, user_data)
        return UserResponse.model_validate(user)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login_data: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate a user and return an access token.

    Args:
        login_data: User email and password.
        db: Database session used to find the account.

    Returns:
        A bearer access token.

    Raises:
        HTTPException: If the email or password is invalid.
    """
    user = authenticate_user(
        db,
        login_data.email,
        login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_logged_in_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Return the public profile of the authenticated user.

    Args:
        current_user: User resolved from the request's bearer token.

    Returns:
        The authenticated user's public profile.
    """
    return UserResponse.model_validate(current_user)
