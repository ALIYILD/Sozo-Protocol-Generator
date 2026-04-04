"""Tests for API LangGraph checkpointer factory."""
from __future__ import annotations

import os

import pytest


def test_memory_mode_when_env_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    from sozo_api import graph_checkpointer as gc

    monkeypatch.setenv("SOZO_GRAPH_CHECKPOINTER", "memory")
    gc.reset_graph_checkpointer()
    cp = gc.get_graph_checkpointer()
    assert type(cp).__name__ in ("MemorySaver", "InMemorySaver")
    gc.reset_graph_checkpointer()


def test_sqlite_mode_uses_sqlite_saver(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from sozo_api import graph_checkpointer as gc

    db = tmp_path / "ckpt.db"
    monkeypatch.setenv("SOZO_GRAPH_CHECKPOINTER", "sqlite")
    monkeypatch.setenv("SOZO_GRAPH_CHECKPOINT_SQLITE", str(db))
    gc.reset_graph_checkpointer()
    cp = gc.get_graph_checkpointer()
    assert type(cp).__name__ == "SqliteSaver"
    gc.reset_graph_checkpointer()
