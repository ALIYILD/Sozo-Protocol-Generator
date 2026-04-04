"""Auth configuration loaded from environment variables."""
from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings

from sozo_auth.runtime import is_production_like_deployment

_PLACEHOLDER_SECRET = "CHANGE-ME-IN-PRODUCTION"


class AuthConfig(BaseSettings):
    """JWT and password policy settings.

    All values can be overridden via environment variables prefixed with
    ``SOZO_AUTH_`` (e.g. ``SOZO_AUTH_SECRET_KEY``).

    In production-like deployments (``SOZO_ENV`` / ``ENVIRONMENT`` =
    production, prod, staging, stg), a non-placeholder secret must be set or
    model validation fails at startup.
    """

    secret_key: str = _PLACEHOLDER_SECRET
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    refresh_token_expire_days: int = 30
    min_password_length: int = 12

    model_config = {"env_prefix": "SOZO_AUTH_"}

    @model_validator(mode="after")
    def _require_strong_secret_in_production(self) -> AuthConfig:
        if not is_production_like_deployment():
            return self
        key = (self.secret_key or "").strip()
        if not key or key == _PLACEHOLDER_SECRET:
            raise ValueError(
                "SOZO_AUTH_SECRET_KEY must be set to a non-default secret when "
                "SOZO_ENV or ENVIRONMENT is production, prod, staging, or stg"
            )
        return self


# Module-level singleton — import this rather than constructing new instances.
auth_config = AuthConfig()
