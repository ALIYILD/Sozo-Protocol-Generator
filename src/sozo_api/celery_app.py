"""Celery application factory for Sozo async background work.

The broker and result backend both point at a local Redis instance that
lives inside the same container (managed by supervisord). This is used by
long-running LangGraph pipelines so the FastAPI request thread is not
blocked for minutes while a single protocol generates.

Environment variables:
    CELERY_BROKER_URL   Broker URL (default: redis://127.0.0.1:6379/0)
    CELERY_RESULT_BACKEND  Result backend URL (default: same as broker)
"""
from __future__ import annotations

import os

from celery import Celery


def _broker_url() -> str:
    return os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")


def _result_backend() -> str:
    return os.environ.get("CELERY_RESULT_BACKEND", _broker_url())


def create_celery_app() -> Celery:
    """Build and configure the Celery app instance."""
    app = Celery(
        "sozo_api",
        broker=_broker_url(),
        backend=_result_backend(),
        include=["sozo_api.tasks.graph_generate"],
    )

    app.conf.update(
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,  # long-running tasks; no prefetch
        task_track_started=True,
        # Let tasks run as long as needed — LangGraph pipelines can take
        # many minutes in the worst case. Redis broker visibility timeout
        # is raised to match so tasks don't get redelivered mid-run.
        broker_transport_options={"visibility_timeout": 60 * 60 * 6},
        result_expires=60 * 60 * 24,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )

    # Auto-discover tasks in sozo_api.tasks (package).
    app.autodiscover_tasks(["sozo_api"], related_name="tasks")
    return app


# Module-level singleton used by `celery -A sozo_api.celery_app.celery_app`
celery_app = create_celery_app()
