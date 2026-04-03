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

    # 2. Generate PRISMA diagram
    try:
        from sozo_generator.evidence.pipeline_tracker import PipelineTracker
        from sozo_generator.evidence.prisma_diagram import PRISMADiagramGenerator

        prisma_counts = evidence.get("prisma_counts", {})
        if prisma_counts:
            # Create a tracker and populate from counts for diagram generation
            gen = PRISMADiagramGenerator()
            tracker = PipelineTracker()

            # We already have the counts — generate diagram directly
            diagram_path = output_dir / f"{slug}_prisma.txt"
            # Write a summary since we don't have the full tracker
            prisma_text = f"PRISMA Summary for {condition.get('display_name', slug)}\n"
            prisma_text += f"Records identified: {prisma_counts.get('records_identified', 0)}\n"
            prisma_text += f"After dedup: {prisma_counts.get('records_after_dedup', 0)}\n"
            prisma_text += f"Screened: {prisma_counts.get('records_screened', 0)}\n"
            prisma_text += f"Included: {prisma_counts.get('studies_included', 0)}\n"
            diagram_path.write_text(prisma_text)
            output_paths["prisma"] = str(diagram_path)
            decisions.append("PRISMA summary generated")
    except Exception as e:
        logger.debug("PRISMA generation skipped: %s", e)

    # 3. Try DOCX rendering
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

        spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=Tier.FELLOW,
            condition_slug=slug,
            condition_name=condition.get("display_name", slug),
            title=f"Evidence-Based Protocol — {condition.get('display_name', slug)}",
            sections=sections,
            references=condition.get("schema_dict", {}).get("references", []),
            build_id=state.get("request_id"),
        )

        from sozo_generator.docx.renderer import DocumentRenderer
        renderer = DocumentRenderer(output_dir=str(output_dir))
        docx_path = renderer.render(spec)
        output_paths["docx"] = str(docx_path)
        decisions.append(f"DOCX rendered: {docx_path}")

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
