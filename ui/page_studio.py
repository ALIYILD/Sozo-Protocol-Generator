"""Document Studio page — agent-based job execution."""
from pathlib import Path

import streamlit as st

from ui.helpers import DOC_TYPE_LABELS, condition_options, zip_files


def render(root: Path, default_output_dir: str, reviews_dir: Path, is_cloud: bool) -> None:
    st.title("Document Studio")
    st.markdown("Upload templates, write prompts, generate documents with protocol visuals.")

    _jobs_dir = Path("/tmp/sozo_jobs") if is_cloud else root / "jobs"
    _ws_dir = Path("/tmp/sozo_workspaces") if is_cloud else root / "workspaces"
    _visuals_dir = Path("/tmp/sozo_visuals") if is_cloud else root / "outputs" / "visuals"
    _visuals_dir.mkdir(parents=True, exist_ok=True)

    try:
        import tempfile as _tmpmod
        from sozo_generator.jobs.manager import JobManager
        from sozo_generator.jobs.planner import JobPlanner
        from sozo_generator.agents.executor import AgentExecutor
        from sozo_generator.jobs.models import JobStatus
        from sozo_generator.agents.registry import list_agents
        from sozo_generator.ai.intent_parser import parse_intent_rules

        jmgr = JobManager(_jobs_dir, _ws_dir)

        for key in ("studio_result", "studio_job", "studio_log"):
            if key not in st.session_state:
                st.session_state[key] = None if key != "studio_log" else []

        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("Input")
            _tpl = st.file_uploader("Upload template or example document", type=["docx"], key="studio_tpl")
            _prompt = st.text_area(
                "What do you need?",
                height=120,
                key="studio_prompt",
                placeholder="e.g., Generate Parkinson's handbook from this template with protocol diagrams",
            )
            _auto_detect = st.toggle("Auto-detect conditions from prompt", value=True, key="studio_auto")
            if not _auto_detect:
                _conditions = st.multiselect(
                    "Select conditions",
                    [s for s, _ in condition_options()],
                    format_func=lambda s: dict(condition_options()).get(s, s),
                    key="studio_conditions",
                )
            else:
                _conditions = []
                if _prompt:
                    _intent = parse_intent_rules(_prompt)
                    if _intent.conditions:
                        st.caption(f"Detected conditions: **{', '.join(_intent.conditions)}**")

            _all_dtypes = list(DOC_TYPE_LABELS.keys())
            _doc_types = st.multiselect(
                "Document types (leave empty for auto)",
                _all_dtypes,
                format_func=lambda k: DOC_TYPE_LABELS.get(k, k),
                key="studio_dt",
            )
            _tiers = st.multiselect(
                "Tiers", ["fellow", "partners"], default=["fellow", "partners"], key="studio_tiers",
            )
            _with_visuals = st.toggle("Generate protocol visuals", value=True, key="studio_vis")
            _doc_comments = st.text_area(
                "Doctor comments (optional)", height=80, key="studio_comments",
                placeholder="e.g., Remove TPS protocols, use conservative language",
            )
            _run = st.button("Generate Documents", type="primary", use_container_width=True, key="studio_run")

        if _run and (_prompt or _conditions or _tpl):
            tpl_path = ""
            if _tpl:
                _tdir = Path(_tmpmod.mkdtemp())
                tpl_path = str(_tdir / _tpl.name)
                Path(tpl_path).write_bytes(_tpl.getvalue())

            comments = [c.strip() for c in _doc_comments.split("\n") if c.strip()] if _doc_comments else []

            if _auto_detect and _prompt:
                _intent = parse_intent_rules(_prompt)
                resolved_conditions = list(_intent.conditions) if _intent.conditions else []
            else:
                resolved_conditions = list(_conditions)

            job = jmgr.create_job(
                source_prompt=_prompt,
                target_conditions=resolved_conditions,
                target_doc_types=_doc_types if _doc_types else [],
                target_tiers=_tiers,
                template_ref=tpl_path,
                doctor_comments=comments,
            )
            planner = JobPlanner()
            plan = planner.plan(job)
            job.plan = plan
            jmgr._save_job(job)

            with right_col:
                st.subheader("Progress")
                _progress_bar = st.progress(0, text="Starting job...")
                _status_area = st.empty()
                _step_counter = [0]
                _total_tasks = max(len(plan.tasks), 1)
                _log_lines: list[str] = []

                def _studio_progress(msg: str) -> None:
                    _step_counter[0] += 1
                    _progress_bar.progress(min(_step_counter[0] / _total_tasks, 0.95), text=msg)
                    _log_lines.append(msg)

                executor = AgentExecutor(jmgr)
                result = executor.execute_job(job, progress_callback=_studio_progress)
                _progress_bar.progress(1.0, text="Complete")

            st.session_state["studio_result"] = result
            st.session_state["studio_job"] = job
            st.session_state["studio_log"] = _log_lines

            if _with_visuals and resolved_conditions:
                try:
                    from sozo_generator.agents.registry import get_agent
                    va = get_agent("visual_agent")
                    va.execute(
                        {"conditions": resolved_conditions},
                        workspace_path=str(_ws_dir / job.job_id),
                        job=job,
                    )
                except Exception as ve:
                    st.session_state["studio_log"].append(f"Visual generation warning: {ve}")

        # Right column output
        _result = st.session_state.get("studio_result")
        _s_job = st.session_state.get("studio_job")

        with right_col:
            st.subheader("Output")
            if _result is None:
                st.info("Configure your inputs on the left and click **Generate Documents** to begin.")
            else:
                if _result.status == JobStatus.AWAITING_REVIEW:
                    st.success(f"Job complete — **{_result.total_documents}** document(s) generated, awaiting review.")
                elif _result.status == JobStatus.FAILED:
                    st.error(f"Job failed: {'; '.join(_result.errors[:3])}")
                else:
                    st.info(f"Job status: {_result.status.value}")

                _docx_artifacts = [
                    Path(art.get("path", ""))
                    for art in (_result.artifacts or [])
                    if Path(art.get("path", "")).exists() and Path(art.get("path", "")).suffix == ".docx"
                ]
                _other_artifacts = [
                    Path(art.get("path", ""))
                    for art in (_result.artifacts or [])
                    if Path(art.get("path", "")).exists() and Path(art.get("path", "")).suffix != ".docx"
                ]

                if _docx_artifacts:
                    st.markdown(f"**Documents ({len(_docx_artifacts)})**")
                    for idx, fpath in enumerate(_docx_artifacts):
                        col_a, col_b = st.columns([3, 1])
                        col_a.markdown(f"{fpath.name}  ({fpath.stat().st_size / 1024:.1f} KB)")
                        with open(fpath, "rb") as f:
                            col_b.download_button(
                                "Download", data=f.read(), file_name=fpath.name,
                                key=f"studio_dl_{idx}_{fpath.stem}",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            )

                if len(_docx_artifacts) > 1:
                    _zip_map = {fp.name: fp for fp in _docx_artifacts}
                    st.download_button(
                        "Download all as ZIP", data=zip_files(_zip_map),
                        file_name="studio_documents.zip", mime="application/zip", key="studio_zip",
                    )

                # Visual gallery
                _visual_pngs: list[Path] = []
                if _s_job:
                    _ws_visuals = Path(_ws_dir / _s_job.job_id / "visuals")
                    if _ws_visuals.exists():
                        _visual_pngs = sorted(_ws_visuals.rglob("*.png"))

                if _visual_pngs:
                    st.markdown(f"**Protocol Visuals ({len(_visual_pngs)})**")
                    for i in range(0, len(_visual_pngs), 2):
                        img_cols = st.columns(2)
                        for j, col in enumerate(img_cols):
                            idx = i + j
                            if idx < len(_visual_pngs):
                                img_path = _visual_pngs[idx]
                                col.image(str(img_path), caption=img_path.stem, use_container_width=True)
                                with open(img_path, "rb") as imgf:
                                    col.download_button(
                                        f"Download {img_path.name}", data=imgf.read(),
                                        file_name=img_path.name,
                                        key=f"studio_img_{idx}_{img_path.stem}", mime="image/png",
                                    )

                if _result.warnings:
                    with st.expander("Warnings"):
                        for w in _result.warnings:
                            st.warning(w)

                _log = st.session_state.get("studio_log", [])
                if _log:
                    with st.expander("Execution Log"):
                        for line in _log:
                            st.text(line)

                # Send to Review Queue
                if _docx_artifacts and _s_job:
                    st.divider()
                    if st.button("Send to Review Queue", key="studio_review_handoff", use_container_width=True):
                        try:
                            from sozo_generator.review.manager import ReviewManager
                            rmgr = ReviewManager(reviews_dir)
                            _review_count = 0
                            for art in _result.artifacts:
                                fpath = Path(art.get("path", ""))
                                if not fpath.exists() or fpath.suffix != ".docx":
                                    continue
                                rmgr.create_review(
                                    build_id=f"{_s_job.job_id}_{fpath.stem}",
                                    condition_slug=art.get("condition", "unknown"),
                                    document_type=art.get("type", art.get("doc_type", "handbook")),
                                    tier=art.get("tier", "fellow"),
                                )
                                rmgr.submit_for_review(f"{_s_job.job_id}_{fpath.stem}")
                                _review_count += 1
                            st.success(f"Sent **{_review_count}** document(s) to the Review Queue.")
                        except Exception as rev_err:
                            st.error(f"Review handoff error: {rev_err}")

        # Recent jobs
        st.divider()
        st.subheader("Recent Jobs")
        _all_jobs = jmgr.list_jobs()
        if _all_jobs:
            for j in _all_jobs[:20]:
                _sc = {
                    "created": "gray", "running": "blue", "awaiting_review": "orange",
                    "completed": "green", "failed": "red", "canceled": "gray",
                }.get(j.status.value, "gray")
                with st.expander(f":{_sc}[{j.status.value.upper()}] {j.job_id} — {j.source_prompt[:60]}"):
                    st.markdown(f"**Created:** {j.created_at}")
                    st.markdown(f"**Conditions:** {', '.join(j.target_conditions)}")
                    st.markdown(f"**Documents:** {j.total_documents}")
                    if j.errors:
                        st.error(f"Errors: {'; '.join(j.errors[:3])}")
                    if j.artifacts:
                        st.markdown(f"**Artifacts:** {len(j.artifacts)}")
                        for art in j.artifacts:
                            fpath = Path(art.get("path", ""))
                            if fpath.exists() and fpath.suffix == ".docx":
                                with open(fpath, "rb") as f:
                                    st.download_button(
                                        f"Download {fpath.name}", data=f.read(), file_name=fpath.name,
                                        key=f"hist_{j.job_id}_{fpath.stem}",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    )
                            elif fpath.exists() and fpath.suffix == ".png":
                                st.image(str(fpath), caption=fpath.stem, width=200)
        else:
            st.info("No jobs yet. Use the input panel above to create your first document generation job.")

        st.divider()
        with st.expander("Available Agents"):
            for name in list_agents():
                from sozo_generator.agents.registry import get_agent
                a = get_agent(name)
                review_tag = " (requires review)" if a.requires_human_review else ""
                st.markdown(f"- **{a.name}**: {a.role}{review_tag}")

    except Exception as e:
        st.error(f"Studio error: {e}")
