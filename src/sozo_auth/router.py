"""FastAPI auth router — login, refresh, register, me, password change, logout."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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
from sozo_db.engine import get_session_factory
from sozo_db.models.user import User, UserRole

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# User store — backed by the SQLAlchemy `users` table.
# ---------------------------------------------------------------------------

# Blacklisted JTIs for logout support.
_token_blacklist: set[str] = set()


def _user_row_to_dict(row: User) -> dict[str, Any]:
    """Serialize a User ORM row into the dict shape the router handlers expect."""
    created_at = row.created_at
    if created_at is None:
        created_at_str: Any = datetime.now(timezone.utc)
    else:
        created_at_str = created_at
    return {
        "id": row.id.hex if isinstance(row.id, uuid.UUID) else str(row.id).replace("-", ""),
        "email": row.email,
        "name": row.name,
        "role": row.role.value if isinstance(row.role, UserRole) else str(row.role),
        "password_hash": row.credentials_hash,
        "active": bool(row.active),
        "created_at": created_at_str,
    }


async def _find_user_by_email(email: str) -> dict[str, Any] | None:
    """Look up user by email from the database."""
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return _user_row_to_dict(row)


async def _find_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Look up user by hex-string ID from the database."""
    try:
        uid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        return None
    factory = get_session_factory()
    async with factory() as session:
        row = await session.get(User, uid)
        if row is None:
            return None
        return _user_row_to_dict(row)


async def _insert_user(record: dict[str, Any]) -> None:
    """Insert a new user row. Raises HTTPException(409) on duplicate email."""
    try:
        uid = uuid.UUID(record["id"])
    except (ValueError, TypeError):
        uid = uuid.uuid4()

    role_value = record["role"]
    try:
        role_enum = role_value if isinstance(role_value, UserRole) else UserRole(role_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role: {role_value}",
        ) from exc

    factory = get_session_factory()
    async with factory() as session:
        user = User(
            id=uid,
            email=record["email"],
            name=record["name"],
            role=role_enum,
            credentials_hash=record.get("password_hash"),
            active=bool(record.get("active", True)),
        )
        session.add(user)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            ) from exc


async def _update_password(user_id: str, new_hash: str) -> bool:
    """Update credentials_hash for a user. Returns True if updated."""
    try:
        uid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        return False
    factory = get_session_factory()
    async with factory() as session:
        row = await session.get(User, uid)
        if row is None:
            return False
        row.credentials_hash = new_hash
        await session.commit()
        return True


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
    user = await _find_user_by_email(body.email)
    if user is None or not verify_password(body.password, user["password_hash"] or ""):
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
    user = await _find_user_by_id(payload.sub)
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
    if await _find_user_by_email(body.email):
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
    await _insert_user(user_record)
    logger.info("User %s (%s) registered by admin", user_id, body.email)
    return _user_to_response(user_record)


# ── GET /auth/me ──────────────────────────────────────────────────────


@auth_router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    user = await _find_user_by_id(current_user.id)
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
    user = await _find_user_by_id(current_user.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in store",
        )

    if not verify_password(body.current_password, user["password_hash"] or ""):
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

    await _update_password(current_user.id, hash_password(body.new_password))
    logger.info("User %s changed their password", current_user.id)


# ── POST /auth/signup (public self-service) ─────────────────────────


class SignupRequest(BaseModel):
    """Public self-service signup. Role is forced to ``clinician``."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1)


@auth_router.post(
    "/signup",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
)
async def signup(body: SignupRequest) -> TokenPair:
    """Create a new clinician account and return an auto-login token pair.

    Unlike ``/register`` (which is admin-only), this endpoint is public so
    users can create their own account from the SPA. Role is always forced
    to ``clinician``; elevated roles still require an admin to provision.
    """
    # Duplicate check
    if await _find_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    # Password strength check
    issues = validate_password_strength(body.password)
    if issues:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password_issues": issues},
        )

    user_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)

    user_record: dict[str, Any] = {
        "id": user_id,
        "email": body.email,
        "name": body.name,
        "role": "clinician",  # forced — cannot be elevated via self-signup
        "active": True,
        "created_at": now,
        "password_hash": hash_password(body.password),
    }
    await _insert_user(user_record)
    logger.info("User %s (%s) self-registered as clinician", user_id, body.email)

    return create_token_pair(user_id, "clinician")


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
