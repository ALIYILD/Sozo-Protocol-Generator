"""Task status tracking via Redis — provides polling endpoint data for the API."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis

logger = logging.getLogger(__name__)

_DEFAULT_STATUS_TTL = 86400  # 24 hours
_ACTIVE_TASKS_KEY = "sozo:tasks:active"


class TaskStatusTracker:
    """Track task status in Redis for API polling.

    Uses a dedicated Redis DB (default /2) separate from Celery broker/backend
    to avoid key collisions.

    Status lifecycle:  PENDING -> STARTED -> PROGRESS -> SUCCESS | FAILURE | REVOKED
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/2", ttl: int = _DEFAULT_STATUS_TTL):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl

    def _task_key(self, task_id: str) -> str:
        return f"sozo:task:{task_id}"

    def set_status(
        self,
        task_id: str,
        status: str,
        progress: float = 0.0,
        message: str = "",
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Update task status in Redis.

        Args:
            task_id: Celery task ID.
            status: One of PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, REVOKED.
            progress: 0.0-1.0 completion fraction.
            message: Human-readable status message.
            metadata: Arbitrary JSON-serializable data (output paths, build_id, etc.).
            user_id: Owner of the task (for filtering).
        """
        key = self._task_key(task_id)
        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message,
            "metadata": json.dumps(metadata or {}),
            "updated_at": now,
        }

        if user_id:
            payload["user_id"] = user_id

        # Only set created_at on first write
        existing = self.redis.hget(key, "created_at")
        if not existing:
            payload["created_at"] = now

        pipe = self.redis.pipeline()
        pipe.hset(key, mapping=payload)
        pipe.expire(key, self.ttl)

        # Track in active set if not terminal
        if status in ("PENDING", "STARTED", "PROGRESS"):
            score = datetime.now(timezone.utc).timestamp()
            pipe.zadd(_ACTIVE_TASKS_KEY, {task_id: score})
        else:
            pipe.zrem(_ACTIVE_TASKS_KEY, task_id)

        pipe.execute()

    def get_status(self, task_id: str) -> Optional[dict]:
        """Retrieve current status for a task.

        Returns:
            Status dict or None if task not found.
        """
        key = self._task_key(task_id)
        data = self.redis.hgetall(key)
        if not data:
            return None

        data["progress"] = float(data.get("progress", 0))
        data["metadata"] = json.loads(data.get("metadata", "{}"))
        return data

    def list_active_tasks(self, user_id: Optional[str] = None) -> list[dict]:
        """List all currently active (non-terminal) tasks.

        Args:
            user_id: If provided, filter to tasks owned by this user.

        Returns:
            List of status dicts, newest first.
        """
        task_ids = self.redis.zrevrange(_ACTIVE_TASKS_KEY, 0, -1)
        results = []

        pipe = self.redis.pipeline()
        for tid in task_ids:
            pipe.hgetall(self._task_key(tid))
        raw_results = pipe.execute()

        for data in raw_results:
            if not data:
                continue
            if user_id and data.get("user_id") != user_id:
                continue
            data["progress"] = float(data.get("progress", 0))
            data["metadata"] = json.loads(data.get("metadata", "{}"))
            results.append(data)

        return results

    def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """Remove tasks from the active set that have been stuck for too long.

        Returns:
            Number of stale tasks cleaned up.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - max_age_seconds
        stale_ids = self.redis.zrangebyscore(_ACTIVE_TASKS_KEY, "-inf", cutoff)

        if not stale_ids:
            return 0

        pipe = self.redis.pipeline()
        for tid in stale_ids:
            pipe.zrem(_ACTIVE_TASKS_KEY, tid)
            # Mark them as failed
            key = self._task_key(tid)
            pipe.hset(key, mapping={
                "status": "FAILURE",
                "message": "Task timed out (stale cleanup)",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
        pipe.execute()

        logger.warning("Cleaned up %d stale active tasks", len(stale_ids))
        return len(stale_ids)
