"""Regression: unified graph intake, API-shaped initial state, and condition precedence."""
from __future__ import annotations

import pytest

from sozo_graph.unified_graph import create_initial_state, condition_resolver_node


class TestCreateInitialStateStructuredIntake:
    """HTTP-shaped payloads must land in ``intake`` structurally, not only in prompt text."""

    def test_condition_slug_and_normalized_request_seed_intake(self):
        state = create_initial_state(
            user_prompt="Protocol",
            condition_slug="parkinsons",
            normalized_request={
                "condition_slug": "parkinsons",
                "doc_type": "evidence_based_protocol",
                "modality": "tdcs",
            },
        )
        assert state["intake"]["condition_slug"] == "parkinsons"
        assert state["intake"]["user_prompt"] == "Protocol"
        assert state["intake"]["normalized_request"]["condition_slug"] == "parkinsons"
        assert (
            state["intake"]["normalized_request"]["doc_type"]
            == "evidence_based_protocol"
        )
        assert state["intake"]["normalized_request"]["modality"] == "tdcs"

    def test_explicit_param_overwrites_normalized_request_slug(self):
        state = create_initial_state(
            user_prompt="x",
            condition_slug="parkinsons",
            normalized_request={"condition_slug": "depression"},
        )
        assert state["intake"]["condition_slug"] == "parkinsons"
        assert state["intake"]["normalized_request"]["condition_slug"] == "parkinsons"

    def test_prompt_only_backward_compatible(self):
        state = create_initial_state(
            user_prompt="tDCS evidence-based protocol for major depression",
        )
        assert state["intake"].get("condition_slug") is None
        assert "normalized_request" not in state["intake"]


class TestUnifiedConditionResolverPrecedence:
    def test_explicit_slug_over_ambiguous_prompt(self):
        state = {
            "intake": {
                "condition_slug": "parkinsons",
                "user_prompt": "clinical neuromodulation protocol details only",
            },
            "condition": {},
        }
        out = condition_resolver_node(state)
        cond = out["condition"]
        assert cond.get("condition_valid") is True
        assert cond.get("slug") == "parkinsons"
        assert cond.get("resolution_source") == "explicit_intake"

    def test_structured_conflict_flags_review_fields(self):
        state = {
            "intake": {
                "condition_slug": "depression",
                "user_prompt": (
                    "Prepare an evidence-based Parkinson's disease motor protocol"
                ),
            },
            "condition": {},
        }
        out = condition_resolver_node(state)
        cond = out["condition"]
        assert cond.get("condition_valid") is True
        assert cond.get("slug") == "depression"
        assert cond.get("intake_conflict") is True
        assert cond.get("intake_conflict_note")
        assert "parkinsons" in cond["intake_conflict_note"].lower()
        assert any(
            "condition_intake_conflict" in w for w in out["intake"]["parse_warnings"]
        )

    def test_prompt_inference_when_no_structured_slug(self):
        state = {
            "intake": {
                "user_prompt": "tDCS protocol for major depression with left DLPFC target",
            },
            "condition": {},
        }
        out = condition_resolver_node(state)
        cond = out["condition"]
        assert cond.get("condition_valid") is True
        assert cond.get("slug") == "depression"
        assert cond.get("resolution_source") == "prompt_inferred"


class TestMVPConditionResolverPrecedence:
    def test_explicit_intake_beats_normalized_request(self):
        from sozo_graph.nodes.condition_resolver import condition_resolver

        state = {
            "intake": {
                "condition_slug": "parkinsons",
                "normalized_request": {"condition_slug": "depression"},
            },
            "condition": {},
        }
        result = condition_resolver(state)
        assert result["condition"]["slug"] == "parkinsons"
        assert result["condition"]["resolution_source"] == "explicit_intake"
        assert any(
            "intake_condition_slug_mismatch" in w
            for w in result["intake"]["parse_warnings"]
        )
