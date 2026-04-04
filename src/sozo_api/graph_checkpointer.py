"""Process-wide LangGraph checkpointer for the FastAPI app.

Default: SQLite on disk (``outputs/langgraph_checkpoints.db``) so review interrupts
survive process restarts. Override with environment variables (see below).

Tests should set ``SOZO_GRAPH_CHECKPOINTER=memory`` (see ``tests/conftest.py``).
"""
from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CHECKPOINTER: Any = None


def reset_graph_checkpointer() -> None:
    """Clear singleton (e.g. between tests). Next ``get_graph_checkpointer()`` rebuilds."""
    global _CHECKPOINTER
    _CHECKPOINTER = None


def get_graph_checkpointer() -> Any:
    """Return the shared checkpointer for this process."""
    global _CHECKPOINTER
    if _CHECKPOINTER is not None:
        return _CHECKPOINTER

    mode = os.environ.get("SOZO_GRAPH_CHECKPOINTER", "sqlite").strip().lower()

    if mode == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        _CHECKPOINTER = MemorySaver()
        logger.info("LangGraph checkpointer: MemorySaver")
        return _CHECKPOINTER

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        logger.warning(
            "langgraph.checkpoint.sqlite unavailable; install langgraph-checkpoint-sqlite. "
            "Using MemorySaver.",
        )
        from langgraph.checkpoint.memory import MemorySaver

        _CHECKPOINTER = MemorySaver()
        return _CHECKPOINTER

    raw = os.environ.get("SOZO_GRAPH_CHECKPOINT_SQLITE", "").strip()
    if raw:
        path = Path(raw)
    else:
        base = Path(os.environ.get("SOZO_OUTPUT_DIR", "outputs"))
        path = base / "langgraph_checkpoints.db"
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), check_same_thread=False)
    _CHECKPOINTER = SqliteSaver(conn)
    try:
        _CHECKPOINTER.setup()
    except Exception as exc:
        logger.warning("SqliteSaver.setup: %s", exc)

    logger.info("LangGraph checkpointer: SqliteSaver (%s)", path)
    return _CHECKPOINTER
