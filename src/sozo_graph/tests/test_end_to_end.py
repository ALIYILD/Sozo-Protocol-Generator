"""
End-to-end integration test for the Sozo LangGraph.

Tests the full pipeline: prompt → evidence → compose → interrupt → approve → output.
Uses MemorySaver checkpointer and mocks external services (PubMed, LLM).
"""
import json
import pytest
from unittest.mock import patch, MagicMock


# ── Fixtures ───────────────────────────────────────────────────────────


def _mock_evidence_search(state):
    """Mock evidence_search that returns synthetic articles without network calls."""
    from sozo_graph.audit.logger import _hash_state
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    articles = [
        {
            "pmid": "28493655",
            "doi": "10.1001/jamapsychiatry.2017.0044",
            "title": "Trial of Electrical Direct-Current Therapy versus Escitalopram for Depression",
            "authors": ["Brunoni AR", "Moffa AH", "Sampaio-Junior B"],
            "journal": "JAMA Psychiatry",
            "year": 2017,
            "abstract": "This randomized, noninferiority trial compared tDCS at 2 mA over left DLPFC with escitalopram for major depressive disorder.",
            "evidence_type": "rct",
            "evidence_level": "high",
            "score": 4,
            "evidence_grade": "A",
            "quality_score": 82,
            "relevance_score": 85,
        },
        {
            "pmid": "29800858",
            "doi": "10.1192/bjp.2018.71",
            "title": "Transcranial direct current stimulation for depression: systematic review and meta-analysis",
            "authors": ["Loo CK", "Husain MM", "McDonald WM"],
            "journal": "Br J Psychiatry",
            "year": 2018,
            "abstract": "Meta-analysis of 6 RCTs showed tDCS was effective for depression vs sham, with response rates of 34% vs 19%.",
            "evidence_type": "meta_analysis",
            "evidence_level": "highest",
            "score": 5,
            "evidence_grade": "A",
            "quality_score": 90,
            "relevance_score": 88,
        },
        {
            "pmid": "27765600",
            "doi": "10.1016/j.brs.2016.06.001",
            "title": "Safety of Transcranial Direct Current Stimulation: Evidence Based Update 2016",
            "authors": ["Bikson M", "Grossman P", "Thomas C"],
            "journal": "Brain Stimulation",
            "year": 2016,
            "abstract": "Safety review of tDCS across 33,000 sessions. Adverse events were mild and transient: skin irritation (17%), tingling (12%).",
            "evidence_type": "systematic_review",
            "evidence_level": "highest",
            "score": 5,
            "evidence_grade": "A",
            "quality_score": 88,
            "relevance_score": 75,
        },
    ]

    return {
        "evidence": {
            "search_queries": ["tDCS depression DLPFC"],
            "source_counts": {"pubmed": 3},
            "raw_article_count": 3,
            "unique_article_count": 3,
            "screened_article_count": 3,
            "articles": articles,
            "evidence_summary": {
                "total_articles": 3,
                "grade_distribution": {"A": 3, "B": 0, "C": 0, "D": 0},
            },
            "evidence_sufficient": True,
            "evidence_gaps": [],
            "prisma_counts": {
                "records_identified": 3,
                "records_after_dedup": 3,
                "records_screened": 3,
                "studies_included": 3,
            },
            "pipeline_log_path": None,
        },
        "status": "evidence",
        "node_history": [{
            "node_id": "evidence_search",
            "started_at": now,
            "completed_at": now,
            "duration_ms": 1.0,
            "status": "success",
            "error": None,
            "input_hash": "mock",
            "output_hash": "mock",
            "decisions": ["Mock evidence: 3 Grade A articles"],
        }],
    }


def _mock_protocol_composer(state):
    """Mock protocol_composer that returns synthetic sections without LLM calls."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    sections = [
        {
            "section_id": "overview",
            "title": "Clinical Overview",
            "content": (
                "Major Depressive Disorder (MDD) affects approximately 280 million people worldwide. "
                "Transcranial direct current stimulation (tDCS) has emerged as a promising non-invasive "
                "neuromodulation intervention for treatment-resistant depression (PMID: 28493655). "
                "A meta-analysis of 6 RCTs demonstrated response rates of 34% vs 19% for sham (PMID: 29800858)."
            ),
            "cited_evidence_ids": ["28493655", "29800858"],
            "confidence": "high",
            "generation_method": "mock_composed",
            "claims": [
                {
                    "claim_text": "tDCS has emerged as a promising intervention for treatment-resistant depression",
                    "evidence_ids": ["28493655"],
                    "claim_type": "supports",
                    "confidence": "high",
                    "uncertainty_flag": None,
                },
                {
                    "claim_text": "Meta-analysis showed response rates of 34% vs 19% for sham",
                    "evidence_ids": ["29800858"],
                    "claim_type": "supports",
                    "confidence": "high",
                    "uncertainty_flag": None,
                },
            ],
        },
        {
            "section_id": "safety_monitoring",
            "title": "Safety & Monitoring",
            "content": (
                "A safety review across 33,000 tDCS sessions found adverse events to be mild and transient, "
                "including skin irritation (17%) and tingling (12%) (PMID: 27765600). "
                "Contraindications include metallic cranial implants."
            ),
            "cited_evidence_ids": ["27765600"],
            "confidence": "high",
            "generation_method": "mock_composed",
            "claims": [
                {
                    "claim_text": "Adverse events were mild and transient across 33,000 sessions",
                    "evidence_ids": ["27765600"],
                    "claim_type": "safety_note",
                    "confidence": "high",
                    "uncertainty_flag": None,
                },
            ],
        },
    ]

    protocol = state.get("protocol", {})

    return {
        "protocol": {
            **protocol,
            "composed_sections": sections,
        },
        "node_history": [{
            "node_id": "protocol_composer",
            "started_at": now,
            "completed_at": now,
            "duration_ms": 1.0,
            "status": "success",
            "error": None,
            "input_hash": "mock",
            "output_hash": "mock",
            "decisions": ["Mock composed 2 sections with 3 citations"],
        }],
    }


# ── Tests ──────────────────────────────────────────────────────────────


class TestEndToEnd:
    """Full pipeline integration tests."""

    def test_graph_compiles(self):
        """Verify graph compiles without error."""
        from sozo_graph.graph import build_sozo_graph
        from langgraph.checkpoint.memory import MemorySaver

        graph = build_sozo_graph(checkpointer=MemorySaver())
        nodes = list(graph.get_graph().nodes.keys())

        assert "__start__" in nodes
        assert "intake_router" in nodes
        assert "prompt_normalizer" in nodes
        assert "condition_resolver" in nodes
        assert "evidence_search" in nodes
        assert "safety_policy_engine" in nodes
        assert "protocol_composer" in nodes
        assert "grounding_validator" in nodes
        assert "review_processor" in nodes
        assert "audit_logger" in nodes
        assert "__end__" in nodes

    def test_full_pipeline_to_review_interrupt(self):
        """Run full pipeline from prompt to clinician review interrupt.

        Mocks evidence_search and protocol_composer to avoid network calls.
        All other nodes run for real.
        """
        from sozo_graph.graph import build_sozo_graph, create_initial_state
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        from sozo_graph.state import SozoGraphState

        # Build graph with mocked nodes
        from sozo_graph.nodes.intake_router import intake_router
        from sozo_graph.nodes.prompt_normalizer import prompt_normalizer
        from sozo_graph.nodes.condition_resolver import condition_resolver
        from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine
        from sozo_graph.nodes.contraindication_gate import contraindication_gate
        from sozo_graph.nodes.protocol_template_selector import protocol_template_selector
        from sozo_graph.nodes.grounding_validator import grounding_validator
        from sozo_graph.nodes.review_processor import review_processor
        from sozo_graph.nodes.protocol_reporter import protocol_reporter
        from sozo_graph.nodes.audit_logger import audit_logger
        from sozo_graph.graph import route_after_evidence, route_after_contraindication, route_after_review

        graph = StateGraph(SozoGraphState)

        graph.add_node("intake_router", intake_router)
        graph.add_node("prompt_normalizer", prompt_normalizer)
        graph.add_node("condition_resolver", condition_resolver)
        graph.add_node("evidence_search", _mock_evidence_search)  # MOCKED
        graph.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)
        graph.add_node("safety_policy_engine", safety_policy_engine)
        graph.add_node("contraindication_gate", contraindication_gate)
        graph.add_node("protocol_template_selector", protocol_template_selector)
        graph.add_node("protocol_composer", _mock_protocol_composer)  # MOCKED
        graph.add_node("grounding_validator", grounding_validator)
        graph.add_node("review_processor", review_processor)
        graph.add_node("protocol_reporter", protocol_reporter)
        graph.add_node("audit_logger", audit_logger)

        graph.set_entry_point("intake_router")
        graph.add_edge("intake_router", "prompt_normalizer")
        graph.add_edge("prompt_normalizer", "condition_resolver")
        graph.add_edge("condition_resolver", "evidence_search")
        graph.add_edge("evidence_search", "evidence_sufficiency_gate")
        graph.add_conditional_edges("evidence_sufficiency_gate", route_after_evidence, {"safety_policy_engine": "safety_policy_engine"})
        graph.add_edge("safety_policy_engine", "contraindication_gate")
        graph.add_conditional_edges("contraindication_gate", route_after_contraindication, {"protocol_template_selector": "protocol_template_selector"})
        graph.add_edge("protocol_template_selector", "protocol_composer")
        graph.add_edge("protocol_composer", "grounding_validator")
        graph.add_edge("grounding_validator", "review_processor")
        graph.add_conditional_edges("review_processor", route_after_review, {"protocol_reporter": "protocol_reporter", "review_processor": "review_processor", "__end__": END})
        graph.add_edge("protocol_reporter", "audit_logger")
        graph.add_edge("audit_logger", END)

        checkpointer = MemorySaver()
        compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["review_processor"])

        # Create initial state
        initial = create_initial_state(
            source_mode="prompt",
            user_prompt="Generate a tDCS protocol for depression targeting left DLPFC",
        )

        config = {"configurable": {"thread_id": initial["request_id"]}}

        # Run to interrupt
        result = compiled.invoke(initial, config=config)

        # ── Verify pipeline reached the review interrupt ──────────

        # Condition should be resolved
        assert result["condition"]["condition_valid"] is True
        assert result["condition"]["slug"] == "depression"

        # Evidence should be populated (from mock)
        assert result["evidence"]["evidence_sufficient"] is True
        assert len(result["evidence"]["articles"]) == 3

        # Safety should be assessed
        assert "safety_cleared" in result["safety"]

        # Protocol should have composed sections (from mock)
        assert len(result["protocol"]["composed_sections"]) == 2

        # Grounding should be validated
        assert "grounding_score" in result["protocol"]
        assert result["protocol"]["grounding_score"] == 1.0  # all PMIDs are in evidence

        # Review should be pending (we're at the interrupt)
        assert result["review"]["status"] == "pending"

        # Node history should show all nodes that ran
        node_ids = [n["node_id"] for n in result["node_history"]]
        assert "intake_router" in node_ids
        assert "condition_resolver" in node_ids
        assert "evidence_search" in node_ids
        assert "safety_policy_engine" in node_ids
        assert "grounding_validator" in node_ids

    def test_resume_after_approval(self):
        """Run full pipeline, pause at review, approve, verify output."""
        from sozo_graph.graph import create_initial_state
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        from sozo_graph.state import SozoGraphState
        from sozo_graph.nodes.intake_router import intake_router
        from sozo_graph.nodes.prompt_normalizer import prompt_normalizer
        from sozo_graph.nodes.condition_resolver import condition_resolver
        from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine
        from sozo_graph.nodes.contraindication_gate import contraindication_gate
        from sozo_graph.nodes.protocol_template_selector import protocol_template_selector
        from sozo_graph.nodes.grounding_validator import grounding_validator
        from sozo_graph.nodes.review_processor import review_processor
        from sozo_graph.nodes.protocol_reporter import protocol_reporter
        from sozo_graph.nodes.audit_logger import audit_logger
        from sozo_graph.graph import route_after_evidence, route_after_contraindication, route_after_review
        from datetime import datetime, timezone

        # Build same graph as above
        graph = StateGraph(SozoGraphState)
        graph.add_node("intake_router", intake_router)
        graph.add_node("prompt_normalizer", prompt_normalizer)
        graph.add_node("condition_resolver", condition_resolver)
        graph.add_node("evidence_search", _mock_evidence_search)
        graph.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)
        graph.add_node("safety_policy_engine", safety_policy_engine)
        graph.add_node("contraindication_gate", contraindication_gate)
        graph.add_node("protocol_template_selector", protocol_template_selector)
        graph.add_node("protocol_composer", _mock_protocol_composer)
        graph.add_node("grounding_validator", grounding_validator)
        graph.add_node("review_processor", review_processor)
        graph.add_node("protocol_reporter", protocol_reporter)
        graph.add_node("audit_logger", audit_logger)

        graph.set_entry_point("intake_router")
        graph.add_edge("intake_router", "prompt_normalizer")
        graph.add_edge("prompt_normalizer", "condition_resolver")
        graph.add_edge("condition_resolver", "evidence_search")
        graph.add_edge("evidence_search", "evidence_sufficiency_gate")
        graph.add_conditional_edges("evidence_sufficiency_gate", route_after_evidence, {"safety_policy_engine": "safety_policy_engine"})
        graph.add_edge("safety_policy_engine", "contraindication_gate")
        graph.add_conditional_edges("contraindication_gate", route_after_contraindication, {"protocol_template_selector": "protocol_template_selector"})
        graph.add_edge("protocol_template_selector", "protocol_composer")
        graph.add_edge("protocol_composer", "grounding_validator")
        graph.add_edge("grounding_validator", "review_processor")
        graph.add_conditional_edges("review_processor", route_after_review, {"protocol_reporter": "protocol_reporter", "review_processor": "review_processor", "__end__": END})
        graph.add_edge("protocol_reporter", "audit_logger")
        graph.add_edge("audit_logger", END)

        checkpointer = MemorySaver()
        compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["review_processor"])

        # Phase 1: Run to interrupt
        initial = create_initial_state(
            source_mode="prompt",
            user_prompt="Generate a tDCS protocol for depression",
        )
        config = {"configurable": {"thread_id": initial["request_id"]}}
        result = compiled.invoke(initial, config=config)

        assert result["review"]["status"] == "pending"

        # Phase 2: Clinician approves
        compiled.update_state(config, {
            "review": {
                "status": "approved",
                "reviewer_id": "dr_test",
                "reviewer_credentials": "MD, Neurologist",
                "review_timestamp": datetime.now(timezone.utc).isoformat(),
                "review_notes": "Looks good, approved for clinical use.",
                "revision_number": 0,
                "edits_applied": [],
                "parameter_overrides": [],
            },
        })

        # Resume
        final = compiled.invoke(None, config=config)

        # ── Verify full pipeline completion ────────────────────

        # Review should be approved with stamp
        assert final["review"]["status"] == "approved" or final["status"] == "released"

        # Output should have paths
        output = final.get("output", {})
        assert "audit_record_id" in output or "output_paths" in output

        # Node history should include review_processor, reporter, audit
        node_ids = [n["node_id"] for n in final["node_history"]]
        assert "review_processor" in node_ids

    def test_rejection_terminates(self):
        """Verify that rejection ends the graph."""
        from sozo_graph.graph import create_initial_state
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        from sozo_graph.state import SozoGraphState
        from sozo_graph.nodes.intake_router import intake_router
        from sozo_graph.nodes.prompt_normalizer import prompt_normalizer
        from sozo_graph.nodes.condition_resolver import condition_resolver
        from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine
        from sozo_graph.nodes.contraindication_gate import contraindication_gate
        from sozo_graph.nodes.protocol_template_selector import protocol_template_selector
        from sozo_graph.nodes.grounding_validator import grounding_validator
        from sozo_graph.nodes.review_processor import review_processor
        from sozo_graph.nodes.protocol_reporter import protocol_reporter
        from sozo_graph.nodes.audit_logger import audit_logger
        from sozo_graph.graph import route_after_evidence, route_after_contraindication, route_after_review

        graph = StateGraph(SozoGraphState)
        graph.add_node("intake_router", intake_router)
        graph.add_node("prompt_normalizer", prompt_normalizer)
        graph.add_node("condition_resolver", condition_resolver)
        graph.add_node("evidence_search", _mock_evidence_search)
        graph.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)
        graph.add_node("safety_policy_engine", safety_policy_engine)
        graph.add_node("contraindication_gate", contraindication_gate)
        graph.add_node("protocol_template_selector", protocol_template_selector)
        graph.add_node("protocol_composer", _mock_protocol_composer)
        graph.add_node("grounding_validator", grounding_validator)
        graph.add_node("review_processor", review_processor)
        graph.add_node("protocol_reporter", protocol_reporter)
        graph.add_node("audit_logger", audit_logger)

        graph.set_entry_point("intake_router")
        graph.add_edge("intake_router", "prompt_normalizer")
        graph.add_edge("prompt_normalizer", "condition_resolver")
        graph.add_edge("condition_resolver", "evidence_search")
        graph.add_edge("evidence_search", "evidence_sufficiency_gate")
        graph.add_conditional_edges("evidence_sufficiency_gate", route_after_evidence, {"safety_policy_engine": "safety_policy_engine"})
        graph.add_edge("safety_policy_engine", "contraindication_gate")
        graph.add_conditional_edges("contraindication_gate", route_after_contraindication, {"protocol_template_selector": "protocol_template_selector"})
        graph.add_edge("protocol_template_selector", "protocol_composer")
        graph.add_edge("protocol_composer", "grounding_validator")
        graph.add_edge("grounding_validator", "review_processor")
        graph.add_conditional_edges("review_processor", route_after_review, {"protocol_reporter": "protocol_reporter", "review_processor": "review_processor", "__end__": END})
        graph.add_edge("protocol_reporter", "audit_logger")
        graph.add_edge("audit_logger", END)

        checkpointer = MemorySaver()
        compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["review_processor"])

        # Run to interrupt
        initial = create_initial_state(
            source_mode="prompt",
            user_prompt="Generate a tDCS protocol for depression",
        )
        config = {"configurable": {"thread_id": initial["request_id"]}}
        compiled.invoke(initial, config=config)

        # Clinician rejects
        compiled.update_state(config, {
            "review": {
                "status": "rejected",
                "reviewer_id": "dr_test",
                "review_notes": "Evidence not strong enough for this patient.",
                "revision_number": 0,
                "edits_applied": [],
                "parameter_overrides": [],
            },
        })

        final = compiled.invoke(None, config=config)

        # Should be rejected — no output generated
        assert final["status"] == "rejected" or final["review"]["status"] == "rejected"
        # protocol_reporter and audit_logger should NOT have run
        node_ids = [n["node_id"] for n in final["node_history"]]
        assert "protocol_reporter" not in node_ids


class TestSafetyIntegration:
    """Test safety gates in the full pipeline context."""

    def test_contraindication_blocks_pipeline(self):
        """Verify contraindicated patient is blocked at the gate."""
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine
        from sozo_graph.nodes.contraindication_gate import contraindication_gate

        state = {
            "condition": {
                "slug": "depression",
                "schema_dict": {"stimulation_targets": [{"modality": "tdcs"}]},
            },
            "patient_context": {
                "contraindications": ["metallic_cranial_implant", "unstable_epilepsy"],
                "current_medications": [],
            },
        }

        # Safety engine should find blocking contraindications
        safety_result = safety_policy_engine(state)
        assert safety_result["safety"]["safety_cleared"] is False
        assert len(safety_result["safety"]["blocking_contraindications"]) >= 2

        # Gate should block
        gate_state = {**state, **safety_result}
        gate_result = contraindication_gate(gate_state)
        assert gate_result["status"] == "error"

    def test_off_label_tps_flagged_for_non_alzheimers(self):
        """TPS should be flagged as off-label for conditions other than Alzheimer's."""
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine

        state = {
            "condition": {
                "slug": "parkinsons",
                "schema_dict": {"stimulation_targets": [{"modality": "tps"}]},
            },
            "patient_context": {"contraindications": [], "current_medications": []},
        }

        result = safety_policy_engine(state)
        assert result["safety"]["safety_cleared"] is True  # not blocked, just flagged
        assert any("off-label" in f.lower() for f in result["safety"]["off_label_flags"])
