"""Ensure graph nodes preserve output.protocol_id through render paths."""
from __future__ import annotations

import pytest

pytest.importorskip("langgraph")


def test_document_renderer_preserves_protocol_id(monkeypatch):
    from sozo_graph import unified_graph

    def fake_render(*_a, **_kw):
        return {"output_paths": {"json": "/tmp/x.json"}, "output_formats": ["json"]}

    monkeypatch.setattr(unified_graph.integration, "render_output", fake_render)

    state = {
        "request_id": "tid",
        "version": "1.0",
        "condition": {"slug": "demo"},
        "protocol": {"composed_sections": []},
        "evidence": {},
        "review": {},
        "output": {"protocol_id": "550e8400-e29b-41d4-a716-446655440000"},
    }
    out = unified_graph.document_renderer_node(state)
    assert out["output"]["protocol_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert out["output"]["output_paths"]["json"] == "/tmp/x.json"

