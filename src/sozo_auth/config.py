"""Auth configuration loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    """JWT and password policy settings.

    All values can be overridden via environment variables prefixed with
    ``SOZO_AUTH_`` (e.g. ``SOZO_AUTH_SECRET_KEY``).
    """

    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    refresh_token_expire_days: int = 30
    min_password_length: int = 12

    model_config = {"env_prefix": "SOZO_AUTH_"}


# Module-level singleton — import this rather than constructing new instances.
auth_config = AuthConfig()
