"""Visual Preview page — generate and display clinical protocol visualisations."""
from pathlib import Path

import streamlit as st

from ui.helpers import condition_options, load_registry

VISUAL_TYPES = [
    ("qeeg_topomap",        "QEEG 10-10 Topographic Map"),
    ("mri_target_view",     "MRI-Style Stimulation Targets (Sagittal)"),
    ("axial_brain_view",    "Axial Brain View (Top-Down)"),
    ("coronal_brain_view",  "Coronal Brain View (Front-Facing)"),
    ("protocol_panel",      "Protocol Montage Panel (TPS + tDCS)"),
    ("connectivity_map",    "Network Connectivity Heatmap"),
    ("spectral_topomap",    "EEG Spectral Band Profile"),
    ("treatment_timeline",  "SOZO Treatment Session Timeline"),
    ("dose_response",       "Dose-Response Tracking Template"),
    ("impedance_map",       "Electrode Impedance Map"),
    ("brain_map",           "Brain Target Map (Schematic)"),
    ("network_diagram",     "Network Diagram (Hexagon)"),
    ("symptom_flow",        "Symptom-Network-Modality Flow"),
    ("patient_journey",     "Patient Journey (8-Stage)"),
    ("all",                 "Generate ALL visuals"),
]


def render() -> None:
    st.title("Visual Preview")
    st.markdown(
        "Generate and preview clinical visualizations for any condition. "
        "Select a condition and visual type, then click **Generate** to see the output."
    )

    cond_opts = condition_options()
    display_names = [d for _, d in cond_opts]
    slugs = [s for s, _ in cond_opts]

    vtype_keys = [k for k, _ in VISUAL_TYPES]
    vtype_labels = [v for _, v in VISUAL_TYPES]

    col1, col2 = st.columns(2)
    with col1:
        sel_idx = st.selectbox(
            "Condition", range(len(display_names)),
            format_func=lambda i: display_names[i], key="vis_cond",
        )
        selected_slug = slugs[sel_idx]
    with col2:
        vtype_idx = st.selectbox(
            "Visual Type", range(len(vtype_labels)),
            format_func=lambda i: vtype_labels[i], key="vis_type",
        )
        selected_vtype = vtype_keys[vtype_idx]

    if not st.button("Generate Visual", type="primary", key="vis_gen_btn"):
        return

    with st.spinner(f"Generating {vtype_labels[vtype_idx]} for {display_names[sel_idx]}..."):
        try:
            import tempfile
            from sozo_generator.generation.service import GenerationService

            registry = load_registry()
            condition = registry.get(selected_slug)
            tmpdir = Path(tempfile.mkdtemp(prefix="sozo_vis_"))
            generators = GenerationService._get_visual_generators()

            if selected_vtype == "all":
                generated: dict[str, str] = {}
                for vkey, vlabel in VISUAL_TYPES[:-1]:
                    gen = generators.get(vkey)
                    if gen:
                        try:
                            result = gen(condition, str(tmpdir))
                            if result:
                                if isinstance(result, list):
                                    for i, p in enumerate(result):
                                        generated[f"{vlabel} ({i+1})"] = p
                                else:
                                    generated[vlabel] = result
                        except Exception as e:
                            st.warning(f"{vlabel}: {e}")

                if generated:
                    st.success(f"Generated {len(generated)} visuals")
                    for label, fpath in generated.items():
                        fpath = Path(fpath)
                        if fpath.exists():
                            st.markdown(f"**{label}**")
                            st.image(str(fpath), use_container_width=True)
                            with open(fpath, "rb") as f:
                                st.download_button(
                                    f"Download {fpath.name}", f.read(),
                                    file_name=fpath.name, mime="image/png",
                                    key=f"dl_{fpath.stem}",
                                )
                            st.divider()
                else:
                    st.warning("No visuals were generated.")
            else:
                gen = generators.get(selected_vtype)
                if gen is None:
                    st.error(f"Generator not available for: {selected_vtype}")
                else:
                    result = gen(condition, str(tmpdir))
                    if result:
                        paths = result if isinstance(result, list) else [result]
                        for fpath in paths:
                            fpath = Path(fpath)
                            if fpath.exists():
                                st.image(str(fpath), use_container_width=True)
                                with open(fpath, "rb") as f:
                                    st.download_button(
                                        f"Download {fpath.name}", f.read(),
                                        file_name=fpath.name, mime="image/png",
                                    )
                                st.caption(f"Size: {fpath.stat().st_size // 1024} KB")
                    else:
                        st.info("No visual generated (condition may not have matching targets).")

        except Exception as e:
            st.error(f"Visual generation failed: {e}")
            import traceback
            st.code(traceback.format_exc())
