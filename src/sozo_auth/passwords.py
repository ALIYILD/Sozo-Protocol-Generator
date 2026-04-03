"""Password hashing, verification, and strength validation using passlib + bcrypt."""
from __future__ import annotations

import re

from passlib.context import CryptContext

from sozo_auth.config import auth_config

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return ``True`` if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


def validate_password_strength(password: str) -> list[str]:
    """Check password against policy rules and return a list of issues.

    An empty list means the password passes all checks.
    """
    issues: list[str] = []

    if len(password) < auth_config.min_password_length:
        issues.append(
            f"Password must be at least {auth_config.min_password_length} characters long"
        )
    if not re.search(r"[A-Z]", password):
        issues.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        issues.append("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        issues.append("Password must contain at least one digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        issues.append("Password must contain at least one special character")

    return issues
