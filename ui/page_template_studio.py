"""Template Studio page — upload, learn, and generate from template profiles."""
from pathlib import Path

import streamlit as st

from ui.helpers import condition_options


def render() -> None:
    st.title("Template Studio")
    st.markdown(
        "Upload a gold-standard DOCX template, learn its structure, "
        "then generate new documents for any condition matching the template's style."
    )

    tab1, tab2, tab3 = st.tabs(["Upload & Learn", "Stored Profiles", "Generate from Template"])

    with tab1:
        _render_upload_learn()

    with tab2:
        _render_stored_profiles()

    with tab3:
        _render_generate()


def _render_upload_learn() -> None:
    st.subheader("Upload Template")
    uploaded = st.file_uploader("Choose a DOCX template", type=["docx"], key="tpl_upload")
    if not uploaded:
        return

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(uploaded.read())
        tmp_path = f.name

    tpl_name = st.text_input(
        "Profile name",
        value=uploaded.name.replace(".docx", "").replace("_", " "),
    )

    if not st.button("Ingest Template", type="primary"):
        return

    with st.spinner("Parsing template structure..."):
        try:
            from sozo_generator.template_profiles.builder import build_template_profile
            from sozo_generator.template_profiles.store import TemplateProfileStore

            profile = build_template_profile(tmp_path, name=tpl_name)
            store = TemplateProfileStore()
            store.save(profile)

            st.success(f"Template profile created: **{profile.profile_id}**")

            col1, col2, col3 = st.columns(3)
            col1.metric("Sections", profile.total_sections)
            col2.metric("Tables", profile.total_tables)
            col3.metric("Figures", profile.total_figures)

            st.markdown(
                f"**Type**: {profile.template_type} | **Doc type**: {profile.inferred_doc_type} "
                f"| **Tier**: {profile.tier}"
            )
            st.markdown(f"**Source condition**: {profile.source_condition}")

            st.subheader("Learned Section Map")
            for s in profile.section_map:
                evidence = " [evidence]" if s.requires_evidence else ""
                tables = f" [{s.table_count} tables]" if s.table_expected else ""
                st.markdown(
                    f"{'  ' * (s.heading_level - 1)}- **{s.title}** "
                    f"({s.estimated_word_count}w, {s.content_kind}){evidence}{tables}"
                )

            st.subheader("Formatting Profile")
            st.json(profile.formatting_profile.model_dump())

            st.subheader("Tone Profile")
            st.json(profile.tone_profile.model_dump(exclude={"sample_excerpts"}))

        except Exception as e:
            st.error(f"Ingestion failed: {e}")


def _render_stored_profiles() -> None:
    st.subheader("Stored Template Profiles")
    try:
        from sozo_generator.template_profiles.store import TemplateProfileStore
        store = TemplateProfileStore()
        profiles = store.list_profiles()

        if profiles:
            for p in profiles:
                with st.expander(f"{p['name']} ({p['profile_id']})"):
                    st.markdown(
                        f"**Type**: {p['template_type']} | **Doc type**: {p['inferred_doc_type']} "
                        f"| **Tier**: {p['tier']}"
                    )
                    st.markdown(f"**Sections**: {p['total_sections']} | **Source condition**: {p['source_condition']}")
                    st.markdown(f"**Created**: {p['created_at']}")
        else:
            st.info("No template profiles stored yet. Upload a template in the 'Upload & Learn' tab.")
    except Exception as e:
        st.error(f"Could not load profiles: {e}")


def _render_generate() -> None:
    st.subheader("Generate from Template")
    try:
        from sozo_generator.template_profiles.store import TemplateProfileStore
        store = TemplateProfileStore()
        profiles = store.list_profiles()

        if not profiles:
            st.info("No template profiles available. Upload a template first.")
            return

        profile_names = [f"{p['name']} ({p['profile_id']})" for p in profiles]
        profile_ids = [p["profile_id"] for p in profiles]

        sel_profile_idx = st.selectbox(
            "Template Profile", range(len(profile_names)), format_func=lambda i: profile_names[i],
        )
        sel_profile_id = profile_ids[sel_profile_idx]

        cond_opts = condition_options()
        display_names = [d for _, d in cond_opts]
        slugs = [s for s, _ in cond_opts]
        sel_cond_idx = st.selectbox(
            "Target Condition", range(len(display_names)),
            format_func=lambda i: display_names[i], key="tpl_cond",
        )
        sel_condition = slugs[sel_cond_idx]

        col1, col2 = st.columns(2)
        with col1:
            sel_tier = st.selectbox("Tier", ["partners", "fellow"], key="tpl_tier")
        with col2:
            use_ai = st.checkbox("Use AI drafting", value=False, key="tpl_ai")

        with_research = st.checkbox("Search PubMed for evidence", value=False, key="tpl_research")

        if not st.button("Generate Document", type="primary", key="tpl_gen_btn"):
            return

        with st.spinner(f"Generating {display_names[sel_cond_idx]} document from template..."):
            try:
                from sozo_generator.generation.service import GenerationService
                svc = GenerationService(with_visuals=True, with_qa=True)
                result = svc.generate_from_template(
                    template_id=sel_profile_id,
                    condition=sel_condition,
                    tier=sel_tier,
                    with_ai=use_ai,
                    with_research=with_research,
                )

                if result.success:
                    st.success(f"Document generated: {result.output_path}")
                    st.markdown(f"**Build ID**: {result.build_id}")

                    if result.qa_issues:
                        with st.expander(f"Review Issues ({len(result.qa_issues)})"):
                            for issue in result.qa_issues:
                                st.markdown(f"- {issue}")

                    out_path = Path(result.output_path)
                    if out_path.exists():
                        with open(out_path, "rb") as f:
                            st.download_button(
                                "Download DOCX",
                                f.read(),
                                file_name=out_path.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            )
                else:
                    st.error(f"Generation failed: {result.error}")
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"Could not load template system: {e}")
