"""Protocol Graph page — LangGraph-powered evidence pipeline with human review."""
from pathlib import Path

import streamlit as st


def render(default_output_dir: str) -> None:
    st.title("Protocol Graph — Evidence-Based Generation")
    st.markdown(
        "Generate protocols using the LangGraph pipeline. "
        "The graph runs through evidence search, safety checks, and composition, "
        "then pauses for your review before finalizing."
    )

    # Session state initialisation
    if "graph_state" not in st.session_state:
        st.session_state.graph_state = None
    if "graph_thread_id" not in st.session_state:
        st.session_state.graph_thread_id = None
    if "graph_phase" not in st.session_state:
        st.session_state.graph_phase = "input"
    if "graph_checkpointer" not in st.session_state:
        try:
            from langgraph.checkpoint.memory import MemorySaver
            st.session_state.graph_checkpointer = MemorySaver()
        except ImportError:
            st.session_state.graph_checkpointer = None

    phase = st.session_state.graph_phase

    if phase == "input":
        _render_input_phase()
    elif phase == "review":
        _render_review_phase()
    elif phase == "completed":
        _render_completed_phase()
    elif phase == "rejected":
        _render_rejected_phase()


# ── Phase renderers ──────────────────────────────────────────────────────────

def _render_input_phase() -> None:
    st.subheader("1. Define Protocol Request")
    col1, col2 = st.columns([2, 1])

    with col1:
        user_prompt = st.text_area(
            "What protocol do you need?",
            placeholder="e.g. Generate a tDCS protocol for treatment-resistant depression targeting left DLPFC",
            height=100,
            key="graph_prompt",
        )
        with st.expander("Patient Context (optional)", expanded=False):
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                patient_age = st.number_input("Age", min_value=0, max_value=120, value=0, key="graph_age")
                patient_sex = st.selectbox("Sex", ["", "Male", "Female", "Other"], key="graph_sex")
            with p_col2:
                patient_meds = st.text_input("Current Medications (comma-separated)", key="graph_meds")
                patient_contras = st.text_input("Known Contraindications (comma-separated)", key="graph_contras")

    with col2:
        st.markdown("**Settings**")
        tier = st.selectbox("Tier", ["fellow", "partners"], key="graph_tier")

    if not st.button("Generate Protocol", type="primary", disabled=not user_prompt):
        return

    patient_context = None
    if patient_age or patient_sex or patient_meds or patient_contras:
        patient_context = {
            "age": patient_age if patient_age else None,
            "sex": patient_sex if patient_sex else None,
            "current_medications": [m.strip() for m in patient_meds.split(",") if m.strip()] if patient_meds else [],
            "contraindications": [c.strip() for c in patient_contras.split(",") if c.strip()] if patient_contras else [],
        }

    with st.spinner("Running evidence pipeline..."):
        try:
            from sozo_graph.graph import build_sozo_graph, create_initial_state
            from sozo_graph.graph import route_after_evidence, route_after_contraindication, route_after_review
            from sozo_graph.state import SozoGraphState
            from sozo_graph.nodes.intake_router import intake_router
            from sozo_graph.nodes.prompt_normalizer import prompt_normalizer
            from sozo_graph.nodes.condition_resolver import condition_resolver
            from sozo_graph.nodes.evidence_search import evidence_search
            from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate
            from sozo_graph.nodes.safety_policy_engine import safety_policy_engine
            from sozo_graph.nodes.contraindication_gate import contraindication_gate
            from sozo_graph.nodes.protocol_template_selector import protocol_template_selector
            from sozo_graph.nodes.protocol_composer import protocol_composer
            from sozo_graph.nodes.grounding_validator import grounding_validator
            from sozo_graph.nodes.review_processor import review_processor
            from sozo_graph.nodes.protocol_reporter import protocol_reporter
            from sozo_graph.nodes.audit_logger import audit_logger
            from langgraph.graph import StateGraph, END

            graph = StateGraph(SozoGraphState)
            for name, node in [
                ("intake_router", intake_router), ("prompt_normalizer", prompt_normalizer),
                ("condition_resolver", condition_resolver), ("evidence_search", evidence_search),
                ("evidence_sufficiency_gate", evidence_sufficiency_gate),
                ("safety_policy_engine", safety_policy_engine),
                ("contraindication_gate", contraindication_gate),
                ("protocol_template_selector", protocol_template_selector),
                ("protocol_composer", protocol_composer), ("grounding_validator", grounding_validator),
                ("review_processor", review_processor), ("protocol_reporter", protocol_reporter),
                ("audit_logger", audit_logger),
            ]:
                graph.add_node(name, node)

            graph.set_entry_point("intake_router")
            graph.add_edge("intake_router", "prompt_normalizer")
            graph.add_edge("prompt_normalizer", "condition_resolver")
            graph.add_edge("condition_resolver", "evidence_search")
            graph.add_edge("evidence_search", "evidence_sufficiency_gate")
            graph.add_conditional_edges("evidence_sufficiency_gate", route_after_evidence,
                                        {"safety_policy_engine": "safety_policy_engine"})
            graph.add_edge("safety_policy_engine", "contraindication_gate")
            graph.add_conditional_edges("contraindication_gate", route_after_contraindication,
                                        {"protocol_template_selector": "protocol_template_selector"})
            graph.add_edge("protocol_template_selector", "protocol_composer")
            graph.add_edge("protocol_composer", "grounding_validator")
            graph.add_edge("grounding_validator", "review_processor")
            graph.add_conditional_edges("review_processor", route_after_review,
                                        {"protocol_reporter": "protocol_reporter",
                                         "review_processor": "review_processor",
                                         "__end__": END})
            graph.add_edge("protocol_reporter", "audit_logger")
            graph.add_edge("audit_logger", END)

            checkpointer = st.session_state.graph_checkpointer
            compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["review_processor"])

            initial = create_initial_state(
                source_mode="prompt",
                user_prompt=user_prompt,
                patient_context=patient_context,
                tier=tier,
            )
            config = {"configurable": {"thread_id": initial["request_id"]}}
            result = compiled.invoke(initial, config=config)

            st.session_state.graph_state = result
            st.session_state.graph_thread_id = initial["request_id"]
            st.session_state.graph_compiled = compiled
            st.session_state.graph_config = config
            st.session_state.graph_phase = "review"
            st.rerun()

        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            import traceback
            st.code(traceback.format_exc())


def _render_review_phase() -> None:
    state = st.session_state.graph_state
    if not state:
        st.warning("No protocol draft available. Please generate one first.")
        if st.button("Back to Input"):
            st.session_state.graph_phase = "input"
            st.rerun()
        st.stop()

    condition = state.get("condition", {})
    evidence = state.get("evidence", {})
    safety = state.get("safety", {})
    protocol = state.get("protocol", {})
    node_history = state.get("node_history", [])

    st.subheader(f"2. Review Protocol — {condition.get('display_name', 'Unknown')}")

    m1, m2, m3, m4, m5 = st.columns(5)
    grade_dist = evidence.get("evidence_summary", {}).get("grade_distribution", {})
    m1.metric("Condition", condition.get("slug", "?"))
    m2.metric("Evidence Articles", evidence.get("screened_article_count", len(evidence.get("articles", []))))
    m3.metric("Grade A", grade_dist.get("A", 0))
    m4.metric("Grounding Score", f"{protocol.get('grounding_score', 0):.0%}")
    m5.metric("Safety", "Cleared" if safety.get("safety_cleared") else "BLOCKED")

    tab_sections, tab_evidence, tab_safety, tab_audit = st.tabs(
        ["Protocol Sections", "Evidence", "Safety", "Audit Trail"]
    )

    with tab_sections:
        sections = protocol.get("composed_sections", [])
        if not sections:
            st.info("No sections composed (check evidence and safety tabs for issues).")
        for section in sections:
            with st.expander(f"{section.get('title', 'Untitled')} [{section.get('confidence', '?')}]", expanded=True):
                st.markdown(section.get("content", "*No content*"))
                cited = section.get("cited_evidence_ids", [])
                if cited:
                    st.caption(f"Citations: {', '.join(cited)}")
                claims = section.get("claims", [])
                if claims:
                    st.markdown("**Claims:**")
                    for claim in claims:
                        flag = f" | {claim['uncertainty_flag']}" if claim.get("uncertainty_flag") else ""
                        st.markdown(
                            f"- [{claim.get('confidence', '?')}] {claim.get('claim_text', '')[:100]} "
                            f"(refs: {', '.join(claim.get('evidence_ids', []))}){flag}"
                        )
        issues = protocol.get("grounding_issues", [])
        if issues:
            st.markdown("---")
            st.markdown("**Grounding Issues:**")
            for issue in issues:
                severity = issue.get("severity", "info")
                icon = {"block": "X", "warning": "!", "info": "i"}.get(severity, "")
                st.markdown(f"[{severity}] {issue.get('section_id', '')}: {issue.get('message', '')}")

    with tab_evidence:
        articles = evidence.get("articles", [])
        if articles:
            st.markdown(f"**{len(articles)} articles** after search, dedup, and screening:")
            for a in articles[:20]:
                grade = a.get("evidence_grade", "?")
                grade_color = {"A": "green", "B": "orange", "C": "gray", "D": "red"}.get(grade, "gray")
                st.markdown(
                    f"- :{grade_color}[**{grade}**] {a.get('title', 'Untitled')[:100]} "
                    f"({', '.join(a.get('authors', [])[:2])}, {a.get('year', '?')}) "
                    f"— PMID: {a.get('pmid', 'N/A')}"
                )
        else:
            st.info("No evidence articles found.")

        prisma = evidence.get("prisma_counts", {})
        if prisma:
            st.markdown("---")
            st.markdown("**PRISMA Flow:**")
            pc1, pc2, pc3, pc4 = st.columns(4)
            pc1.metric("Identified", prisma.get("records_identified", 0))
            pc2.metric("After Dedup", prisma.get("records_after_dedup", 0))
            pc3.metric("Screened", prisma.get("records_screened", 0))
            pc4.metric("Included", prisma.get("studies_included", 0))

    with tab_safety:
        if safety.get("safety_cleared"):
            st.success("Safety assessment: CLEARED")
        else:
            st.error("Safety assessment: BLOCKED")
            for b in safety.get("blocking_contraindications", []):
                st.markdown(f"- {b}")
        for f in safety.get("off_label_flags", []):
            st.warning(f"Off-label: {f}")
        for c in safety.get("consent_requirements", []):
            st.markdown(f"- {c}")
        for w in safety.get("proceed_with_warnings", []):
            st.markdown(f"- {w}")

    with tab_audit:
        st.markdown(f"**{len(node_history)} nodes executed:**")
        for entry in node_history:
            status_icon = {"success": "[OK]", "error": "[ERR]", "skipped": "[SKIP]"}.get(entry.get("status", ""), "")
            st.markdown(f"{status_icon} **{entry.get('node_id', '?')}** — {entry.get('duration_ms', 0):.0f}ms")
            for d in entry.get("decisions", [])[:3]:
                st.caption(f"  → {d[:120]}")

    st.markdown("---")
    st.subheader("3. Your Decision")
    rev_col1, _ = st.columns([2, 1])
    with rev_col1:
        reviewer_id = st.text_input("Reviewer ID", placeholder="e.g. dr_smith", key="reviewer_id")
        review_notes = st.text_area("Review Notes (optional)", key="review_notes", height=80)

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("Approve Protocol", type="primary", disabled=not reviewer_id):
            _do_review_action("approved", reviewer_id, review_notes)
    with btn_col2:
        if st.button("Reject Protocol", disabled=not reviewer_id):
            _do_review_action("rejected", reviewer_id, review_notes)
    with btn_col3:
        if st.button("Start Over"):
            st.session_state.graph_phase = "input"
            st.session_state.graph_state = None
            st.rerun()


def _render_completed_phase() -> None:
    state = st.session_state.graph_state
    st.subheader("Protocol Approved & Released")
    st.success("The protocol has been approved by the clinician and output files generated.")

    output = state.get("output", {}) if state else {}
    paths = output.get("output_paths", {})
    if paths:
        st.markdown("**Output files:**")
        for fmt, path in paths.items():
            fpath = Path(path)
            if fpath.exists():
                st.markdown(f"- **{fmt.upper()}**: `{path}`")
                with open(fpath, "rb") as f:
                    st.download_button(f"Download {fmt.upper()}", f.read(), file_name=fpath.name, key=f"dl_{fmt}")
            else:
                st.markdown(f"- {fmt}: {path} (file not found)")

    audit_id = output.get("audit_record_id")
    if audit_id:
        st.caption(f"Audit record: {audit_id}")

    if st.button("Generate Another Protocol"):
        st.session_state.graph_phase = "input"
        st.session_state.graph_state = None
        st.rerun()


def _render_rejected_phase() -> None:
    st.subheader("Protocol Rejected")
    state = st.session_state.graph_state
    review = state.get("review", {}) if state else {}
    st.warning(
        f"Rejected by {review.get('reviewer_id', 'unknown')}: "
        f"{review.get('review_notes', 'No reason given')}"
    )
    if st.button("Generate Another Protocol"):
        st.session_state.graph_phase = "input"
        st.session_state.graph_state = None
        st.rerun()


def _do_review_action(decision: str, reviewer_id: str, review_notes: str) -> None:
    """Resume the LangGraph pipeline after clinician review."""
    from datetime import datetime, timezone

    try:
        compiled = st.session_state.graph_compiled
        config = st.session_state.graph_config

        compiled.update_state(config, {
            "review": {
                "status": decision,
                "reviewer_id": reviewer_id,
                "review_timestamp": datetime.now(timezone.utc).isoformat(),
                "review_notes": review_notes,
                "revision_number": st.session_state.graph_state.get("review", {}).get("revision_number", 0),
                "edits_applied": [],
                "parameter_overrides": [],
            },
        })

        result = compiled.invoke(None, config=config)
        st.session_state.graph_state = result
        st.session_state.graph_phase = "completed" if decision == "approved" else "rejected"
        st.rerun()

    except Exception as e:
        st.error(f"Review action failed: {e}")
        import traceback
        st.code(traceback.format_exc())
