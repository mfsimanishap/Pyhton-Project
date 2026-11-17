"""Authentication request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Fields required to register a user.

    Attributes:
        name: User's display name.
        email: User's unique email address.
        password: Plaintext password supplied for account creation.
    """

    name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Public user information returned by the API.

    Attributes:
        id: User's database identifier.
        name: User's display name.
        email: User's email address.
        created_at: Account creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class UserLogin(BaseModel):
    """Credentials submitted when logging in.

    Attributes:
        email: Email address associated with the account.
        password: Plaintext password to verify.
    """

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Bearer token returned after successful authentication.

    Attributes:
        access_token: Signed token used to authenticate requests.
        token_type: Authorization scheme for the token.
    """

    access_token: str
    token_type: str = "bearer"
