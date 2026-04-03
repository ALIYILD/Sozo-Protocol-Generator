"""
Sozo Workers — Celery-based background job processing for the Sozo Protocol Generator.

Provides async task execution for:
- Protocol generation (single, batch, personalized)
- Evidence pipeline refresh and staleness checks
- Document export (PDF, DOCX, visuals)
"""
from .app import celery_app

__all__ = ["celery_app"]
