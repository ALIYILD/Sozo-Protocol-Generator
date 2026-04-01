"""
Claim traceability — attaches structured claim objects to document sections,
linking clinical claims to their supporting evidence.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

from ..core.enums import ClaimCategory, ConfidenceLabel
from ..schemas.contracts import (
    ClaimCitationLink,
    ClaimCitationMap,
    EvidenceBundle,
    EvidenceItem,
    EvidenceRelation,
)
from ..schemas.documents import DocumentSpec, SectionClaim, SectionContent

logger = logging.getLogger(__name__)

# Map section IDs to likely claim categories
_SECTION_CATEGORY_MAP: dict[str, ClaimCategory] = {
    "overview": ClaimCategory.PATHOPHYSIOLOGY,
    "pathophysiology": ClaimCategory.PATHOPHYSIOLOGY,
    "anatomy": ClaimCategory.BRAIN_REGIONS,
    "networks": ClaimCategory.NETWORK_INVOLVEMENT,
    "symptom_network": ClaimCategory.NETWORK_INVOLVEMENT,
    "phenotypes": ClaimCategory.CLINICAL_PHENOTYPES,
    "phenotype_classification": ClaimCategory.CLINICAL_PHENOTYPES,
    "assessments": ClaimCategory.ASSESSMENT_TOOLS,
    "protocols": ClaimCategory.STIMULATION_PARAMETERS,
    "stimulation_targets": ClaimCategory.STIMULATION_TARGETS,
    "safety": ClaimCategory.SAFETY,
    "contraindications": ClaimCategory.CONTRAINDICATIONS,
    "inclusion_exclusion": ClaimCategory.INCLUSION_CRITERIA,
    "responder": ClaimCategory.RESPONDER_CRITERIA,
    "evidence_gaps": ClaimCategory.PATHOPHYSIOLOGY,
    "references": ClaimCategory.PATHOPHYSIOLOGY,
}

# PMID regex for extracting from reference text
_PMID_RE = re.compile(r"PMID[:\s]*(\d{7,9})", re.IGNORECASE)


def attach_claims_to_spec(
    spec: DocumentSpec,
    bundles: list[EvidenceBundle],
    condition_references: list[dict],
) -> DocumentSpec:
    """
    Walk all sections in a DocumentSpec and attach SectionClaim objects
    based on matching evidence bundles.

    This does not modify the prose content — it adds structured metadata
    that downstream renderers and QA can inspect.
    """
    bundle_by_category: dict[str, EvidenceBundle] = {}
    for b in bundles:
        bundle_by_category[b.category.value] = b

    # Extract PMIDs from condition references
    all_pmids = _extract_pmids_from_refs(condition_references)

    for section in spec.sections:
        _attach_claims_recursive(section, bundle_by_category, all_pmids)

    return spec


def _attach_claims_recursive(
    section: SectionContent,
    bundle_map: dict[str, EvidenceBundle],
    all_pmids: set[str],
) -> None:
    """Recursively attach claims to a section and its subsections."""
    category = _SECTION_CATEGORY_MAP.get(section.section_id)
    if category is None:
        # Try partial match
        for key, cat in _SECTION_CATEGORY_MAP.items():
            if key in section.section_id:
                category = cat
                break

    if category:
        bundle = bundle_map.get(category.value)
        if bundle:
            section.evidence_bundle_id = bundle.bundle_id
            claim = _create_claim_from_bundle(section, bundle, category)
            section.claims.append(claim)
            section.confidence_label = claim.confidence
            section.evidence_pmids = claim.supporting_pmids[:10]
        else:
            # No evidence bundle → mark as insufficient
            claim = SectionClaim(
                claim_id=f"claim-{section.section_id}-0",
                text=f"Content for {section.title}",
                category=category.value,
                confidence=ConfidenceLabel.INSUFFICIENT.value,
                insufficient_evidence=True,
                requires_review=True,
            )
            section.claims.append(claim)
            section.confidence_label = ConfidenceLabel.INSUFFICIENT.value

    # Recurse into subsections
    for sub in section.subsections:
        _attach_claims_recursive(sub, bundle_map, all_pmids)


def _create_claim_from_bundle(
    section: SectionContent,
    bundle: EvidenceBundle,
    category: ClaimCategory,
) -> SectionClaim:
    """Create a SectionClaim from an evidence bundle."""
    supporting = [
        i.pmid for i in bundle.items
        if i.relation == EvidenceRelation.SUPPORTS and i.pmid
    ]
    contradicting = [
        i.pmid for i in bundle.items
        if i.relation == EvidenceRelation.CONTRADICTS and i.pmid
    ]

    insufficient = bundle.confidence in (
        ConfidenceLabel.INSUFFICIENT,
        ConfidenceLabel.REVIEW_REQUIRED,
    )
    needs_review = insufficient or bundle.has_contradictions

    return SectionClaim(
        claim_id=f"claim-{section.section_id}-{bundle.bundle_id}",
        text=f"Clinical content for {section.title}",
        category=category.value,
        confidence=bundle.confidence.value,
        supporting_pmids=supporting,
        contradicting_pmids=contradicting,
        insufficient_evidence=insufficient,
        requires_review=needs_review,
    )


def build_claim_citation_map(
    spec: DocumentSpec,
) -> ClaimCitationMap:
    """
    Build a complete ClaimCitationMap from a DocumentSpec that has
    claims already attached to its sections.
    """
    claims: list[ClaimCitationLink] = []
    _collect_claims_recursive(spec.sections, claims)

    total = len(claims)
    unsupported = sum(1 for c in claims if c.insufficient_evidence)
    review_required = sum(1 for c in claims if c.requires_review)

    return ClaimCitationMap(
        condition_slug=spec.condition_slug,
        document_type=spec.document_type.value,
        tier=spec.tier.value,
        claims=claims,
        total_claims=total,
        unsupported_claims=unsupported,
        review_required_claims=review_required,
    )


def _collect_claims_recursive(
    sections: list[SectionContent],
    out: list[ClaimCitationLink],
) -> None:
    """Walk sections and collect all claims as ClaimCitationLink objects."""
    for section in sections:
        for sc in section.claims:
            link = ClaimCitationLink(
                claim_id=sc.claim_id,
                claim_text=sc.text,
                category=ClaimCategory(sc.category) if sc.category else ClaimCategory.PATHOPHYSIOLOGY,
                confidence=ConfidenceLabel(sc.confidence) if sc.confidence else ConfidenceLabel.INSUFFICIENT,
                pmids=sc.supporting_pmids,
                requires_review=sc.requires_review,
                insufficient_evidence=sc.insufficient_evidence,
            )
            out.append(link)
        _collect_claims_recursive(section.subsections, out)


def _extract_pmids_from_refs(refs: list[dict]) -> set[str]:
    """Extract all PMIDs from condition reference list."""
    pmids: set[str] = set()
    for ref in refs:
        text = ""
        if isinstance(ref, str):
            text = ref
        elif isinstance(ref, dict):
            text = " ".join(str(v) for v in ref.values())
        for match in _PMID_RE.findall(text):
            pmids.add(match)
    return pmids
