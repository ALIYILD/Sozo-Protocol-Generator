"""Role-based access control: permissions, role mappings, and FastAPI dependency."""
from __future__ import annotations

from enum import Enum
from typing import Callable

from fastapi import Depends, HTTPException, status

from sozo_auth.models import UserResponse


class Permission(str, Enum):
    """Fine-grained permissions used across SOZO endpoints."""

    VIEW_PROTOCOLS = "view_protocols"
    CREATE_PROTOCOLS = "create_protocols"
    REVIEW_PROTOCOLS = "review_protocols"
    APPROVE_PROTOCOLS = "approve_protocols"
    MANAGE_PATIENTS = "manage_patients"
    VIEW_AUDIT = "view_audit"
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"


# Which permissions each role grants.
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "readonly": {
        Permission.VIEW_PROTOCOLS,
    },
    "clinician": {
        Permission.VIEW_PROTOCOLS,
        Permission.CREATE_PROTOCOLS,
        Permission.MANAGE_PATIENTS,
    },
    "reviewer": {
        Permission.VIEW_PROTOCOLS,
        Permission.CREATE_PROTOCOLS,
        Permission.MANAGE_PATIENTS,
        Permission.REVIEW_PROTOCOLS,
        Permission.APPROVE_PROTOCOLS,
    },
    "admin": {
        Permission.VIEW_PROTOCOLS,
        Permission.CREATE_PROTOCOLS,
        Permission.REVIEW_PROTOCOLS,
        Permission.APPROVE_PROTOCOLS,
        Permission.MANAGE_PATIENTS,
        Permission.VIEW_AUDIT,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SYSTEM,
    },
    "operator": {
        Permission.VIEW_PROTOCOLS,
        Permission.VIEW_AUDIT,
        Permission.MANAGE_SYSTEM,
    },
}


def has_permission(role: str, permission: Permission) -> bool:
    """Return ``True`` if *role* is granted *permission*."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(permission: Permission) -> Callable:
    """FastAPI dependency factory that checks whether the current user has *permission*.

    Usage::

        @router.get("/admin/audit", dependencies=[Depends(require_permission(Permission.VIEW_AUDIT))])
        async def audit_log(): ...
    """
    from sozo_auth.dependencies import get_current_user  # deferred to avoid circular import

    async def _check(user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if not has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required",
            )
        return user

    return _check
