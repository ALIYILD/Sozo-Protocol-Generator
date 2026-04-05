"""Instrumentation helper for graph nodes.

Wraps every node function to log entry+exit+duration AND persist node
progress to the graph_runs DB row keyed by the current thread_id. This
is the only way callers of /api/graph/status/{thread_id} can see what's
happening inside long-running nodes like evidence_search / LLM synthesis
before the LangGraph checkpointer writes its next sparse checkpoint.

Design notes
------------
* Node functions are invoked synchronously by LangGraph inside the
  Celery worker (``graph.invoke``). There is no running event loop at
  that point, so we follow the existing pattern in
  ``sozo_api.tasks.graph_generate`` and use ``asyncio.run`` to drive a
  short-lived async SQLAlchemy session for the progress writes. If an
  event loop IS already running (e.g. tests invoking nodes from async
  code) we silently skip the DB write rather than crashing the node.
* We reuse ``GraphRun.node_history`` and ``GraphRun.status`` — no
  schema changes. Each decorator invocation appends a lightweight entry
  (running → success/failed) to ``node_history`` and leaves the
  coarser ``status`` column alone (the Celery task and final persist
  own that column's lifecycle: queued → running → error/complete).
* The decorator is a no-op on the node's return value: whatever the
  wrapped function returns is what LangGraph sees.
* Any DB / logging failure inside the instrumentation is swallowed —
  observability must never break the pipeline.
"""
from __future__ import annotations

import asyncio
import logging
import time
import traceback
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)


def _get_thread_id(state: Any) -> str | None:
    """Extract thread_id from a graph state (dict or object)."""
    if state is None:
        return None
    try:
        if isinstance(state, dict):
            tid = state.get("request_id") or state.get("thread_id")
        else:
            tid = getattr(state, "request_id", None) or getattr(state, "thread_id", None)
        if tid:
            return str(tid)
    except Exception:  # pragma: no cover
        return None
    return None


def _append_node_history(thread_id: str, entry: dict) -> None:
    """Append an entry to GraphRun.node_history for the given thread.

    Best-effort: any failure is logged at debug and suppressed so
    observability never breaks the pipeline.
    """
    if not thread_id:
        return

    async def _run() -> None:
        from sozo_db.engine import get_session_factory
        from sozo_db.repositories.graph_run_repo import GraphRunRepository

        factory = get_session_factory()
        async with factory() as session:
            repo = GraphRunRepository(session)
            run = await repo.get_by_thread_id(thread_id)
            if run is None:
                return
            history = list(run.node_history or [])
            history.append(entry)
            run.node_history = history
            await session.flush()
            await session.commit()

    try:
        # If a loop is already running in this thread, skip — we cannot
        # safely drive another one from sync context, and the Celery
        # worker path does NOT have a running loop here.
        try:
            asyncio.get_running_loop()
            logger.debug(
                "node_tracker: running loop detected, skipping DB write for %s",
                thread_id,
            )
            return
        except RuntimeError:
            pass
        asyncio.run(_run())
    except Exception as exc:  # pragma: no cover — best-effort
        logger.debug(
            "node_tracker: DB write skipped for thread=%s: %s",
            thread_id,
            exc,
        )


def node_tracker(node_name: str) -> Callable:
    """Decorator: log + persist node progress for a LangGraph node.

    Usage::

        @node_tracker("evidence_search")
        def evidence_search_node(state: SozoGraphState) -> dict:
            ...

    Applied ON TOP of any other decorator (e.g. ``@audited_node``).
    The decorator is signature-preserving and returns the wrapped
    function's exact return value on success; on failure it re-raises
    the original exception after recording it.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: Any, *args: Any, **kwargs: Any) -> Any:
            start = time.monotonic()
            started_at = datetime.now(timezone.utc).isoformat()
            thread_id = _get_thread_id(state) or ""

            logger.info(
                "[graph_node] %s ENTRY thread=%s", node_name, thread_id,
            )
            _append_node_history(
                thread_id,
                {
                    "node_name": node_name,
                    "status": "running",
                    "started_at": started_at,
                    "source": "node_tracker",
                },
            )

            try:
                result = func(state, *args, **kwargs)
            except Exception as exc:
                duration_ms = round((time.monotonic() - start) * 1000, 2)
                completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(
                    "[graph_node] %s FAILED thread=%s duration_ms=%s error=%s\n%s",
                    node_name,
                    thread_id,
                    duration_ms,
                    exc,
                    traceback.format_exc(),
                )
                _append_node_history(
                    thread_id,
                    {
                        "node_name": node_name,
                        "status": "failed",
                        "started_at": started_at,
                        "completed_at": completed_at,
                        "duration_ms": duration_ms,
                        "error": str(exc)[:500],
                        "source": "node_tracker",
                    },
                )
                raise

            duration_ms = round((time.monotonic() - start) * 1000, 2)
            completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(
                "[graph_node] %s EXIT thread=%s duration_ms=%s",
                node_name,
                thread_id,
                duration_ms,
            )
            _append_node_history(
                thread_id,
                {
                    "node_name": node_name,
                    "status": "success",
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_ms": duration_ms,
                    "source": "node_tracker",
                },
            )
            return result

        return wrapper

    return decorator
