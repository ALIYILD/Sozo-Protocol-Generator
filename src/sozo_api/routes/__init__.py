"""SOZO API route modules.

All routers are registered in sozo_api.server.create_app().
"""
from sozo_api.routes.protocols import router as protocols_router
from sozo_api.routes.patients import router as patients_router
from sozo_api.routes.reviews import router as reviews_router
from sozo_api.routes.audit import router as audit_router

__all__ = [
    "protocols_router",
    "patients_router",
    "reviews_router",
    "audit_router",
]
