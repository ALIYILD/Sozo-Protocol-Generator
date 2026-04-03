"""Celery configuration backed by pydantic-settings."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class CeleryConfig(BaseSettings):
    """Celery worker configuration.

    All values can be overridden via environment variables prefixed with
    ``SOZO_CELERY_`` (e.g. ``SOZO_CELERY_BROKER_URL``).
    """

    model_config = SettingsConfigDict(
        env_prefix="SOZO_CELERY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: list[str] = ["json"]
    timezone: str = "UTC"
    task_track_started: bool = True
    task_time_limit: int = 600  # 10 minutes hard limit
    task_soft_time_limit: int = 540  # 9 minutes soft limit
    worker_prefetch_multiplier: int = 1  # fair scheduling
    task_acks_late: bool = True  # ack after completion (crash safety)
    worker_max_tasks_per_child: int = 50  # recycle workers to prevent memory leaks
    task_reject_on_worker_lost: bool = True  # requeue if worker dies
    task_default_queue: str = "sozo_default"
    task_default_routing_key: str = "sozo.default"
