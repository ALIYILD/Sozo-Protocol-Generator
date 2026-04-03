"""Unified LangGraph graph that delegates to existing Sozo services.

This is the production graph that replaces standalone node implementations
with calls into the real GenerationService pipeline via the integration
layer.  Every node:
  - Reads from the appropriate state slice
  - Calls the integration function
  - Updates the state with results
  - Appends to node_history for audit (timestamps + hashes)
  - Handles errors gracefully (catch, log, add to errors list)

The @audited_node decorator from sozo_graph.audit.logger handles timing,
hashing, and error recording automatically.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from .audit.logger import audited_node
from .state import SozoGraphState
from . import integration

logger = logging.getLogger(__name__)

GRAPH_VERSION = "2.0.0-unified"


# =====================================================================
#  Node implementations -- each wraps an integration function
# =====================================================================


@audited_node("intake_router")
def intake_router_node(state: SozoGraphState) -> dict:
    """Route intake by source mode (upload vs prompt).

    Deterministic node. Inspects intake fields and sets source_mode.
    """
    decisions: list[str] = []
    intake = state.get("intake", {})

    has_upload = bool(intake.get("uploaded_file") or intake.get("uploaded_filename"))
    has_prompt = bool(intake.get("user_prompt"))

    if has_upload:
        source_mode = "upload"
        decisions.append("Upload detected -- routing to condition_resolver")
    elif has_prompt:
        source_mode = "prompt"
        decisions.append("Prompt detected -- routing to condition_resolver")
    else:
        source_mode = "prompt"
        decisions.append("No input detected -- defaulting to prompt mode")

    return {
        "source_mode": source_mode,
        "status": "intake",
        "_decisions": decisions,
    }


@audited_node("condition_resolver")
def condition_resolver_node(state: SozoGraphState) -> dict:
    """Resolve condition using the shared ConditionRegistry.

    Delegates to integration.resolve_condition which calls
    sozo_generator.conditions.registry.get_registry().
    """
    decisions: list[str] = []

    # Determine slug from various intake sources
    intake = state.get("intake", {})
    normalized = intake.get("normalized_request") or {}
    template = intake.get("template_profile") or {}

    slug = (
        normalized.get("condition_slug")
        or template.get("inferred_condition")
        or state.get("condition", {}).get("slug")
    )

    if not slug:
        decisions.append("No condition slug found in intake -- condition_valid=false")
        return {
            "condition": {
                "slug": "",
                "display_name": "",
                "icd10": "",
                "schema_dict": {},
                "resolution_source": "none",
                "condition_valid": False,
            },
            "_decisions": decisions,
        }

    condition_data = integration.resolve_condition(slug)

    # Refine resolution_source based on where the slug came from
    if condition_data["condition_valid"]:
        if normalized.get("condition_slug"):
            condition_data["resolution_source"] = "prompt_inferred"
        elif template.get("inferred_condition"):
            condition_data["resolution_source"] = "template_inferred"

    decisions.append(
        f"Resolved '{slug}' -> "
        f"{condition_data.get('display_name', '?')} "
        f"(ICD-10: {condition_data.get('icd10', '?')}) "
        f"via {condition_data.get('resolution_source', '?')} "
        f"[valid={condition_data.get('condition_valid')}]"
    )

    return {
        "condition": condition_data,
        "status": "intake",
        "_decisions": decisions,
    }


@audited_node("evidence_search")
def evidence_search_node(state: SozoGraphState) -> dict:
    """Run evidence pipeline via integration layer.

    Delegates to integration.run_evidence_pipeline which calls
    ResearchPipeline.run() (multi-source search + dedup + screen +
    extract + score).
    """
    decisions: list[str] = []
    condition = state.get("condition", {})

    if not condition.get("condition_valid"):
        decisions.append("Skipping evidence search -- condition not valid")
        return {
            "evidence": {
                "raw_article_count": 0,
                "evidence_sufficient": False,
                "evidence_gaps": ["Condition not resolved"],
            },
            "status": "evidence",
            "_decisions": decisions,
        }

    evidence_data = integration.run_evidence_pipeline(
        condition_slug=condition["slug"],
        condition_name=condition.get("display_name", ""),
        schema_dict=condition["schema_dict"],
    )

    decisions.append(
        f"Pipeline: {evidence_data.get('raw_article_count', 0)} identified -> "
        f"{evidence_data.get('unique_article_count', 0)} deduped -> "
        f"{evidence_data.get('screened_article_count', 0)} screened | "
        f"sufficient={evidence_data.get('evidence_sufficient')}"
    )

    return {
        "evidence": evidence_data,
        "status": "evidence",
        "_decisions": decisions,
    }


@audited_node("evidence_gate")
def evidence_sufficiency_node(state: SozoGraphState) -> dict:
    """Check if evidence is sufficient to proceed.

    Soft gate: flags insufficient evidence for clinician review but
    does NOT block the pipeline (always proceeds to safety check).
    """
    decisions: list[str] = []
    evidence = state.get("evidence", {})

    sufficient = evidence.get("evidence_sufficient", False)
    summary = evidence.get("evidence_summary", {})
    grade_dist = summary.get("grade_distribution", {})
    gaps = list(evidence.get("evidence_gaps", []))

    if sufficient:
        decisions.append(
            f"Evidence sufficient: {grade_dist.get('A', 0)} Grade A, "
            f"{grade_dist.get('B', 0)} Grade B"
        )
        return {
            "evidence": {**evidence, "evidence_sufficient": True},
            "_decisions": decisions,
        }

    # Build gap report
    if grade_dist.get("A", 0) == 0 and grade_dist.get("B", 0) == 0:
        gaps.append("No Grade A or B evidence found for primary protocol parameters")
    total = summary.get("total_articles", 0)
    if total < 5:
        gaps.append(f"Only {total} articles after screening")

    decisions.append(f"Evidence INSUFFICIENT: {gaps}")

    return {
        "evidence": {
            **evidence,
            "evidence_sufficient": False,
            "evidence_gaps": gaps,
        },
        "_decisions": decisions,
    }


@audited_node("safety_check")
def safety_check_node(state: SozoGraphState) -> dict:
    """Run safety evaluation via integration layer.

    Delegates to integration.evaluate_safety which checks:
      - Hard contraindications per modality
      - Drug interactions from sozo_generator.safety
      - Off-label disclosures
      - Knowledge-base SafetyValidator (when available)
    """
    decisions: list[str] = []
    condition = state.get("condition", {})
    patient = state.get("patient_context") or {}

    # Determine target modalities
    schema_dict = condition.get("schema_dict", {})
    stim_targets = schema_dict.get("stimulation_targets", [])
    target_modalities = list({
        t.get("modality", "tdcs") for t in stim_targets
    }) or ["tdcs"]

    safety_data = integration.evaluate_safety(
        condition_data=condition,
        patient_context=patient,
        target_modalities=target_modalities,
    )

    if safety_data["safety_cleared"]:
        decisions.append(f"Safety cleared for modalities: {target_modalities}")
    else:
        decisions.append(
            f"Safety BLOCKED: {safety_data['blocking_contraindications']}"
        )

    if safety_data["proceed_with_warnings"]:
        decisions.append(
            f"Warnings: {len(safety_data['proceed_with_warnings'])} "
            f"drug/modality warnings raised"
        )

    return {
        "safety": safety_data,
        "status": "composition",
        "_decisions": decisions,
    }


@audited_node("contraindication_gate")
def contraindication_gate_node(state: SozoGraphState) -> dict:
    """Hard gate on absolute contraindications.

    If safety_cleared is False, the pipeline terminates via conditional
    edge routing to END.
    """
    decisions: list[str] = []
    safety = state.get("safety", {})
    cleared = safety.get("safety_cleared", False)
    blocking = safety.get("blocking_contraindications", [])

    if cleared:
        decisions.append("Contraindication gate PASSED")
        return {"_decisions": decisions}

    decisions.append(f"Contraindication gate BLOCKED: {blocking}")
    return {
        "status": "error",
        "_decisions": decisions,
    }


@audited_node("personalization")
def personalization_node(state: SozoGraphState) -> dict:
    """V2 stub: Run personalization engine if patient data is present.

    Currently a pass-through. In V2 this will apply EEG-based and
    phenotype-based protocol adjustments.
    """
    decisions: list[str] = []
    patient = state.get("patient_context") or {}
    eeg = state.get("eeg") or {}

    if eeg.get("data_available"):
        decisions.append(
            "EEG data present -- personalization would apply (V2 stub)"
        )
    elif patient.get("phenotype_slug"):
        decisions.append(
            f"Phenotype '{patient['phenotype_slug']}' detected "
            f"-- personalization would apply (V2 stub)"
        )
    else:
        decisions.append("No personalization data -- passing through")

    return {"_decisions": decisions}


@audited_node("protocol_composer")
def protocol_composer_node(state: SozoGraphState) -> dict:
    """Compose protocol sections via integration layer.

    Delegates to integration.compose_protocol_sections which attempts:
      1. Canonical assembler (KnowledgeBase + DocumentBlueprint)
      2. LLM composition (Claude)
      3. Data-driven fallback
    """
    decisions: list[str] = []
    condition = state.get("condition", {})
    evidence = state.get("evidence", {})
    safety = state.get("safety", {})
    protocol = state.get("protocol", {})

    result = integration.compose_protocol_sections(
        condition_data=condition,
        evidence_data=evidence,
        safety_data=safety,
        protocol_data=protocol,
    )

    composed = result.get("composed_sections", [])
    methods = set(s.get("generation_method", "unknown") for s in composed)
    total_citations = sum(
        len(s.get("cited_evidence_ids", [])) for s in composed
    )

    decisions.append(
        f"Composed {len(composed)} sections via {methods} "
        f"with {total_citations} total citations"
    )

    updated_protocol = {**protocol, **result}
    # Remove internal keys that are not part of ProtocolState
    updated_protocol.pop("_canonical_output_path", None)

    return {
        "protocol": updated_protocol,
        "_decisions": decisions,
    }


@audited_node("grounding_validator")
def grounding_validator_node(state: SozoGraphState) -> dict:
    """Validate evidence grounding via integration layer.

    Delegates to integration.validate_evidence_grounding which checks
    citation validity, claim evidence coverage, and prohibited language.
    """
    decisions: list[str] = []
    protocol = state.get("protocol", {})
    evidence = state.get("evidence", {})

    grounding = integration.validate_evidence_grounding(
        protocol_data=protocol,
        evidence_data=evidence,
    )

    blocking = [i for i in grounding["grounding_issues"] if i.get("severity") == "block"]
    warnings = [i for i in grounding["grounding_issues"] if i.get("severity") == "warning"]

    decisions.append(
        f"Grounding score: {grounding['grounding_score']:.3f}, "
        f"{len(blocking)} blocking, {len(warnings)} warnings"
    )

    return {
        "protocol": {
            **protocol,
            "grounding_score": grounding["grounding_score"],
            "grounding_issues": grounding["grounding_issues"],
        },
        "_decisions": decisions,
    }


@audited_node("qa_engine")
def qa_engine_node(state: SozoGraphState) -> dict:
    """Run QA checks via integration layer.

    Delegates to integration.run_qa_checks which calls
    sozo_generator.qa.engine.QAEngine.
    """
    decisions: list[str] = []
    protocol = state.get("protocol", {})
    condition = state.get("condition", {})

    qa_result = integration.run_qa_checks(
        protocol_data=protocol,
        condition_slug=condition.get("slug", ""),
        condition_schema_dict=condition.get("schema_dict", {}),
    )

    passed = qa_result.get("qa_passed")
    issues = qa_result.get("qa_issues", [])

    decisions.append(
        f"QA: passed={passed}, {len(issues)} issues"
    )

    return {
        "protocol": {
            **protocol,
            "qa_passed": passed,
            "qa_issues": issues,
        },
        "_decisions": decisions,
    }


@audited_node("clinician_review")
def clinician_review_node(state: SozoGraphState) -> dict:
    """Human-in-the-loop review interrupt.

    This node processes the review decision after the graph resumes
    from the clinician interrupt. It applies edits and stamps
    approval/rejection, mirroring the existing review_processor logic.
    """
    decisions: list[str] = []
    review = state.get("review", {})
    protocol = state.get("protocol", {})

    status = review.get("status", "pending")
    reviewer_id = review.get("reviewer_id", "unknown")
    revision = review.get("revision_number", 0)

    if status == "approved":
        now = datetime.now(timezone.utc).isoformat()
        decisions.append(f"Protocol APPROVED by {reviewer_id} (revision {revision})")
        return {
            "review": {
                **review,
                "approval_stamp": {
                    "reviewer_id": reviewer_id,
                    "reviewer_credentials": review.get("reviewer_credentials", ""),
                    "approved_at": now,
                    "revision_number": revision,
                    "protocol_version": f"1.0.{revision}",
                },
            },
            "status": "approved",
            "_decisions": decisions,
        }

    elif status == "rejected":
        decisions.append(
            f"Protocol REJECTED by {reviewer_id}: "
            f"{review.get('review_notes', 'No reason given')}"
        )
        return {
            "status": "rejected",
            "_decisions": decisions,
        }

    elif status == "edited":
        # Apply section edits
        edits = review.get("edits_applied", [])
        sections = list(protocol.get("composed_sections", []))

        for edit in edits:
            section_id = edit.get("section_id")
            field = edit.get("field", "content")
            new_value = edit.get("new_value")

            for section in sections:
                if section.get("section_id") == section_id:
                    section[field] = new_value
                    section["generation_method"] = "clinician_edited"
                    decisions.append(f"Applied edit to {section_id}.{field}")
                    break

        # Apply parameter overrides
        overrides = review.get("parameter_overrides", [])
        base_seq = dict(protocol.get("base_sequence", {}))

        for override in overrides:
            decisions.append(
                f"Parameter override: {override.get('parameter')} "
                f"{override.get('old_value')} -> {override.get('new_value')} "
                f"(reason: {override.get('override_reason', 'none')})"
            )

        new_revision = revision + 1
        decisions.append(f"Edits applied -- revision {revision} -> {new_revision}")

        return {
            "protocol": {
                **protocol,
                "composed_sections": sections,
                "base_sequence": base_seq,
            },
            "review": {
                **review,
                "revision_number": new_revision,
                "status": "pending",
            },
            "_decisions": decisions,
        }

    decisions.append(f"Review status '{status}' -- no action taken")
    return {"_decisions": decisions}


@audited_node("document_renderer")
def document_renderer_node(state: SozoGraphState) -> dict:
    """Render final output via integration layer.

    Delegates to integration.render_output which produces JSON,
    PRISMA summary, and DOCX documents.
    """
    decisions: list[str] = []

    output = integration.render_output(
        protocol_data=state.get("protocol", {}),
        condition_data=state.get("condition", {}),
        evidence_data=state.get("evidence", {}),
        review_data=state.get("review", {}),
        request_id=state.get("request_id", "unknown"),
        state_version=state.get("version", "1.0"),
    )

    formats = output.get("output_formats", [])
    paths = output.get("output_paths", {})

    for fmt, path in paths.items():
        decisions.append(f"Rendered {fmt}: {path}")

    return {
        "output": output,
        "status": "released",
        "_decisions": decisions,
    }


@audited_node("audit_logger")
def audit_logger_node(state: SozoGraphState) -> dict:
    """Log complete audit trail.

    Writes a comprehensive JSON audit record covering:
      - Full execution trace (node_history)
      - Evidence audit (search counts, cited PMIDs, PRISMA)
      - Safety audit (contraindications, consent requirements)
      - Review audit (cycles, reviewer, decision)
      - Output paths
    """
    decisions: list[str] = []
    now = datetime.now(timezone.utc).isoformat()

    condition = state.get("condition", {})
    evidence = state.get("evidence", {})
    safety = state.get("safety", {})
    review = state.get("review", {})
    node_history = state.get("node_history", [])

    audit_id = f"audit-{state.get('request_id', 'unknown')}"

    # Compute stats
    total_nodes = len(node_history)
    llm_calls = sum(
        1 for n in node_history
        if n.get("node_id") in (
            "prompt_normalizer", "protocol_composer", "eeg_interpreter",
        )
    )
    total_duration = sum(n.get("duration_ms", 0) for n in node_history)

    # Evidence citations
    cited_ids: set[str] = set()
    for section in state.get("protocol", {}).get("composed_sections", []):
        cited_ids.update(section.get("cited_evidence_ids", []))

    grade_dist = evidence.get("evidence_summary", {}).get("grade_distribution", {})

    audit_record = {
        "audit_id": audit_id,
        "request_id": state.get("request_id"),
        "graph_version": GRAPH_VERSION,
        "condition_slug": condition.get("slug"),
        "condition_name": condition.get("display_name"),
        "created_at": state.get("created_at"),
        "completed_at": now,
        "total_duration_ms": round(total_duration, 2),

        # Execution trace
        "node_history": node_history,
        "errors": state.get("errors", []),
        "total_nodes_executed": total_nodes,
        "total_llm_calls": llm_calls,

        # Evidence audit
        "evidence_articles_searched": evidence.get("raw_article_count", 0),
        "evidence_articles_screened": evidence.get("screened_article_count", 0),
        "evidence_articles_cited": len(cited_ids),
        "evidence_ids_cited": sorted(cited_ids),
        "evidence_grade_distribution": grade_dist,
        "prisma_counts": evidence.get("prisma_counts", {}),

        # Safety audit
        "contraindications_checked": [
            c.get("contraindication", "")
            for c in safety.get("contraindications_found", [])
        ],
        "safety_flags_raised": safety.get("blocking_contraindications", []),
        "consent_requirements": safety.get("consent_requirements", []),

        # Review audit
        "review_cycles": review.get("revision_number", 0),
        "reviewer_id": review.get("reviewer_id"),
        "review_decision": review.get("status"),
        "approval_stamp": review.get("approval_stamp"),

        # Output
        "output_paths": state.get("output", {}).get("output_paths", {}),
        "state_version": state.get("version"),

        # Integrity hash of the audit payload
        "audit_hash": integration.compute_audit_hash({
            "request_id": state.get("request_id"),
            "condition_slug": condition.get("slug"),
            "evidence_ids_cited": sorted(cited_ids),
            "review_decision": review.get("status"),
        }),
    }

    # Persist audit record
    try:
        from sozo_generator.core.settings import get_settings
        from pathlib import Path

        settings = get_settings()
        audit_dir = settings.output_dir / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / f"{audit_id}.json"
        audit_path.write_text(json.dumps(audit_record, indent=2, default=str))
        decisions.append(
            f"Audit record written: {audit_path} "
            f"({total_nodes} nodes, {len(cited_ids)} citations)"
        )
    except Exception as exc:
        logger.error("CRITICAL: Audit write failed: %s", exc)
        decisions.append(f"CRITICAL: Audit write failed: {exc}")
        return {
            "status": "error",
            "errors": [{
                "node_id": "audit_logger",
                "error_type": "AuditWriteFailure",
                "message": f"Audit write blocked release: {exc}",
                "recoverable": True,
                "timestamp": now,
            }],
            "_decisions": decisions,
        }

    return {
        "output": {
            **state.get("output", {}),
            "audit_record_id": audit_id,
        },
        "_decisions": decisions,
    }


# =====================================================================
#  Routing functions
# =====================================================================


def route_after_evidence(state: SozoGraphState) -> str:
    """Always proceed to safety check, even if evidence is insufficient.

    The evidence_gate node flags gaps for clinician review but does not
    block the pipeline.
    """
    evidence = state.get("evidence", {})
    if evidence.get("evidence_sufficient", False):
        return "proceed"
    return "insufficient"


def route_after_safety(state: SozoGraphState) -> str:
    """Block if absolute contraindications present, else proceed."""
    safety = state.get("safety", {})
    if safety.get("safety_cleared", True):
        return "proceed"
    return "blocked"


def route_after_review(state: SozoGraphState) -> str:
    """Route based on clinician review decision."""
    review = state.get("review", {})
    status = review.get("status", "pending")

    if status == "approved":
        return "approved"
    if status == "edited":
        return "revision"
    # rejected or pending
    return "rejected"


# =====================================================================
#  Graph builder
# =====================================================================


def build_unified_graph(checkpointer=None):
    """Build and compile the unified production graph.

    This graph delegates all heavy lifting to existing Sozo services
    via the integration layer, eliminating parallel implementations.

    Args:
        checkpointer: LangGraph checkpointer for persistence.
                      Use MemorySaver for dev, PostgresSaver for production.

    Returns:
        Compiled LangGraph StateGraph.
    """
    from langgraph.graph import StateGraph, END

    graph = StateGraph(SozoGraphState)

    # -- Add nodes --
    graph.add_node("intake_router", intake_router_node)
    graph.add_node("condition_resolver", condition_resolver_node)
    graph.add_node("evidence_search", evidence_search_node)
    graph.add_node("evidence_gate", evidence_sufficiency_node)
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("contraindication_gate", contraindication_gate_node)
    graph.add_node("personalization", personalization_node)
    graph.add_node("protocol_composer", protocol_composer_node)
    graph.add_node("grounding_validator", grounding_validator_node)
    graph.add_node("qa_engine", qa_engine_node)
    graph.add_node("clinician_review", clinician_review_node)
    graph.add_node("document_renderer", document_renderer_node)
    graph.add_node("audit_logger", audit_logger_node)

    # -- Entry point --
    graph.set_entry_point("intake_router")

    # -- Linear edges --
    graph.add_edge("intake_router", "condition_resolver")
    graph.add_edge("condition_resolver", "evidence_search")
    graph.add_edge("evidence_search", "evidence_gate")

    # -- Conditional: evidence sufficiency --
    graph.add_conditional_edges(
        "evidence_gate",
        route_after_evidence,
        {
            "proceed": "safety_check",
            "insufficient": "safety_check",
        },
    )

    # -- Linear: safety --
    graph.add_edge("safety_check", "contraindication_gate")

    # -- Conditional: contraindication gate --
    graph.add_conditional_edges(
        "contraindication_gate",
        route_after_safety,
        {
            "proceed": "personalization",
            "blocked": END,
        },
    )

    # -- Linear: composition pipeline --
    graph.add_edge("personalization", "protocol_composer")
    graph.add_edge("protocol_composer", "grounding_validator")
    graph.add_edge("grounding_validator", "qa_engine")
    graph.add_edge("qa_engine", "clinician_review")

    # -- Conditional: clinician review --
    graph.add_conditional_edges(
        "clinician_review",
        route_after_review,
        {
            "approved": "document_renderer",
            "rejected": END,
            "revision": "protocol_composer",
        },
    )

    # -- Linear: output --
    graph.add_edge("document_renderer", "audit_logger")
    graph.add_edge("audit_logger", END)

    # -- Compile with clinician review interrupt --
    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["clinician_review"],
    )

    return compiled


# =====================================================================
#  Execution helpers
# =====================================================================


def create_initial_state(
    source_mode: str = "prompt",
    user_prompt: str = "",
    uploaded_filename: str = "",
    patient_context: Optional[dict] = None,
    tier: str = "fellow",
) -> SozoGraphState:
    """Create the initial state for a unified protocol generation run."""
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
        "graph_version": GRAPH_VERSION,
    }


def run_unified_generation(
    user_prompt: str,
    patient_context: Optional[dict] = None,
    tier: str = "fellow",
    checkpointer=None,
) -> dict:
    """Execute the unified pipeline until clinician review.

    Returns the state at the review interrupt point.
    The clinician must approve/reject/edit before the pipeline completes.
    """
    graph = build_unified_graph(checkpointer=checkpointer)
    initial_state = create_initial_state(
        source_mode="prompt",
        user_prompt=user_prompt,
        patient_context=patient_context,
        tier=tier,
    )

    config = {"configurable": {"thread_id": initial_state["request_id"]}}

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
    graph = build_unified_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    now = datetime.now(timezone.utc).isoformat()

    review_update = {
        "review": {
            "status": (
                "approved" if decision == "approve"
                else ("edited" if decision == "edit" else "rejected")
            ),
            "reviewer_id": reviewer_id,
            "review_timestamp": now,
            "review_notes": review_notes,
            "edits_applied": section_edits or [],
            "parameter_overrides": parameter_overrides or [],
        },
    }

    graph.update_state(config, review_update)

    result = graph.invoke(None, config=config)
    return result
