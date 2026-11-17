"""Password hashing and verification helpers."""

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password.

    Args:
        password: The plaintext password to hash.

    Returns:
        The encoded password hash.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Check a plaintext password against its stored hash.

    Args:
        plain_password: The password supplied by the user.
        hashed_password: The encoded hash stored for the user.

    Returns:
        Whether the password matches the hash.
    """
    return password_hash.verify(plain_password, hashed_password)
