"""Tests for the unified LangGraph builder and initial state."""
from __future__ import annotations

import pytest

from sozo_graph.unified_graph import (
    GRAPH_VERSION,
    build_unified_graph,
    create_initial_state,
)


# ── build_unified_graph ──────────────────────────────────────────────────


class TestBuildUnifiedGraph:
    def test_returns_compiled_graph(self):
        try:
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()
        except ImportError:
            checkpointer = None
        graph = build_unified_graph(checkpointer=checkpointer)
        assert graph is not None

    def test_graph_has_expected_node_count(self):
        try:
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()
        except ImportError:
            checkpointer = None
        graph = build_unified_graph(checkpointer=checkpointer)
        # The graph should have 13 nodes
        # (intake_router, condition_resolver, evidence_search, evidence_gate,
        #  safety_check, contraindication_gate, personalization,
        #  protocol_composer, grounding_validator, qa_engine,
        #  clinician_review, document_renderer, audit_logger)
        # Plus __start__ and __end__ added by LangGraph
        node_names = set(graph.get_graph().nodes.keys())
        expected_nodes = {
            "intake_router",
            "condition_resolver",
            "evidence_search",
            "evidence_gate",
            "safety_check",
            "contraindication_gate",
            "personalization",
            "protocol_composer",
            "grounding_validator",
            "qa_engine",
            "clinician_review",
            "document_renderer",
            "audit_logger",
        }
        # All expected nodes should be present
        for node in expected_nodes:
            assert node in node_names, f"Missing node: {node}"

    def test_graph_has_13_custom_nodes(self):
        try:
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()
        except ImportError:
            checkpointer = None
        graph = build_unified_graph(checkpointer=checkpointer)
        node_names = set(graph.get_graph().nodes.keys())
        # Remove LangGraph internal nodes (__start__, __end__)
        custom_nodes = {n for n in node_names if not n.startswith("__")}
        assert len(custom_nodes) == 13


# ── create_initial_state ─────────────────────────────────────────────────


class TestCreateInitialState:
    def test_returns_dict(self):
        state = create_initial_state()
        assert isinstance(state, dict)

    def test_has_request_id(self):
        state = create_initial_state()
        assert "request_id" in state
        assert len(state["request_id"]) > 0

    def test_has_status_intake(self):
        state = create_initial_state()
        assert state["status"] == "intake"

    def test_has_graph_version(self):
        state = create_initial_state()
        assert state["graph_version"] == GRAPH_VERSION

    def test_source_mode_default_prompt(self):
        state = create_initial_state()
        assert state["source_mode"] == "prompt"

    def test_source_mode_upload(self):
        state = create_initial_state(source_mode="upload")
        assert state["source_mode"] == "upload"

    def test_user_prompt_set(self):
        state = create_initial_state(user_prompt="Generate tDCS protocol for depression")
        assert state["intake"]["user_prompt"] == "Generate tDCS protocol for depression"

    def test_patient_context_passed(self):
        ctx = {"patient_id": "P001", "age": 45}
        state = create_initial_state(patient_context=ctx)
        assert state["patient_context"] == ctx

    def test_empty_collections_initialized(self):
        state = create_initial_state()
        assert state["node_history"] == []
        assert state["errors"] == []
        assert state["condition"] == {}
        assert state["evidence"] == {}

    def test_review_defaults(self):
        state = create_initial_state()
        assert state["review"]["status"] == "pending"
        assert state["review"]["revision_number"] == 0

    def test_tier_default(self):
        state = create_initial_state()
        assert state["protocol"]["tier"] == "fellow"

    def test_tier_custom(self):
        state = create_initial_state(tier="partners")
        assert state["protocol"]["tier"] == "partners"
