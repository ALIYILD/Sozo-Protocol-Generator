"""
protocol_reporter — renders approved protocol to output formats.

Type: Deterministic
Wraps: sozo_generator.docx.renderer and PRISMA diagram generator.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("protocol_reporter")
def protocol_reporter(state: SozoGraphState) -> dict:
    """Render the approved protocol to DOCX and JSON."""
    decisions = []
    condition = state.get("condition", {})
    protocol = state.get("protocol", {})
    evidence = state.get("evidence", {})
    review = state.get("review", {})

    slug = condition.get("slug", "unknown")
    output_paths = {}

    from sozo_generator.core.settings import get_settings
    settings = get_settings()
    output_dir = settings.output_dir / "protocols" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save protocol JSON
    protocol_json_path = output_dir / f"{slug}_protocol.json"
    protocol_data = {
        "request_id": state.get("request_id"),
        "condition": {
            "slug": slug,
            "display_name": condition.get("display_name"),
            "icd10": condition.get("icd10"),
        },
        "base_sequence": protocol.get("base_sequence"),
        "sections": protocol.get("composed_sections"),
        "grounding_score": protocol.get("grounding_score"),
        "evidence_summary": evidence.get("evidence_summary"),
        "review": {
            "status": review.get("status"),
            "reviewer_id": review.get("reviewer_id"),
            "approval_stamp": review.get("approval_stamp"),
            "revision_number": review.get("revision_number"),
        },
        "version": state.get("version"),
    }
    protocol_json_path.write_text(json.dumps(protocol_data, indent=2, default=str))
    output_paths["json"] = str(protocol_json_path)
    decisions.append(f"Protocol JSON saved: {protocol_json_path}")

    # 2. Generate PRISMA flow diagram
    prisma_text_diagram = ""
    prisma_mermaid = ""
    try:
        from sozo_generator.evidence.pipeline_tracker import PipelineTracker, PRISMAFlowCounts
        from sozo_generator.evidence.prisma_diagram import PRISMADiagramGenerator, PRISMADiagramData

        prisma_counts_raw = evidence.get("prisma_counts", {})
        if prisma_counts_raw:
            # Reconstruct PRISMAFlowCounts from dict
            counts = PRISMAFlowCounts(**{
                k: v for k, v in prisma_counts_raw.items()
                if k in PRISMAFlowCounts.__dataclass_fields__
            }) if hasattr(PRISMAFlowCounts, '__dataclass_fields__') else PRISMAFlowCounts()
            # Manually set fields that exist
            for k, v in prisma_counts_raw.items():
                if hasattr(counts, k):
                    setattr(counts, k, v)

            gen = PRISMADiagramGenerator()

            # Build a minimal tracker populated from counts
            tracker = PipelineTracker()
            # Simulate events for each count to generate proper diagram
            for i in range(counts.records_identified):
                tracker.log_identification(f"study-{i}", "multi-source")
            for i in range(counts.records_after_dedup):
                tracker.log_dedup(f"study-{i}", is_duplicate=False)
            for i in range(counts.records_identified - counts.records_after_dedup):
                tracker.log_dedup(f"dup-{i}", merged_into=f"study-0")
            from sozo_generator.evidence.pipeline_tracker import PipelineDecision
            for i in range(min(counts.records_screened, counts.records_after_dedup)):
                tracker.log_screening(f"study-{i}", PipelineDecision.INCLUDE, "Relevant")

            diagram = gen.generate(
                tracker,
                condition_slug=slug,
                condition_name=condition.get("display_name", slug),
            )
            prisma_text_diagram = diagram.text_diagram
            prisma_mermaid = diagram.mermaid_diagram

            # Save text diagram
            diagram_path = output_dir / f"{slug}_prisma_flow.txt"
            diagram_path.write_text(prisma_text_diagram)
            output_paths["prisma_text"] = str(diagram_path)

            # Save Mermaid diagram
            mermaid_path = output_dir / f"{slug}_prisma_mermaid.md"
            mermaid_path.write_text(f"```mermaid\n{prisma_mermaid}\n```\n")
            output_paths["prisma_mermaid"] = str(mermaid_path)

            decisions.append(
                f"PRISMA flow diagram generated: "
                f"{counts.records_identified} identified → "
                f"{counts.records_after_dedup} deduped → "
                f"{counts.studies_included} included"
            )
    except Exception as e:
        logger.debug("PRISMA generation skipped: %s", e)
        decisions.append(f"PRISMA diagram skipped: {e}")

    # 3. Try DOCX rendering (with PRISMA appendix)
    try:
        from sozo_generator.schemas.documents import DocumentSpec, SectionContent
        from sozo_generator.core.enums import DocumentType, Tier

        sections = []
        for s in protocol.get("composed_sections", []):
            sections.append(SectionContent(
                section_id=s.get("section_id", ""),
                title=s.get("title", ""),
                content=s.get("content", ""),
                evidence_pmids=s.get("cited_evidence_ids", []),
                confidence_label=s.get("confidence"),
            ))

        # Append PRISMA flow diagram as appendix section
        if prisma_text_diagram:
            prisma_section = SectionContent(
                section_id="appendix_prisma",
                title="Appendix: PRISMA 2020 Evidence Flow Diagram",
                content=prisma_text_diagram,
                confidence_label="high",
            )
            sections.append(prisma_section)
            decisions.append("PRISMA flow diagram appended to DOCX as appendix section")

        # Append evidence summary section
        grade_dist = evidence.get("evidence_summary", {}).get("grade_distribution", {})
        evidence_appendix_lines = [
            f"Total articles after screening: {evidence.get('screened_article_count', len(evidence.get('articles', [])))}",
            f"Grade distribution: A={grade_dist.get('A', 0)}, B={grade_dist.get('B', 0)}, "
            f"C={grade_dist.get('C', 0)}, D={grade_dist.get('D', 0)}",
            "",
            "Top cited articles:",
        ]
        for a in evidence.get("articles", [])[:10]:
            authors = ", ".join(a.get("authors", [])[:3])
            if len(a.get("authors", [])) > 3:
                authors += " et al."
            pmid_str = f"PMID: {a['pmid']}" if a.get("pmid") else ""
            evidence_appendix_lines.append(
                f"[{a.get('evidence_grade', '?')}] {authors} ({a.get('year', '?')}). "
                f"{a.get('title', 'Untitled')[:100]}. "
                f"{a.get('journal', '')}. {pmid_str}"
            )

        evidence_section = SectionContent(
            section_id="appendix_evidence",
            title="Appendix: Evidence Summary",
            content="\n".join(evidence_appendix_lines),
            evidence_pmids=[a.get("pmid") for a in evidence.get("articles", [])[:10] if a.get("pmid")],
            confidence_label="high",
        )
        sections.append(evidence_section)

        spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=Tier.FELLOW,
            condition_slug=slug,
            condition_name=condition.get("display_name", slug),
            title=f"Evidence-Based Protocol \u2014 {condition.get('display_name', slug)}",
            sections=sections,
            references=condition.get("schema_dict", {}).get("references", []),
            build_id=state.get("request_id"),
        )

        from sozo_generator.docx.renderer import DocumentRenderer
        renderer = DocumentRenderer(output_dir=str(output_dir))
        docx_path = renderer.render(spec)
        output_paths["docx"] = str(docx_path)
        decisions.append(f"DOCX rendered with {len(sections)} sections (incl. appendices): {docx_path}")

    except Exception as e:
        logger.warning("DOCX rendering failed: %s", e)
        decisions.append(f"DOCX rendering failed: {e}")

    return {
        "output": {
            "output_paths": output_paths,
            "output_formats": list(output_paths.keys()),
        },
        "status": "released",
        "_decisions": decisions,
    }
