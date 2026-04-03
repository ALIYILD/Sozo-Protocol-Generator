"""Tests for the override promotion system."""
import json
import pytest
from pathlib import Path


# ── Model Tests ───────────────────────────────────────────────────────────


class TestPromotionModels:
    def test_promotion_candidate(self):
        from sozo_generator.knowledge.revision.promotion import PromotionCandidate
        c = PromotionCandidate(pattern_summary="test", repeat_count=3)
        assert c.candidate_id.startswith("cand-")
        assert c.repeat_count == 3

    def test_promotion_proposal(self):
        from sozo_generator.knowledge.revision.promotion import PromotionProposal, PromotionTarget
        p = PromotionProposal(
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            target_file="test.yaml",
            proposed_change_summary="Add column to table",
        )
        assert p.proposal_id.startswith("promo-")
        assert p.status == "draft"
        text = p.to_text()
        assert "PROMOTION PROPOSAL" in text

    def test_promotion_impact_report(self):
        from sozo_generator.knowledge.revision.promotion import PromotionImpactReport
        r = PromotionImpactReport(
            affected_yaml_files=["test.yaml"],
            affected_conditions=["parkinsons", "depression"],
            impacted_generation_paths=10,
        )
        assert "10 generation paths" in r.to_text()


# ── Detection Tests ──────────────────────────────────────────────────────


class TestCandidateDetection:
    def test_detect_from_revision_history(self):
        """Detection should find patterns from existing revision history files."""
        from sozo_generator.knowledge.revision.promotion import PromotionEngine
        engine = PromotionEngine()
        candidates = engine.detect_candidates()
        # May have candidates from test regenerations
        assert isinstance(candidates, list)

    def test_detect_returns_structured_candidates(self):
        from sozo_generator.knowledge.revision.promotion import PromotionEngine, PromotionCandidate
        engine = PromotionEngine()
        candidates = engine.detect_candidates()
        for c in candidates:
            assert isinstance(c, PromotionCandidate)
            assert c.candidate_id
            assert c.pattern_summary


# ── Proposal Creation Tests ──────────────────────────────────────────────


class TestProposalCreation:
    def test_create_proposal_from_candidate(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionCandidate, PromotionTarget
        )
        engine = PromotionEngine()
        candidate = PromotionCandidate(
            pattern_summary="Repeated pathophysiology expansion",
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            target_section="pathophysiology",
            repeat_count=4,
            confidence=0.8,
        )
        proposal = engine.create_proposal(candidate, "Expand pathophysiology section template")
        assert proposal.target_type == PromotionTarget.BLUEPRINT_SECTION
        assert proposal.status == "draft"

    def test_evidence_sensitive_flagging(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionCandidate, PromotionTarget
        )
        engine = PromotionEngine()
        candidate = PromotionCandidate(
            pattern_summary="Contraindication update",
            target_type=PromotionTarget.KNOWLEDGE_CONDITION,
            target_section="safety",
            evidence_sensitive=True,
        )
        proposal = engine.create_proposal(candidate)
        assert proposal.evidence_sensitive is True
        assert proposal.requires_clinical_approval is True
        assert not proposal.safe_to_apply


# ── Impact Analysis Tests ────────────────────────────────────────────────


class TestImpactAnalysis:
    def test_blueprint_impact(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionProposal, PromotionTarget
        )
        engine = PromotionEngine()
        proposal = PromotionProposal(
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            target_field="pathophysiology",
        )
        report = engine.analyze_impact(proposal)
        assert report.impacted_generation_paths > 0
        assert len(report.affected_conditions) >= 16  # All conditions

    def test_shared_rule_impact_is_broad(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionProposal, PromotionTarget
        )
        engine = PromotionEngine()
        proposal = PromotionProposal(
            target_type=PromotionTarget.SHARED_RULE,
            target_field="governance",
        )
        report = engine.analyze_impact(proposal)
        assert report.impacted_generation_paths > 100  # 16 conditions × 8 blueprints × 2 tiers


# ── Approval Workflow Tests ──────────────────────────────────────────────


class TestApprovalWorkflow:
    def test_approve_proposal(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionCandidate, PromotionTarget
        )
        engine = PromotionEngine()
        candidate = PromotionCandidate(
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            target_section="assessments",
        )
        proposal = engine.create_proposal(candidate, "Add timing column")
        approved = engine.approve(proposal, "Dr. Smith", "Reviewed and approved")
        assert approved.status == "approved"
        assert approved.approved_by == "Dr. Smith"

    def test_reject_proposal(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionCandidate, PromotionTarget
        )
        engine = PromotionEngine()
        candidate = PromotionCandidate(
            target_type=PromotionTarget.KNOWLEDGE_CONDITION,
            evidence_sensitive=True,
        )
        proposal = engine.create_proposal(candidate)
        rejected = engine.reject(proposal, "Dr. Smith", "Needs more evidence review")
        assert rejected.status == "rejected"

    def test_cannot_apply_unapproved(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionProposal, PromotionTarget
        )
        engine = PromotionEngine()
        proposal = PromotionProposal(
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            status="draft",
        )
        result = engine.apply_promotion(proposal)
        assert not result.applied
        assert "must be 'approved'" in result.error


# ── Dry Run Tests ────────────────────────────────────────────────────────


class TestDryRun:
    def test_dry_run_no_changes(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionProposal, PromotionTarget
        )
        engine = PromotionEngine()
        proposal = PromotionProposal(
            target_type=PromotionTarget.SHARED_RULE,
            target_file="sozo_knowledge/knowledge/shared/governance_rules.yaml",
            status="approved",
            approved_by="Dr. Test",
        )
        result = engine.apply_promotion(proposal, dry_run=True)
        assert not result.applied
        assert "DRY RUN" in result.warnings[0]
        assert result.validation_passed


# ── Policy Tests ─────────────────────────────────────────────────────────


class TestPromotionPolicy:
    def test_auto_promotable_types(self):
        from sozo_generator.knowledge.revision.promotion import (
            _AUTO_PROMOTABLE, PromotionTarget
        )
        assert PromotionTarget.BLUEPRINT_SECTION in _AUTO_PROMOTABLE
        assert PromotionTarget.BLUEPRINT_TABLE in _AUTO_PROMOTABLE
        assert PromotionTarget.SHARED_RULE in _AUTO_PROMOTABLE

    def test_clinical_review_types(self):
        from sozo_generator.knowledge.revision.promotion import (
            _REQUIRES_CLINICAL_REVIEW, PromotionTarget
        )
        assert PromotionTarget.KNOWLEDGE_CONDITION in _REQUIRES_CLINICAL_REVIEW
        assert PromotionTarget.KNOWLEDGE_CONTRAINDICATION in _REQUIRES_CLINICAL_REVIEW
        assert PromotionTarget.BLUEPRINT_SECTION not in _REQUIRES_CLINICAL_REVIEW

    def test_safe_to_apply_logic(self):
        from sozo_generator.knowledge.revision.promotion import (
            PromotionEngine, PromotionCandidate, PromotionTarget
        )
        engine = PromotionEngine()

        # Safe: blueprint section, not evidence-sensitive, high confidence
        safe_candidate = PromotionCandidate(
            target_type=PromotionTarget.BLUEPRINT_SECTION,
            confidence=0.8,
            evidence_sensitive=False,
        )
        safe_proposal = engine.create_proposal(safe_candidate)
        assert safe_proposal.safe_to_apply is True

        # Unsafe: knowledge condition, evidence-sensitive
        unsafe_candidate = PromotionCandidate(
            target_type=PromotionTarget.KNOWLEDGE_CONDITION,
            confidence=0.3,
            evidence_sensitive=True,
        )
        unsafe_proposal = engine.create_proposal(unsafe_candidate)
        assert unsafe_proposal.safe_to_apply is False
