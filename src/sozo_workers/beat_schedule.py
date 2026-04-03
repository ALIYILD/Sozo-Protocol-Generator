"""Celery Beat periodic task schedule."""
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # Daily at 02:00 UTC — check for stale evidence
    "evidence-staleness-check-daily": {
        "task": "sozo_workers.tasks.evidence_tasks.check_evidence_staleness",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "sozo_maintenance"},
    },
    # Weekly on Sunday at 03:00 UTC — full evidence refresh
    "evidence-full-refresh-weekly": {
        "task": "sozo_workers.tasks.evidence_tasks.scheduled_evidence_refresh",
        "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),
        "options": {"queue": "sozo_maintenance"},
    },
    # Hourly — clean up stale active task entries
    "active-task-cleanup-hourly": {
        "task": "sozo_workers.tasks.evidence_tasks.check_evidence_staleness",
        "schedule": crontab(minute=30),
        "options": {"queue": "sozo_maintenance"},
        "kwargs": {},
    },
}
