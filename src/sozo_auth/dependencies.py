"""FastAPI dependencies for extracting and validating the current user."""
from __future__ import annotations

from typing import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sozo_auth.models import UserResponse
from sozo_auth.tokens import decode_token

_bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UserResponse:
    """Extract and validate the JWT from the ``Authorization: Bearer <token>`` header.

    Returns a ``UserResponse`` populated from the token payload.  In a full
    deployment this would look up the user in the database; for now we
    synthesise a minimal ``UserResponse`` from the token claims so that
    downstream dependencies (role checks, permission checks) work immediately.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Replace with a real DB lookup using payload.sub as user_id.
    return UserResponse(
        id=payload.sub,
        email=f"{payload.sub}@sozo.local",  # placeholder until DB lookup
        name=payload.sub,
        role=payload.role,
        active=True,
        created_at=payload.iat or payload.exp,
    )


def require_role(*roles: str) -> Callable:
    """Return a FastAPI dependency that restricts access to the given *roles*.

    Usage::

        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_panel(): ...
    """

    async def _check_role(
        user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not authorised. Required: {', '.join(roles)}",
            )
        return user

    return _check_role


# Pre-built role dependencies for common access levels.
require_clinician = require_role("clinician", "reviewer", "admin")
require_reviewer = require_role("reviewer", "admin")
require_admin = require_role("admin")
