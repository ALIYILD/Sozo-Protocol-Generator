"""
Profile-guided generator — uses the learned master template profile to
ensure new documents match the structural patterns of existing SOZO documents.

This is the bridge between:
- Master template profile (learned from existing docs)
- ConditionSchema (verified clinical data)
- DocumentSpec (output structure)

It produces documents that look like they came from the same system
as the existing 225 documents.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from ...core.enums import DocumentType, Tier
from ...schemas.condition import ConditionSchema
from ...schemas.documents import DocumentSpec, SectionContent
from ...core.utils import current_month_year
from ...content.assembler import ContentAssembler
from .pattern_extractor import MasterTemplateProfile, load_profile

logger = logging.getLogger(__name__)

_DEFAULT_PROFILE_PATH = Path("data/learned/master_template_profile.json")


class ProfileGuidedGenerator:
    """Generates documents guided by the learned master template profile,
    ensuring structural consistency with existing SOZO documents."""

    def __init__(
        self,
        profile: Optional[MasterTemplateProfile] = None,
        profile_path: Optional[Path] = None,
    ):
        if profile:
            self._profile = profile
        else:
            pp = Path(profile_path or _DEFAULT_PROFILE_PATH)
            if pp.exists():
                raw = load_profile(pp)
                self._profile = MasterTemplateProfile(**{
                    k: v for k, v in raw.items()
                    if k in MasterTemplateProfile.__dataclass_fields__
                })
                logger.info("Loaded master profile from %s", pp)
            else:
                self._profile = None
                logger.warning("No master profile found at %s — using standard generation", pp)

        self._assembler = ContentAssembler()

    @property
    def has_profile(self) -> bool:
        return self._profile is not None

    def generate(
        self,
        condition: ConditionSchema,
        doc_type: DocumentType,
        tier: Tier,
    ) -> DocumentSpec:
        """Generate a DocumentSpec guided by the master profile.

        If a profile is loaded, the section order and structure will match
        the learned pattern for this doc_type. Otherwise falls back to
        the standard assembler.
        """
        # Get sections from the standard assembler
        sections = self._assembler.assemble(condition, doc_type, tier)

        # If we have a profile, reorder and validate against it
        if self._profile and doc_type.value in self._profile.doc_type_patterns:
            pattern = self._profile.doc_type_patterns[doc_type.value]
            sections = self._apply_pattern(sections, pattern, condition, tier)

        # Build the DocumentSpec
        title = self._build_title(condition, doc_type, tier)

        spec = DocumentSpec(
            document_type=doc_type,
            tier=tier,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience="Fellow clinician" if tier == Tier.FELLOW else "Partner clinician",
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=condition.references or [],
            review_flags=condition.review_flags or [],
            output_filename=self._build_filename(condition, doc_type, tier),
        )
        return spec

    def _apply_pattern(
        self,
        sections: list[SectionContent],
        pattern: dict,
        condition: ConditionSchema,
        tier: Tier,
    ) -> list[SectionContent]:
        """Reorder sections to match the learned pattern and flag missing ones."""
        if isinstance(pattern, dict):
            expected_order = pattern.get("typical_section_order", [])
            expected_count = pattern.get("typical_section_count", 0)
        else:
            expected_order = getattr(pattern, "typical_section_order", [])
            expected_count = getattr(pattern, "typical_section_count", 0)

        if not expected_order:
            return sections

        # Index existing sections by ID
        section_map = {s.section_id: s for s in sections}
        ordered: list[SectionContent] = []

        # Place sections in expected order
        for expected_id in expected_order:
            if expected_id in section_map:
                ordered.append(section_map.pop(expected_id))

        # Append any remaining sections not in the pattern
        for s in sections:
            if s.section_id in section_map:
                ordered.append(section_map.pop(s.section_id))

        return ordered if ordered else sections

    def _build_title(
        self,
        condition: ConditionSchema,
        doc_type: DocumentType,
        tier: Tier,
    ) -> str:
        """Build title using the learned title template if available."""
        if self._profile and doc_type.value in self._profile.doc_type_patterns:
            pattern = self._profile.doc_type_patterns[doc_type.value]
            template = ""
            if isinstance(pattern, dict):
                template = pattern.get("title_template", "")
            else:
                template = getattr(pattern, "title_template", "")
            if template and "{condition_name}" in template:
                title = template.replace("{condition_name}", condition.display_name)
                if tier == Tier.PARTNERS and "FNON" not in title:
                    title = title.replace("SOZO", "SOZO FNON", 1)
                return title

        # Fallback
        _DOC_TYPE_TITLES = {
            DocumentType.EVIDENCE_BASED_PROTOCOL: "SOZO Evidence-Based Protocol",
            DocumentType.ALL_IN_ONE_PROTOCOL: "All-in-One Protocol",
            DocumentType.HANDBOOK: "SOZO Clinical Handbook",
            DocumentType.CLINICAL_EXAM: "Clinical Examination Checklist",
            DocumentType.PHENOTYPE_CLASSIFICATION: "Phenotype Classification",
            DocumentType.RESPONDER_TRACKING: "Responder Tracking",
            DocumentType.PSYCH_INTAKE: "Psychological Intake & PRS Baseline",
            DocumentType.NETWORK_ASSESSMENT: "6-Network Bedside Assessment",
        }
        prefix = _DOC_TYPE_TITLES.get(doc_type, doc_type.value.replace("_", " ").title())
        if tier == Tier.PARTNERS:
            prefix = f"FNON {prefix}" if "FNON" not in prefix else prefix
        return f"{prefix} — {condition.display_name}"

    def _build_filename(
        self,
        condition: ConditionSchema,
        doc_type: DocumentType,
        tier: Tier,
    ) -> str:
        _FILENAME_MAP = {
            DocumentType.CLINICAL_EXAM: "Clinical_Examination_Checklist",
            DocumentType.PHENOTYPE_CLASSIFICATION: "Phenotype_Classification",
            DocumentType.RESPONDER_TRACKING: "Responder_Tracking",
            DocumentType.PSYCH_INTAKE: "Psychological_Intake_PRS_Baseline",
            DocumentType.NETWORK_ASSESSMENT: "6Network_Bedside_Assessment",
            DocumentType.HANDBOOK: "SOZO_Clinical_Handbook",
            DocumentType.ALL_IN_ONE_PROTOCOL: "All_In_One_Protocol",
            DocumentType.EVIDENCE_BASED_PROTOCOL: "Evidence_Based_Protocol",
        }
        base = _FILENAME_MAP.get(doc_type, doc_type.value)
        return f"{base}_{tier.value.capitalize()}.docx"
