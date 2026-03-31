"""SOZO Protocol Generator — Streamlit UI."""
import io
import sys
import zipfile
from pathlib import Path

import streamlit as st

# ── Project root on sys.path ────────────────────────────────────────────────
ROOT = Path(__file__).parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOZO Protocol Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Lazy imports (cached) ────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load_registry():
    from sozo_generator.conditions.registry import get_registry
    return get_registry()


@st.cache_data(show_spinner=False)
def _condition_options():
    """Return list of (slug, display_name) tuples."""
    registry = _load_registry()
    slugs = [
        "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
        "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
        "ms", "autism", "long_covid", "tinnitus", "insomnia",
    ]
    options = []
    for slug in slugs:
        try:
            meta = registry.get_meta(slug)
            display = meta.get("display_name", slug.replace("_", " ").title())
        except Exception:
            display = slug.replace("_", " ").title()
        options.append((slug, display))
    return options


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
    st.image("https://via.placeholder.com/200x60/1a1a2e/ffffff?text=SOZO+Brain+Center",
             use_container_width=True)
    st.title("🧠 SOZO Generator")
    st.caption("Clinical Protocol Document Generator")
    st.divider()

    page = st.radio(
        "Navigate",
        ["Generate Documents", "Conditions Overview", "QA Report", "Evidence Ingest"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("v1.0.0  ·  SOZO Brain Center")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE DOCUMENTS
# ════════════════════════════════════════════════════════════════════════════
if page == "Generate Documents":
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
            value=str(ROOT / "outputs" / "documents"),
        )

    st.divider()

    if st.button("⚡ Generate", type="primary", use_container_width=True):
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
                use_container_width=True,
            )


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
    st.dataframe(df, use_container_width=True, hide_index=True)

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
    output_dir = col1.text_input("Documents directory", value=str(ROOT / "outputs" / "documents"))
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
