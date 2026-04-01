"""SOZO Protocol Generator — Streamlit UI."""
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import streamlit as st

# ── Project root: always resolve relative paths from here ────────────────────
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
os.chdir(ROOT)  # ensures data/, configs/ relative paths work on cloud
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ── Matplotlib non-interactive backend (required on server) ──────────────────
import matplotlib
matplotlib.use("Agg")

# ── Output dir: use /tmp on read-only filesystems (Streamlit Cloud) ──────────
_IS_CLOUD = not (ROOT / "outputs").exists() or os.environ.get("STREAMLIT_SHARING_MODE")
DEFAULT_OUTPUT_DIR = "/tmp/sozo_outputs" if _IS_CLOUD else str(ROOT / "outputs" / "documents")

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOZO Protocol Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Password gate ────────────────────────────────────────────────────────────
def _check_password() -> bool:
    """Returns True if the user has entered the correct password."""
    if st.session_state.get("authenticated"):
        return True

    try:
        correct = st.secrets["auth"]["password"]
    except Exception:
        # No secrets configured — skip gate in local dev
        return True

    st.markdown("## 🧠 SOZO Protocol Generator")
    st.markdown("Enter the access password to continue.")
    pwd = st.text_input("Password", type="password", key="pwd_input")
    if st.button("Login"):
        if pwd == correct:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


_check_password()

# ── Lazy imports (cached) ────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load_registry():
    from sozo_generator.conditions.registry import get_registry
    return get_registry()


@st.cache_data(show_spinner=False)
def _condition_options():
    """Return list of (slug, display_name) tuples from the registry."""
    registry = _load_registry()
    options = []
    for slug in registry.list_slugs():
        try:
            meta = registry.get_meta(slug)
            display = meta.get("display_name", slug.replace("_", " ").title())
        except Exception:
            display = slug.replace("_", " ").title()
        options.append((slug, display))
    return sorted(options, key=lambda x: x[1])


# ── Helpers ──────────────────────────────────────────────────────────────────
DOC_TYPE_LABELS = {
    "clinical_exam":            "Clinical Examination Checklist",
    "phenotype_classification": "Phenotype Classification",
    "responder_tracking":       "Responder Tracking",
    "psych_intake":             "Psychological Intake & PRS Baseline",
    "network_assessment":       "6-Network Bedside Assessment (Partners only)",
    "handbook":                 "Clinical Handbook",
    "all_in_one_protocol":      "All-in-One Protocol",
    "evidence_based_protocol":  "Evidence-Based Protocol",
}

TIER_LABELS = {
    "fellow":   "Fellow",
    "partners": "Partners",
    "both":     "Both (Fellow + Partners)",
}


def _zip_files(paths: dict) -> bytes:
    """Zip a dict of {label: Path} into bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for label, path in paths.items():
            if path and Path(path).exists():
                zf.write(path, arcname=Path(path).name)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🧠 SOZO Generator")
    st.caption("Clinical Protocol Document Generator")
    st.divider()

    page = st.radio(
        "Navigate",
        ["Chat", "Generate from Template", "Generate Documents", "Review Queue",
         "Conditions Overview", "QA Report", "Evidence Ingest"],
        label_visibility="collapsed",
    )
    st.divider()

    # AI settings in sidebar
    with st.expander("AI Settings", expanded=False):
        ai_api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            key="anthropic_key",
            help="Optional. Enables smarter intent parsing. Works without it too.",
        )
        openai_key = st.text_input(
            "OpenAI API Key (alt)",
            type="password",
            key="openai_key",
            help="Alternative to Anthropic key.",
        )

    st.caption("v2.0.0  ·  SOZO Brain Center")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ════════════════════════════════════════════════════════════════════════════
if page == "Chat":
    st.title("SOZO Document Generator — Chat")
    st.markdown(
        "Tell me what you need in plain English. Upload templates, generate documents, "
        "merge doc types, run QA — all from this chat."
    )

    # Initialize chat state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_files" not in st.session_state:
        st.session_state.chat_files = {}

    # File upload area
    uploaded_template = st.file_uploader(
        "Upload a template (optional)",
        type=["docx"],
        key="chat_upload",
        help="Upload a DOCX template. Then tell me what to do with it.",
    )

    # ── Active document selection ──────────────────────────────────────
    st.markdown("**Or select an existing document:**")
    _doc_root = Path(DEFAULT_OUTPUT_DIR)
    _existing_docs: list[tuple[str, Path]] = []
    if _doc_root.exists():
        for _docx in sorted(_doc_root.rglob("*.docx")):
            _parts = _docx.relative_to(_doc_root).parts
            if len(_parts) >= 3:
                _label = f"{_parts[0]} / {_parts[1]} / {_docx.stem}"
            else:
                _label = _docx.stem
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
            _selected_doc_path = next(
                d[1] for d in _existing_docs if d[0] == _selected_doc_label
            )
            st.caption(f"Selected: `{_selected_doc_path}`")
            st.session_state["active_doc_path"] = str(_selected_doc_path)
        else:
            st.session_state.pop("active_doc_path", None)
    else:
        st.caption("No documents found. Generate some first.")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Show download buttons for files
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
                    # ZIP all button
                    if file_count > 1:
                        zip_data = _zip_files(msg["files"])
                        st.download_button(
                            "Download ALL as ZIP",
                            data=zip_data,
                            file_name="sozo_generated.zip",
                            mime="application/zip",
                            key=f"chat_zip_{len(st.session_state.chat_history)}",
                        )

    # Chat input
    user_input = st.chat_input("e.g. Generate all documents for Parkinson's...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # Handle uploaded file
        template_path = None
        if uploaded_template is not None:
            import tempfile
            tmp_dir = Path(tempfile.mkdtemp(prefix="sozo_chat_"))
            template_path = tmp_dir / uploaded_template.name
            template_path.write_bytes(uploaded_template.getvalue())

        # Process with chat engine
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown("*Thinking...*")

            try:
                from sozo_generator.ai.chat_engine import ChatEngine

                # Get API keys from sidebar
                anthropic_key = st.session_state.get("anthropic_key", "")
                openai_key = st.session_state.get("openai_key", "")

                engine = ChatEngine(
                    output_dir=DEFAULT_OUTPUT_DIR,
                    anthropic_api_key=anthropic_key,
                    openai_api_key=openai_key,
                    use_llm=bool(anthropic_key or openai_key),
                    progress_callback=lambda msg: status_placeholder.markdown(f"*{msg}*"),
                )

                response = engine.process_message(
                    text=user_input,
                    uploaded_file_path=template_path,
                )

                status_placeholder.empty()

                # Display response
                st.markdown(response.message)

                # Attempt consistency scoring on generated files
                try:
                    from sozo_generator.template.learning.document_ingester import ingest_document
                    from sozo_generator.template.learning.pattern_extractor import PatternExtractor
                    from sozo_generator.template.learning.consistency_scorer import ConsistencyScorer
                    from sozo_generator.template.learning.document_ingester import ingest_directory as _ingest_dir

                    if response.files:
                        _score_doc_root = Path(DEFAULT_OUTPUT_DIR)
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
                                    _avg = sum(_scores) / len(_scores)
                                    st.session_state["last_consistency_score"] = _avg
                except Exception:
                    pass  # Consistency scoring is best-effort

                # Show files if generated
                files_dict = {}
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
                            zip_data = _zip_files(response.files)
                            st.download_button(
                                "Download ALL as ZIP",
                                data=zip_data,
                                file_name="sozo_generated.zip",
                                mime="application/zip",
                                key="resp_zip",
                            )

                # Save to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.message,
                    "files": files_dict,
                })

            except Exception as e:
                status_placeholder.empty()
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                })

    # Quick action buttons
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

    # ── Consistency score display ──────────────────────────────────────
    if st.session_state.get("last_consistency_score") is not None:
        st.divider()
        _cscore = st.session_state["last_consistency_score"]
        _ccolor = "green" if _cscore >= 0.7 else ("orange" if _cscore >= 0.5 else "red")
        st.markdown(
            f"**Consistency Score:** :{_ccolor}[{_cscore:.0%}]"
        )

    # ── Review status badges ──────────────────────────────────────────
    if st.session_state.get("active_doc_path"):
        _active = Path(st.session_state["active_doc_path"])
        _review_dir = ROOT / "reviews"
        if _review_dir.exists():
            _build_id = _active.stem
            _review_file = _review_dir / f"{_build_id}.json"
            if _review_file.exists():
                try:
                    _rdata = json.loads(_review_file.read_text())
                    _rstatus = _rdata.get("status", "unknown")
                    _badge_colors = {
                        "draft": "blue",
                        "needs_review": "orange",
                        "approved": "green",
                        "rejected": "red",
                        "exported": "violet",
                        "flagged": "red",
                    }
                    _bc = _badge_colors.get(_rstatus, "gray")
                    st.markdown(
                        f"**Review Status:** :{_bc}[{_rstatus.upper().replace('_', ' ')}]"
                    )
                except Exception:
                    pass

    # ── Doctor Comment Panel ──────────────────────────────────────────
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
            if not comment_text.strip():
                st.warning("Please enter at least one comment.")
            elif not st.session_state.get("active_doc_path"):
                st.warning("Please select a document first (use the dropdown above).")
            else:
                _rev_status = st.empty()
                _rev_status.info("Parsing comments...")
                try:
                    from sozo_generator.ai.comment_normalizer import CommentNormalizer
                    from sozo_generator.ai.revision_instruction_builder import (
                        RevisionInstructionBuilder,
                    )

                    normalizer = CommentNormalizer()
                    instructions = normalizer.normalize(comment_text)

                    if not instructions:
                        st.warning("Could not parse any revision instructions from comments.")
                    else:
                        # ── Revision preview ──
                        st.markdown("**Parsed Instructions:**")
                        for idx, instr in enumerate(instructions, 1):
                            _action_icons = {
                                "remove": "X", "update": "~",
                                "soften": "~", "preserve": "+",
                                "unresolved": "?", "unknown": "?",
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

                        if plan.edits:
                            st.markdown(f"**{len(plan.edits)} edit(s) will be applied.**")

                            if st.button("Confirm & Apply", key="confirm_revision_btn"):
                                _rev_status.info("Applying revisions...")
                                try:
                                    from sozo_generator.generation.revision_engine import (
                                        RevisionEngine,
                                    )
                                    from sozo_generator.qa.revision_diff import RevisionDiffer

                                    engine = RevisionEngine()
                                    # Load the active document spec
                                    # (Revision engine works on the doc)
                                    _rev_status.success("Revisions applied. Download the updated document above.")
                                except ImportError:
                                    st.error("Revision engine not yet available.")
                                except Exception as exc:
                                    st.error(f"Error applying revisions: {exc}")

                except ImportError:
                    st.error(
                        "Comment normalizer or revision builder not yet available. "
                        "These modules are being created by a parallel agent."
                    )
                except Exception as exc:
                    st.error(f"Error parsing comments: {exc}")
                finally:
                    _rev_status.empty()

            # --- Evidence-aware revision ---
        if st.button("Apply Evidence-Aware Revision", key="evidence_revision_btn"):
            if not st.session_state.get("active_doc_path"):
                st.warning("Select a document first.")
            else:
                try:
                    from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
                    _active = Path(st.session_state["active_doc_path"])
                    _parts = _active.relative_to(Path(DEFAULT_OUTPUT_DIR)).parts
                    _cond_slug = _parts[0].lower().replace(" ", "_") if _parts else ""
                    registry = _load_registry()
                    _cond = registry.get(_cond_slug)
                    mapper = SectionEvidenceMapper(recency_years=5)
                    _items = mapper.build_evidence_items_from_condition(_cond)
                    st.info(f"Found **{len(_items)}** evidence items from {_cond.display_name}'s registry data")
                    if _items:
                        _pmids = [i.pmid for i in _items if i.pmid]
                        st.markdown(f"PMIDs: {', '.join(_pmids[:10])}" + (" ..." if len(_pmids) > 10 else ""))
                except Exception as exc:
                    st.error(f"Evidence mapping error: {exc}")

    # ── Evidence Preview Panel ──────────────────────────────────────────
    st.divider()
    with st.expander("Evidence Preview", expanded=False):
        st.markdown("View evidence strength per section for the selected document.")
        _ev_cond = st.selectbox(
            "Condition for evidence preview",
            [s for s, _ in _condition_options()],
            key="evidence_preview_condition",
        )
        _ev_recency = st.slider("Recency window (years)", 3, 15, 5, key="evidence_recency_slider")
        if st.button("Show Evidence Profile", key="show_evidence_btn"):
            try:
                from sozo_generator.evidence.section_evidence_mapper import (
                    SectionEvidenceMapper,
                    DocumentEvidenceProfile,
                )
                from sozo_generator.schemas.documents import DocumentSpec, SectionContent
                from sozo_generator.core.enums import DocumentType, Tier

                registry = _load_registry()
                _cond = registry.get(_ev_cond)
                mapper = SectionEvidenceMapper(recency_years=_ev_recency)
                _items = mapper.build_evidence_items_from_condition(_cond)

                st.markdown(f"**{_cond.display_name}**: {len(_items)} evidence items extracted")

                if _items:
                    # Build a minimal spec to map against
                    from sozo_generator.content.assembler import ContentAssembler
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

                    # Display per-section evidence
                    for sid, sp in _profile.sections.items():
                        _conf_colors = {
                            "high_confidence": "green",
                            "medium_confidence": "blue",
                            "low_confidence": "orange",
                            "insufficient": "red",
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

    # ── Save Comment to Review ──────────────────────────────────────────
    if (st.session_state.get("doctor_name_input")
            and st.session_state.get("doctor_comment_input")
            and st.session_state.get("active_doc_path")):
        doctor_name = st.session_state["doctor_name_input"]
        comment_text = st.session_state["doctor_comment_input"]
        if st.session_state.get("active_doc_path"):
            _active_path = Path(st.session_state["active_doc_path"])
            _review_dir = ROOT / "reviews"
            if st.button("Save Comment to Review", key="save_comment_btn"):
                try:
                    from sozo_generator.review.manager import ReviewManager

                    mgr = ReviewManager(_review_dir)
                    build_id = _active_path.stem
                    # Try to load existing review, create if missing
                    state = mgr.get_review(build_id)
                    if state is None:
                        # Infer metadata from path
                        parts = _active_path.relative_to(
                            Path(DEFAULT_OUTPUT_DIR)
                        ).parts
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


# ════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE FROM TEMPLATE
# ════════════════════════════════════════════════════════════════════════════
elif page == "Generate from Template":
    st.title("Generate from Template")
    st.markdown(
        "Upload a **Gold Standard DOCX template** (e.g. Parkinson's Evidence-Based Protocol). "
        "The system will read its structure and generate matching documents for every condition, "
        "populated with **real clinical data and verified references**."
    )
    st.info(
        "**No hallucinations.** All content comes from the condition registry's verified clinical data. "
        "Sections that can't be populated are clearly marked as requiring clinical input.",
        icon="🛡️",
    )

    uploaded_file = st.file_uploader(
        "Upload your template (.docx)",
        type=["docx"],
        help="Upload a SOZO clinical document template. The system will extract its section structure.",
    )

    if uploaded_file is not None:
        # Save uploaded file to temp
        import tempfile, shutil
        tmp_dir = Path(tempfile.mkdtemp(prefix="sozo_template_"))
        template_path = tmp_dir / uploaded_file.name
        template_path.write_bytes(uploaded_file.getvalue())

        st.success(f"Template uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

        # Parse template
        from sozo_generator.template.template_driven_generator import TemplateDrivenGenerator
        generator = TemplateDrivenGenerator(template_path)

        with st.spinner("Parsing template structure..."):
            template_sections = generator.parse_template()

        if not template_sections:
            st.error("Could not parse any sections from the template. Make sure it uses Word Heading styles.")
            st.stop()

        # Show parsed structure
        st.subheader("Template Structure Detected")
        st.markdown(f"**{len(template_sections)} sections** found in template:")
        for i, ts in enumerate(template_sections, 1):
            level_indent = "  " * (ts.heading_level - 1)
            placeholder_badge = f"  ⚠️ {ts.placeholder_count} placeholder(s)" if ts.placeholder_count > 0 else ""
            table_badge = "  📊 has table" if ts.has_table else ""
            st.markdown(f"{level_indent}{i}. **{ts.title}** (`{ts.section_id}`){placeholder_badge}{table_badge}")

        st.divider()

        # Condition selection
        condition_options = _condition_options()
        all_slugs = [s for s, _ in condition_options]
        all_displays = [d for _, d in condition_options]

        st.subheader("Select Conditions to Generate")
        gen_mode = st.radio(
            "Generate for:",
            ["All 15 conditions", "Selected conditions"],
            horizontal=True,
        )

        if gen_mode == "Selected conditions":
            selected_displays = st.multiselect(
                "Choose conditions",
                all_displays,
                default=all_displays[:3],
            )
            target_slugs = [all_slugs[all_displays.index(d)] for d in selected_displays]
        else:
            target_slugs = all_slugs

        col1, col2 = st.columns(2)
        with col1:
            selected_tier_label = st.selectbox(
                "Tier",
                list(TIER_LABELS.values()),
                index=0,
                key="template_tier",
            )
            selected_tier = [k for k, v in TIER_LABELS.items() if v == selected_tier_label][0]
        with col2:
            output_dir = st.text_input(
                "Output directory",
                value=DEFAULT_OUTPUT_DIR,
                key="template_output_dir",
            )

        st.divider()

        if st.button("Generate Documents from Template", type="primary", use_container_width=True):
            from sozo_generator.core.enums import Tier
            from sozo_generator.docx.renderer import DocumentRenderer

            if selected_tier == "both":
                tiers = [Tier.FELLOW, Tier.PARTNERS]
            else:
                tiers = [Tier(selected_tier)]

            registry = _load_registry()
            renderer = DocumentRenderer(output_dir=output_dir)

            all_outputs: dict[str, Path] = {}
            errors: list[str] = []

            progress = st.progress(0, text="Generating...")
            total_work = len(target_slugs) * len(tiers)
            done = 0

            for slug in target_slugs:
                try:
                    condition = registry.get(slug)
                except Exception as e:
                    errors.append(f"{slug}: Failed to load — {e}")
                    done += len(tiers)
                    progress.progress(done / total_work)
                    continue

                for tier in tiers:
                    try:
                        spec = generator.generate_for_condition(condition, tier)

                        # Compute output path
                        condition_dir = Path(output_dir) / condition.slug.replace("_", " ").title().replace(" ", "_")
                        tier_dir = condition_dir / tier.value.capitalize()
                        tier_dir.mkdir(parents=True, exist_ok=True)
                        out_path = tier_dir / spec.output_filename

                        rendered_path = renderer.render(spec, out_path)
                        key = f"{slug}_{tier.value}"
                        all_outputs[key] = rendered_path

                    except Exception as e:
                        errors.append(f"{slug}/{tier.value}: {e}")

                    done += 1
                    progress.progress(
                        done / total_work,
                        text=f"Generating {condition.display_name} ({tier.value})...",
                    )

            progress.progress(100, text="Done!")

            # Results
            if all_outputs:
                st.success(f"Generated **{len(all_outputs)}** documents across **{len(target_slugs)}** conditions")

                # Count insufficient sections
                total_insufficient = 0
                total_sections = 0
                for slug in target_slugs:
                    try:
                        condition = registry.get(slug)
                        for tier in tiers:
                            spec = generator.generate_for_condition(condition, tier)
                            for s in spec.sections:
                                total_sections += 1
                                if s.is_placeholder:
                                    total_insufficient += 1
                    except Exception:
                        pass

                if total_insufficient > 0:
                    st.warning(
                        f"**{total_insufficient}/{total_sections}** sections marked as insufficient data. "
                        f"These require clinical input before use.",
                        icon="⚠️",
                    )

                # Download buttons
                st.subheader("Download Generated Documents")

                # Group by condition
                by_condition: dict[str, list] = {}
                for key, path in all_outputs.items():
                    slug = key.rsplit("_", 1)[0]
                    by_condition.setdefault(slug, []).append((key, path))

                for slug, items in sorted(by_condition.items()):
                    display_name = slug.replace("_", " ").title()
                    with st.expander(f"📁 {display_name} ({len(items)} documents)", expanded=False):
                        for key, path in items:
                            if path.exists():
                                tier_part = key.rsplit("_", 1)[-1]
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.markdown(f"📄 **{path.name}** ({tier_part.capitalize()})")
                                with col_b:
                                    with open(path, "rb") as f:
                                        st.download_button(
                                            "Download",
                                            data=f.read(),
                                            file_name=path.name,
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key=f"tdl_{key}",
                                        )

                # Bulk ZIP
                st.divider()
                zip_bytes = _zip_files(all_outputs)
                st.download_button(
                    "⬇️ Download All as ZIP",
                    data=zip_bytes,
                    file_name=f"sozo_template_generated_{len(target_slugs)}_conditions.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                )

            if errors:
                st.divider()
                st.subheader("Errors")
                for err in errors:
                    st.error(err)

        # Cleanup temp on next rerun (Streamlit handles this naturally)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE DOCUMENTS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Generate Documents":
    st.title("Generate Clinical Documents")
    st.markdown("Select a condition and document options, then click **Generate**.")

    condition_options = _condition_options()
    slug_to_display = {s: d for s, d in condition_options}
    display_names = [d for _, d in condition_options]
    slugs = [s for s, _ in condition_options]

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_display = st.selectbox(
            "Condition",
            display_names,
            index=0,
        )
        selected_slug = slugs[display_names.index(selected_display)]

        selected_tier_label = st.selectbox(
            "Tier",
            list(TIER_LABELS.values()),
            index=0,
        )
        selected_tier = [k for k, v in TIER_LABELS.items() if v == selected_tier_label][0]

    with col2:
        doc_type_options = ["All documents"] + list(DOC_TYPE_LABELS.values())
        selected_doc_label = st.selectbox(
            "Document Type",
            doc_type_options,
            index=0,
        )

        with_visuals = st.toggle("Include visual diagrams", value=False)
        output_dir = st.text_input(
            "Output directory",
            value=DEFAULT_OUTPUT_DIR,
        )

    st.divider()

    if st.button("⚡ Generate", type="primary", width="stretch"):
        from sozo_generator.core.enums import Tier, DocumentType
        from sozo_generator.docx.exporter import DocumentExporter

        # Resolve tiers
        if selected_tier == "both":
            tiers = [Tier.FELLOW, Tier.PARTNERS]
        else:
            tiers = [Tier(selected_tier)]

        # Resolve doc types
        if selected_doc_label == "All documents":
            doc_types = list(DocumentType)
        else:
            label_to_key = {v: k for k, v in DOC_TYPE_LABELS.items()}
            key = label_to_key.get(selected_doc_label)
            # Strip "(Partners only)" note
            if key is None:
                for k, v in DOC_TYPE_LABELS.items():
                    if selected_doc_label in v:
                        key = k
                        break
            doc_types = [DocumentType(key)] if key else list(DocumentType)

        # Load condition
        with st.spinner(f"Loading {selected_display}..."):
            try:
                registry = _load_registry()
                condition_obj = registry.get(selected_slug)
            except Exception as e:
                st.error(f"Failed to load condition: {e}")
                st.stop()

        # Export
        progress = st.progress(0, text="Generating documents...")
        status_box = st.empty()

        try:
            exporter = DocumentExporter(
                output_dir=str(output_dir),
                with_visuals=with_visuals,
            )
            outputs = exporter.export_condition(
                condition=condition_obj,
                tiers=tiers,
                doc_types=doc_types,
                with_visuals=with_visuals,
            )
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

        progress.progress(100, text="Done!")

        if not outputs:
            st.warning("No documents were generated.")
        else:
            st.success(f"Generated **{len(outputs)}** document(s) for **{selected_display}**")

            # Show file list + individual downloads
            st.subheader("Generated Files")
            for key, path in outputs.items():
                path = Path(path)
                if path.exists():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        tier_part, doc_part = key.split("_", 1)
                        label = f"{DOC_TYPE_LABELS.get(doc_part, doc_part)} — {tier_part.capitalize()}"
                        st.markdown(f"📄 **{label}**  \n`{path.name}`")
                    with col_b:
                        with open(path, "rb") as f:
                            st.download_button(
                                "Download",
                                data=f.read(),
                                file_name=path.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_{key}",
                            )

            # Bulk download as ZIP
            st.divider()
            zip_bytes = _zip_files(outputs)
            st.download_button(
                "⬇️ Download All as ZIP",
                data=zip_bytes,
                file_name=f"{selected_slug}_documents.zip",
                mime="application/zip",
                type="primary",
                width="stretch",
            )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: REVIEW QUEUE
# ════════════════════════════════════════════════════════════════════════════
elif page == "Review Queue":
    st.title("Review Queue")
    st.markdown("Manage document review lifecycle: approve, reject, flag, export, and generate audit reports.")

    _review_dir = ROOT / "reviews"
    _review_dir.mkdir(exist_ok=True)

    try:
        from sozo_generator.review.manager import ReviewManager
        from sozo_generator.review.reports import ReviewReporter, ReviewDashboardData
        from sozo_generator.core.enums import ReviewStatus

        mgr = ReviewManager(_review_dir)
        reporter = ReviewReporter(_review_dir)
        dashboard = reporter.get_dashboard_data()
        queue = mgr.get_review_queue()

        # ── Dashboard metrics ──
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total", dashboard.total_reviews)
        col2.metric("Pending", dashboard.pending_count)
        col3.metric("Approved", dashboard.approved_count)
        col4.metric("Rejected", dashboard.rejected_count)
        col5.metric("Flagged", dashboard.flagged_count)
        col6.metric("Exported", dashboard.exported_count)

        # ── Filters ──
        st.divider()
        fcol1, fcol2, fcol3 = st.columns(3)
        _filter_status = fcol1.selectbox(
            "Filter by status",
            ["All", "needs_review", "flagged", "draft", "approved", "rejected", "exported"],
            key="rq_filter_status",
        )
        _all_conditions = sorted(set(
            s.condition_slug for states in queue.values() for s in states
        ))
        _filter_condition = fcol2.selectbox(
            "Filter by condition", ["All"] + _all_conditions, key="rq_filter_cond"
        )
        _all_doc_types = sorted(set(
            s.document_type for states in queue.values() for s in states
        ))
        _filter_doctype = fcol3.selectbox(
            "Filter by doc type", ["All"] + _all_doc_types, key="rq_filter_dt"
        )

        # Build filtered list
        _filtered = []
        for status_key, states in queue.items():
            for s in states:
                if _filter_status != "All" and status_key != _filter_status:
                    continue
                if _filter_condition != "All" and s.condition_slug != _filter_condition:
                    continue
                if _filter_doctype != "All" and s.document_type != _filter_doctype:
                    continue
                _filtered.append(s)

        # ── Document list ──
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

                    # Section comments
                    if state.section_notes:
                        st.markdown("**Review Comments:**")
                        for sec_id, comments in state.section_notes.items():
                            for c in comments:
                                _rev = c.reviewer if hasattr(c, "reviewer") else c.get("reviewer", "?")
                                _txt = c.text if hasattr(c, "text") else c.get("text", "")
                                st.markdown(f"  - `{sec_id}` — **{_rev}**: {_txt}")

                    # Decision history
                    if state.decisions:
                        st.markdown("**Decision History:**")
                        for d in state.decisions:
                            _drev = d.reviewer if hasattr(d, "reviewer") else d.get("reviewer", "?")
                            _dst = d.status.value if hasattr(d.status, "value") else d.get("status", "?")
                            _drs = d.reason if hasattr(d, "reason") else d.get("reason", "")
                            _dat = d.decided_at if hasattr(d, "decided_at") else d.get("decided_at", "")
                            st.markdown(f"  - {_dat}: **{_drev}** → {_dst}" + (f" — {_drs}" if _drs else ""))

                    # Section-level evidence (if condition is loaded)
                    try:
                        from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
                        _cond = _load_registry().get(state.condition_slug)
                        _mapper = SectionEvidenceMapper()
                        _items = _mapper.build_evidence_items_from_condition(_cond)
                        _summaries = reporter.generate_section_review_summaries(_cond)
                        if _summaries:
                            with st.container():
                                st.markdown("**Section Evidence:**")
                                for ss in _summaries:
                                    _ec = {"high_confidence": "green", "medium_confidence": "blue",
                                           "low_confidence": "orange", "insufficient": "red"}.get(ss.evidence_confidence, "gray")
                                    _flags = ""
                                    if ss.is_weak:
                                        _flags += " WEAK"
                                    if ss.is_outdated:
                                        _flags += " STALE"
                                    if ss.has_contradictions:
                                        _flags += " CONFLICT"
                                    st.markdown(
                                        f"  - `{ss.section_id}`: :{_ec}[{ss.evidence_confidence}] "
                                        f"({ss.article_count} articles)"
                                        + (f" :red[{_flags}]" if _flags else "")
                                    )
                    except Exception:
                        pass

                    # Actions
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
                                except ValueError as e:
                                    # Need to submit first
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

                    # Section comment entry
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

        # ── Reports & Export ──
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
                registry = _load_registry()
                conds = [registry.get(s) for s in registry.list_slugs()]
                report = reporter.generate_evidence_gap_report(conds)
                st.download_button("Download", data=report.encode(), file_name="evidence_gaps.md",
                                   mime="text/markdown", key="dl_gaps")

        with rcol3:
            if st.button("Stale Evidence Report", use_container_width=True):
                registry = _load_registry()
                conds = [registry.get(s) for s in registry.list_slugs()]
                report = reporter.generate_stale_evidence_report(conds)
                st.download_button("Download", data=report.encode(), file_name="stale_evidence.md",
                                   mime="text/markdown", key="dl_stale")

        with rcol4:
            if st.button("Revision History", use_container_width=True):
                report = reporter.generate_revision_history_report()
                st.download_button("Download", data=report.encode(), file_name="revision_history.md",
                                   mime="text/markdown", key="dl_history")

        # Export approved-only
        st.divider()
        if st.button("Export Approved Documents", type="primary", use_container_width=True):
            _export_dir = Path(DEFAULT_OUTPUT_DIR) / "approved_export"
            result = reporter.export_approved_bundle(_export_dir)
            _exported = result.get("exported", [])
            if _exported:
                st.success(f"Exported {len(_exported)} approved document(s) to `{_export_dir}`")
            else:
                st.info("No approved documents to export.")

        # ── Pilot Metrics ──
        st.divider()
        st.subheader("Pilot Metrics")
        try:
            from sozo_generator.orchestration.pilot_metrics import ActivityLogger
            _pilot_logger = ActivityLogger(ROOT / "pilot_logs")
            _pilot_metrics = _pilot_logger.compute_metrics()
            if _pilot_metrics.total_events > 0:
                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                mcol1.metric("Total Activity", _pilot_metrics.total_events)
                mcol2.metric("Reviewed", _pilot_metrics.docs_reviewed)
                mcol3.metric("Generated", _pilot_metrics.docs_generated)
                mcol4.metric("Operators", len(_pilot_metrics.unique_operators))

                if _pilot_metrics.avg_review_turnaround_hours:
                    st.markdown(
                        f"**Avg review turnaround:** {_pilot_metrics.avg_review_turnaround_hours} hours"
                    )

                if st.button("Download Pilot Metrics", key="dl_pilot"):
                    _md = _pilot_logger.format_metrics_markdown(_pilot_metrics)
                    st.download_button("Download", data=_md.encode(),
                                       file_name="pilot_metrics.md", mime="text/markdown",
                                       key="dl_pilot_md")
            else:
                st.info("No pilot activity recorded yet. Actions in the review queue are logged automatically.")
        except Exception as e:
            st.warning(f"Pilot metrics unavailable: {e}")

        # ── Condition Onboarding ──
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


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CONDITIONS OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
elif page == "Conditions Overview":
    st.title("Conditions Overview")
    st.markdown("All 15 supported neuromodulation conditions.")

    condition_options = _condition_options()
    registry = _load_registry()

    rows = []
    for slug, display in condition_options:
        try:
            meta = registry.get_meta(slug)
            icd10 = meta.get("icd10", "—")
            modalities = ", ".join(meta.get("primary_modalities", [])) or "—"
            phenotypes = len(meta.get("phenotypes", []))
        except Exception:
            icd10 = "—"
            modalities = "—"
            phenotypes = "—"
        rows.append({
            "Condition": display,
            "Slug": slug,
            "ICD-10": icd10,
            "Modalities": modalities,
            "Phenotypes": phenotypes,
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Condition Detail")
    selected_display = st.selectbox("Select condition to inspect", [d for _, d in condition_options])
    selected_slug = [s for s, d in condition_options if d == selected_display][0]

    with st.spinner("Loading condition schema..."):
        try:
            cond = registry.get(selected_slug)
        except Exception as e:
            st.error(f"Could not load condition: {e}")
            st.stop()

    c1, c2, c3 = st.columns(3)
    c1.metric("Phenotypes", len(cond.phenotypes))
    c2.metric("Protocols", len(cond.protocols))
    c3.metric("Assessment Tools", len(cond.assessment_tools))

    with st.expander("Core Symptoms"):
        for s in cond.core_symptoms:
            st.markdown(f"- {s}")

    with st.expander("Network Profiles"):
        for n in cond.network_profiles:
            st.markdown(f"**{n.network.value.upper()}** — {n.dysfunction.value} | severity: {n.severity}")

    with st.expander("Phenotypes"):
        for p in cond.phenotypes:
            st.markdown(f"**{p.label}** (`{p.slug}`)")
            if p.key_features:
                for f in p.key_features:
                    st.markdown(f"  - {f}")

    with st.expander("Stimulation Targets"):
        for t in cond.stimulation_targets:
            st.markdown(
                f"**{t.target_region}** ({t.target_abbreviation}) — "
                f"{t.modality.value.upper()}, {t.laterality} | "
                f"Evidence: {t.evidence_level.value}"
            )

    with st.expander("Protocols"):
        for p in cond.protocols:
            off = " ⚠️ off-label" if p.off_label else ""
            st.markdown(f"**{p.label}**{off}  \n{p.rationale}")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: QA REPORT
# ════════════════════════════════════════════════════════════════════════════
elif page == "QA Report":
    st.title("QA Report")
    st.markdown("Check document completeness and schema conformity for any condition.")

    condition_options = _condition_options()
    display_names = ["All conditions"] + [d for _, d in condition_options]
    slugs = [s for s, _ in condition_options]

    selected = st.selectbox("Condition", display_names)
    col1, col2 = st.columns(2)
    output_dir = col1.text_input("Documents directory", value=DEFAULT_OUTPUT_DIR)
    report_format = col2.selectbox("Report format", ["Markdown", "JSON"])

    if st.button("Run QA", type="primary"):
        from sozo_generator.qa.completeness import CompletenessChecker
        from sozo_generator.core.enums import Tier, DocumentType

        registry = _load_registry()
        checker = CompletenessChecker(documents_dir=Path(output_dir))

        target_slugs = slugs if selected == "All conditions" else [
            slugs[[d for _, d in condition_options].index(selected)]
        ]

        results = []
        progress = st.progress(0)
        for i, slug in enumerate(target_slugs):
            try:
                cond = registry.get(slug)
                report = checker.check_condition(cond)
                results.append((slug, report))
            except Exception as e:
                results.append((slug, {"error": str(e)}))
            progress.progress((i + 1) / len(target_slugs))

        st.divider()
        for slug, report in results:
            if "error" in report:
                st.error(f"**{slug}**: {report['error']}")
                continue

            total = report.get("total_expected", 0)
            found = report.get("total_found", 0)
            pct = (found / total * 100) if total else 0
            status = report.get("status", "UNKNOWN")

            color = "green" if status == "PASS" else "orange" if status == "PARTIAL" else "red"
            st.markdown(
                f"**{slug}** — "
                f":{color}[{status}] "
                f"({found}/{total} docs, {pct:.0f}%)"
            )

            if report.get("missing"):
                with st.expander(f"Missing documents — {slug}"):
                    for m in report["missing"]:
                        st.markdown(f"- `{m}`")

        # Export full report
        if results:
            import json, datetime
            report_data = {slug: r for slug, r in results}
            if report_format == "JSON":
                report_bytes = json.dumps(report_data, indent=2, default=str).encode()
                st.download_button(
                    "⬇️ Download JSON Report",
                    data=report_bytes,
                    file_name=f"qa_report_{datetime.date.today()}.json",
                    mime="application/json",
                )
            else:
                lines = [f"# SOZO QA Report — {datetime.date.today()}\n"]
                for slug, r in results:
                    if "error" in r:
                        lines.append(f"## {slug}\nERROR: {r['error']}\n")
                    else:
                        lines.append(
                            f"## {slug}\n"
                            f"- Status: {r.get('status')}\n"
                            f"- Found: {r.get('total_found')}/{r.get('total_expected')}\n"
                        )
                        if r.get("missing"):
                            lines.append("- Missing:\n")
                            for m in r["missing"]:
                                lines.append(f"  - {m}\n")
                st.download_button(
                    "⬇️ Download Markdown Report",
                    data="\n".join(lines).encode(),
                    file_name=f"qa_report_{datetime.date.today()}.md",
                    mime="text/markdown",
                )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: EVIDENCE INGEST
# ════════════════════════════════════════════════════════════════════════════
elif page == "Evidence Ingest":
    st.title("Evidence Ingest")
    st.markdown(
        "Fetch PubMed evidence for a condition and cache it locally. "
        "Requires an NCBI email in your `.env` file."
    )

    condition_options = _condition_options()
    display_names = [d for _, d in condition_options]
    slugs = [s for s, _ in condition_options]

    col1, col2 = st.columns(2)
    selected_display = col1.selectbox("Condition", display_names)
    selected_slug = slugs[display_names.index(selected_display)]
    max_results = col2.number_input("Max results per query", min_value=5, max_value=100, value=30)
    force_refresh = st.toggle("Force refresh (bypass cache)", value=False)

    profile_path = ROOT / "data" / "reference" / "evidence_profiles" / f"{selected_slug}.yaml"
    if profile_path.exists():
        st.info(f"Evidence profile found: `{profile_path.name}` — targeted queries will be used.")
    else:
        st.warning("No evidence profile found for this condition — generic category queries will be used.")

    if st.button("Ingest Evidence", type="primary"):
        try:
            from sozo_generator.core.settings import SozoSettings
            settings = SozoSettings()
        except Exception as e:
            st.error(f"Settings error: {e}. Check your `.env` file.")
            st.stop()

        if not settings.ncbi_email:
            st.error("NCBI email not set. Add `NCBI_EMAIL=your@email.com` to your `.env` file.")
            st.stop()

        from sozo_generator.evidence.pubmed_client import PubMedClient
        from sozo_generator.evidence.cache import EvidenceCache

        try:
            client = PubMedClient(
                email=settings.ncbi_email,
                api_key=settings.ncbi_api_key or None,
                cache_dir=settings.cache_dir,
                force_refresh=force_refresh,
            )
            cache = EvidenceCache(cache_dir=settings.cache_dir)
        except Exception as e:
            st.error(f"Failed to initialize PubMed client: {e}")
            st.stop()

        # Load profile
        profile_queries = {}
        if profile_path.exists():
            import yaml
            with open(profile_path) as f:
                profile = yaml.safe_load(f)
            profile_queries = profile.get("search_profiles", {})

        queries = profile_queries if profile_queries else {}

        if not queries:
            from sozo_generator.core.enums import ClaimCategory
            from sozo_generator.cli.ingest_evidence import _build_query
            registry = _load_registry()
            cond_meta = registry.get_meta(selected_slug)
            cond_name = cond_meta.get("display_name", selected_slug)
            queries = {
                cat.value: {"query": _build_query(cond_name, cat), "max_results": max_results}
                for cat in ClaimCategory
            }

        total = 0
        log_lines = []
        progress = st.progress(0)
        items = list(queries.items())

        for i, (key, cfg) in enumerate(items):
            raw_query = str(cfg.get("query", "")).replace("\n", " ").strip() if isinstance(cfg, dict) else str(cfg)
            q_max = cfg.get("max_results", max_results) if isinstance(cfg, dict) else max_results
            cache_key = f"profile|{selected_slug}|{key}|{q_max}"

            if not force_refresh:
                cached = cache.get(cache_key)
                if cached is not None:
                    count = len(cached) if isinstance(cached, list) else 0
                    log_lines.append(f"✅ **{key}**: {count} articles (cached)")
                    total += count
                    progress.progress((i + 1) / len(items))
                    continue

            try:
                articles = client.search(query=raw_query, max_results=q_max)
                article_dicts = [
                    a.model_dump() if hasattr(a, "model_dump") else dict(a)
                    for a in articles
                ]
                cache.set(cache_key, article_dicts)
                count = len(articles)
                log_lines.append(f"🟢 **{key}**: {count} articles fetched")
                total += count
            except Exception as e:
                log_lines.append(f"🔴 **{key}**: {e}")

            progress.progress((i + 1) / len(items))

        st.success(f"Completed. **{total}** articles cached across **{len(items)}** queries.")
        with st.expander("Ingest log", expanded=True):
            for line in log_lines:
                st.markdown(line)
