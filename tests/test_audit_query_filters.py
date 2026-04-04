"""Tests for audit_service JSON-backed filters (thread_id, build_id)."""
from __future__ import annotations

import sqlite3

import pytest


@pytest.fixture
def audit_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path):
    dbpath = tmp_path / "audit_only.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{dbpath}")
    conn = sqlite3.connect(dbpath)
    conn.execute(
        """CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor_id TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            input_hash TEXT,
            output_hash TEXT,
            node_name TEXT,
            details TEXT
        )"""
    )
    conn.execute(
        "INSERT INTO audit_log (entity_type, entity_id, action, details) VALUES (?,?,?,?)",
        ("graph_run", "thread-a", "generation_started", '{"thread_id":"thread-a"}'),
    )
    conn.execute(
        "INSERT INTO audit_log (entity_type, entity_id, action, details) VALUES (?,?,?,?)",
        (
            "graph_run",
            "other",
            "graph_review_submitted",
            '{"thread_id":"thread-b","protocol_id":"p1"}',
        ),
    )
    conn.execute(
        "INSERT INTO audit_log (entity_type, entity_id, action, details) VALUES (?,?,?,?)",
        ("protocol", "prot-1", "node_executed", '{"build_id":"build-xyz"}'),
    )
    conn.commit()
    conn.close()
    return dbpath


def test_query_events_thread_id_details_and_entity_id(audit_sqlite) -> None:
    from sozo_api.routes.audit_service import AuditService

    svc = AuditService()
    ev, total = svc.query_events(thread_id="thread-b", page=1, page_size=10)
    assert total == 1
    assert ev[0]["action"] == "graph_review_submitted"

    ev2, t2 = svc.query_events(thread_id="thread-a", page=1, page_size=10)
    assert t2 == 1
    assert ev2[0]["action"] == "generation_started"


def test_query_events_build_id(audit_sqlite) -> None:
    from sozo_api.routes.audit_service import AuditService

    svc = AuditService()
    ev, total = svc.query_events(build_id="build-xyz", page=1, page_size=10)
    assert total == 1
    assert ev[0]["action"] == "node_executed"


def test_query_events_thread_and_build_combined(audit_sqlite) -> None:
    from sozo_api.routes.audit_service import AuditService

    svc = AuditService()
    ev, total = svc.query_events(
        thread_id="thread-b",
        build_id="build-xyz",
        page=1,
        page_size=10,
    )
    assert total == 0
    assert ev == []
