"""Review Queue page — document review lifecycle management."""
from pathlib import Path

import streamlit as st

from ui.helpers import load_registry


def render(reviews_dir: Path, default_output_dir: str, pilot_logs_dir: Path) -> None:
    st.title("Review Queue")
    st.markdown("Manage document review lifecycle: approve, reject, flag, export, and generate audit reports.")

    try:
        from sozo_generator.review.manager import ReviewManager
        from sozo_generator.review.reports import ReviewReporter
        from sozo_generator.core.enums import ReviewStatus

        mgr = ReviewManager(reviews_dir)
        reporter = ReviewReporter(reviews_dir)
        dashboard = reporter.get_dashboard_data()
        queue = mgr.get_review_queue()

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total", dashboard.total_reviews)
        col2.metric("Pending", dashboard.pending_count)
        col3.metric("Approved", dashboard.approved_count)
        col4.metric("Rejected", dashboard.rejected_count)
        col5.metric("Flagged", dashboard.flagged_count)
        col6.metric("Exported", dashboard.exported_count)

        st.divider()
        fcol1, fcol2, fcol3 = st.columns(3)
        _filter_status = fcol1.selectbox(
            "Filter by status",
            ["All", "needs_review", "flagged", "draft", "approved", "rejected", "exported"],
            key="rq_filter_status",
        )
        _all_conditions = sorted(set(s.condition_slug for states in queue.values() for s in states))
        _filter_condition = fcol2.selectbox("Filter by condition", ["All"] + _all_conditions, key="rq_filter_cond")
        _all_doc_types = sorted(set(s.document_type for states in queue.values() for s in states))
        _filter_doctype = fcol3.selectbox("Filter by doc type", ["All"] + _all_doc_types, key="rq_filter_dt")

        _filtered = [
            s
            for status_key, states in queue.items()
            for s in states
            if (_filter_status == "All" or status_key == _filter_status)
            and (_filter_condition == "All" or s.condition_slug == _filter_condition)
            and (_filter_doctype == "All" or s.document_type == _filter_doctype)
        ]

        st.divider()
        if _filtered:
            st.subheader(f"Documents ({len(_filtered)})")
            for state in _filtered:
                _colors = {
                    "draft": "gray", "needs_review": "orange", "approved": "green",
                    "rejected": "red", "flagged": "red", "exported": "blue",
                }
                _c = _colors.get(state.status.value, "gray")
                with st.expander(
                    f":{_c}[{state.status.value.upper().replace('_',' ')}] "
                    f"{state.condition_slug} / {state.document_type} / {state.tier}"
                ):
                    st.markdown(f"**Build ID:** `{state.build_id}`")
                    st.markdown(f"**Created:** {state.created_at}  |  **Updated:** {state.updated_at}")

                    if state.section_notes:
                        st.markdown("**Review Comments:**")
                        for sec_id, comments in state.section_notes.items():
                            for c in comments:
                                _rev = c.reviewer if hasattr(c, "reviewer") else c.get("reviewer", "?")
                                _txt = c.text if hasattr(c, "text") else c.get("text", "")
                                st.markdown(f"  - `{sec_id}` — **{_rev}**: {_txt}")

                    if state.decisions:
                        st.markdown("**Decision History:**")
                        for d in state.decisions:
                            _drev = d.reviewer if hasattr(d, "reviewer") else d.get("reviewer", "?")
                            _dst = d.status.value if hasattr(d.status, "value") else d.get("status", "?")
                            _drs = d.reason if hasattr(d, "reason") else d.get("reason", "")
                            _dat = d.decided_at if hasattr(d, "decided_at") else d.get("decided_at", "")
                            st.markdown(f"  - {_dat}: **{_drev}** → {_dst}" + (f" — {_drs}" if _drs else ""))

                    # Section-level evidence
                    try:
                        from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
                        _cond = load_registry().get(state.condition_slug)
                        _mapper = SectionEvidenceMapper()
                        _items = _mapper.build_evidence_items_from_condition(_cond)
                        _summaries = reporter.generate_section_review_summaries(_cond)
                        if _summaries:
                            st.markdown("**Section Evidence:**")
                            for ss in _summaries:
                                _ec = {
                                    "high_confidence": "green", "medium_confidence": "blue",
                                    "low_confidence": "orange", "insufficient": "red",
                                }.get(ss.evidence_confidence, "gray")
                                _flags = (
                                    (" WEAK" if ss.is_weak else "")
                                    + (" STALE" if ss.is_outdated else "")
                                    + (" CONFLICT" if ss.has_contradictions else "")
                                )
                                st.markdown(
                                    f"  - `{ss.section_id}`: :{_ec}[{ss.evidence_confidence}] "
                                    f"({ss.article_count} articles)"
                                    + (f" :red[{_flags}]" if _flags else "")
                                )
                    except Exception:
                        pass

                    st.markdown("---")
                    _reviewer = st.text_input("Reviewer", key=f"rv_{state.build_id}")
                    _reason = st.text_input("Reason / notes", key=f"rn_{state.build_id}")

                    bcol1, bcol2, bcol3 = st.columns(3)
                    with bcol1:
                        if st.button("Approve", key=f"ap_{state.build_id}", type="primary"):
                            if _reviewer:
                                try:
                                    mgr.approve(state.build_id, _reviewer, _reason)
                                    st.success("Approved")
                                    st.rerun()
                                except ValueError:
                                    try:
                                        mgr.submit_for_review(state.build_id)
                                        mgr.approve(state.build_id, _reviewer, _reason)
                                        st.success("Approved")
                                        st.rerun()
                                    except Exception as e2:
                                        st.error(str(e2))
                            else:
                                st.warning("Enter reviewer name")
                    with bcol2:
                        if st.button("Reject", key=f"rj_{state.build_id}"):
                            if _reviewer and _reason:
                                try:
                                    mgr.reject_with_revision(state.build_id, _reviewer, _reason)
                                    st.warning("Rejected with revision notes")
                                    st.rerun()
                                except ValueError:
                                    try:
                                        mgr.submit_for_review(state.build_id)
                                        mgr.reject_with_revision(state.build_id, _reviewer, _reason)
                                        st.warning("Rejected")
                                        st.rerun()
                                    except Exception as e2:
                                        st.error(str(e2))
                            else:
                                st.warning("Enter reviewer name and reason")
                    with bcol3:
                        if st.button("Flag", key=f"fl_{state.build_id}"):
                            try:
                                mgr.add_flag(state.build_id, _reason or "Flagged", _reviewer or "system")
                                st.error("Flagged")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

                    with st.expander("Add section comment"):
                        _sec_id = st.text_input("Section ID", key=f"sc_id_{state.build_id}")
                        _sec_comment = st.text_area("Comment", key=f"sc_txt_{state.build_id}", height=80)
                        if st.button("Save Comment", key=f"sc_btn_{state.build_id}"):
                            if _reviewer and _sec_id and _sec_comment:
                                mgr.add_section_comment(state.build_id, _sec_id, _reviewer, _sec_comment)
                                st.success("Comment saved")
                                st.rerun()
        else:
            st.info("No documents match the current filters.")

        # Reports & Export
        st.divider()
        st.subheader("Reports & Export")
        rcol1, rcol2, rcol3, rcol4 = st.columns(4)

        with rcol1:
            if st.button("Flagged Items Report", use_container_width=True):
                report = reporter.generate_flagged_report()
                st.download_button("Download", data=report.encode(), file_name="flagged_report.md",
                                   mime="text/markdown", key="dl_flagged")
        with rcol2:
            if st.button("Evidence Gap Report", use_container_width=True):
                registry = load_registry()
                conds = [registry.get(s) for s in registry.list_slugs()]
                report = reporter.generate_evidence_gap_report(conds)
                st.download_button("Download", data=report.encode(), file_name="evidence_gaps.md",
                                   mime="text/markdown", key="dl_gaps")
        with rcol3:
            if st.button("Stale Evidence Report", use_container_width=True):
                registry = load_registry()
                conds = [registry.get(s) for s in registry.list_slugs()]
                report = reporter.generate_stale_evidence_report(conds)
                st.download_button("Download", data=report.encode(), file_name="stale_evidence.md",
                                   mime="text/markdown", key="dl_stale")
        with rcol4:
            if st.button("Revision History", use_container_width=True):
                report = reporter.generate_revision_history_report()
                st.download_button("Download", data=report.encode(), file_name="revision_history.md",
                                   mime="text/markdown", key="dl_history")

        st.divider()
        if st.button("Export Approved Documents", type="primary", use_container_width=True):
            _export_dir = Path(default_output_dir) / "approved_export"
            result = reporter.export_approved_bundle(_export_dir)
            _exported = result.get("exported", [])
            if _exported:
                st.success(f"Exported {len(_exported)} approved document(s) to `{_export_dir}`")
            else:
                st.info("No approved documents to export.")

        # Pilot Metrics
        st.divider()
        st.subheader("Pilot Metrics")
        try:
            from sozo_generator.orchestration.pilot_metrics import ActivityLogger
            _pilot_logger = ActivityLogger(pilot_logs_dir)
            _pilot_metrics = _pilot_logger.compute_metrics()
            if _pilot_metrics.total_events > 0:
                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                mcol1.metric("Total Activity", _pilot_metrics.total_events)
                mcol2.metric("Reviewed", _pilot_metrics.docs_reviewed)
                mcol3.metric("Generated", _pilot_metrics.docs_generated)
                mcol4.metric("Operators", len(_pilot_metrics.unique_operators))
                if _pilot_metrics.avg_review_turnaround_hours:
                    st.markdown(f"**Avg review turnaround:** {_pilot_metrics.avg_review_turnaround_hours} hours")
                if st.button("Download Pilot Metrics", key="dl_pilot"):
                    _md = _pilot_logger.format_metrics_markdown(_pilot_metrics)
                    st.download_button("Download", data=_md.encode(), file_name="pilot_metrics.md",
                                       mime="text/markdown", key="dl_pilot_md")
            else:
                st.info("No pilot activity recorded yet. Actions in the review queue are logged automatically.")
        except Exception as e:
            st.warning(f"Pilot metrics unavailable: {e}")

        # Condition Onboarding
        st.divider()
        st.subheader("Onboard New Condition")
        _new_slug = st.text_input("Condition slug", key="onboard_slug",
                                  help="Lowercase with underscores, e.g. narcolepsy")
        _new_name = st.text_input("Display name", key="onboard_name")
        _new_icd = st.text_input("ICD-10 code", key="onboard_icd")

        if st.button("Create Draft Condition", key="create_draft_btn"):
            if _new_slug and _new_name:
                try:
                    from sozo_generator.conditions.onboarding import ConditionOnboarder
                    ob = ConditionOnboarder()
                    if ob.is_known_condition(_new_slug):
                        st.warning(f"'{_new_slug}' already exists.")
                    else:
                        draft = ob.create_draft_condition(_new_slug, _new_name, _new_icd)
                        st.success(f"Draft created: **{draft.display_name}** (evidence: {draft.overall_evidence_quality.value})")
                        st.warning("DRAFT — all generated documents require clinical review.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Enter slug and display name.")

    except ImportError as e:
        st.error(f"Module not available: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
