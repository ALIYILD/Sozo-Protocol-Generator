"""Chat page — plain-English document generation via ChatEngine."""
import json
from pathlib import Path

import streamlit as st

from ui.helpers import condition_options, load_registry, zip_files


def render(default_output_dir: str, reviews_dir: Path, pilot_logs_dir: Path) -> None:
    st.title("SOZO Document Generator — Chat")
    st.markdown(
        "Tell me what you need in plain English. Upload templates, generate documents, "
        "merge doc types, run QA — all from this chat."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_files" not in st.session_state:
        st.session_state.chat_files = {}

    uploaded_template = st.file_uploader(
        "Upload a template (optional)",
        type=["docx"],
        key="chat_upload",
        help="Upload a DOCX template. Then tell me what to do with it.",
    )

    # Existing document selector
    st.markdown("**Or select an existing document:**")
    _doc_root = Path(default_output_dir)
    _existing_docs: list[tuple[str, Path]] = []
    if _doc_root.exists():
        for _docx in sorted(_doc_root.rglob("*.docx")):
            _parts = _docx.relative_to(_doc_root).parts
            _label = f"{_parts[0]} / {_parts[1]} / {_docx.stem}" if len(_parts) >= 3 else _docx.stem
            _existing_docs.append((_label, _docx))
    if _existing_docs:
        _doc_labels = ["(none)"] + [d[0] for d in _existing_docs]
        _selected_doc_label = st.selectbox(
            "Existing documents",
            _doc_labels,
            key="chat_existing_doc",
            label_visibility="collapsed",
        )
        if _selected_doc_label != "(none)":
            _selected_doc_path = next(d[1] for d in _existing_docs if d[0] == _selected_doc_label)
            st.caption(f"Selected: `{_selected_doc_path}`")
            st.session_state["active_doc_path"] = str(_selected_doc_path)
        else:
            st.session_state.pop("active_doc_path", None)
    else:
        st.caption("No documents found. Generate some first.")

    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("files"):
                file_count = len(msg["files"])
                with st.expander(f"Download {file_count} generated file(s)", expanded=False):
                    for label, fpath in msg["files"].items():
                        fpath = Path(fpath)
                        if fpath.exists():
                            with open(fpath, "rb") as f:
                                st.download_button(
                                    f"Download {fpath.name}",
                                    data=f.read(),
                                    file_name=fpath.name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"chat_dl_{label}_{len(st.session_state.chat_history)}",
                                )
                    if file_count > 1:
                        st.download_button(
                            "Download ALL as ZIP",
                            data=zip_files(msg["files"]),
                            file_name="sozo_generated.zip",
                            mime="application/zip",
                            key=f"chat_zip_{len(st.session_state.chat_history)}",
                        )

    # Chat input
    user_input = st.chat_input("e.g. Generate all documents for Parkinson's...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        template_path = None
        if uploaded_template is not None:
            import tempfile
            tmp_dir = Path(tempfile.mkdtemp(prefix="sozo_chat_"))
            template_path = tmp_dir / uploaded_template.name
            template_path.write_bytes(uploaded_template.getvalue())

        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown("*Thinking...*")
            try:
                from sozo_generator.ai.chat_engine import ChatEngine
                engine = ChatEngine(
                    output_dir=default_output_dir,
                    anthropic_api_key=st.session_state.get("anthropic_key", ""),
                    openai_api_key=st.session_state.get("openai_key", ""),
                    use_llm=bool(
                        st.session_state.get("anthropic_key") or st.session_state.get("openai_key")
                    ),
                    progress_callback=lambda msg: status_placeholder.markdown(f"*{msg}*"),
                )
                response = engine.process_message(text=user_input, uploaded_file_path=template_path)
                status_placeholder.empty()
                st.markdown(response.message)

                # Best-effort consistency scoring
                _try_consistency_scoring(response, default_output_dir)

                files_dict: dict[str, str] = {}
                if response.files:
                    file_count = len(response.files)
                    st.success(f"{file_count} file(s) generated")
                    with st.expander(f"Download {file_count} file(s)", expanded=True):
                        for label, fpath in response.files.items():
                            fpath = Path(fpath)
                            if fpath.exists():
                                files_dict[label] = str(fpath)
                                with open(fpath, "rb") as f:
                                    st.download_button(
                                        f"Download {fpath.name}",
                                        data=f.read(),
                                        file_name=fpath.name,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key=f"resp_dl_{label}",
                                    )
                        if file_count > 1:
                            st.download_button(
                                "Download ALL as ZIP",
                                data=zip_files(response.files),
                                file_name="sozo_generated.zip",
                                mime="application/zip",
                                key="resp_zip",
                            )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.message,
                    "files": files_dict,
                })
            except Exception as e:
                status_placeholder.empty()
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

    # Quick actions
    st.divider()
    st.markdown("**Quick actions:**")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        if st.button("Generate all 15 conditions", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Generate all documents for all 15 conditions"})
            st.rerun()
    with qcol2:
        if st.button("List conditions", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "List all conditions"})
            st.rerun()
    with qcol3:
        if st.button("Run QA on all", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "Run QA on all conditions"})
            st.rerun()
    with qcol4:
        if st.button("Help", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": "help"})
            st.rerun()

    # Consistency score
    if st.session_state.get("last_consistency_score") is not None:
        st.divider()
        _cscore = st.session_state["last_consistency_score"]
        _ccolor = "green" if _cscore >= 0.7 else ("orange" if _cscore >= 0.5 else "red")
        st.markdown(f"**Consistency Score:** :{_ccolor}[{_cscore:.0%}]")

    # Review status badge
    _render_review_status_badge(reviews_dir)

    # Doctor Comment Panel
    st.divider()
    with st.expander("Doctor Comment Panel", expanded=False):
        doctor_name = st.text_input("Reviewer name", key="doctor_name_input")
        comment_text = st.text_area(
            "Clinical comments / revision instructions",
            height=150,
            key="doctor_comment_input",
            placeholder=(
                "Examples:\n"
                "- Remove TPS protocols\n"
                "- Update the safety section with more conservative language\n"
                "- Keep the inclusion criteria unchanged"
            ),
        )
        if st.button("Apply Revision", key="apply_revision_btn"):
            _handle_revision(doctor_name, comment_text, default_output_dir, pilot_logs_dir)

        if st.button("Apply Evidence-Aware Revision", key="evidence_revision_btn"):
            _handle_evidence_revision(default_output_dir)

    # Evidence Preview Panel
    st.divider()
    with st.expander("Evidence Preview", expanded=False):
        _render_evidence_preview()

    # Save Comment to Review
    _render_save_comment(reviews_dir, default_output_dir)


# ── Private helpers ──────────────────────────────────────────────────────────

def _try_consistency_scoring(response, default_output_dir: str) -> None:
    try:
        from sozo_generator.template.learning.document_ingester import ingest_document, ingest_directory as _ingest_dir
        from sozo_generator.template.learning.pattern_extractor import PatternExtractor
        from sozo_generator.template.learning.consistency_scorer import ConsistencyScorer
        from pathlib import Path

        if response.files:
            _score_doc_root = Path(default_output_dir)
            if _score_doc_root.exists():
                _all_fps = _ingest_dir(_score_doc_root)
                if len(_all_fps) >= 5:
                    _extractor = PatternExtractor(_all_fps)
                    _profile = _extractor.extract_master_profile()
                    _scorer = ConsistencyScorer(_profile)
                    _scores = []
                    for _fp_path in response.files.values():
                        _fp_path = Path(_fp_path)
                        if _fp_path.exists() and _fp_path.suffix == ".docx":
                            try:
                                _fp = ingest_document(_fp_path)
                                _rep = _scorer.score_document(_fp)
                                _scores.append(_rep.overall_score)
                            except Exception:
                                pass
                    if _scores:
                        st.session_state["last_consistency_score"] = sum(_scores) / len(_scores)
    except Exception:
        pass


def _render_review_status_badge(reviews_dir: Path) -> None:
    if not st.session_state.get("active_doc_path"):
        return
    _active = Path(st.session_state["active_doc_path"])
    _review_file = reviews_dir / f"{_active.stem}.json"
    if not _review_file.exists():
        return
    try:
        _rdata = json.loads(_review_file.read_text())
        _rstatus = _rdata.get("status", "unknown")
        _badge_colors = {
            "draft": "blue", "needs_review": "orange", "approved": "green",
            "rejected": "red", "exported": "violet", "flagged": "red",
        }
        _bc = _badge_colors.get(_rstatus, "gray")
        st.markdown(f"**Review Status:** :{_bc}[{_rstatus.upper().replace('_', ' ')}]")
    except Exception:
        pass


def _handle_revision(doctor_name: str, comment_text: str, default_output_dir: str, pilot_logs_dir: Path) -> None:
    if not comment_text.strip():
        st.warning("Please enter at least one comment.")
        return
    if not st.session_state.get("active_doc_path"):
        st.warning("Please select a document first (use the dropdown above).")
        return

    _rev_status = st.empty()
    _rev_status.info("Parsing comments...")
    try:
        from sozo_generator.ai.comment_normalizer import CommentNormalizer
        from sozo_generator.ai.revision_instruction_builder import RevisionInstructionBuilder

        normalizer = CommentNormalizer()
        instructions = normalizer.normalize(comment_text)

        if not instructions:
            st.warning("Could not parse any revision instructions from comments.")
            return

        st.markdown("**Parsed Instructions:**")
        for idx, instr in enumerate(instructions, 1):
            _action_icons = {
                "remove": "X", "update": "~", "soften": "~",
                "preserve": "+", "unresolved": "?", "unknown": "?",
            }
            _icon = _action_icons.get(instr.action, "-")
            st.markdown(
                f"{idx}. [{_icon}] **{instr.action}** — "
                f"{instr.target or instr.section_id or 'general'}"
            )

        builder = RevisionInstructionBuilder()
        plan = builder.build(instructions)

        if plan.conflicts:
            st.warning(
                f"{len(plan.conflicts)} conflicting instruction(s) detected. "
                "Please review and clarify."
            )
            for c in plan.conflicts:
                st.markdown(f"- Conflict: {c}")

        _total_edits = (
            len(plan.section_edits) + len(plan.sections_to_remove)
            + len(plan.tone_adjustments) + len(plan.modality_changes)
        )
        if _total_edits > 0:
            st.markdown(f"**{_total_edits} edit(s) will be applied.**")
            if st.button("Confirm & Apply Revision", key="confirm_revision_btn"):
                _apply_revision(plan, _total_edits, doctor_name, default_output_dir, pilot_logs_dir, _rev_status)
        else:
            st.info("No concrete edits to apply. Comments noted for review.")

    except ImportError:
        st.error(
            "Comment normalizer or revision builder not yet available. "
            "These modules are being created by a parallel agent."
        )
    except Exception as exc:
        st.error(f"Error parsing comments: {exc}")
    finally:
        _rev_status.empty()


def _apply_revision(plan, total_edits: int, doctor_name: str, default_output_dir: str, pilot_logs_dir: Path, _rev_status) -> None:
    _rev_status.info("Applying revisions...")
    try:
        from sozo_generator.generation.revision_engine import RevisionEngine
        from sozo_generator.qa.revision_diff import RevisionDiffGenerator
        from sozo_generator.content.assembler import ContentAssembler
        from sozo_generator.docx.renderer import DocumentRenderer
        from sozo_generator.schemas.documents import DocumentSpec
        from sozo_generator.core.enums import DocumentType, Tier
        from pathlib import Path

        _active = Path(st.session_state["active_doc_path"])
        _parts = _active.relative_to(Path(default_output_dir)).parts
        _cond_slug = _parts[0].lower().replace(" ", "_") if _parts else ""
        _tier_str = _parts[1].lower() if len(_parts) > 1 else "fellow"
        _tier = Tier.FELLOW if "fellow" in _tier_str else Tier.PARTNERS

        _registry = load_registry()
        _cond = _registry.get(_cond_slug)
        _assembler = ContentAssembler()
        _sections = _assembler.assemble(_cond, DocumentType.EVIDENCE_BASED_PROTOCOL, _tier)
        _orig_spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=_tier,
            condition_slug=_cond.slug,
            condition_name=_cond.display_name,
            title=f"Revised — {_cond.display_name}",
            sections=_sections,
            references=_cond.references or [],
        )
        _engine = RevisionEngine()
        _revised, _summary = _engine.apply_revision(_orig_spec, plan, _cond)

        _differ = RevisionDiffGenerator()
        _diff = _differ.generate_diff(_orig_spec, _revised)

        st.markdown("**Revision Summary:**")
        st.markdown(f"- Modified: {_diff.total_modified}")
        st.markdown(f"- Removed: {_diff.total_removed}")
        st.markdown(f"- Unchanged: {_diff.total_unchanged}")
        if _summary.tone_changes:
            st.markdown(f"- Tone adjustments: {_summary.tone_changes}")

        with st.expander("Section-level diff", expanded=True):
            for sd in _diff.section_diffs:
                if sd.change_type == "modified":
                    st.markdown(f"  ~ **{sd.section_id}**: {sd.detail}")
                elif sd.change_type == "removed":
                    st.markdown(f"  - ~~{sd.section_id}~~: removed")
                elif sd.change_type == "added":
                    st.markdown(f"  + **{sd.section_id}**: added")

        _out_dir = Path(default_output_dir) / _cond.slug / "Revised"
        _out_dir.mkdir(parents=True, exist_ok=True)
        _revised.output_filename = f"{_cond.slug}_revised_{_tier.value}.docx"
        _out_path = _out_dir / _revised.output_filename
        _renderer = DocumentRenderer(output_dir=str(Path(default_output_dir)))
        _rendered = _renderer.render(_revised, _out_path)

        _rev_status.empty()
        st.success(f"Revised document generated: {_rendered.name}")
        with open(_rendered, "rb") as _f:
            st.download_button(
                "Download Revised Document",
                data=_f.read(),
                file_name=_rendered.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_revised_doc",
            )

        try:
            from sozo_generator.orchestration.pilot_metrics import ActivityLogger
            _al = ActivityLogger(pilot_logs_dir)
            _al.log("revision", operator=doctor_name, build_id=_active.stem,
                    condition_slug=_cond.slug, detail=f"{total_edits} edits applied")
        except Exception:
            pass

    except Exception as exc:
        _rev_status.empty()
        st.error(f"Error applying revisions: {exc}")


def _handle_evidence_revision(default_output_dir: str) -> None:
    if not st.session_state.get("active_doc_path"):
        st.warning("Select a document first.")
        return
    try:
        from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
        from pathlib import Path

        _active = Path(st.session_state["active_doc_path"])
        _parts = _active.relative_to(Path(default_output_dir)).parts
        _cond_slug = _parts[0].lower().replace(" ", "_") if _parts else ""
        registry = load_registry()
        _cond = registry.get(_cond_slug)
        mapper = SectionEvidenceMapper(recency_years=5)
        _items = mapper.build_evidence_items_from_condition(_cond)
        st.info(f"Found **{len(_items)}** evidence items from {_cond.display_name}'s registry data")
        if _items:
            _pmids = [i.pmid for i in _items if i.pmid]
            st.markdown(f"PMIDs: {', '.join(_pmids[:10])}" + (" ..." if len(_pmids) > 10 else ""))
    except Exception as exc:
        st.error(f"Evidence mapping error: {exc}")


def _render_evidence_preview() -> None:
    st.markdown("View evidence strength per section for the selected document.")
    _ev_cond = st.selectbox(
        "Condition for evidence preview",
        [s for s, _ in condition_options()],
        key="evidence_preview_condition",
    )
    _ev_recency = st.slider("Recency window (years)", 3, 15, 5, key="evidence_recency_slider")
    if st.button("Show Evidence Profile", key="show_evidence_btn"):
        try:
            from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
            from sozo_generator.schemas.documents import DocumentSpec
            from sozo_generator.core.enums import DocumentType, Tier
            from sozo_generator.content.assembler import ContentAssembler

            registry = load_registry()
            _cond = registry.get(_ev_cond)
            mapper = SectionEvidenceMapper(recency_years=_ev_recency)
            _items = mapper.build_evidence_items_from_condition(_cond)
            st.markdown(f"**{_cond.display_name}**: {len(_items)} evidence items extracted")

            if _items:
                assembler = ContentAssembler()
                _sections = assembler.assemble(_cond, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW)
                _spec = DocumentSpec(
                    document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
                    tier=Tier.FELLOW,
                    condition_slug=_cond.slug,
                    condition_name=_cond.display_name,
                    title="Evidence Preview",
                    sections=_sections,
                )
                _profile = mapper.map_to_sections(_spec, _items)
                for sid, sp in _profile.sections.items():
                    _conf_colors = {
                        "high_confidence": "green", "medium_confidence": "blue",
                        "low_confidence": "orange", "insufficient": "red",
                    }
                    _color = _conf_colors.get(sp.confidence, "gray")
                    _warn = ""
                    if sp.has_contradictions:
                        _warn = " | CONFLICTING"
                    if sp.needs_review:
                        _warn += " | NEEDS REVIEW"
                    st.markdown(
                        f"- **{sid}**: :{_color}[{sp.confidence}] "
                        f"({sp.article_count} articles, "
                        f"newest {sp.newest_year or '?'}"
                        f"{_warn})"
                    )
                if _profile.weak_sections:
                    st.warning(f"Weak evidence in: {', '.join(_profile.weak_sections)}")
                if _profile.outdated_sections:
                    st.warning(f"Outdated evidence in: {', '.join(_profile.outdated_sections)}")
                if _profile.conflicting_sections:
                    st.warning(f"Conflicting evidence in: {', '.join(_profile.conflicting_sections)}")
            else:
                st.info("No evidence items found in condition registry.")
        except Exception as exc:
            st.error(f"Evidence preview error: {exc}")


def _render_save_comment(reviews_dir: Path, default_output_dir: str) -> None:
    if not (
        st.session_state.get("doctor_name_input")
        and st.session_state.get("doctor_comment_input")
        and st.session_state.get("active_doc_path")
    ):
        return
    doctor_name = st.session_state["doctor_name_input"]
    comment_text = st.session_state["doctor_comment_input"]
    _active_path = Path(st.session_state["active_doc_path"])
    if st.button("Save Comment to Review", key="save_comment_btn"):
        try:
            from sozo_generator.review.manager import ReviewManager
            mgr = ReviewManager(reviews_dir)
            build_id = _active_path.stem
            state = mgr.get_review(build_id)
            if state is None:
                parts = _active_path.relative_to(Path(default_output_dir)).parts
                _cond = parts[0] if len(parts) > 0 else "unknown"
                _tier = parts[1] if len(parts) > 1 else "unknown"
                state = mgr.create_review(
                    build_id=build_id,
                    condition_slug=_cond,
                    document_type="unknown",
                    tier=_tier,
                )
            mgr.add_section_comment(
                build_id=build_id,
                section_id="general",
                reviewer=doctor_name,
                text=comment_text,
            )
            st.success(f"Comment saved by {doctor_name}.")
        except Exception as exc:
            st.error(f"Error saving comment: {exc}")
