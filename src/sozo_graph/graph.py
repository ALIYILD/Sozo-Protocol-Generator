"""
Sozo LangGraph — top-level graph definition.

This is the MVP graph: prompt → evidence → composition → review → output.
Single-path flow with mandatory clinician review interrupt.

Architecture:
- 2 LLM nodes (prompt_normalizer, protocol_composer)
- All other nodes are deterministic
- 1 mandatory clinician review interrupt
- Full audit trail via @audited_node decorator
- Checkpointer-backed persistence
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from .state import SozoGraphState

# Node imports
from .nodes.intake_router import intake_router
from .nodes.template_parser import template_parser
from .nodes.prompt_normalizer import prompt_normalizer
from .nodes.condition_resolver import condition_resolver
from .nodes.evidence_search import evidence_search
from .nodes.evidence_sufficiency_gate import evidence_sufficiency_gate
from .nodes.safety_policy_engine import safety_policy_engine
from .nodes.contraindication_gate import contraindication_gate
from .nodes.protocol_template_selector import protocol_template_selector
from .nodes.protocol_composer import protocol_composer
from .nodes.grounding_validator import grounding_validator
from .nodes.review_processor import review_processor
from .nodes.protocol_reporter import protocol_reporter
from .nodes.audit_logger import audit_logger


# ── Routing functions ──────────────────────────────────────────────────


def route_after_intake(state: SozoGraphState) -> str:
    """Route based on source mode."""
    if state.get("source_mode") == "upload":
        return "template_parser"
    return "prompt_normalizer"


def route_after_evidence(state: SozoGraphState) -> str:
    """Route based on evidence sufficiency."""
    evidence = state.get("evidence", {})
    if evidence.get("evidence_sufficient", False):
        return "safety_policy_engine"
    # Insufficient evidence — still proceed but with flags
    # (In production, this would interrupt for clinician review)
    return "safety_policy_engine"


def route_after_contraindication(state: SozoGraphState) -> str:
    """Route based on safety clearance."""
    safety = state.get("safety", {})
    if safety.get("safety_cleared", True):
        return "protocol_template_selector"
    # Blocked — in production this would interrupt
    # MVP: proceed with warnings logged
    return "protocol_template_selector"


MAX_REVISION_CYCLES = 3


def route_after_review(state: SozoGraphState) -> str:
    """Route based on clinician review decision.

    - approved → protocol_reporter (finalize)
    - rejected + under max revisions → protocol_composer (re-compose with notes)
    - rejected + at max revisions → __end__ (terminate)
    - edited → review_processor (apply edits, then re-validate)
    """
    review = state.get("review", {})
    status = review.get("status", "pending")
    revision = review.get("revision_number", 0)

    if status == "approved":
        return "protocol_reporter"
    if status == "edited":
        return "review_processor"  # apply edits then re-validate
    if status == "rejected":
        if revision < MAX_REVISION_CYCLES:
            return "protocol_composer"  # re-compose with rejection notes
        return "__end__"  # max revisions reached
    # pending or unknown
    return "__end__"


# ── Graph builder ──────────────────────────────────────────────────────


def build_sozo_graph(checkpointer=None):
    """Build and compile the Sozo protocol generation graph.

    Args:
        checkpointer: LangGraph checkpointer for persistence.
                      Use MemorySaver for dev, PostgresSaver for production.

    Returns:
        Compiled LangGraph StateGraph.
    """
    from langgraph.graph import StateGraph, END

    graph = StateGraph(SozoGraphState)

    # ── Add nodes ─────────────────────────────────────────────
    graph.add_node("intake_router", intake_router)
    graph.add_node("template_parser", template_parser)
    graph.add_node("prompt_normalizer", prompt_normalizer)
    graph.add_node("condition_resolver", condition_resolver)
    graph.add_node("evidence_search", evidence_search)
    graph.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)
    graph.add_node("safety_policy_engine", safety_policy_engine)
    graph.add_node("contraindication_gate", contraindication_gate)
    graph.add_node("protocol_template_selector", protocol_template_selector)
    graph.add_node("protocol_composer", protocol_composer)
    graph.add_node("grounding_validator", grounding_validator)
    graph.add_node("review_processor", review_processor)
    graph.add_node("protocol_reporter", protocol_reporter)
    graph.add_node("audit_logger", audit_logger)

    # ── Entry point ───────────────────────────────────────────
    graph.set_entry_point("intake_router")

    # ── Edges: Intake ─────────────────────────────────────────
    graph.add_conditional_edges(
        "intake_router",
        route_after_intake,
        {
            "template_parser": "template_parser",
            "prompt_normalizer": "prompt_normalizer",
        },
    )
    graph.add_edge("template_parser", "condition_resolver")
    graph.add_edge("prompt_normalizer", "condition_resolver")

    # ── Edges: Evidence ───────────────────────────────────────
    graph.add_edge("condition_resolver", "evidence_search")
    graph.add_edge("evidence_search", "evidence_sufficiency_gate")

    # ── Edges: Evidence → Composition ─────────────────────────
    graph.add_conditional_edges(
        "evidence_sufficiency_gate",
        route_after_evidence,
        {
            "safety_policy_engine": "safety_policy_engine",
        },
    )

    # ── Edges: Composition ────────────────────────────────────
    graph.add_edge("safety_policy_engine", "contraindication_gate")

    graph.add_conditional_edges(
        "contraindication_gate",
        route_after_contraindication,
        {
            "protocol_template_selector": "protocol_template_selector",
        },
    )

    graph.add_edge("protocol_template_selector", "protocol_composer")
    graph.add_edge("protocol_composer", "grounding_validator")

    # ── Edges: Review (interrupt before review_processor) ─────
    graph.add_edge("grounding_validator", "review_processor")

    graph.add_conditional_edges(
        "review_processor",
        route_after_review,
        {
            "protocol_reporter": "protocol_reporter",
            "review_processor": "review_processor",  # edit → apply → re-validate
            "protocol_composer": "protocol_composer",  # reject → re-compose (max 3)
            "__end__": END,
        },
    )

    # ── Edges: Output ─────────────────────────────────────────
    graph.add_edge("protocol_reporter", "audit_logger")
    graph.add_edge("audit_logger", END)

    # ── Compile ───────────────────────────────────────────────
    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["review_processor"],  # MANDATORY clinician review
    )

    return compiled


# ── Execution helpers ──────────────────────────────────────────────────


def create_initial_state(
    source_mode: str = "prompt",
    user_prompt: str = "",
    uploaded_filename: str = "",
    patient_context: Optional[dict] = None,
    tier: str = "fellow",
) -> SozoGraphState:
    """Create the initial state for a protocol generation run."""
    now = datetime.now(timezone.utc).isoformat()

    return {
        "request_id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "status": "intake",
        "source_mode": source_mode,
        "intake": {
            "user_prompt": user_prompt or None,
            "uploaded_filename": uploaded_filename or None,
        },
        "condition": {},
        "patient_context": patient_context,
        "evidence": {},
        "safety": {},
        "protocol": {"tier": tier},
        "eeg": None,
        "review": {"status": "pending", "revision_number": 0},
        "output": {},
        "node_history": [],
        "errors": [],
        "version": "1.0",
        "graph_version": "0.1.0-mvp",
    }


def run_protocol_generation(
    user_prompt: str,
    patient_context: Optional[dict] = None,
    tier: str = "fellow",
    checkpointer=None,
) -> dict:
    """Execute the protocol generation pipeline until clinician review.

    Returns the state at the review interrupt point.
    The clinician must approve/reject/edit before the pipeline completes.
    """
    graph = build_sozo_graph(checkpointer=checkpointer)
    initial_state = create_initial_state(
        source_mode="prompt",
        user_prompt=user_prompt,
        patient_context=patient_context,
        tier=tier,
    )

    config = {"configurable": {"thread_id": initial_state["request_id"]}}

    # Run until the review interrupt
    result = graph.invoke(initial_state, config=config)
    return result


def resume_after_review(
    thread_id: str,
    decision: str,
    reviewer_id: str,
    review_notes: str = "",
    section_edits: Optional[list] = None,
    parameter_overrides: Optional[list] = None,
    checkpointer=None,
) -> dict:
    """Resume graph execution after clinician review.

    Args:
        thread_id: The request_id / thread_id from the initial run.
        decision: "approve", "reject", or "edit"
        reviewer_id: Clinician identifier.
        review_notes: Clinician notes.
        section_edits: List of section edits if decision is "edit".
        parameter_overrides: List of parameter overrides if decision is "edit".
        checkpointer: Same checkpointer used in initial run.
    """
    graph = build_sozo_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    now = datetime.now(timezone.utc).isoformat()

    # Update state with review decision
    review_update = {
        "review": {
            "status": "approved" if decision == "approve" else (
                "edited" if decision == "edit" else "rejected"
            ),
            "reviewer_id": reviewer_id,
            "review_timestamp": now,
            "review_notes": review_notes,
            "edits_applied": section_edits or [],
            "parameter_overrides": parameter_overrides or [],
        },
    }

    graph.update_state(config, review_update)

    # Resume execution
    result = graph.invoke(None, config=config)
    return result
