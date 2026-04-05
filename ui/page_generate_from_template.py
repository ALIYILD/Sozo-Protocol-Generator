"""Generate from Template page — template-driven batch document generation."""
from pathlib import Path

import streamlit as st

from ui.helpers import TIER_LABELS, condition_options, load_registry, zip_files


def render(default_output_dir: str) -> None:
    st.title("Generate from Template")
    st.markdown(
        "Upload a **Gold Standard DOCX template** (e.g. Parkinson's Evidence-Based Protocol). "
        "The system will read its structure and generate matching documents for every condition, "
        "populated with **real clinical data and verified references**."
    )
    st.info(
        "**No hallucinations.** All content comes from the condition registry's verified clinical data. "
        "Sections that can't be populated are clearly marked as requiring clinical input.",
        icon="🛡️",
    )

    uploaded_file = st.file_uploader(
        "Upload your template (.docx)",
        type=["docx"],
        help="Upload a SOZO clinical document template. The system will extract its section structure.",
    )

    if uploaded_file is None:
        return

    import tempfile
    tmp_dir = Path(tempfile.mkdtemp(prefix="sozo_template_"))
    template_path = tmp_dir / uploaded_file.name
    template_path.write_bytes(uploaded_file.getvalue())

    st.success(f"Template uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    from sozo_generator.template.template_driven_generator import TemplateDrivenGenerator
    generator = TemplateDrivenGenerator(template_path)

    with st.spinner("Parsing template structure..."):
        template_sections = generator.parse_template()

    if not template_sections:
        st.error("Could not parse any sections from the template. Make sure it uses Word Heading styles.")
        st.stop()

    st.subheader("Template Structure Detected")
    st.markdown(f"**{len(template_sections)} sections** found in template:")
    for i, ts in enumerate(template_sections, 1):
        level_indent = "  " * (ts.heading_level - 1)
        placeholder_badge = f"  {ts.placeholder_count} placeholder(s)" if ts.placeholder_count > 0 else ""
        table_badge = "  has table" if ts.has_table else ""
        st.markdown(f"{level_indent}{i}. **{ts.title}** (`{ts.section_id}`){placeholder_badge}{table_badge}")

    st.divider()

    cond_opts = condition_options()
    all_slugs = [s for s, _ in cond_opts]
    all_displays = [d for _, d in cond_opts]

    st.subheader("Select Conditions to Generate")
    gen_mode = st.radio("Generate for:", ["All 15 conditions", "Selected conditions"], horizontal=True)

    if gen_mode == "Selected conditions":
        selected_displays = st.multiselect("Choose conditions", all_displays, default=all_displays[:3])
        target_slugs = [all_slugs[all_displays.index(d)] for d in selected_displays]
    else:
        target_slugs = all_slugs

    col1, col2 = st.columns(2)
    with col1:
        selected_tier_label = st.selectbox(
            "Tier", list(TIER_LABELS.values()), index=0, key="template_tier",
        )
        selected_tier = [k for k, v in TIER_LABELS.items() if v == selected_tier_label][0]
    with col2:
        output_dir = st.text_input("Output directory", value=default_output_dir, key="template_output_dir")

    st.divider()

    if not st.button("Generate Documents from Template", type="primary", use_container_width=True):
        return

    from sozo_generator.core.enums import Tier
    from sozo_generator.docx.renderer import DocumentRenderer

    tiers = [Tier.FELLOW, Tier.PARTNERS] if selected_tier == "both" else [Tier(selected_tier)]
    registry = load_registry()
    renderer = DocumentRenderer(output_dir=output_dir)

    all_outputs: dict[str, Path] = {}
    errors: list[str] = []
    progress = st.progress(0, text="Generating...")
    total_work = len(target_slugs) * len(tiers)
    done = 0

    for slug in target_slugs:
        try:
            condition = registry.get(slug)
        except Exception as e:
            errors.append(f"{slug}: Failed to load — {e}")
            done += len(tiers)
            progress.progress(done / total_work)
            continue

        for tier in tiers:
            try:
                spec = generator.generate_for_condition(condition, tier)
                condition_dir = Path(output_dir) / condition.slug.replace("_", " ").title().replace(" ", "_")
                tier_dir = condition_dir / tier.value.capitalize()
                tier_dir.mkdir(parents=True, exist_ok=True)
                out_path = tier_dir / spec.output_filename
                rendered_path = renderer.render(spec, out_path)
                all_outputs[f"{slug}_{tier.value}"] = rendered_path
            except Exception as e:
                errors.append(f"{slug}/{tier.value}: {e}")
            done += 1
            progress.progress(done / total_work, text=f"Generating {condition.display_name} ({tier.value})...")

    progress.progress(100, text="Done!")

    if all_outputs:
        st.success(f"Generated **{len(all_outputs)}** documents across **{len(target_slugs)}** conditions")

        # Count insufficient sections
        total_insufficient = 0
        total_sections = 0
        for slug in target_slugs:
            try:
                condition = registry.get(slug)
                for tier in tiers:
                    spec = generator.generate_for_condition(condition, tier)
                    for s in spec.sections:
                        total_sections += 1
                        if s.is_placeholder:
                            total_insufficient += 1
            except Exception:
                pass

        if total_insufficient > 0:
            st.warning(
                f"**{total_insufficient}/{total_sections}** sections marked as insufficient data. "
                "These require clinical input before use.",
                icon="⚠️",
            )

        st.subheader("Download Generated Documents")
        by_condition: dict[str, list] = {}
        for key, path in all_outputs.items():
            slug = key.rsplit("_", 1)[0]
            by_condition.setdefault(slug, []).append((key, path))

        for slug, items in sorted(by_condition.items()):
            display_name = slug.replace("_", " ").title()
            with st.expander(f"{display_name} ({len(items)} documents)", expanded=False):
                for key, path in items:
                    if path.exists():
                        tier_part = key.rsplit("_", 1)[-1]
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**{path.name}** ({tier_part.capitalize()})")
                        with col_b:
                            with open(path, "rb") as f:
                                st.download_button(
                                    "Download", data=f.read(), file_name=path.name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"tdl_{key}",
                                )

        st.divider()
        st.download_button(
            "Download All as ZIP",
            data=zip_files(all_outputs),
            file_name=f"sozo_template_generated_{len(target_slugs)}_conditions.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )

    if errors:
        st.divider()
        st.subheader("Errors")
        for err in errors:
            st.error(err)
