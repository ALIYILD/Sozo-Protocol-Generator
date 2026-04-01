"""
Document composer — merges, filters, and composes custom documents
from existing condition data.

SAFETY: All content comes from ConditionSchema (pre-verified data).
This module assembles and rearranges — it never generates clinical text.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..core.enums import DocumentType, Tier
from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent
from ..content.assembler import ContentAssembler
from ..docx.exporter import DocumentExporter
from ..docx.renderer import DocumentRenderer

logger = logging.getLogger(__name__)


class DocComposer:
    """Composes custom documents by merging, filtering, or combining
    sections from the standard generation pipeline."""

    def __init__(self, output_dir: str = "outputs/documents/"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.renderer = DocumentRenderer(output_dir=str(self.output_dir))
        self.assembler = ContentAssembler(output_base=str(self.output_dir))

    def generate_standard(
        self,
        condition: ConditionSchema,
        doc_types: list[str],
        tier: str = "both",
    ) -> dict[str, Path]:
        """Generate standard documents for a condition."""
        from ..core.enums import Tier as TierEnum, DocumentType as DTEnum

        tiers = [TierEnum.FELLOW, TierEnum.PARTNERS] if tier == "both" else [TierEnum(tier)]
        dt_enums = []
        for dt in doc_types:
            try:
                dt_enums.append(DTEnum(dt))
            except ValueError:
                logger.warning("Unknown doc type: %s", dt)

        if not dt_enums:
            dt_enums = list(DTEnum)

        exporter = DocumentExporter(
            output_dir=str(self.output_dir),
            with_visuals=False,
        )
        outputs = exporter.export_condition(
            condition=condition,
            tiers=tiers,
            doc_types=dt_enums,
            with_visuals=False,
        )
        return outputs

    def generate_from_template(
        self,
        condition: ConditionSchema,
        template_path: Path,
        tier: str = "both",
    ) -> dict[str, Path]:
        """Generate documents using an uploaded template."""
        from ..template.template_driven_generator import TemplateDrivenGenerator
        from ..core.enums import Tier as TierEnum

        tiers = [TierEnum.FELLOW, TierEnum.PARTNERS] if tier == "both" else [TierEnum(tier)]
        gen = TemplateDrivenGenerator(template_path)
        gen.parse_template()

        outputs = {}
        for t in tiers:
            spec = gen.generate_for_condition(condition, t)
            cond_dir = self.output_dir / condition.slug
            tier_dir = cond_dir / t.value.capitalize()
            tier_dir.mkdir(parents=True, exist_ok=True)
            out_path = tier_dir / spec.output_filename
            rendered = self.renderer.render(spec, out_path)
            outputs[f"{condition.slug}_{t.value}"] = rendered

        return outputs

    def merge_documents(
        self,
        condition: ConditionSchema,
        doc_types_to_merge: list[str],
        tier: str = "fellow",
        custom_title: Optional[str] = None,
    ) -> Path:
        """
        Merge multiple document types into a single combined document.

        Pulls sections from each document type and combines them into one
        DocumentSpec, then renders to a single DOCX file.
        """
        from ..core.enums import Tier as TierEnum, DocumentType as DTEnum

        tier_enum = TierEnum(tier) if tier != "both" else TierEnum.FELLOW

        all_sections: list[SectionContent] = []
        merged_references: list[dict] = []
        merged_review_flags: list[str] = []

        for dt_str in doc_types_to_merge:
            try:
                dt_enum = DTEnum(dt_str)
            except ValueError:
                logger.warning("Unknown doc type for merge: %s", dt_str)
                continue

            # Get sections from assembler
            sections = self.assembler.assemble(condition, dt_enum, tier_enum)

            # Add a separator heading
            separator = SectionContent(
                section_id=f"merged_{dt_str}",
                title=f"— {dt_str.replace('_', ' ').title()} —",
                content="",
            )
            all_sections.append(separator)
            all_sections.extend(sections)

        # Deduplicate references
        seen_refs = set()
        for ref in (condition.references or []):
            ref_str = str(ref)
            if ref_str not in seen_refs:
                merged_references.append(ref)
                seen_refs.add(ref_str)

        merged_review_flags = list(set(condition.review_flags or []))

        title = custom_title or f"Combined Document — {condition.display_name}"
        from ..core.utils import current_month_year

        spec = DocumentSpec(
            document_type=DTEnum.EVIDENCE_BASED_PROTOCOL,
            tier=tier_enum,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience="Fellow clinician" if tier_enum == TierEnum.FELLOW else "Partner clinician",
            confidentiality_mark="CONFIDENTIAL",
            sections=all_sections,
            references=merged_references,
            review_flags=merged_review_flags,
            output_filename=f"{condition.slug}_merged_{tier}.docx",
        )

        out_dir = self.output_dir / condition.slug / "Merged"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / spec.output_filename

        result = self.renderer.render(spec, out_path)
        logger.info("Merged document: %s", result)
        return result

    def generate_all_for_condition(
        self,
        condition: ConditionSchema,
        tier: str = "both",
    ) -> dict[str, Path]:
        """Generate all document types for one condition."""
        return self.generate_standard(condition, doc_types=[], tier=tier)

    def generate_all_conditions(
        self,
        registry,
        doc_types: list[str],
        tier: str = "both",
    ) -> dict[str, dict[str, Path]]:
        """Generate documents for all conditions in registry."""
        results = {}
        for slug in registry.list_slugs():
            try:
                condition = registry.get(slug)
                outputs = self.generate_standard(condition, doc_types=doc_types, tier=tier)
                results[slug] = outputs
            except Exception as e:
                logger.error("Failed to generate for %s: %s", slug, e)
                results[slug] = {"error": str(e)}
        return results
