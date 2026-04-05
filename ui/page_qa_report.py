"""QA Report page — document completeness checks."""
from pathlib import Path

import streamlit as st

from ui.helpers import condition_options, load_registry


def render(default_output_dir: str) -> None:
    st.title("QA Report")
    st.markdown("Check document completeness and schema conformity for any condition.")

    cond_opts = condition_options()
    display_names = ["All conditions"] + [d for _, d in cond_opts]
    slugs = [s for s, _ in cond_opts]

    selected = st.selectbox("Condition", display_names)
    col1, col2 = st.columns(2)
    output_dir = col1.text_input("Documents directory", value=default_output_dir)
    report_format = col2.selectbox("Report format", ["Markdown", "JSON"])

    if not st.button("Run QA", type="primary"):
        return

    from sozo_generator.qa.completeness import CompletenessChecker
    from sozo_generator.core.enums import Tier, DocumentType

    registry = load_registry()
    checker = CompletenessChecker(documents_dir=Path(output_dir))

    target_slugs = slugs if selected == "All conditions" else [
        slugs[[d for _, d in cond_opts].index(selected)]
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
        st.markdown(f"**{slug}** — :{color}[{status}] ({found}/{total} docs, {pct:.0f}%)")

        if report.get("missing"):
            with st.expander(f"Missing documents — {slug}"):
                for m in report["missing"]:
                    st.markdown(f"- `{m}`")

    if results:
        import json
        import datetime
        report_data = {slug: r for slug, r in results}
        if report_format == "JSON":
            st.download_button(
                "Download JSON Report",
                data=json.dumps(report_data, indent=2, default=str).encode(),
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
                "Download Markdown Report",
                data="\n".join(lines).encode(),
                file_name=f"qa_report_{datetime.date.today()}.md",
                mime="text/markdown",
            )
