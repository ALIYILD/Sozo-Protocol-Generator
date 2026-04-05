"""Operator Cockpit page — platform-wide readiness dashboard."""
import streamlit as st

from ui.helpers import condition_options


def render() -> None:
    st.title("Operator Cockpit")
    st.markdown("Platform-wide operational visibility — readiness, blockers, release status.")

    try:
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()

        ov = svc.overview()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conditions", ov.conditions_count)
        col2.metric("Blueprints", ov.blueprints_count)
        col3.metric("Documents Ready", ov.documents_ready)
        col4.metric("Review Required", ov.documents_review_required)

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Evidence PMIDs", f"{ov.total_pmids:,}")
        col6.metric("Total Sections", f"{ov.total_sections:,}")
        col7.metric("Regenerations", ov.regeneration_history_count)
        col8.metric("Knowledge Valid", "YES" if ov.knowledge_valid else "NO")

        st.divider()

        st.subheader("Condition Status")
        summaries = svc.conditions_summary()
        import pandas as pd
        df = pd.DataFrame([
            {"Condition": cs.condition, "Ready": cs.ready, "Review": cs.review_required,
             "Incomplete": cs.incomplete, "PMIDs": cs.total_pmids}
            for cs in summaries
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("Release Pack Inspector")
        cond_opts = condition_options()
        display_names = [d for _, d in cond_opts]
        slugs = [s for s, _ in cond_opts]

        col_a, col_b = st.columns(2)
        with col_a:
            sel_idx = st.selectbox("Condition", range(len(display_names)),
                                   format_func=lambda i: display_names[i], key="ck_cond")
        with col_b:
            sel_tier = st.selectbox("Tier", ["fellow", "partners"], key="ck_tier")

        pack = svc.pack_summary(slugs[sel_idx], sel_tier)
        if pack["release_ready"]:
            st.success(f"RELEASE READY — {pack['ready']}/{pack['total']} documents")
        else:
            st.warning(f"NOT READY — {pack['ready']}/{pack['total']} ready")
        if pack.get("blocked_docs"):
            st.markdown("**Blocked:**")
            for bd in pack["blocked_docs"]:
                st.markdown(f"- {bd['doc_type']}: {bd['reason']} ({bd['placeholders']} placeholders)")

        st.divider()

        st.subheader("Release Blockers")
        blockers = svc.blockers()
        if blockers:
            st.warning(f"{len(blockers)} blockers across platform")
            for b in blockers[:15]:
                st.markdown(f"- **{b.condition}/{b.doc_type}/{b.tier}**: {b.summary}")
        else:
            st.success("No blockers — all documents are release-ready!")

    except Exception as e:
        st.error(f"Cockpit error: {e}")
