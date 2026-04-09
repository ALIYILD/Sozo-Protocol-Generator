"""Auth configuration loaded from environment variables."""
from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings

from sozo_auth.runtime import is_production_like_deployment

# Keep placeholder obvious, but long enough to avoid HS256 key-length warnings in dev/tests.
_PLACEHOLDER_SECRET = "CHANGE-ME-IN-PRODUCTION-CHANGE-ME-IN-PRODUCTION"
_PLACEHOLDER_SECRET_PREFIX = "CHANGE-ME-IN-PRODUCTION"


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
    #: Backward-compatibility toggle: allow refresh tokens missing the JWT ``type`` claim.
    #: Safer default is False; can be enabled temporarily during migrations.
    allow_legacy_refresh_tokens_without_type: bool = False

    model_config = {"env_prefix": "SOZO_AUTH_"}

    @model_validator(mode="after")
    def _require_strong_secret_in_production(self) -> AuthConfig:
        if not is_production_like_deployment():
            return self
        key = (self.secret_key or "").strip()
        if not key or key == _PLACEHOLDER_SECRET or key.startswith(_PLACEHOLDER_SECRET_PREFIX):
            raise ValueError(
                "SOZO_AUTH_SECRET_KEY must be set to a non-default secret when "
                "SOZO_ENV or ENVIRONMENT is production, prod, staging, or stg"
            )
        return self


_auth_config: AuthConfig | None = None


def get_auth_config() -> AuthConfig:
    """Return a cached AuthConfig instance.

    Kept lazy to avoid import-time failures when tests temporarily set production-like
    env vars and expect ValidationError only when constructing AuthConfig explicitly.
    """
    global _auth_config
    if _auth_config is None:
        _auth_config = AuthConfig()
    return _auth_config


class _AuthConfigProxy:
    """Lazy proxy for backwards-compatible `auth_config` import sites."""

    def __getattr__(self, item: str):
        return getattr(get_auth_config(), item)


# Backwards-compatible module-level name (lazy, not instantiated at import time).
auth_config = _AuthConfigProxy()
