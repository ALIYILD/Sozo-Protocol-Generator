"""Tests for sozo_generator.content.claim_tracer — claim traceability."""
from __future__ import annotations

import pytest

from sozo_generator.core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    DocumentType,
    EvidenceRelation,
    Modality,
    Tier,
)
from sozo_generator.schemas.contracts import EvidenceBundle, EvidenceItem
from sozo_generator.schemas.documents import DocumentSpec, SectionContent


# ── Helpers ─────────────────────────────────────────────────────────────


def _make_spec(sections: list[SectionContent] | None = None) -> DocumentSpec:
    """Build a minimal DocumentSpec for testing."""
    return DocumentSpec(
        document_type=DocumentType.CLINICAL_EXAM,
        tier=Tier.FELLOW,
        condition_slug="test",
        condition_name="Test Condition",
        title="Test Document",
        sections=sections or [],
    )


def _make_bundle(
    bundle_id: str,
    category: ClaimCategory,
    items: list[EvidenceItem] | None = None,
    confidence: ConfidenceLabel = ConfidenceLabel.HIGH,
) -> EvidenceBundle:
    return EvidenceBundle(
        bundle_id=bundle_id,
        condition_slug="test",
        category=category,
        items=items or [],
        confidence=confidence,
    )


def _make_evidence_item(
    pmid: str = "12345678",
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS,
) -> EvidenceItem:
    return EvidenceItem(pmid=pmid, title="Study", relation=relation)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# attach_claims_to_spec
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestAttachClaimsToSpec:
    def test_attaches_claims_to_matching_sections(self):
        from sozo_generator.content.claim_tracer import attach_claims_to_spec

        sections = [
            SectionContent(
                section_id="safety",
                title="Safety",
                content="Safety information here.",
            ),
            SectionContent(
                section_id="pathophysiology",
                title="Pathophysiology",
                content="Neural mechanisms.",
            ),
        ]
        spec = _make_spec(sections=sections)

        bundles = [
            _make_bundle(
                "b_safety",
                ClaimCategory.SAFETY,
                items=[_make_evidence_item(pmid="11111111")],
            ),
            _make_bundle(
                "b_patho",
                ClaimCategory.PATHOPHYSIOLOGY,
                items=[_make_evidence_item(pmid="22222222")],
            ),
        ]

        result = attach_claims_to_spec(spec, bundles, condition_references=[])
        safety_section = result.sections[0]
        patho_section = result.sections[1]

        assert len(safety_section.claims) == 1
        assert safety_section.evidence_bundle_id == "b_safety"

        assert len(patho_section.claims) == 1
        assert patho_section.evidence_bundle_id == "b_patho"

    def test_section_without_bundle_gets_insufficient(self):
        from sozo_generator.content.claim_tracer import attach_claims_to_spec

        sections = [
            SectionContent(
                section_id="safety",
                title="Safety",
                content="Safety section with no matching bundle.",
            ),
        ]
        spec = _make_spec(sections=sections)

        # Provide no matching bundle for safety
        bundles = [
            _make_bundle("b_patho", ClaimCategory.PATHOPHYSIOLOGY),
        ]

        result = attach_claims_to_spec(spec, bundles, condition_references=[])
        safety_section = result.sections[0]

        assert len(safety_section.claims) == 1
        assert safety_section.claims[0].insufficient_evidence is True
        assert safety_section.claims[0].requires_review is True

    def test_returns_same_spec_object(self):
        from sozo_generator.content.claim_tracer import attach_claims_to_spec

        spec = _make_spec(
            sections=[
                SectionContent(section_id="overview", title="Overview"),
            ]
        )
        result = attach_claims_to_spec(spec, [], [])
        assert result is spec

    def test_partial_section_id_match(self):
        from sozo_generator.content.claim_tracer import attach_claims_to_spec

        sections = [
            SectionContent(
                section_id="symptom_network_connectivity",
                title="Symptom Network",
            ),
        ]
        spec = _make_spec(sections=sections)
        bundles = [
            _make_bundle(
                "b_net",
                ClaimCategory.NETWORK_INVOLVEMENT,
                items=[_make_evidence_item()],
            ),
        ]
        result = attach_claims_to_spec(spec, bundles, [])
        # "symptom_network" is a partial match key in the map
        assert len(result.sections[0].claims) >= 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# build_claim_citation_map
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestBuildClaimCitationMap:
    def test_collects_all_claims(self):
        from sozo_generator.content.claim_tracer import (
            attach_claims_to_spec,
            build_claim_citation_map,
        )

        sections = [
            SectionContent(section_id="safety", title="Safety"),
            SectionContent(section_id="pathophysiology", title="Patho"),
        ]
        spec = _make_spec(sections=sections)
        bundles = [
            _make_bundle(
                "b_safety",
                ClaimCategory.SAFETY,
                items=[_make_evidence_item(pmid="11111111")],
            ),
            _make_bundle(
                "b_patho",
                ClaimCategory.PATHOPHYSIOLOGY,
                items=[_make_evidence_item(pmid="22222222")],
            ),
        ]
        spec = attach_claims_to_spec(spec, bundles, [])
        ccm = build_claim_citation_map(spec)

        assert ccm.condition_slug == "test"
        assert ccm.total_claims == 2
        assert len(ccm.claims) == 2

    def test_tracks_unsupported_claims(self):
        from sozo_generator.content.claim_tracer import (
            attach_claims_to_spec,
            build_claim_citation_map,
        )

        sections = [
            SectionContent(section_id="safety", title="Safety"),
        ]
        spec = _make_spec(sections=sections)
        # No matching bundles -> insufficient
        spec = attach_claims_to_spec(spec, [], [])
        ccm = build_claim_citation_map(spec)

        assert ccm.unsupported_claims == 1
        assert ccm.review_required_claims == 1

    def test_empty_spec(self):
        from sozo_generator.content.claim_tracer import build_claim_citation_map

        spec = _make_spec(sections=[])
        ccm = build_claim_citation_map(spec)
        assert ccm.total_claims == 0
        assert ccm.claims == []

    def test_nested_subsections(self):
        from sozo_generator.content.claim_tracer import (
            attach_claims_to_spec,
            build_claim_citation_map,
        )

        sub = SectionContent(
            section_id="contraindications",
            title="Contraindications",
        )
        parent = SectionContent(
            section_id="safety",
            title="Safety",
            subsections=[sub],
        )
        spec = _make_spec(sections=[parent])
        bundles = [
            _make_bundle(
                "b_safety",
                ClaimCategory.SAFETY,
                items=[_make_evidence_item()],
            ),
            _make_bundle(
                "b_contra",
                ClaimCategory.CONTRAINDICATIONS,
                items=[_make_evidence_item(pmid="99999999")],
            ),
        ]
        spec = attach_claims_to_spec(spec, bundles, [])
        ccm = build_claim_citation_map(spec)
        # Should have claims from both parent and subsection
        assert ccm.total_claims == 2
