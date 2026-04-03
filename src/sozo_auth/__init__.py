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
from sozo_auth.passwords import hash_password, validate_password_strength, verify_password
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
from sozo_auth.router import auth_router

__all__ = [
    # Config
    "AuthConfig",
    # Models
    "UserCreate",
    "UserResponse",
    "TokenPair",
    "TokenPayload",
    "PasswordChange",
    # Passwords
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
    # Router
    "auth_router",
]
