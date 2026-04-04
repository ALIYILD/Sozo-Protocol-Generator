"""CORS settings derived from environment (production-safe defaults)."""
from __future__ import annotations

import os

from sozo_auth.runtime import is_production_like_deployment

_DEFAULT_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


def resolve_cors_allow_origins_and_credentials() -> tuple[list[str], bool]:
    """Return ``(allow_origins, allow_credentials)`` for ``CORSMiddleware``.

    * ``SOZO_CORS_ORIGINS`` — comma-separated explicit origins. If a single
      entry is ``*``, credentials are disabled (browser-safe).
    * Production-like deployments must set ``SOZO_CORS_ORIGINS`` explicitly.
    * Development defaults allow common local frontend ports with credentials.
    """
    raw = os.environ.get("SOZO_CORS_ORIGINS", "").strip()

    if not raw:
        if is_production_like_deployment():
            raise RuntimeError(
                "SOZO_CORS_ORIGINS must be set to a comma-separated list of "
                "allowed origins when SOZO_ENV or ENVIRONMENT is production, "
                "prod, staging, or stg"
            )
        return (list(_DEFAULT_DEV_ORIGINS), True)

    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        raise RuntimeError("SOZO_CORS_ORIGINS is set but lists no valid origins")

    if any(o == "*" for o in origins):
        if len(origins) > 1:
            raise RuntimeError(
                "SOZO_CORS_ORIGINS cannot combine '*' with other origin entries"
            )
        return (["*"], False)

    return (origins, True)
