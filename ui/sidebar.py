"""Sidebar controls for the SOZO Generator app."""
from pathlib import Path

import streamlit as st

PAGES = [
    "Chat",
    "Studio",
    "Protocol Graph",
    "Template Studio",
    "Generate from Template",
    "Generate Documents",
    "Visual Preview",
    "Operator Cockpit",
    "Review Queue",
    "Conditions Overview",
    "QA Report",
    "Evidence Ingest",
]


def render_sidebar(reviews_dir: Path) -> str:
    """Render the full sidebar and return the selected page name."""
    with st.sidebar:
        st.title("SOZO Generator")
        st.caption("Clinical Protocol Document Generator")
        st.divider()

        page = st.radio(
            "Navigate",
            PAGES,
            label_visibility="collapsed",
        )
        st.divider()

        # AI settings
        with st.expander("AI Settings", expanded=False):
            st.text_input(
                "Anthropic API Key",
                type="password",
                key="anthropic_key",
                help="Optional. Enables smarter intent parsing. Works without it too.",
            )
            st.text_input(
                "OpenAI API Key (alt)",
                type="password",
                key="openai_key",
                help="Alternative to Anthropic key.",
            )

        # Patient Context (V2)
        with st.expander("Patient Context (V2)", expanded=False):
            patient_age = st.number_input(
                "Age", min_value=18, max_value=100, value=35, key="sidebar_patient_age",
            )
            patient_sex = st.selectbox(
                "Sex", ["male", "female", "other"], key="sidebar_patient_sex",
            )
            patient_medications = st.text_area(
                "Current Medications (comma-separated)",
                key="sidebar_patient_meds",
                placeholder="e.g. sertraline, lithium, metformin",
                height=68,
            )
            patient_history = st.text_area(
                "Medical History (comma-separated)",
                key="sidebar_patient_history",
                placeholder="e.g. epilepsy, cardiac pacemaker, pregnancy",
                height=68,
            )

            if st.button("Run Safety Check", key="sidebar_safety_btn"):
                try:
                    from sozo_generator.safety import evaluate_patient_safety

                    _meds_raw = patient_medications or ""
                    _hist_raw = patient_history or ""
                    safety_result = evaluate_patient_safety(
                        patient_demographics={"age": patient_age, "sex": patient_sex},
                        medications=[
                            {"name": m.strip(), "drug_class": m.strip()}
                            for m in _meds_raw.split(",") if m.strip()
                        ],
                        medical_history=[
                            h.strip() for h in _hist_raw.split(",") if h.strip()
                        ],
                    )
                    st.session_state["safety_result"] = safety_result
                except ImportError:
                    st.warning(
                        "Safety module not yet available. "
                        "Install `sozo_generator.safety` to enable patient safety checks."
                    )
                except Exception as exc:
                    st.error(f"Safety check failed: {exc}")

            _sr = st.session_state.get("safety_result")
            if _sr is not None:
                _cleared = (
                    getattr(_sr, "cleared", None)
                    if not isinstance(_sr, dict)
                    else _sr.get("cleared")
                )
                if _cleared:
                    st.success("Patient CLEARED for neuromodulation")
                else:
                    st.error("Patient NOT CLEARED")

                _warnings = (
                    getattr(_sr, "warnings", [])
                    if not isinstance(_sr, dict)
                    else _sr.get("warnings", [])
                )
                if _warnings:
                    st.markdown("**Warnings:**")
                    for _w in _warnings:
                        st.warning(str(_w))

                _blocked = (
                    getattr(_sr, "blocked_modalities", [])
                    if not isinstance(_sr, dict)
                    else _sr.get("blocked_modalities", [])
                )
                if _blocked:
                    st.markdown("**Blocked Modalities:**")
                    for _b in _blocked:
                        st.error(str(_b))

        # Evidence Health
        with st.expander("Evidence Health", expanded=False):
            try:
                from sozo_generator.evidence.staleness import get_staleness_report

                _stale_report = get_staleness_report()
                _health = (
                    getattr(_stale_report, "overall_health", "unknown")
                    if not isinstance(_stale_report, dict)
                    else _stale_report.get("overall_health", "unknown")
                )
                _health_colors = {"green": "green", "yellow": "orange", "red": "red"}
                _hc = _health_colors.get(str(_health).lower(), "gray")
                st.markdown(f"**Overall Health:** :{_hc}[{str(_health).upper()}]")

                def _attr(obj, name, default=0):
                    return getattr(obj, name, default) if not isinstance(obj, dict) else obj.get(name, default)

                _fresh = _attr(_stale_report, "fresh")
                _aging = _attr(_stale_report, "aging")
                _stale_count = _attr(_stale_report, "stale")
                _expired = _attr(_stale_report, "expired")

                ec1, ec2 = st.columns(2)
                ec1.metric("Fresh", _fresh)
                ec2.metric("Aging", _aging)
                ec3, ec4 = st.columns(2)
                ec3.metric("Stale", _stale_count)
                ec4.metric("Expired", _expired)

                _priority = _attr(_stale_report, "high_priority_refreshes", [])
                if _priority:
                    st.markdown("**High-Priority Refreshes:**")
                    for _hp in _priority:
                        st.markdown(f"- {_hp}")
            except ImportError:
                st.info(
                    "Evidence staleness module not available. "
                    "Install `sozo_generator.evidence.staleness` to enable."
                )
            except Exception as exc:
                st.warning(f"Could not load evidence health: {exc}")

        st.caption("v2.0.0  ·  SOZO Brain Center")

    return page
