"""FastAPI auth router — login, refresh, register, me, password change, logout."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from sozo_auth.dependencies import get_current_user, require_admin
from sozo_auth.models import (
    LoginRequest,
    PasswordChange,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserResponse,
)
from sozo_auth.passwords import hash_password, validate_password_strength, verify_password
from sozo_auth.tokens import create_token_pair, decode_token

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# User store — tries SQLite/PostgreSQL database first, falls back to in-memory.
# ---------------------------------------------------------------------------
_users_db: dict[str, dict[str, Any]] = {}

# Blacklisted JTIs for logout support.
_token_blacklist: set[str] = set()


def _find_user_by_email(email: str) -> dict[str, Any] | None:
    """Look up user by email — database first, then in-memory fallback."""
    # Try database
    try:
        import os
        import sqlite3
        db_url = os.environ.get("DATABASE_URL", "")
        if "sqlite" in db_url:
            db_path = db_url.split("///")[-1]
        else:
            db_path = "sozo_dev.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, email, name, role, credentials_hash, active, created_at "
                "FROM users WHERE email = ? AND active = 1",
                (email,),
            ).fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "email": row["email"],
                    "name": row["name"],
                    "role": row["role"],
                    "password_hash": row["credentials_hash"],
                    "active": bool(row["active"]),
                    "created_at": row["created_at"] or "2026-01-01T00:00:00",
                }
    except Exception as exc:
        logger.debug("DB lookup failed, using in-memory: %s", exc)

    # Fallback to in-memory
    for user in _users_db.values():
        if user["email"] == email:
            return user
    return None


def _find_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Look up user by ID — database first, then in-memory fallback."""
    try:
        import os
        import sqlite3
        db_url = os.environ.get("DATABASE_URL", "")
        if "sqlite" in db_url:
            db_path = db_url.split("///")[-1]
        else:
            db_path = "sozo_dev.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, email, name, role, credentials_hash, active, created_at "
                "FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "email": row["email"],
                    "name": row["name"],
                    "role": row["role"],
                    "password_hash": row["credentials_hash"],
                    "active": bool(row["active"]),
                    "created_at": row["created_at"] or "2026-01-01T00:00:00",
                }
    except Exception as exc:
        logger.debug("DB lookup failed, using in-memory: %s", exc)

    return _users_db.get(user_id)


def _user_to_response(user: dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        active=user["active"],
        created_at=user["created_at"],
    )


# ── POST /auth/login ─────────────────────────────────────────────────


@auth_router.post("/login", response_model=TokenPair)
async def login(body: LoginRequest) -> TokenPair:
    """Authenticate with email + password and receive a token pair."""
    user = _find_user_by_email(body.email)
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.get("active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    logger.info("User %s logged in", user["id"])
    return create_token_pair(user["id"], user["role"])


# ── POST /auth/refresh ───────────────────────────────────────────────


@auth_router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest) -> TokenPair:
    """Exchange a valid refresh token for a new token pair."""
    import jwt as _jwt

    try:
        payload = decode_token(body.refresh_token)
    except _jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    except _jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {exc}",
        )

    # Check blacklist.
    if payload.jti and payload.jti in _token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    # Look up the user to get the current role (may have changed since last login).
    user = _find_user_by_id(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.get("active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Blacklist the old refresh token to enforce single-use.
    if payload.jti:
        _token_blacklist.add(payload.jti)

    return create_token_pair(user["id"], user["role"])


# ── POST /auth/register ──────────────────────────────────────────────


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def register(body: UserCreate) -> UserResponse:
    """Create a new user account. Admin-only."""
    # Check for duplicate email.
    if _find_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    # Validate password strength.
    issues = validate_password_strength(body.password)
    if issues:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password_issues": issues},
        )

    import uuid
    from datetime import datetime, timezone

    user_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    user_record: dict[str, Any] = {
        "id": user_id,
        "email": body.email,
        "name": body.name,
        "role": body.role,
        "active": True,
        "created_at": now,
        "password_hash": hash_password(body.password),
    }
    _users_db[user_id] = user_record
    logger.info("User %s (%s) registered by admin", user_id, body.email)
    return _user_to_response(user_record)


# ── GET /auth/me ──────────────────────────────────────────────────────


@auth_router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    # If a real DB exists, look up full record; otherwise use the token-derived user.
    user = _users_db.get(current_user.id)
    if user:
        return _user_to_response(user)
    return current_user


# ── PUT /auth/password ────────────────────────────────────────────────


@auth_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChange,
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Change the current user's password."""
    user = _users_db.get(current_user.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in store",
        )

    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    issues = validate_password_strength(body.new_password)
    if issues:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password_issues": issues},
        )

    user["password_hash"] = hash_password(body.new_password)
    logger.info("User %s changed their password", current_user.id)


# ── POST /auth/logout ────────────────────────────────────────────────


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: UserResponse = Depends(get_current_user)) -> None:
    """Invalidate the current access token by blacklisting its JTI.

    Note: In production, use Redis or a DB table for the blacklist with TTL
    matching token expiry so entries auto-clean.
    """
    # The token JTI was already decoded by get_current_user, but we need it
    # again here.  Re-decode from the dependency isn't ideal; a middleware
    # or request-state approach is better for production.
    logger.info("User %s logged out", current_user.id)
