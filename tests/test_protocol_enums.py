"""Tests for protocol lifecycle enums."""
from __future__ import annotations

import pytest

from sozo_generator.core.protocol_enums import (
    ProtocolStatus,
    UserRole,
    ReviewStatus,
    GenerationMethod,
    PersonalizationConfidence,
)


# ── ProtocolStatus transitions ────────────────────────────────────────────


class TestProtocolStatusTransitions:
    def test_draft_to_pending_review_valid(self):
        assert ProtocolStatus.DRAFT.can_transition_to(ProtocolStatus.PENDING_REVIEW) is True

    def test_draft_to_archived_valid(self):
        assert ProtocolStatus.DRAFT.can_transition_to(ProtocolStatus.ARCHIVED) is True

    def test_pending_review_to_approved_valid(self):
        assert ProtocolStatus.PENDING_REVIEW.can_transition_to(ProtocolStatus.APPROVED) is True

    def test_pending_review_to_rejected_valid(self):
        assert ProtocolStatus.PENDING_REVIEW.can_transition_to(ProtocolStatus.REJECTED) is True

    def test_approved_to_superseded_valid(self):
        assert ProtocolStatus.APPROVED.can_transition_to(ProtocolStatus.SUPERSEDED) is True

    def test_approved_to_archived_valid(self):
        assert ProtocolStatus.APPROVED.can_transition_to(ProtocolStatus.ARCHIVED) is True

    def test_rejected_to_draft_valid(self):
        assert ProtocolStatus.REJECTED.can_transition_to(ProtocolStatus.DRAFT) is True

    def test_archived_to_draft_invalid(self):
        assert ProtocolStatus.ARCHIVED.can_transition_to(ProtocolStatus.DRAFT) is False

    def test_archived_to_any_invalid(self):
        for target in ProtocolStatus:
            assert ProtocolStatus.ARCHIVED.can_transition_to(target) is False

    def test_superseded_to_any_invalid(self):
        for target in ProtocolStatus:
            assert ProtocolStatus.SUPERSEDED.can_transition_to(target) is False

    def test_draft_to_approved_invalid(self):
        """Cannot skip directly from DRAFT to APPROVED."""
        assert ProtocolStatus.DRAFT.can_transition_to(ProtocolStatus.APPROVED) is False

    def test_draft_to_rejected_invalid(self):
        assert ProtocolStatus.DRAFT.can_transition_to(ProtocolStatus.REJECTED) is False


# ── Terminal states ──────────────────────────────────────────────────────


class TestTerminalStates:
    def test_superseded_has_no_transitions(self):
        transitions = ProtocolStatus.valid_transitions()
        assert transitions[ProtocolStatus.SUPERSEDED] == set()

    def test_archived_has_no_transitions(self):
        transitions = ProtocolStatus.valid_transitions()
        assert transitions[ProtocolStatus.ARCHIVED] == set()

    def test_all_statuses_have_transition_entry(self):
        transitions = ProtocolStatus.valid_transitions()
        for status in ProtocolStatus:
            assert status in transitions


# ── UserRole values ──────────────────────────────────────────────────────


class TestUserRole:
    def test_clinician_value(self):
        assert UserRole.CLINICIAN.value == "clinician"

    def test_admin_value(self):
        assert UserRole.ADMIN.value == "admin"

    def test_readonly_value(self):
        assert UserRole.READONLY.value == "readonly"

    def test_all_roles_are_strings(self):
        for role in UserRole:
            assert isinstance(role.value, str)

    def test_expected_role_count(self):
        assert len(UserRole) == 5


# ── ReviewStatus values ──────────────────────────────────────────────────


class TestReviewStatus:
    def test_pending_value(self):
        assert ReviewStatus.PENDING.value == "pending"

    def test_approved_value(self):
        assert ReviewStatus.APPROVED.value == "approved"

    def test_rejected_value(self):
        assert ReviewStatus.REJECTED.value == "rejected"

    def test_revision_requested_value(self):
        assert ReviewStatus.REVISION_REQUESTED.value == "revision_requested"

    def test_expected_status_count(self):
        assert len(ReviewStatus) == 4


# ── GenerationMethod values ──────────────────────────────────────────────


class TestGenerationMethod:
    def test_all_methods_are_strings(self):
        for method in GenerationMethod:
            assert isinstance(method.value, str)

    def test_manual_value(self):
        assert GenerationMethod.MANUAL.value == "manual"

    def test_personalized_value(self):
        assert GenerationMethod.PERSONALIZED.value == "personalized"


# ── PersonalizationConfidence values ──────────────────────────────────────


class TestPersonalizationConfidence:
    def test_high_value(self):
        assert PersonalizationConfidence.HIGH.value == "high"

    def test_insufficient_value(self):
        assert PersonalizationConfidence.INSUFFICIENT.value == "insufficient"

    def test_expected_count(self):
        assert len(PersonalizationConfidence) == 4
