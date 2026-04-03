"""Shared SQLite database helper for all API routes.

Resolves the database path from DATABASE_URL environment variable,
handling both relative and absolute paths for local dev and Fly.io.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def get_db_path() -> str:
    """Resolve SQLite database path from DATABASE_URL.

    Handles:
      - sqlite+aiosqlite:////absolute/path  →  /absolute/path
      - sqlite+aiosqlite:///relative/path   →  relative/path (from cwd)
      - sqlite:///path                       →  path
      - empty / non-sqlite                   →  sozo_dev.db (fallback)
    """
    db_url = os.environ.get("DATABASE_URL", "")
    if "sqlite" not in db_url:
        return "sozo_dev.db"

    # Strip scheme: "sqlite+aiosqlite:///path" → "path" or "/path"
    # After split on "://", we get "sqlite+aiosqlite" and "//path" or "///path"
    if ":///" in db_url:
        raw = db_url.split(":///", 1)[-1]
        # If starts with / it's absolute (was ////)
        # Otherwise relative (was ///)
        return raw if raw else "sozo_dev.db"

    return "sozo_dev.db"


def get_db() -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and FK enforcement."""
    path = get_db_path()
    # Ensure parent directory exists
    parent = Path(path).parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
