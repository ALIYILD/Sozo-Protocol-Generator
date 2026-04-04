"""Deployment profile helpers for auth and API hardening."""
from __future__ import annotations

import os


def is_production_like_deployment() -> bool:
    """True when SOZO_ENV / ENVIRONMENT marks a deployed (non-local) profile.

    Default when unset is ``development`` (relaxed JWT/CORS defaults).
    """
    v = (
        os.environ.get("SOZO_ENV") or os.environ.get("ENVIRONMENT") or "development"
    ).strip().lower()
    return v in ("production", "prod", "staging", "stg")
