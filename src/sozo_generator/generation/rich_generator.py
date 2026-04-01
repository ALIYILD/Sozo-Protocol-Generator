"""
Rich document generator — produces documents that match the quality and depth
of existing SOZO documents by:

1. Using harvested content from the content library (real clinician-written prose)
2. Adapting content from the closest matching condition
3. Optionally using an AI agent (Claude/GPT) with large context to write
   condition-specific sections that match the template style

SAFETY:
- Library-based generation uses only existing clinician-reviewed content
- AI-generated content is ALWAYS marked as AI-DRAFTED and requires review
- PMIDs and clinical claims are NEVER fabricated by the AI
- The AI is given the template pattern and condition data, never asked to invent
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent, SectionClaim
from ..core.enums import DocumentType, Tier, ConfidenceLabel
from ..core.utils import current_month_year
from ..template.learning.content_harvester import (
    ContentHarvester,
    ContentLibrary,
    HarvestedSection,
)

logger = logging.getLogger(__name__)

_LIBRARY_PATH = Path("data/learned/content_library.json")

# Map doc types to standard section ordering
_DOC_TYPE_SECTION_ORDER = {
    "handbook": [
        "header", "document_control", "introduction", "modalities",
        "fnon_framework", "stage_1", "stage_2", "stage_3", "stage_4",
        "stage_5", "stage_6", "stage_7", "stage_8",
        "governance", "references",
    ],
    "clinical_exam": [
        "header", "document_control", "patient_info", "scoring",
        "network_assessment", "examination", "screening", "phenotype",
        "summary", "signature",
    ],
}


class RichDocumentGenerator:
    """Generates rich documents using the content library + optional AI."""

    def __init__(
        self,
        library_path: Optional[Path] = None,
        anthropic_api_key: str = "",
        openai_api_key: str = "",
    ):
        self._library: Optional[ContentLibrary] = None
        self._harvester = ContentHarvester()
        self._library_path = Path(library_path or _LIBRARY_PATH)
        self._anthropic_key = anthropic_api_key
        self._openai_key = openai_api_key

        if self._library_path.exists():
            self._library = self._harvester.load_library(self._library_path)
            logger.info(
                "Loaded content library: %d sections from %d docs",
                self._library.total_sections,
                self._library.total_documents,
            )

    @property
    def has_library(self) -> bool:
        return self._library is not None and self._library.total_sections > 0

    @property
    def has_ai(self) -> bool:
        return bool(self._anthropic_key or self._openai_key)

    def generate(
        self,
        condition: ConditionSchema,
        doc_type: str,
        tier: str = "fellow",
        use_ai: bool = False,
    ) -> DocumentSpec:
        """Generate a rich document using library content + optional AI.

        Strategy:
        1. For each section in the template, find the best harvested content
        2. Adapt it to the target condition (replace names, ICD codes)
        3. Fill with condition-specific data from ConditionSchema
        4. If use_ai=True, enhance thin sections with AI-drafted prose
        5. Mark AI sections clearly
        """
        if not self.has_library:
            logger.warning("No content library — falling back to standard generation")
            from ..content.assembler import ContentAssembler
            assembler = ContentAssembler()
            tier_enum = Tier.FELLOW if "fellow" in tier.lower() else Tier.PARTNERS
            doc_type_enum = DocumentType(doc_type)
            sections = assembler.assemble(condition, doc_type_enum, tier_enum)
            return DocumentSpec(
                document_type=doc_type_enum,
                tier=tier_enum,
                condition_slug=condition.slug,
                condition_name=condition.display_name,
                title=f"{doc_type.replace('_', ' ').title()} — {condition.display_name}",
                sections=sections,
                references=condition.references or [],
                version=condition.version,
                date_label=current_month_year(),
            )

        tier_enum = Tier.FELLOW if "fellow" in tier.lower() else Tier.PARTNERS

        # Get all sections for this doc_type from the library
        sections = self._build_sections_from_library(
            condition, doc_type, tier, use_ai
        )

        # Build the title from template pattern
        title = self._build_title(condition, doc_type, tier_enum)

        spec = DocumentSpec(
            document_type=DocumentType(doc_type) if doc_type in [dt.value for dt in DocumentType] else DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=tier_enum,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience="Fellow clinician" if tier_enum == Tier.FELLOW else "Partner clinician",
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=condition.references or [],
            review_flags=condition.review_flags or [],
            output_filename=f"{condition.slug}_{doc_type}_{tier}.docx",
        )
        return spec

    def _build_sections_from_library(
        self,
        condition: ConditionSchema,
        doc_type: str,
        tier: str,
        use_ai: bool,
    ) -> list[SectionContent]:
        """Build sections using library content adapted to target condition."""
        sections: list[SectionContent] = []

        # Get all section keys for this doc type
        dt_keys = sorted(
            k for k in self._library.sections.keys()
            if k.startswith(f"{doc_type}::")
        )

        for key in dt_keys:
            # Get best section (prefer same condition, else richest)
            best = self._harvester.get_best_section(
                self._library, doc_type, key.split("::", 1)[1],
                prefer_condition=condition.slug,
            )
            if not best:
                continue

            # Adapt content to target condition
            if best.source_condition == condition.slug:
                # Same condition — use as-is
                content = best.content
            else:
                # Different condition — adapt names
                content = self._harvester.adapt_content(
                    best, condition.slug, condition.display_name
                )

            # Enrich with condition-specific data
            content = self._enrich_with_condition_data(content, best, condition)

            # Build tables
            tables = []
            for td in best.table_data:
                adapted_rows = []
                for row in td.get("rows", []):
                    adapted_row = [
                        self._adapt_text(cell, best.source_condition,
                                         condition.slug, condition.display_name)
                        for cell in row
                    ]
                    adapted_rows.append(adapted_row)
                tables.append({
                    "headers": td.get("headers", []),
                    "rows": adapted_rows,
                    "caption": self._adapt_text(
                        td.get("caption", ""), best.source_condition,
                        condition.slug, condition.display_name,
                    ),
                })

            section = SectionContent(
                section_id=best.section_id,
                title=self._adapt_text(
                    best.title, best.source_condition,
                    condition.slug, condition.display_name
                ),
                content=content,
                tables=tables,
                confidence_label=(
                    ConfidenceLabel.MEDIUM.value
                    if best.source_condition != condition.slug
                    else None
                ),
            )

            # If content is thin and AI is available, enhance it
            if use_ai and self.has_ai and best.word_count < 50:
                ai_content = self._ai_enhance_section(
                    section, condition, doc_type
                )
                if ai_content:
                    section.content = ai_content
                    section.review_flags.append("AI_DRAFTED — REQUIRES CLINICAL REVIEW")

            sections.append(section)

        return sections

    def _enrich_with_condition_data(
        self,
        content: str,
        source_section: HarvestedSection,
        condition: ConditionSchema,
    ) -> str:
        """Add condition-specific data to adapted content."""
        # Replace ICD-10 placeholder
        content = re.sub(r"\([A-Z]\d{2}(?:\.\d)?\)", f"({condition.icd10})", content)

        return content

    def _adapt_text(
        self,
        text: str,
        source_slug: str,
        target_slug: str,
        target_name: str,
    ) -> str:
        """Replace source condition references with target condition."""
        from .rich_generator import _CONDITION_NAMES
        if source_slug in _CONDITION_NAMES:
            for name in _CONDITION_NAMES[source_slug]:
                text = re.sub(re.escape(name), target_name, text, flags=re.IGNORECASE)
        return text

    def _build_title(self, condition: ConditionSchema, doc_type: str, tier: Tier) -> str:
        _TITLES = {
            "handbook": "SOZO Clinical Handbook",
            "clinical_exam": "Clinical Examination Checklist",
            "evidence_based_protocol": "SOZO Evidence-Based Protocol",
            "all_in_one_protocol": "All-in-One Protocol",
            "phenotype_classification": "Phenotype Classification",
            "responder_tracking": "Responder Tracking",
            "psych_intake": "Psychological Intake & PRS Baseline",
            "network_assessment": "6-Network Bedside Assessment",
        }
        prefix = _TITLES.get(doc_type, doc_type.replace("_", " ").title())
        if tier == Tier.PARTNERS and "FNON" not in prefix:
            prefix = f"FNON {prefix}"
        return f"{prefix} — {condition.display_name}"

    def _ai_enhance_section(
        self,
        section: SectionContent,
        condition: ConditionSchema,
        doc_type: str,
    ) -> Optional[str]:
        """Use AI to write rich clinical prose for a thin section.

        The AI is given:
        - The section title and current content
        - The condition's clinical data
        - Instruction to match SOZO template style
        - Explicit instruction to NOT fabricate PMIDs or claims

        Returns enhanced content or None if AI is unavailable.
        """
        prompt = f"""You are a clinical document writer for SOZO Brain Center.
Write the content for the following section of a {doc_type.replace('_', ' ')} document
for {condition.display_name} ({condition.icd10}).

Section: {section.title}
Current content: {section.content[:200]}

Condition overview: {condition.overview[:500]}
Evidence quality: {condition.overall_evidence_quality.value}

RULES:
- Write in formal clinical English matching SOZO Brain Center document style
- Use evidence-graded language (e.g., "Evidence suggests..." not "It is proven that...")
- Do NOT fabricate PMIDs, journal names, or specific study results
- Do NOT invent clinical claims not supported by the condition data
- Include appropriate hedging for areas of limited evidence
- Keep to 150-300 words for this section
- Reference the condition's specific clinical features

Write the section content:"""

        try:
            if self._anthropic_key:
                return self._call_anthropic(prompt)
            elif self._openai_key:
                return self._call_openai(prompt)
        except Exception as e:
            logger.warning("AI enhancement failed for %s: %s", section.section_id, e)

        return None

    def _call_anthropic(self, prompt: str) -> Optional[str]:
        import httpx
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self._anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]

    def _call_openai(self, prompt: str) -> Optional[str]:
        import httpx
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._openai_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


# Re-export for adapt_text to avoid circular import
from ..template.learning.content_harvester import _CONDITION_NAMES
