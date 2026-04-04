"""
SOZO Auth — Authentication and authorization module for the Sozo Protocol Generator.

Provides JWT-based authentication, role-based access control, and FastAPI
dependencies for securing API endpoints.
"""
from __future__ import annotations

from sozo_auth.config import AuthConfig
from sozo_auth.models import (
    PasswordChange,
    TokenPair,
    TokenPayload,
    UserCreate,
    UserResponse,
)
from sozo_auth.tokens import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
)
from sozo_auth.dependencies import (
    get_current_user,
    require_admin,
    require_clinician,
    require_reviewer,
    require_role,
)
from sozo_auth.rbac import (
    Permission,
    ROLE_PERMISSIONS,
    has_permission,
    require_permission,
)

__all__ = [
    # Config
    "AuthConfig",
    # Models
    "UserCreate",
    "UserResponse",
    "TokenPair",
    "TokenPayload",
    "PasswordChange",
    # Passwords (lazy — requires passlib)
    "hash_password",
    "verify_password",
    "validate_password_strength",
    # Tokens
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
    # Dependencies
    "get_current_user",
    "require_role",
    "require_clinician",
    "require_reviewer",
    "require_admin",
    # RBAC
    "Permission",
    "ROLE_PERMISSIONS",
    "has_permission",
    "require_permission",
    # Router (lazy — pulls password hashing)
    "auth_router",
]


def __getattr__(name: str):
    if name in ("hash_password", "verify_password", "validate_password_strength"):
        from sozo_auth import passwords as _pw

        return getattr(_pw, name)
    if name == "auth_router":
        from sozo_auth.router import auth_router as _router

        return _router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
