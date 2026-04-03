"""Auth-specific Pydantic models for request/response validation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for creating a new user account."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1)
    role: str = Field(default="clinician", pattern=r"^(readonly|clinician|reviewer|admin|operator)$")


class UserResponse(BaseModel):
    """Public user representation — never includes password hash."""

    id: str
    email: str
    name: str
    role: str
    active: bool = True
    created_at: datetime


class TokenPair(BaseModel):
    """Access + refresh token pair returned on login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: str  # user_id
    role: str
    exp: datetime
    iat: Optional[datetime] = None
    jti: Optional[str] = None


class PasswordChange(BaseModel):
    """Payload for changing a password."""

    current_password: str
    new_password: str


class LoginRequest(BaseModel):
    """Payload for the login endpoint."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload for the token refresh endpoint."""

    refresh_token: str
