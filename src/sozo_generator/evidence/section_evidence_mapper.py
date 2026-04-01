"""
Section-level evidence mapper — maps evidence items to document sections,
computes per-section evidence strength, and enables evidence-aware generation.

SAFETY: Evidence data comes from ConditionSchema references and PubMed cache.
This module NEVER fabricates PMIDs or clinical claims.
"""
from __future__ import annotations

import logging
import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
    EvidenceRelation,
    EvidenceType,
    Modality,
)
from ..schemas.condition import ConditionSchema
from ..schemas.contracts import EvidenceBundle, EvidenceItem, SectionEvidenceMap
from ..schemas.documents import DocumentSpec, SectionClaim, SectionContent

logger = logging.getLogger(__name__)

# ── Section-to-category mapping (reused from content/claim_tracer.py) ──

_SECTION_CATEGORY_MAP: dict[str, ClaimCategory] = {
    "overview": ClaimCategory.PATHOPHYSIOLOGY,
    "pathophysiology": ClaimCategory.PATHOPHYSIOLOGY,
    "anatomy": ClaimCategory.BRAIN_REGIONS,
    "brain_region": ClaimCategory.BRAIN_REGIONS,
    "networks": ClaimCategory.NETWORK_INVOLVEMENT,
    "symptom_network": ClaimCategory.NETWORK_INVOLVEMENT,
    "phenotypes": ClaimCategory.CLINICAL_PHENOTYPES,
    "phenotype_classification": ClaimCategory.CLINICAL_PHENOTYPES,
    "assessments": ClaimCategory.ASSESSMENT_TOOLS,
    "protocols": ClaimCategory.STIMULATION_PARAMETERS,
    "stimulation_targets": ClaimCategory.STIMULATION_TARGETS,
    "stimulation_parameters": ClaimCategory.STIMULATION_PARAMETERS,
    "modality": ClaimCategory.MODALITY_RATIONALE,
    "safety": ClaimCategory.SAFETY,
    "contraindications": ClaimCategory.CONTRAINDICATIONS,
    "inclusion": ClaimCategory.INCLUSION_CRITERIA,
    "exclusion": ClaimCategory.EXCLUSION_CRITERIA,
    "inclusion_exclusion": ClaimCategory.INCLUSION_CRITERIA,
    "responder": ClaimCategory.RESPONDER_CRITERIA,
    "evidence_gaps": ClaimCategory.PATHOPHYSIOLOGY,
    "references": ClaimCategory.PATHOPHYSIOLOGY,
}

# Category keywords for matching items to categories (from clusterer.py)
_CATEGORY_KEYWORDS: dict[ClaimCategory, list[str]] = {
    ClaimCategory.PATHOPHYSIOLOGY: [
        "pathophysiology", "mechanism", "neurobiology", "etiology",
        "neuroinflammation", "neurodegeneration",
    ],
    ClaimCategory.BRAIN_REGIONS: [
        "cortex", "cortical", "subcortical", "prefrontal", "dlpfc",
        "hippocampus", "amygdala", "brain region",
    ],
    ClaimCategory.NETWORK_INVOLVEMENT: [
        "network", "connectivity", "resting state", "connectome",
        "default mode", "salience", "central executive",
    ],
    ClaimCategory.CLINICAL_PHENOTYPES: [
        "phenotype", "subtype", "classification", "clinical presentation",
    ],
    ClaimCategory.ASSESSMENT_TOOLS: [
        "scale", "questionnaire", "measure", "assessment", "psychometric",
    ],
    ClaimCategory.STIMULATION_TARGETS: [
        "target", "montage", "electrode", "stimulation site",
    ],
    ClaimCategory.STIMULATION_PARAMETERS: [
        "dosage", "intensity", "duration", "parameter", "protocol",
    ],
    ClaimCategory.MODALITY_RATIONALE: [
        "rationale", "efficacy", "effectiveness", "mechanism of action",
    ],
    ClaimCategory.SAFETY: [
        "safety", "adverse", "side effect", "tolerability",
    ],
    ClaimCategory.CONTRAINDICATIONS: [
        "contraindication", "precaution", "risk", "seizure",
    ],
    ClaimCategory.RESPONDER_CRITERIA: [
        "responder", "predictor", "biomarker", "treatment response",
    ],
    ClaimCategory.INCLUSION_CRITERIA: [
        "inclusion", "eligibility", "selection",
    ],
    ClaimCategory.EXCLUSION_CRITERIA: [
        "exclusion", "ineligible",
    ],
}

# Evidence-level score mapping
_LEVEL_SCORE: dict[EvidenceLevel, float] = {
    EvidenceLevel.HIGHEST: 5.0,
    EvidenceLevel.HIGH: 4.0,
    EvidenceLevel.MEDIUM: 3.0,
    EvidenceLevel.LOW: 2.0,
    EvidenceLevel.VERY_LOW: 1.0,
    EvidenceLevel.MISSING: 0.0,
}

# Study types considered RCT-class
_RCT_TYPES: set[EvidenceType] = {
    EvidenceType.RCT,
    EvidenceType.LARGE_RCT,
    EvidenceType.CONTROLLED_TRIAL,
}

_SR_TYPES: set[EvidenceType] = {
    EvidenceType.SYSTEMATIC_REVIEW,
    EvidenceType.META_ANALYSIS,
    EvidenceType.CLINICAL_PRACTICE_GUIDELINE,
}

# Confidence-language mapping (from confidence.py)
_CONFIDENCE_LANGUAGE: dict[ConfidenceLabel, str] = {
    ConfidenceLabel.HIGH: "Evidence-based:",
    ConfidenceLabel.MEDIUM: "Supported by emerging evidence:",
    ConfidenceLabel.LOW: "Consensus-informed (limited evidence):",
    ConfidenceLabel.INSUFFICIENT: "\u26a0 Requires clinical review \u2014 evidence insufficient:",
    ConfidenceLabel.REVIEW_REQUIRED: "\u26a0 REVIEW REQUIRED:",
}

# PMID regex
_PMID_RE = re.compile(r"(\d{7,9})")

# Evidence-level string mapping for parsing
_LEVEL_STRINGS: dict[str, EvidenceLevel] = {
    "highest": EvidenceLevel.HIGHEST,
    "high": EvidenceLevel.HIGH,
    "medium": EvidenceLevel.MEDIUM,
    "low": EvidenceLevel.LOW,
    "very_low": EvidenceLevel.VERY_LOW,
}

# Evidence-type string mapping for parsing
_TYPE_STRINGS: dict[str, EvidenceType] = {
    "rct": EvidenceType.RCT,
    "large_rct": EvidenceType.LARGE_RCT,
    "systematic_review": EvidenceType.SYSTEMATIC_REVIEW,
    "meta_analysis": EvidenceType.META_ANALYSIS,
    "narrative_review": EvidenceType.NARRATIVE_REVIEW,
    "cohort_study": EvidenceType.COHORT_STUDY,
    "pilot_study": EvidenceType.PILOT_STUDY,
    "clinical_practice_guideline": EvidenceType.CLINICAL_PRACTICE_GUIDELINE,
    "consensus_statement": EvidenceType.CONSENSUS_STATEMENT,
    "controlled_trial": EvidenceType.CONTROLLED_TRIAL,
    "case_series": EvidenceType.CASE_SERIES,
    "case_report": EvidenceType.CASE_REPORT,
    "expert_opinion": EvidenceType.EXPERT_OPINION,
    "feasibility_study": EvidenceType.FEASIBILITY_STUDY,
    "indirect_evidence": EvidenceType.INDIRECT_EVIDENCE,
    "manual_entry": EvidenceType.MANUAL_ENTRY,
}


# ── Data classes ────────────────────────────────────────────────────────


@dataclass
class SectionEvidenceProfile:
    """Evidence profile for one document section."""

    section_id: str = ""
    article_count: int = 0
    highest_evidence_level: str = ""
    mean_evidence_score: float = 0.0
    median_year: Optional[int] = None
    newest_year: Optional[int] = None
    oldest_year: Optional[int] = None
    has_rct: bool = False
    has_systematic_review: bool = False
    has_contradictions: bool = False
    contradiction_notes: list[str] = field(default_factory=list)
    pmids: list[str] = field(default_factory=list)
    confidence: str = ""  # ConfidenceLabel value
    clinical_language_prefix: str = ""
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)


@dataclass
class DocumentEvidenceProfile:
    """Evidence profile for a full document."""

    condition_slug: str = ""
    total_articles: int = 0
    sections: dict[str, SectionEvidenceProfile] = field(default_factory=dict)
    weak_sections: list[str] = field(default_factory=list)
    unsupported_sections: list[str] = field(default_factory=list)
    conflicting_sections: list[str] = field(default_factory=list)
    overall_confidence: str = ""
    overall_evidence_score: float = 0.0
    outdated_sections: list[str] = field(default_factory=list)


# ── Main mapper class ──────────────────────────────────────────────────


class SectionEvidenceMapper:
    """Maps evidence to document sections and computes strength profiles."""

    def __init__(self, recency_years: int = 5, min_articles_for_confidence: int = 2):
        self.recency_years = recency_years
        self.min_articles = min_articles_for_confidence
        self._current_year = datetime.now().year

    def build_evidence_items_from_condition(
        self, condition: ConditionSchema,
    ) -> list[EvidenceItem]:
        """Extract EvidenceItem objects from a condition's references and assessment tools.
        Uses ONLY data already present in the ConditionSchema -- never fabricates."""
        items: list[EvidenceItem] = []

        # From references
        for ref in condition.references or []:
            item = self._ref_to_evidence_item(ref, condition.slug)
            if item is not None:
                items.append(item)

        # From assessment tools with PMIDs
        for tool in condition.assessment_tools or []:
            if tool.evidence_pmid and not tool.evidence_pmid.startswith("placeholder"):
                items.append(
                    EvidenceItem(
                        pmid=tool.evidence_pmid,
                        title=f"{tool.name} ({tool.abbreviation})",
                        evidence_type=EvidenceType.NARRATIVE_REVIEW,
                        evidence_level=EvidenceLevel.MEDIUM,
                        relation=EvidenceRelation.SUPPORTS,
                        condition_slug=condition.slug,
                    )
                )

        logger.info(
            "Built %d evidence items from condition '%s' (%d refs, %d assessment tools)",
            len(items),
            condition.slug,
            len(condition.references or []),
            len(condition.assessment_tools or []),
        )
        return items

    def map_to_sections(
        self,
        spec: DocumentSpec,
        items: list[EvidenceItem],
        modality_filter: Optional[Modality] = None,
        study_type_filter: Optional[EvidenceType] = None,
        max_years: Optional[int] = None,
    ) -> DocumentEvidenceProfile:
        """Map evidence items to document sections and build profiles."""
        effective_max_years = max_years if max_years is not None else self.recency_years

        # Apply global filters
        filtered_items = self._apply_filters(
            items, modality_filter, study_type_filter, effective_max_years,
        )

        # Categorise items
        items_by_category: dict[ClaimCategory, list[EvidenceItem]] = {}
        for item in filtered_items:
            cat = self._classify_item(item)
            items_by_category.setdefault(cat, []).append(item)

        # Build per-section profiles
        section_profiles: dict[str, SectionEvidenceProfile] = {}
        all_pmids: set[str] = set()

        for section in spec.sections:
            profile = self._build_section_profile(section, items_by_category)
            section_profiles[section.section_id] = profile
            all_pmids.update(profile.pmids)

            # Recurse into subsections
            for sub in section.subsections:
                sub_profile = self._build_section_profile(sub, items_by_category)
                section_profiles[sub.section_id] = sub_profile
                all_pmids.update(sub_profile.pmids)

        # Compute document-level aggregates
        weak = []
        unsupported = []
        conflicting = []
        outdated = []
        all_scores = []

        for sid, prof in section_profiles.items():
            if prof.article_count == 0:
                unsupported.append(sid)
            elif prof.article_count < self.min_articles or prof.mean_evidence_score < 2.0:
                weak.append(sid)

            if prof.has_contradictions:
                conflicting.append(sid)

            if prof.newest_year is not None and (self._current_year - prof.newest_year) > effective_max_years:
                outdated.append(sid)

            if prof.mean_evidence_score > 0:
                all_scores.append(prof.mean_evidence_score)

        overall_score = statistics.mean(all_scores) if all_scores else 0.0
        overall_conf = self._score_to_confidence(overall_score, len(all_pmids))

        doc_profile = DocumentEvidenceProfile(
            condition_slug=spec.condition_slug,
            total_articles=len(all_pmids),
            sections=section_profiles,
            weak_sections=weak,
            unsupported_sections=unsupported,
            conflicting_sections=conflicting,
            overall_confidence=overall_conf.value,
            overall_evidence_score=round(overall_score, 2),
            outdated_sections=outdated,
        )

        logger.info(
            "Mapped %d items to %d sections for '%s': "
            "%d weak, %d unsupported, %d conflicting, %d outdated",
            len(filtered_items),
            len(section_profiles),
            spec.condition_slug,
            len(weak),
            len(unsupported),
            len(conflicting),
            len(outdated),
        )
        return doc_profile

    def apply_evidence_to_spec(
        self, spec: DocumentSpec, profile: DocumentEvidenceProfile,
    ) -> DocumentSpec:
        """Annotate a DocumentSpec with evidence metadata from the profile.
        Sets confidence_label, evidence_pmids, and claims on each section."""
        for section in spec.sections:
            self._apply_profile_to_section(section, profile)
            for sub in section.subsections:
                self._apply_profile_to_section(sub, profile)
        return spec

    def get_weak_sections(self, profile: DocumentEvidenceProfile) -> list[str]:
        """Return section IDs with weak or no evidence support."""
        return list(set(profile.weak_sections + profile.unsupported_sections))

    def get_outdated_sections(
        self, profile: DocumentEvidenceProfile, max_age_years: int = 5,
    ) -> list[str]:
        """Return section IDs where the newest evidence is older than max_age_years."""
        outdated: list[str] = []
        for sid, prof in profile.sections.items():
            if prof.newest_year is not None:
                if (self._current_year - prof.newest_year) > max_age_years:
                    outdated.append(sid)
            elif prof.article_count == 0:
                # No evidence at all is also effectively outdated
                pass
        return outdated

    # ── Private helpers ─────────────────────────────────────────────────

    def _ref_to_evidence_item(
        self, ref: dict, condition_slug: str,
    ) -> Optional[EvidenceItem]:
        """Parse a dict from condition.references into an EvidenceItem.
        Returns None if the ref has no usable identifier."""
        if not isinstance(ref, dict):
            return None

        pmid = str(ref.get("pmid") or ref.get("PMID") or "").strip()
        doi = str(ref.get("doi") or ref.get("DOI") or "").strip() or None
        title = str(ref.get("title") or ref.get("Title") or "").strip()
        authors = str(ref.get("authors") or ref.get("authors_short") or "").strip()
        journal = str(ref.get("journal") or "").strip() or None
        year = ref.get("year") or ref.get("Year")
        if isinstance(year, str):
            try:
                year = int(year)
            except ValueError:
                year = None

        # Parse evidence level
        level_str = str(ref.get("evidence_level") or ref.get("level") or "medium").strip().lower()
        evidence_level = _LEVEL_STRINGS.get(level_str, EvidenceLevel.MEDIUM)

        # Parse evidence type
        type_str = str(ref.get("evidence_type") or ref.get("type") or "narrative_review").strip().lower()
        evidence_type = _TYPE_STRINGS.get(type_str, EvidenceType.NARRATIVE_REVIEW)

        # Must have at least a PMID or title
        if not pmid and not title:
            return None

        return EvidenceItem(
            pmid=pmid if pmid else None,
            doi=doi,
            title=title,
            authors_short=authors,
            journal=journal,
            year=year,
            evidence_type=evidence_type,
            evidence_level=evidence_level,
            relation=EvidenceRelation.SUPPORTS,
            condition_slug=condition_slug,
            key_finding=str(ref.get("key_finding") or ref.get("notes") or ""),
        )

    def _apply_filters(
        self,
        items: list[EvidenceItem],
        modality_filter: Optional[Modality],
        study_type_filter: Optional[EvidenceType],
        max_years: int,
    ) -> list[EvidenceItem]:
        """Apply modality, study type, and recency filters."""
        result: list[EvidenceItem] = []
        cutoff_year = self._current_year - max_years

        for item in items:
            # Modality filter
            if modality_filter is not None:
                if item.modalities and modality_filter not in item.modalities:
                    continue

            # Study type filter
            if study_type_filter is not None:
                if item.evidence_type != study_type_filter:
                    continue

            # Recency filter: only filter out items with a known year that is too old
            if item.year is not None and item.year < cutoff_year:
                continue

            result.append(item)
        return result

    def _classify_item(self, item: EvidenceItem) -> ClaimCategory:
        """Classify an evidence item into a ClaimCategory using keyword heuristics."""
        text = f"{item.title} {item.key_finding}".lower()

        scores: dict[ClaimCategory, float] = {}
        for category, keywords in _CATEGORY_KEYWORDS.items():
            score = sum(1.0 for kw in keywords if kw in text)
            if item.modalities and category in {
                ClaimCategory.STIMULATION_TARGETS,
                ClaimCategory.STIMULATION_PARAMETERS,
                ClaimCategory.SAFETY,
            }:
                score += 0.5
            scores[category] = score

        best = max(scores, key=lambda c: scores[c])
        if scores[best] == 0.0:
            return ClaimCategory.PATHOPHYSIOLOGY
        return best

    def _section_to_category(self, section_id: str) -> Optional[ClaimCategory]:
        """Map a section_id to a ClaimCategory."""
        # Direct match
        if section_id in _SECTION_CATEGORY_MAP:
            return _SECTION_CATEGORY_MAP[section_id]
        # Partial match
        for key, cat in _SECTION_CATEGORY_MAP.items():
            if key in section_id:
                return cat
        return None

    def _build_section_profile(
        self,
        section: SectionContent,
        items_by_category: dict[ClaimCategory, list[EvidenceItem]],
    ) -> SectionEvidenceProfile:
        """Build an evidence profile for a single section."""
        category = self._section_to_category(section.section_id)

        if category is None:
            return SectionEvidenceProfile(
                section_id=section.section_id,
                confidence=ConfidenceLabel.INSUFFICIENT.value,
                clinical_language_prefix=_CONFIDENCE_LANGUAGE[ConfidenceLabel.INSUFFICIENT],
                needs_review=True,
                review_reasons=["No category mapping for section"],
            )

        relevant_items = items_by_category.get(category, [])

        if not relevant_items:
            return SectionEvidenceProfile(
                section_id=section.section_id,
                confidence=ConfidenceLabel.INSUFFICIENT.value,
                clinical_language_prefix=_CONFIDENCE_LANGUAGE[ConfidenceLabel.INSUFFICIENT],
                needs_review=True,
                review_reasons=["No evidence items for this section"],
            )

        # Compute stats
        pmids = [i.pmid for i in relevant_items if i.pmid]
        years = [i.year for i in relevant_items if i.year is not None]
        scores = [_LEVEL_SCORE.get(i.evidence_level, 0.0) for i in relevant_items]
        mean_score = statistics.mean(scores) if scores else 0.0

        has_rct = any(i.evidence_type in _RCT_TYPES for i in relevant_items)
        has_sr = any(i.evidence_type in _SR_TYPES for i in relevant_items)

        # Determine highest evidence level
        max_score = max(scores) if scores else 0.0
        highest_level = ""
        for level, score_val in sorted(_LEVEL_SCORE.items(), key=lambda x: x[1], reverse=True):
            if max_score >= score_val:
                highest_level = level.value
                break

        # Check contradictions
        supporting = [i for i in relevant_items if i.relation == EvidenceRelation.SUPPORTS]
        contradicting = [i for i in relevant_items if i.relation == EvidenceRelation.CONTRADICTS]
        has_contradictions = len(supporting) > 0 and len(contradicting) > 0
        contradiction_notes = []
        if has_contradictions:
            contradiction_notes.append(
                f"{len(contradicting)} item(s) contradict {len(supporting)} supporting item(s)"
            )

        # Confidence
        confidence = self._score_to_confidence(mean_score, len(relevant_items))
        if has_contradictions:
            confidence = ConfidenceLabel.REVIEW_REQUIRED

        # Review needs
        needs_review = (
            confidence in (ConfidenceLabel.INSUFFICIENT, ConfidenceLabel.REVIEW_REQUIRED)
            or len(relevant_items) < self.min_articles
        )
        review_reasons = []
        if len(relevant_items) < self.min_articles:
            review_reasons.append(
                f"Only {len(relevant_items)} article(s); minimum is {self.min_articles}"
            )
        if has_contradictions:
            review_reasons.append("Contradicting evidence found")
        if mean_score < 2.0:
            review_reasons.append(f"Low mean evidence score: {mean_score:.1f}")

        return SectionEvidenceProfile(
            section_id=section.section_id,
            article_count=len(relevant_items),
            highest_evidence_level=highest_level,
            mean_evidence_score=round(mean_score, 2),
            median_year=int(statistics.median(years)) if years else None,
            newest_year=max(years) if years else None,
            oldest_year=min(years) if years else None,
            has_rct=has_rct,
            has_systematic_review=has_sr,
            has_contradictions=has_contradictions,
            contradiction_notes=contradiction_notes,
            pmids=pmids,
            confidence=confidence.value,
            clinical_language_prefix=_CONFIDENCE_LANGUAGE.get(confidence, "Note:"),
            needs_review=needs_review,
            review_reasons=review_reasons,
        )

    def _apply_profile_to_section(
        self,
        section: SectionContent,
        profile: DocumentEvidenceProfile,
    ) -> None:
        """Apply profile data to a single section."""
        sec_profile = profile.sections.get(section.section_id)
        if sec_profile is None:
            return

        section.confidence_label = sec_profile.confidence
        section.evidence_pmids = sec_profile.pmids[:10]

        # Add or update a SectionClaim reflecting the evidence state
        claim = SectionClaim(
            claim_id=f"evmap-{section.section_id}",
            text=f"Evidence-mapped content for {section.title}",
            category=self._section_to_category(section.section_id).value
            if self._section_to_category(section.section_id)
            else "",
            confidence=sec_profile.confidence,
            supporting_pmids=sec_profile.pmids,
            insufficient_evidence=sec_profile.confidence == ConfidenceLabel.INSUFFICIENT.value,
            requires_review=sec_profile.needs_review,
        )
        section.claims.append(claim)

        # Add review flags if needed
        if sec_profile.needs_review and sec_profile.review_reasons:
            for reason in sec_profile.review_reasons:
                flag = f"evidence_mapper: {reason}"
                if flag not in section.review_flags:
                    section.review_flags.append(flag)

    def _score_to_confidence(
        self, mean_score: float, item_count: int,
    ) -> ConfidenceLabel:
        """Convert a mean evidence score and count to a confidence label."""
        if item_count == 0:
            return ConfidenceLabel.INSUFFICIENT
        if mean_score >= 3.5 and item_count >= self.min_articles:
            return ConfidenceLabel.HIGH
        if mean_score >= 2.5 and item_count >= self.min_articles:
            return ConfidenceLabel.MEDIUM
        if mean_score >= 1.5:
            return ConfidenceLabel.LOW
        return ConfidenceLabel.INSUFFICIENT
