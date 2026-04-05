"""Conditions Overview page — tabular summary of all 15 conditions."""
import streamlit as st

from ui.helpers import condition_options, load_registry


def render() -> None:
    st.title("Conditions Overview")
    st.markdown("All 15 supported neuromodulation conditions.")

    cond_opts = condition_options()
    registry = load_registry()

    rows = []
    for slug, display in cond_opts:
        try:
            meta = registry.get_meta(slug)
            icd10 = meta.get("icd10", "—")
            modalities = ", ".join(meta.get("primary_modalities", [])) or "—"
            phenotypes = len(meta.get("phenotypes", []))
        except Exception:
            icd10 = "—"
            modalities = "—"
            phenotypes = "—"
        rows.append({"Condition": display, "Slug": slug, "ICD-10": icd10, "Modalities": modalities, "Phenotypes": phenotypes})

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Condition Detail")
    selected_display = st.selectbox("Select condition to inspect", [d for _, d in cond_opts])
    selected_slug = [s for s, d in cond_opts if d == selected_display][0]

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
            off = " (off-label)" if p.off_label else ""
            st.markdown(f"**{p.label}**{off}  \n{p.rationale}")
