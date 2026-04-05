"""Generate Documents page — single-condition document export."""
from pathlib import Path

import streamlit as st

from ui.helpers import DOC_TYPE_LABELS, TIER_LABELS, condition_options, load_registry, zip_files


def render(default_output_dir: str) -> None:
    st.title("Generate Clinical Documents")
    st.markdown("Select a condition and document options, then click **Generate**.")

    cond_opts = condition_options()
    slug_to_display = {s: d for s, d in cond_opts}
    display_names = [d for _, d in cond_opts]
    slugs = [s for s, _ in cond_opts]

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_display = st.selectbox("Condition", display_names, index=0)
        selected_slug = slugs[display_names.index(selected_display)]

        selected_tier_label = st.selectbox("Tier", list(TIER_LABELS.values()), index=0)
        selected_tier = [k for k, v in TIER_LABELS.items() if v == selected_tier_label][0]

    with col2:
        doc_type_options = ["All documents"] + list(DOC_TYPE_LABELS.values())
        selected_doc_label = st.selectbox("Document Type", doc_type_options, index=0)

        with_visuals = st.toggle("Include visual diagrams", value=False)
        output_dir = st.text_input("Output directory", value=default_output_dir)

    st.divider()

    if not st.button("Generate", type="primary"):
        return

    from sozo_generator.core.enums import Tier, DocumentType
    from sozo_generator.docx.exporter import DocumentExporter

    tiers = [Tier.FELLOW, Tier.PARTNERS] if selected_tier == "both" else [Tier(selected_tier)]

    if selected_doc_label == "All documents":
        doc_types = list(DocumentType)
    else:
        label_to_key = {v: k for k, v in DOC_TYPE_LABELS.items()}
        key = label_to_key.get(selected_doc_label)
        if key is None:
            for k, v in DOC_TYPE_LABELS.items():
                if selected_doc_label in v:
                    key = k
                    break
        doc_types = [DocumentType(key)] if key else list(DocumentType)

    with st.spinner(f"Loading {selected_display}..."):
        try:
            registry = load_registry()
            condition_obj = registry.get(selected_slug)
        except Exception as e:
            st.error(f"Failed to load condition: {e}")
            st.stop()

    progress = st.progress(0, text="Generating documents...")

    try:
        exporter = DocumentExporter(output_dir=str(output_dir), with_visuals=with_visuals)
        outputs = exporter.export_condition(
            condition=condition_obj, tiers=tiers, doc_types=doc_types, with_visuals=with_visuals,
        )
    except Exception as e:
        st.error(f"Generation failed: {e}")
        st.stop()

    progress.progress(100, text="Done!")

    if not outputs:
        st.warning("No documents were generated.")
        return

    st.success(f"Generated **{len(outputs)}** document(s) for **{selected_display}**")
    st.subheader("Generated Files")
    for key, path in outputs.items():
        path = Path(path)
        if path.exists():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                tier_part, doc_part = key.split("_", 1)
                label = f"{DOC_TYPE_LABELS.get(doc_part, doc_part)} — {tier_part.capitalize()}"
                st.markdown(f"**{label}**  \n`{path.name}`")
            with col_b:
                with open(path, "rb") as f:
                    st.download_button(
                        "Download", data=f.read(), file_name=path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_{key}",
                    )

    st.divider()
    st.download_button(
        "Download All as ZIP",
        data=zip_files(outputs),
        file_name=f"{selected_slug}_documents.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )

    # Personalization Engine
    with st.expander("Personalization Engine", expanded=False):
        try:
            from sozo_generator.personalization import PersonalizationEngine
            _pe = PersonalizationEngine()
            _patient_ctx = {
                "age": st.session_state.get("sidebar_patient_age", 35),
                "sex": st.session_state.get("sidebar_patient_sex", "male"),
                "medications": [
                    m.strip()
                    for m in (st.session_state.get("sidebar_patient_meds") or "").split(",")
                    if m.strip()
                ],
                "medical_history": [
                    h.strip()
                    for h in (st.session_state.get("sidebar_patient_history") or "").split(",")
                    if h.strip()
                ],
            }
            _pers_result = _pe.personalize(condition_slug=selected_slug, patient_context=_patient_ctx)

            def _attr(obj, name, default=None):
                return getattr(obj, name, default) if not isinstance(obj, dict) else obj.get(name, default)

            _phenotype = _attr(_pers_result, "matched_phenotype")
            _confidence = _attr(_pers_result, "confidence_score")
            _band = _attr(_pers_result, "confidence_band")
            _protocol = _attr(_pers_result, "recommended_protocol")
            _explanation = _attr(_pers_result, "explanation")

            if _phenotype:
                st.markdown(f"**Matched Phenotype:** {_phenotype}")
            if _confidence is not None:
                _band_str = f" ({_band})" if _band else ""
                _conf_color = "green" if (_confidence or 0) >= 0.7 else ("orange" if (_confidence or 0) >= 0.4 else "red")
                st.markdown(f"**Confidence:** :{_conf_color}[{_confidence:.0%}{_band_str}]")
            if _protocol:
                st.markdown("**Recommended Protocol:**")
                if isinstance(_protocol, dict):
                    for _pk, _pv in _protocol.items():
                        st.markdown(f"- **{_pk}**: {_pv}")
                else:
                    st.markdown(str(_protocol))
            if _explanation:
                st.info(str(_explanation))
        except ImportError:
            st.info("Personalization engine not yet available. Install `sozo_generator.personalization` to enable.")
        except Exception as exc:
            st.warning(f"Personalization error: {exc}")

    # Assessment Scores
    with st.expander("Assessment Scores", expanded=False):
        try:
            from sozo_generator.schemas.patient import VALIDATED_SCALES, get_scale
            _scale_names = list(VALIDATED_SCALES.keys()) if isinstance(VALIDATED_SCALES, dict) else [str(s) for s in VALIDATED_SCALES]
            _sel_scale = st.selectbox("Assessment Scale", _scale_names, key="assess_scale_select")
            _score_val = st.number_input("Score", min_value=0, max_value=200, value=0, key="assess_score_input")

            if _sel_scale and _score_val > 0:
                _scale_obj = get_scale(_sel_scale)
                if _scale_obj:
                    _severity = None
                    if hasattr(_scale_obj, "classify"):
                        _severity = _scale_obj.classify(_score_val)
                    elif isinstance(_scale_obj, dict) and "thresholds" in _scale_obj:
                        for _tname, _trange in sorted(_scale_obj["thresholds"].items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0):
                            if isinstance(_trange, (int, float)) and _score_val >= _trange:
                                _severity = _tname
                            elif isinstance(_trange, (list, tuple)) and len(_trange) == 2:
                                if _trange[0] <= _score_val <= _trange[1]:
                                    _severity = _tname
                    if _severity:
                        _sev_colors = {"mild": "green", "moderate": "orange", "severe": "red", "minimal": "green", "normal": "green"}
                        _sc = _sev_colors.get(str(_severity).lower(), "blue")
                        st.markdown(f"**Severity Classification:** :{_sc}[{_severity}]")
                    else:
                        st.info(f"Score {_score_val} on {_sel_scale} — classification not available.")
                else:
                    st.warning(f"Scale '{_sel_scale}' not found.")
        except ImportError:
            st.info("Assessment scales module not yet available.")
        except Exception as exc:
            st.warning(f"Assessment scoring error: {exc}")
