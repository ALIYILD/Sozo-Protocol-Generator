"""
Condition onboarding -- handles unknown/new conditions that are not yet
in the validated registry. Creates draft ConditionSchema with conservative
defaults and mandatory review requirements.

SAFETY: Draft conditions have lower confidence and always require review.
"""
from __future__ import annotations

import logging
from typing import Optional

from ..schemas.condition import ConditionSchema, NetworkProfile, SafetyNote
from ..core.enums import EvidenceLevel, NetworkKey, NetworkDysfunction, ReviewStatus

logger = logging.getLogger(__name__)

# Standard safety notes that apply to ALL conditions
_UNIVERSAL_SAFETY = [
    SafetyNote(
        category="contraindication",
        description="Implanted metallic devices in the skull",
        severity="absolute",
    ),
    SafetyNote(
        category="contraindication",
        description="Active seizure disorder (relative)",
        severity="high",
    ),
    SafetyNote(
        category="contraindication",
        description="Pregnancy (relative — insufficient evidence)",
        severity="high",
    ),
    SafetyNote(
        category="precaution",
        description="All neuromodulation at SOZO is off-label unless CE/FDA approved for specific indication",
        severity="moderate",
    ),
    SafetyNote(
        category="monitoring",
        description="Monitor for adverse events at every session",
        severity="moderate",
    ),
]


class ConditionOnboarder:
    """Creates draft condition profiles for conditions not in the validated registry."""

    def is_known_condition(self, slug: str) -> bool:
        """Check if a condition is in the validated registry."""
        try:
            from ..conditions.registry import get_registry
            return get_registry().exists(slug)
        except Exception:
            return False

    def create_draft_condition(
        self,
        slug: str,
        display_name: str,
        icd10: str = "",
        overview: str = "",
    ) -> ConditionSchema:
        """Create a minimal draft ConditionSchema with conservative defaults.

        Draft conditions:
        - Have overall_evidence_quality = MISSING
        - Have review_flags indicating draft status
        - Include universal safety notes
        - Have empty protocols (must be added by clinician)
        - Are clearly marked as unvalidated
        """
        # Build with conservative defaults
        return ConditionSchema(
            slug=slug,
            display_name=display_name,
            icd10=icd10 or "DRAFT",
            overview=overview or (
                f"[DRAFT CONDITION — NOT YET VALIDATED]\n\n"
                f"{display_name} has been onboarded as a draft condition. "
                f"All clinical content requires review and validation by a qualified clinician "
                f"before any documents can be used for clinical purposes.\n\n"
                f"Evidence quality: INSUFFICIENT — no validated evidence bundle exists."
            ),
            pathophysiology="[REQUIRES CLINICAL INPUT — Draft condition]",
            safety_notes=list(_UNIVERSAL_SAFETY),
            contraindications=[
                "Implanted metallic devices in skull",
                "Active seizure disorder (relative)",
                "[Additional condition-specific contraindications must be added by clinician]",
            ],
            review_flags=[
                "DRAFT_CONDITION",
                "REQUIRES_CLINICAL_VALIDATION",
                "NO_EVIDENCE_BUNDLE",
                "ALL_SECTIONS_REQUIRE_REVIEW",
            ],
            overall_evidence_quality=EvidenceLevel.MISSING,
            evidence_gaps=[
                "No evidence bundle exists for this condition",
                "All clinical claims require validation",
                "Treatment protocols must be added by qualified clinician",
            ],
            version="0.1-draft",
        )

    def get_default_review_status(self, condition: ConditionSchema) -> str:
        """Return the appropriate default review status for a condition.
        Draft/low-evidence conditions default to NEEDS_REVIEW."""
        if "DRAFT_CONDITION" in (condition.review_flags or []):
            return ReviewStatus.NEEDS_REVIEW.value
        if condition.overall_evidence_quality in (EvidenceLevel.MISSING, EvidenceLevel.VERY_LOW):
            return ReviewStatus.NEEDS_REVIEW.value
        if condition.overall_evidence_quality == EvidenceLevel.LOW:
            return ReviewStatus.NEEDS_REVIEW.value
        return ReviewStatus.DRAFT.value

    def is_draft(self, condition: ConditionSchema) -> bool:
        """Check if a condition is a draft."""
        return "DRAFT_CONDITION" in (condition.review_flags or [])
