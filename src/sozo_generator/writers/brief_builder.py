"""
Section Brief Builder — creates structured briefs for AI section writing.

Each brief contains everything the section writer needs:
- Template expectations (structure, length, tone)
- Condition-specific data from internal sources
- Evidence summary from research orchestration
- Style constraints from template profile
- Rules about what can and cannot be claimed
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from ..template_profiles.models import (
    DraftedSection,
    ResearchBundle,
    SectionBrief,
    TemplateSectionSpec,
    ToneProfile,
)
from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)


class BriefBuilder:
    """Builds structured briefs for section-by-section document generation.

    Usage:
        builder = BriefBuilder(condition, template_sections, research_bundles, tone)
        briefs = builder.build_all()
    """

    def __init__(
        self,
        condition: ConditionSchema,
        tier: str,
        doc_type: str,
        template_sections: list[TemplateSectionSpec],
        research_bundles: dict[str, ResearchBundle],
        tone_profile: ToneProfile,
    ):
        self.condition = condition
        self.tier = tier
        self.doc_type = doc_type
        self.sections = template_sections
        self.bundles = research_bundles
        self.tone = tone_profile

    def build_all(self) -> list[SectionBrief]:
        """Build briefs for all sections."""
        return [self.build_brief(s) for s in self.sections]

    def build_brief(self, section: TemplateSectionSpec) -> SectionBrief:
        """Build a brief for a single section."""
        bundle = self.bundles.get(section.section_id, ResearchBundle(
            condition_slug=self.condition.slug,
            section_id=section.section_id,
        ))

        # Extract relevant condition data for this section
        condition_data = self._extract_condition_data(section)

        # Determine required topics
        required_topics = self._determine_required_topics(section)

        # Determine expected visuals
        expected_visuals = self._determine_visuals(section)

        # Build citations list
        citations = []
        for source in bundle.sources:
            if source.pmid:
                citations.append({
                    "pmid": source.pmid,
                    "title": source.title,
                    "year": source.year,
                    "evidence_level": source.evidence_level,
                })

        return SectionBrief(
            target_condition=self.condition.slug,
            target_condition_name=self.condition.display_name,
            tier=self.tier,
            doc_type=self.doc_type,
            section_spec=section,
            style_constraints=self.tone,
            internal_condition_data=condition_data,
            evidence_summary=bundle.evidence_summary,
            citations_available=citations,
            required_topics=required_topics,
            expected_visuals=expected_visuals,
        )

    def _extract_condition_data(self, section: TemplateSectionSpec) -> dict[str, Any]:
        """Extract relevant condition data for a section."""
        data: dict[str, Any] = {
            "condition_name": self.condition.display_name,
            "icd10": self.condition.icd10,
            "slug": self.condition.slug,
        }

        sid = section.section_id.lower()

        if "overview" in sid:
            data["overview"] = self.condition.overview
            data["core_symptoms"] = self.condition.core_symptoms

        if "pathophysiology" in sid:
            data["pathophysiology"] = self.condition.pathophysiology

        if "brain" in sid or "anatomy" in sid or "structure" in sid:
            data["brain_regions"] = self.condition.key_brain_regions
            data["brain_descriptions"] = self.condition.brain_region_descriptions

        if "network" in sid or "fnon" in sid:
            data["network_profiles"] = [
                {
                    "network": p.network.value,
                    "dysfunction": p.dysfunction.value,
                    "relevance": p.relevance,
                    "severity": p.severity,
                    "primary": p.primary,
                }
                for p in self.condition.network_profiles
            ]
            data["fnon_rationale"] = self.condition.fnon_rationale

        if "phenotype" in sid:
            data["phenotypes"] = [
                {
                    "slug": p.slug,
                    "label": p.label,
                    "description": p.description,
                    "key_features": p.key_features,
                    "primary_networks": [n.value for n in p.primary_networks],
                }
                for p in self.condition.phenotypes
            ]

        if "protocol" in sid or "tdcs" in sid or "tps" in sid or "stimulation" in sid:
            data["protocols"] = [
                {
                    "protocol_id": p.protocol_id,
                    "label": p.label,
                    "modality": p.modality.value,
                    "target_region": p.target_region,
                    "parameters": p.parameters,
                    "rationale": p.rationale,
                    "evidence_level": p.evidence_level.value,
                    "off_label": p.off_label,
                }
                for p in self.condition.protocols
            ]
            data["stimulation_targets"] = [
                {
                    "modality": t.modality.value,
                    "target_region": t.target_region,
                    "rationale": t.rationale,
                    "evidence_level": t.evidence_level.value,
                    "off_label": t.off_label,
                }
                for t in self.condition.stimulation_targets
            ]

        if "safety" in sid or "contraindication" in sid:
            data["safety_notes"] = [
                {"category": n.category, "description": n.description, "severity": n.severity}
                for n in self.condition.safety_notes
            ]
            data["contraindications"] = self.condition.contraindications

        if "assessment" in sid:
            data["assessment_tools"] = [
                {
                    "name": t.name,
                    "abbreviation": t.abbreviation,
                    "domains": t.domains,
                    "timing": t.timing,
                    "evidence_pmid": t.evidence_pmid,
                }
                for t in self.condition.assessment_tools
            ]

        if "inclusion" in sid or "exclusion" in sid:
            data["inclusion_criteria"] = self.condition.inclusion_criteria
            data["exclusion_criteria"] = self.condition.exclusion_criteria

        if "responder" in sid:
            data["responder_criteria"] = self.condition.responder_criteria
            data["non_responder_pathway"] = self.condition.non_responder_pathway

        if "reference" in sid:
            data["references"] = self.condition.references

        if "governance" in sid:
            data["governance_rules"] = self.condition.governance_rules

        return data

    def _determine_required_topics(self, section: TemplateSectionSpec) -> list[str]:
        """Determine required topics based on section type and condition."""
        topics = []
        sid = section.section_id.lower()

        if "overview" in sid:
            topics.extend(["epidemiology", "clinical presentation", "treatment landscape"])
        if "pathophysiology" in sid:
            topics.extend(["neural mechanisms", "circuit dysfunction", "biomarkers"])
        if "protocol" in sid:
            topics.extend(["stimulation parameters", "session duration", "safety monitoring"])
        if "safety" in sid:
            topics.extend(["contraindications", "adverse effects", "stopping rules", "off-label disclosure"])

        # TPS always needs off-label warning (except Alzheimer's)
        if "tps" in sid and self.condition.slug != "alzheimers":
            topics.append("TPS off-label disclosure required")

        return topics

    def _determine_visuals(self, section: TemplateSectionSpec) -> list[str]:
        """Determine expected visuals for a section."""
        visuals = []
        sid = section.section_id.lower()

        if "brain" in sid or "anatomy" in sid:
            visuals.append("brain_map")
        if "network" in sid:
            visuals.append("network_diagram")
        if "protocol" in sid or "tdcs" in sid:
            visuals.append("protocol_panel")
        if "eeg" in sid or "montage" in sid:
            visuals.append("qeeg_topomap")

        if section.visual_expected and section.visual_type_hint:
            if section.visual_type_hint not in visuals:
                visuals.append(section.visual_type_hint)

        return visuals
