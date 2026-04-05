"""Canonical long-document pipeline UI page."""
import json
import os
import time
from pathlib import Path
from typing import Optional

import streamlit as st

# ---------------------------------------------------------------------------
# Fallback condition slugs if the registry cannot be loaded
# ---------------------------------------------------------------------------
_FALLBACK_SLUGS = [
    "parkinsons",
    "depression",
    "anxiety",
    "ocd",
    "ptsd",
    "bipolar",
    "schizophrenia",
    "alzheimers",
    "epilepsy",
    "migraine",
    "chronic_pain",
    "fibromyalgia",
    "tinnitus",
    "stroke_rehab",
    "tbi",
    "adhd",
    "autism",
    "tourette",
    "essential_tremor",
    "dystonia",
    "cluster_headache",
    "treatment_resistant_depression",
    "anorexia",
    "addiction",
    "insomnia",
    "tinnitus_hyperacusis",
    "spinal_cord_injury",
]

_DOC_TYPE_OPTIONS = ["handbook", "protocol", "assessment", "all_in_one"]
_VARIANT_OPTIONS = ["fellow", "partners"]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render(output_dir: str = "outputs") -> None:
    """Render the Canonical Pipeline page."""
    st.title("Canonical Document Pipeline")
    st.caption(
        "Evidence-grounded long-form clinical documents — "
        "structured generation, section-by-section"
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Blueprint Viewer", "QA Report", "Demo"])

    with tab1:
        _render_generate_tab(output_dir)

    with tab2:
        _render_blueprint_tab()

    with tab3:
        _render_qa_tab()

    with tab4:
        _render_demo_tab(output_dir)


# ---------------------------------------------------------------------------
# Tab 1 — Generate
# ---------------------------------------------------------------------------

def _render_generate_tab(output_dir: str) -> None:
    """Full pipeline: select options → generate → download."""

    # Initialise session state keys
    for key in ("cp_gen_result", "cp_gen_log", "last_canonical_doc_path"):
        if key not in st.session_state:
            st.session_state[key] = None

    # ── Load condition slugs ──────────────────────────────────────────────
    slugs: list[str] = _FALLBACK_SLUGS
    try:
        from sozo_generator.conditions.registry import get_registry
        registry = get_registry()
        loaded = [c.slug for c in registry.list_all()]
        if loaded:
            slugs = loaded
    except Exception as reg_err:
        st.caption(f"Registry unavailable ({reg_err}); using fallback condition list.")

    # ── Form controls ─────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Configuration")

        condition_slug = st.selectbox(
            "Condition",
            slugs,
            index=slugs.index("parkinsons") if "parkinsons" in slugs else 0,
            key="cp_gen_condition",
        )

        variant = st.radio(
            "Variant",
            _VARIANT_OPTIONS,
            horizontal=True,
            key="cp_gen_variant",
        )

        document_type = st.radio(
            "Document type",
            _DOC_TYPE_OPTIONS,
            horizontal=True,
            key="cp_gen_doc_type",
        )

        target_pages = st.slider(
            "Target pages",
            min_value=20,
            max_value=120,
            value=60,
            step=5,
            key="cp_gen_pages",
        )

        api_key = st.text_input(
            "API key (LLM generation)",
            type="password",
            key="cp_gen_api_key",
            help="Anthropic or OpenAI key required for LLM section generation.",
        )

        skip_figures = st.checkbox(
            "Skip figure generation",
            value=False,
            key="cp_gen_skip_figures",
        )

        generate_btn = st.button(
            "Generate Document",
            type="primary",
            use_container_width=True,
            key="cp_gen_run",
        )

    # ── Generation ────────────────────────────────────────────────────────
    if generate_btn:
        if api_key:
            os.environ.setdefault("ANTHROPIC_API_KEY", api_key)

        st.session_state["cp_gen_result"] = None
        st.session_state["cp_gen_log"] = []

        with col_right:
            st.subheader("Progress")
            progress_bar = st.progress(0, text="Initialising orchestrator…")
            status_box = st.empty()
            log_lines: list[str] = []

            try:
                from sozo_generator.orchestration.document_orchestrator import (
                    DocumentOrchestrator,
                )

                orchestrator = DocumentOrchestrator(
                    output_base_dir=output_dir,
                    skip_assets=skip_figures,
                )

                # Intercept blueprint build step for progress
                original_blueprint_build = orchestrator._get("blueprint_builder").build

                def _tracked_blueprint_build(*args, **kwargs):
                    progress_bar.progress(10, text="Building blueprint…")
                    log_lines.append("Building blueprint…")
                    return original_blueprint_build(*args, **kwargs)

                progress_bar.progress(5, text="Loading condition…")
                log_lines.append(f"Loading condition: {condition_slug}")
                status_box.info(f"Condition: **{condition_slug}** | Variant: **{variant}** | Type: **{document_type}**")

                t0 = time.time()
                result = orchestrator.generate(
                    condition_slug=condition_slug,
                    variant=variant,
                    document_type=document_type,
                    target_page_count=target_pages,
                )
                duration = time.time() - t0
                log_lines.append(f"Pipeline complete in {duration:.1f}s")

                progress_bar.progress(100, text="Done!")
                st.session_state["cp_gen_result"] = result
                st.session_state["cp_gen_log"] = log_lines

                # Store canonical JSON path for QA tab
                json_path = result.output_paths.get("json")
                if json_path and Path(json_path).exists():
                    st.session_state["last_canonical_doc_path"] = json_path

            except Exception as gen_err:
                progress_bar.progress(0, text="Failed")
                st.error(f"Generation failed: {gen_err}")
                log_lines.append(f"ERROR: {gen_err}")
                st.session_state["cp_gen_log"] = log_lines

    # ── Output panel ──────────────────────────────────────────────────────
    result = st.session_state.get("cp_gen_result")

    with col_right:
        st.subheader("Output")

        if result is None:
            st.info("Configure options on the left and click **Generate Document** to begin.")
        else:
            # Status badge
            if result.success:
                qa_badge = ":green[PASS]" if result.qa_passed else ":red[FAIL]"
                st.success(
                    f"Generation complete — QA: {qa_badge}  "
                    f"| Sections: **{result.sections_generated}**  "
                    f"| Duration: **{result.duration_seconds:.1f}s**"
                )
            else:
                st.error("Generation failed.")
                for err in result.errors:
                    st.error(err)

            # Metrics row
            m1, m2, m3 = st.columns(3)
            m1.metric("Sections", result.sections_generated)
            m2.metric("Duration (s)", f"{result.duration_seconds:.1f}")
            qa_label = "PASS" if result.qa_passed else "FAIL"
            m3.metric("QA Status", qa_label)

            # Download buttons
            st.markdown("**Downloads**")
            docx_path = result.output_paths.get("docx")
            html_path = result.output_paths.get("html")

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                if docx_path and Path(docx_path).exists():
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            "Download DOCX",
                            data=f.read(),
                            file_name=Path(docx_path).name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="cp_dl_docx",
                        )
                else:
                    st.caption("DOCX not available")

            with dl_col2:
                if html_path and Path(html_path).exists():
                    with open(html_path, "rb") as f:
                        st.download_button(
                            "Download HTML",
                            data=f.read(),
                            file_name=Path(html_path).name,
                            mime="text/html",
                            key="cp_dl_html",
                        )
                else:
                    st.caption("HTML not available")

            # Warnings
            if result.warnings:
                with st.expander(f"Warnings ({len(result.warnings)})"):
                    for w in result.warnings:
                        st.warning(w)

            # Execution log
            log = st.session_state.get("cp_gen_log", [])
            if log:
                with st.expander("Execution Log"):
                    for line in log:
                        st.text(line)


# ---------------------------------------------------------------------------
# Tab 2 — Blueprint Viewer
# ---------------------------------------------------------------------------

def _render_blueprint_tab() -> None:
    """Build and display a DocumentBlueprint as an expandable section tree."""

    if "cp_bp_blueprint" not in st.session_state:
        st.session_state["cp_bp_blueprint"] = None

    slugs: list[str] = _FALLBACK_SLUGS
    try:
        from sozo_generator.conditions.registry import get_registry
        registry = get_registry()
        loaded = [c.slug for c in registry.list_all()]
        if loaded:
            slugs = loaded
    except Exception:
        pass

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Options")
        bp_condition = st.selectbox(
            "Condition",
            slugs,
            index=slugs.index("parkinsons") if "parkinsons" in slugs else 0,
            key="cp_bp_condition",
        )
        bp_variant = st.radio(
            "Variant",
            _VARIANT_OPTIONS,
            horizontal=True,
            key="cp_bp_variant",
        )
        bp_doc_type = st.radio(
            "Document type",
            _DOC_TYPE_OPTIONS,
            horizontal=True,
            key="cp_bp_doc_type",
        )
        bp_pages = st.slider(
            "Target pages",
            min_value=20,
            max_value=120,
            value=60,
            step=5,
            key="cp_bp_pages",
        )
        build_btn = st.button(
            "Build Blueprint",
            type="primary",
            use_container_width=True,
            key="cp_bp_run",
        )

    if build_btn:
        try:
            with st.spinner("Building blueprint…"):
                from sozo_generator.planning.document_blueprint_builder import (
                    DocumentBlueprintBuilder,
                )
                builder = DocumentBlueprintBuilder()
                blueprint = builder.build(
                    condition_slug=bp_condition,
                    variant=bp_variant,
                    document_type=bp_doc_type,
                    target_page_count=bp_pages,
                )
            st.session_state["cp_bp_blueprint"] = blueprint
        except Exception as bp_err:
            st.error(f"Blueprint build failed: {bp_err}")

    blueprint = st.session_state.get("cp_bp_blueprint")

    with col_right:
        if blueprint is None:
            st.info("Select options and click **Build Blueprint** to preview the document structure.")
            return

        st.subheader(f"Blueprint: {blueprint.title}")
        st.caption(blueprint.subtitle)

        # Summary metrics
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Sections", len(blueprint.sections))
        s2.metric("Target words", f"{blueprint.target_word_count:,}")
        s3.metric("Target pages", blueprint.target_page_count)
        s4.metric("Required assets", len(blueprint.required_asset_ids))

        st.divider()

        # Section tree
        for idx, section in enumerate(blueprint.sections, start=1):
            # Build expander label with word count
            label = f"{idx}. {section.title}  —  {section.target_word_count:,} words"
            with st.expander(label):
                # Subsections
                if section.subsections:
                    st.markdown("**Subsections**")
                    for sub in section.subsections:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• {sub}")

                # Asset badges
                blocks_with_type = []
                try:
                    for block in (section.blocks or []):
                        btype = getattr(block, "block_type", None)
                        if btype in ("table", "figure", "chart", "image", "diagram"):
                            blocks_with_type.append(btype)
                except Exception:
                    pass

                if blocks_with_type:
                    badge_html = " ".join(
                        f'<span style="background:#1d4ed8;color:white;padding:2px 8px;'
                        f'border-radius:12px;font-size:0.75rem;margin-right:4px">'
                        f'{bt}</span>'
                        for bt in blocks_with_type
                    )
                    st.markdown(badge_html, unsafe_allow_html=True)

                # Required asset IDs for this section
                if section.required_asset_ids:
                    st.markdown("**Required assets**")
                    for aid in section.required_asset_ids:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;`{aid}`")

        st.divider()

        # Save blueprint JSON download
        try:
            bp_json = json.dumps(blueprint.model_dump(mode="json"), indent=2, ensure_ascii=False)
            bp_filename = (
                f"blueprint_{blueprint.condition_slug}_{blueprint.variant}"
                f"_{blueprint.document_type}.json"
            )
            st.download_button(
                "Save Blueprint JSON",
                data=bp_json,
                file_name=bp_filename,
                mime="application/json",
                key="cp_bp_download",
            )
        except Exception as dump_err:
            st.warning(f"Could not serialise blueprint for download: {dump_err}")


# ---------------------------------------------------------------------------
# Tab 3 — QA Report
# ---------------------------------------------------------------------------

def _render_qa_tab() -> None:
    """Upload a canonical document JSON and run all QA validators."""

    if "cp_qa_report" not in st.session_state:
        st.session_state["cp_qa_report"] = None

    st.subheader("QA Report")

    # ── Source selection ───────────────────────────────────────────────────
    last_json_path: Optional[str] = st.session_state.get("last_canonical_doc_path")

    source_opts = ["Upload JSON file"]
    if last_json_path and Path(last_json_path).exists():
        source_opts = ["Use last generated document", "Upload JSON file"]

    source_choice = st.radio(
        "Document source",
        source_opts,
        horizontal=True,
        key="cp_qa_source",
    )

    uploaded_file = None
    doc_path_to_use: Optional[str] = None

    if source_choice == "Upload JSON file":
        uploaded_file = st.file_uploader(
            "Upload canonical document JSON",
            type=["json"],
            key="cp_qa_upload",
        )
    else:
        doc_path_to_use = last_json_path
        st.caption(f"Using: `{last_json_path}`")

    run_qa_btn = st.button(
        "Run QA Validators",
        type="primary",
        key="cp_qa_run",
    )

    if run_qa_btn:
        doc_data: Optional[dict] = None

        if source_choice == "Upload JSON file":
            if uploaded_file is None:
                st.error("Please upload a canonical document JSON file.")
                return
            try:
                doc_data = json.loads(uploaded_file.read().decode("utf-8"))
            except Exception as parse_err:
                st.error(f"Could not parse uploaded JSON: {parse_err}")
                return
        else:
            if not doc_path_to_use or not Path(doc_path_to_use).exists():
                st.error("Last generated document not found. Please upload a file instead.")
                return
            try:
                with open(doc_path_to_use, encoding="utf-8") as fh:
                    doc_data = json.load(fh)
            except Exception as load_err:
                st.error(f"Could not load document: {load_err}")
                return

        # Run QA
        try:
            with st.spinner("Running QA validators…"):
                from sozo_generator.schemas.canonical import CanonicalDocument
                from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner

                document = CanonicalDocument.model_validate(doc_data)
                runner = DocumentQARunner()
                qa_report = runner.run(document)

            st.session_state["cp_qa_report"] = qa_report
        except Exception as qa_err:
            st.error(f"QA run failed: {qa_err}")

    # ── Display report ─────────────────────────────────────────────────────
    report = st.session_state.get("cp_qa_report")
    if report is None:
        st.info("Select a document source and click **Run QA Validators** to begin.")
        return

    st.divider()

    # Overall badge
    if report.overall_passed:
        st.success("Overall result: **PASS**")
    else:
        st.error("Overall result: **FAIL**")

    # Metric row
    m1, m2, m3 = st.columns(3)
    m1.metric("Block issues", getattr(report, "block_count", 0))
    m2.metric("Warnings", getattr(report, "warning_count", 0))
    m3.metric("Info", getattr(report, "info_count", 0))

    st.divider()

    # Per-validator results
    st.markdown("**Validator Results**")
    for vr in getattr(report, "validator_results", []):
        v_label = f"{'PASS' if vr.passed else 'FAIL'} — {vr.validator_id}"
        with st.expander(v_label):
            issues = getattr(vr, "issues", [])
            if not issues:
                st.success("No issues.")
            else:
                blocks = [i for i in issues if getattr(i, "severity", "") == "block"]
                warnings = [i for i in issues if getattr(i, "severity", "") == "warning"]
                infos = [i for i in issues if getattr(i, "severity", "") not in ("block", "warning")]

                for issue in blocks:
                    loc = f" (at {issue.location})" if getattr(issue, "location", None) else ""
                    st.error(f"[BLOCK] {issue.message}{loc}")

                for issue in warnings:
                    loc = f" (at {issue.location})" if getattr(issue, "location", None) else ""
                    st.warning(f"[WARNING] {issue.message}{loc}")

                for issue in infos:
                    loc = f" (at {issue.location})" if getattr(issue, "location", None) else ""
                    st.info(f"[INFO] {issue.message}{loc}")

    st.divider()

    # Machine-readable JSON download
    try:
        report_dict = report.to_dict() if hasattr(report, "to_dict") else json.loads(
            report.model_dump_json() if hasattr(report, "model_dump_json") else "{}"
        )
        st.download_button(
            "Download QA Report JSON",
            data=json.dumps(report_dict, indent=2, default=str),
            file_name=f"qa_report_{getattr(report, 'document_id', 'unknown')}.json",
            mime="application/json",
            key="cp_qa_dl",
        )
    except Exception as dl_err:
        st.caption(f"Download not available: {dl_err}")


# ---------------------------------------------------------------------------
# Tab 4 — Demo
# ---------------------------------------------------------------------------

def _render_demo_tab(output_dir: str) -> None:
    """Pre-filled demo: parkinsons / partners / protocol. One-click run."""

    if "cp_demo_result" not in st.session_state:
        st.session_state["cp_demo_result"] = None

    DEMO_CONDITION = "parkinsons"
    DEMO_VARIANT = "partners"
    DEMO_DOC_TYPE = "protocol"
    DEMO_PAGES = 60

    st.subheader("Demo Run")
    st.markdown(
        f"Pre-filled: **{DEMO_CONDITION}** / **{DEMO_VARIANT}** / **{DEMO_DOC_TYPE}** / "
        f"**{DEMO_PAGES} pages**"
    )

    run_demo_btn = st.button(
        "Run Demo",
        type="primary",
        use_container_width=True,
        key="cp_demo_run",
    )

    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    log_placeholder = st.empty()

    if run_demo_btn:
        st.session_state["cp_demo_result"] = None
        log_lines: list[str] = []

        progress_placeholder.progress(0, text="Starting demo…")
        status_placeholder.info(
            f"Generating **{DEMO_CONDITION}** {DEMO_DOC_TYPE} ({DEMO_VARIANT})…"
        )

        try:
            from sozo_generator.orchestration.document_orchestrator import (
                DocumentOrchestrator,
            )

            with st.spinner("Running canonical pipeline…"):
                orchestrator = DocumentOrchestrator(
                    output_base_dir=output_dir,
                    skip_assets=False,
                )

                progress_placeholder.progress(10, text="Building blueprint…")
                log_lines.append("Blueprint: in progress")
                log_placeholder.code("\n".join(log_lines))

                t0 = time.time()
                result = orchestrator.generate(
                    condition_slug=DEMO_CONDITION,
                    variant=DEMO_VARIANT,
                    document_type=DEMO_DOC_TYPE,
                    target_page_count=DEMO_PAGES,
                )
                duration = time.time() - t0

            progress_placeholder.progress(100, text="Demo complete!")
            log_lines.append(f"Pipeline finished in {duration:.1f}s")
            log_lines.append(f"Sections generated: {result.sections_generated}")
            log_lines.append(f"QA passed: {result.qa_passed}")
            log_placeholder.code("\n".join(log_lines))

            st.session_state["cp_demo_result"] = result

            # Store for QA tab
            json_path = result.output_paths.get("json")
            if json_path and Path(json_path).exists():
                st.session_state["last_canonical_doc_path"] = json_path

        except Exception as demo_err:
            progress_placeholder.progress(0, text="Demo failed")
            status_placeholder.error(f"Demo failed: {demo_err}")
            log_lines.append(f"ERROR: {demo_err}")
            log_placeholder.code("\n".join(log_lines))

    # ── Demo result display ────────────────────────────────────────────────
    demo_result = st.session_state.get("cp_demo_result")
    if demo_result is None:
        return

    st.divider()

    if demo_result.success:
        qa_label = "PASS" if demo_result.qa_passed else "FAIL"
        qa_color = "green" if demo_result.qa_passed else "red"
        status_placeholder.success(
            f"Demo complete — QA: :{qa_color}[**{qa_label}**]"
        )
    else:
        status_placeholder.error("Demo generation failed.")

    # Summary metrics
    st.subheader("Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sections generated", demo_result.sections_generated)
    c2.metric("Duration (s)", f"{demo_result.duration_seconds:.1f}")
    c3.metric("QA", "PASS" if demo_result.qa_passed else "FAIL")

    # Output file links
    st.subheader("Generated Files")
    for fmt, path in demo_result.output_paths.items():
        p = Path(path)
        if p.exists():
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"**{fmt.upper()}** — `{p.name}`  ({p.stat().st_size / 1024:.1f} KB)")
            with open(p, "rb") as f:
                col_b.download_button(
                    f"Download {fmt.upper()}",
                    data=f.read(),
                    file_name=p.name,
                    key=f"cp_demo_dl_{fmt}",
                )
        else:
            st.caption(f"{fmt.upper()}: file not found at `{path}`")

    if demo_result.warnings:
        with st.expander(f"Warnings ({len(demo_result.warnings)})"):
            for w in demo_result.warnings:
                st.warning(w)

    st.info("The canonical JSON is now available for the **QA Report** tab.")
