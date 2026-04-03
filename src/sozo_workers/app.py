"""Celery application instance for Sozo workers."""
from __future__ import annotations

from celery import Celery

from .config import CeleryConfig

config = CeleryConfig()

celery_app = Celery("sozo")

# Apply all config values as a flat dict — Celery reads them as top-level attrs.
celery_app.conf.update(
    broker_url=config.broker_url,
    result_backend=config.result_backend,
    task_serializer=config.task_serializer,
    result_serializer=config.result_serializer,
    accept_content=config.accept_content,
    timezone=config.timezone,
    task_track_started=config.task_track_started,
    task_time_limit=config.task_time_limit,
    task_soft_time_limit=config.task_soft_time_limit,
    worker_prefetch_multiplier=config.worker_prefetch_multiplier,
    task_acks_late=config.task_acks_late,
    worker_max_tasks_per_child=config.worker_max_tasks_per_child,
    task_reject_on_worker_lost=config.task_reject_on_worker_lost,
    task_default_queue=config.task_default_queue,
    task_default_routing_key=config.task_default_routing_key,
)

# Auto-discover task modules
celery_app.autodiscover_tasks([
    "sozo_workers.tasks",
])

# Import beat schedule so periodic tasks are registered
from .beat_schedule import CELERYBEAT_SCHEDULE  # noqa: E402

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
