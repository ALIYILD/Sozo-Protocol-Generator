"""Evidence Ingest page — PubMed ingestion and staleness checks."""
from pathlib import Path

import streamlit as st

from ui.helpers import condition_options, load_registry


def render(root: Path) -> None:
    st.title("Evidence Ingest")
    st.markdown(
        "Fetch PubMed evidence for a condition and cache it locally. "
        "Requires an NCBI email in your `.env` file."
    )

    cond_opts = condition_options()
    display_names = [d for _, d in cond_opts]
    slugs = [s for s, _ in cond_opts]

    col1, col2 = st.columns(2)
    selected_display = col1.selectbox("Condition", display_names)
    selected_slug = slugs[display_names.index(selected_display)]
    max_results = col2.number_input("Max results per query", min_value=5, max_value=100, value=30)
    force_refresh = st.toggle("Force refresh (bypass cache)", value=False)

    profile_path = root / "data" / "reference" / "evidence_profiles" / f"{selected_slug}.yaml"
    if profile_path.exists():
        st.info(f"Evidence profile found: `{profile_path.name}` — targeted queries will be used.")
    else:
        st.warning("No evidence profile found for this condition — generic category queries will be used.")

    if st.button("Ingest Evidence", type="primary"):
        _run_ingest(selected_slug, max_results, force_refresh, profile_path)

    # Staleness Check
    st.divider()
    st.subheader("Evidence Staleness Check")
    _stale_recency = st.slider("Recency window (years)", 1, 15, 5, key="stale_recency")
    if st.button("Check Evidence Staleness", key="check_stale_btn"):
        try:
            from sozo_generator.evidence.refresh import EvidenceRefresher
            _refresher = EvidenceRefresher(recency_years=_stale_recency)
            _cond = load_registry().get(selected_slug)
            _result = _refresher.assess_staleness(_cond)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Items", _result.total_items)
            col_b.metric("Fresh", _result.fresh_items)
            col_c.metric("Stale", _result.stale_items)

            if _result.stale_sections:
                st.warning(f"Stale sections: {', '.join(_result.stale_sections)}")
            if _result.qa_rerun_needed:
                st.error("Evidence is substantially stale — QA re-run recommended.")
                if st.button("Re-run QA", key="rerun_qa_btn"):
                    _result2 = _refresher.refresh_and_rerun_qa(_cond)
                    if _result2.qa_report:
                        _result2.qa_report.compute_counts()
                        _qa_status = (
                            "PASS" if _result2.qa_report.passed
                            else f"FAIL ({_result2.qa_report.block_count} blocks)"
                        )
                        st.markdown(f"QA result: **{_qa_status}**, {_result2.qa_report.warning_count} warnings")
            else:
                st.success("Evidence is reasonably current.")
        except Exception as e:
            st.error(f"Staleness check failed: {e}")

    # Live Refresh Status
    st.divider()
    st.subheader("Live Refresh Status")
    try:
        from sozo_generator.evidence.live_refresh import LiveEvidenceRefresher
        _lr = LiveEvidenceRefresher()
        if _lr.is_live_available:
            st.success("Live PubMed refresh is available (Biopython installed).")
        else:
            st.info(
                "Live PubMed refresh is **not available** — Biopython is not installed. "
                "The system uses cached evidence data. Install `biopython` to enable live refresh."
            )
    except Exception:
        st.info("Live refresh status could not be determined.")


def _run_ingest(selected_slug: str, max_results: int, force_refresh: bool, profile_path: Path) -> None:
    try:
        from sozo_generator.core.settings import SozoSettings
        settings = SozoSettings()
    except Exception as e:
        st.error(f"Settings error: {e}. Check your `.env` file.")
        return

    if not settings.ncbi_email:
        st.error("NCBI email not set. Add `NCBI_EMAIL=your@email.com` to your `.env` file.")
        return

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
        return

    profile_queries: dict = {}
    if profile_path.exists():
        import yaml
        with open(profile_path) as f:
            profile = yaml.safe_load(f)
        profile_queries = profile.get("search_profiles", {})

    queries = profile_queries or {}
    if not queries:
        from sozo_generator.core.enums import ClaimCategory
        from sozo_generator.cli.ingest_evidence import _build_query
        cond_meta = load_registry().get_meta(selected_slug)
        cond_name = cond_meta.get("display_name", selected_slug)
        queries = {
            cat.value: {"query": _build_query(cond_name, cat), "max_results": max_results}
            for cat in ClaimCategory
        }

    total = 0
    log_lines: list[str] = []
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
                log_lines.append(f"**{key}**: {count} articles (cached)")
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
            log_lines.append(f"**{key}**: {count} articles fetched")
            total += count
        except Exception as e:
            log_lines.append(f"**{key}**: {e}")

        progress.progress((i + 1) / len(items))

    st.success(f"Completed. **{total}** articles cached across **{len(items)}** queries.")
    with st.expander("Ingest log", expanded=True):
        for line in log_lines:
            st.markdown(line)
