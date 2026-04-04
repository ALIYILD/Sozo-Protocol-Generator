"""Process-wide LangGraph checkpointer for the FastAPI app.

Default: SQLite on disk (``outputs/langgraph_checkpoints.db``) so review interrupts
survive process restarts. Override with environment variables (see below).

- ``memory`` — ephemeral in-process saver (tests default this in ``conftest.py``).
- ``sqlite`` — file-backed ``SqliteSaver`` (default in production single-node).
- ``postgres`` — shared ``PostgresSaver`` via ``psycopg_pool`` for multi-worker /
  multi-instance (install optional deps: ``pip install '.[postgres-checkpoint]'``).

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
_POSTGRES_POOL: Any = None


def reset_graph_checkpointer() -> None:
    """Clear singleton (e.g. between tests). Next ``get_graph_checkpointer()`` rebuilds."""
    global _CHECKPOINTER, _POSTGRES_POOL
    if _POSTGRES_POOL is not None:
        try:
            _POSTGRES_POOL.close(timeout=10.0)
        except TypeError:
            # Older psycopg_pool without timeout=
            _POSTGRES_POOL.close()
        except Exception as exc:
            logger.debug("Graph checkpointer pool close: %s", exc)
        _POSTGRES_POOL = None
    _CHECKPOINTER = None


def _sync_psycopg_conninfo(url: str) -> str:
    """Normalize async SQLAlchemy / Heroku URLs to a psycopg connection string."""
    u = url.strip()
    if u.startswith("postgresql+asyncpg://"):
        return "postgresql://" + u.split("postgresql+asyncpg://", 1)[1]
    if u.startswith("postgres://"):
        return "postgresql://" + u.split("postgres://", 1)[1]
    return u


def _checkpoint_sqlite_path() -> Path:
    raw = os.environ.get("SOZO_GRAPH_CHECKPOINT_SQLITE", "").strip()
    if raw:
        return Path(raw)
    base = Path(os.environ.get("SOZO_OUTPUT_DIR", "outputs"))
    return base / "langgraph_checkpoints.db"


def _make_sqlite_checkpointer() -> Any:
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        logger.warning(
            "langgraph.checkpoint.sqlite unavailable; install langgraph-checkpoint-sqlite. "
            "Using MemorySaver.",
        )
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()

    path = _checkpoint_sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), check_same_thread=False)
    saver = SqliteSaver(conn)
    try:
        saver.setup()
    except Exception as exc:
        logger.warning("SqliteSaver.setup: %s", exc)

    logger.info("LangGraph checkpointer: SqliteSaver (%s)", path)
    return saver


def _make_memory_checkpointer() -> Any:
    from langgraph.checkpoint.memory import MemorySaver

    saver = MemorySaver()
    logger.info("LangGraph checkpointer: MemorySaver")
    return saver


def _postgres_conninfo() -> str:
    explicit = os.environ.get("SOZO_GRAPH_CHECKPOINT_POSTGRES", "").strip()
    if explicit:
        return _sync_psycopg_conninfo(explicit)
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if db_url and "postgres" in db_url.lower():
        return _sync_psycopg_conninfo(db_url)
    return ""


def _make_postgres_checkpointer() -> Any | None:
    global _POSTGRES_POOL

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from psycopg_pool import ConnectionPool
        from psycopg.rows import dict_row
    except ImportError:
        logger.warning(
            "Postgres checkpointer requires langgraph-checkpoint-postgres and psycopg "
            "(e.g. pip install '.[postgres-checkpoint]').",
        )
        return None

    conninfo = _postgres_conninfo()
    if not conninfo:
        logger.warning(
            "SOZO_GRAPH_CHECKPOINTER=postgres but no connection string: set "
            "SOZO_GRAPH_CHECKPOINT_POSTGRES or DATABASE_URL (postgresql).",
        )
        return None

    max_size = int(os.environ.get("SOZO_GRAPH_CHECKPOINT_POOL_MAX_SIZE", "20"))
    min_size = int(os.environ.get("SOZO_GRAPH_CHECKPOINT_POOL_MIN_SIZE", "1"))
    try:
        pool = ConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            open=True,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
            },
        )
        saver = PostgresSaver(pool)
        saver.setup()
    except Exception as exc:
        logger.exception("Postgres checkpointer init failed: %s", exc)
        return None

    _POSTGRES_POOL = pool
    logger.info(
        "LangGraph checkpointer: PostgresSaver (pool min=%s max=%s)",
        min_size,
        max_size,
    )
    return saver


def get_graph_checkpointer() -> Any:
    """Return the shared checkpointer for this process."""
    global _CHECKPOINTER
    if _CHECKPOINTER is not None:
        return _CHECKPOINTER

    mode = os.environ.get("SOZO_GRAPH_CHECKPOINTER", "sqlite").strip().lower()

    if mode == "memory":
        _CHECKPOINTER = _make_memory_checkpointer()
        return _CHECKPOINTER

    if mode == "postgres":
        pg = _make_postgres_checkpointer()
        if pg is not None:
            _CHECKPOINTER = pg
            return _CHECKPOINTER
        logger.warning("Falling back to SqliteSaver after Postgres checkpointer failure.")
        _CHECKPOINTER = _make_sqlite_checkpointer()
        return _CHECKPOINTER

    _CHECKPOINTER = _make_sqlite_checkpointer()
    return _CHECKPOINTER
