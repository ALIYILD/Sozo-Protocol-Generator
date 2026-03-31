"""Common builder utilities shared across all document types."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_references_section(condition: ConditionSchema) -> SectionContent:
    ref_lines = []
    for i, ref in enumerate(condition.references, 1):
        authors = ref.get("authors", "")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "[Title not available]")
        journal = ref.get("journal", "")
        pmid = ref.get("pmid", "")
        doi = ref.get("doi", "")
        line = f"{i}. {authors} ({year}). {title}."
        if journal:
            line += f" {journal}."
        if pmid:
            line += f" PMID: {pmid}."
        if doi:
            line += f" DOI: {doi}."
        ref_lines.append(line)

    return SectionContent(
        section_id="references",
        title="References & Evidence Sources",
        content="\n\n".join(ref_lines) if ref_lines else "[No references recorded — evidence review required]",
        is_placeholder=not bool(condition.references),
    )


def build_evidence_gaps_section(condition: ConditionSchema) -> SectionContent:
    if not condition.evidence_gaps:
        return SectionContent(
            section_id="evidence_gaps",
            title="Evidence Gaps",
            content="No major evidence gaps identified at time of generation.",
        )
    content = "The following evidence gaps were identified during document generation and require clinician attention:\n\n"
    content += "\n".join(f"[GAP] {gap}" for gap in condition.evidence_gaps)
    return SectionContent(
        section_id="evidence_gaps",
        title="Evidence Gaps & Areas Requiring Clinical Review",
        content=content,
        review_flags=condition.evidence_gaps,
    )
