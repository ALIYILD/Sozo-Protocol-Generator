"""JWT token creation and decoding using PyJWT."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from sozo_auth.config import auth_config
from sozo_auth.models import TokenPair, TokenPayload


def create_access_token(user_id: str, role: str) -> str:
    """Create a short-lived access JWT."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "exp": now + timedelta(minutes=auth_config.access_token_expire_minutes),
        "iat": now,
        "jti": uuid.uuid4().hex,
        "type": "access",
    }
    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh JWT (no role — forces re-lookup on refresh)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "exp": now + timedelta(days=auth_config.refresh_token_expire_days),
        "iat": now,
        "jti": uuid.uuid4().hex,
        "type": "refresh",
    }
    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)


def create_token_pair(user_id: str, role: str) -> TokenPair:
    """Return a paired access + refresh token."""
    return TokenPair(
        access_token=create_access_token(user_id, role),
        refresh_token=create_refresh_token(user_id),
    )


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT, returning its payload.

    Raises ``jwt.ExpiredSignatureError`` if the token has expired and
    ``jwt.InvalidTokenError`` for any other validation failure.
    """
    raw = jwt.decode(
        token,
        auth_config.secret_key,
        algorithms=[auth_config.algorithm],
    )
    return TokenPayload(
        sub=raw["sub"],
        role=raw.get("role", "readonly"),
        exp=datetime.fromtimestamp(raw["exp"], tz=timezone.utc),
        iat=datetime.fromtimestamp(raw["iat"], tz=timezone.utc) if "iat" in raw else None,
        jti=raw.get("jti"),
    )
