"""Clinician review workflow API routes.

The review system is the clinician-in-the-loop gate. No protocol can be
approved without explicit clinician review and sign-off.

All endpoints return stub/mock data suitable for frontend development.
Real implementations will query the protocol store and audit log.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from sozo_auth.dependencies import require_reviewer

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/reviews",
    tags=["reviews"],
    dependencies=[Depends(require_reviewer)],
)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ReviewComment(BaseModel):
    """A single comment attached to a review.

    Attributes:
        section_slug: Protocol section this comment targets.
            ``None`` indicates a general / whole-protocol comment.
        text: Free-text comment body.
        severity: One of ``comment``, ``suggestion``, ``required_change``,
            ``blocking``.  Higher severities gate approval.
    """

    section_slug: Optional[str] = None
    text: str
    severity: str = Field(
        default="comment",
        description="comment | suggestion | required_change | blocking",
    )


class SubmitReviewRequest(BaseModel):
    """Payload for submitting a review decision.

    Attributes:
        decision: One of ``approve``, ``reject``, ``request_revision``.
        comments: Per-section or general comments.
        overall_notes: Optional free-text summary from the reviewer.
    """

    decision: str = Field(
        ...,
        description="approve | reject | request_revision",
    )
    comments: list[ReviewComment] = []
    overall_notes: Optional[str] = None


class ReviewResponse(BaseModel):
    """Persisted review record returned after submission."""

    review_id: UUID
    protocol_id: UUID
    protocol_version: int
    reviewer: str
    status: str
    comments: list[ReviewComment]
    overall_notes: Optional[str]
    reviewed_at: datetime
    signature_hash: Optional[str]


class ReviewQueueItem(BaseModel):
    """Summary row shown in the review queue list."""

    protocol_id: UUID
    version: int
    condition_name: str
    modality: str
    submitted_by: str
    submitted_at: datetime
    evidence_level: str
    qa_issues_count: int
    priority: str = Field(
        ...,
        description="normal | high (high when safety/QA flags present)",
    )


class ProtocolReviewView(BaseModel):
    """Full protocol data formatted for the review screen."""

    protocol_id: UUID
    version: int
    condition: dict
    modality: dict
    sections: list[dict]
    safety: dict
    evidence_summary: dict
    qa_report: dict
    previous_reviews: list[ReviewResponse]
    generation_metadata: dict


class ReviewDiffView(BaseModel):
    """Section-level diff between two protocol versions."""

    protocol_id: UUID
    from_version: int
    to_version: int
    changes: list[dict]


# ---------------------------------------------------------------------------
# Stub data helpers
# ---------------------------------------------------------------------------

_STUB_PROTOCOL_ID = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
_STUB_REVIEWER = "dr.chen@sozo-clinic.example"
_STUB_CREATOR = "generator@sozo.example"
_NOW = datetime.now(timezone.utc)


def _stub_queue_items() -> list[dict]:
    """Return a small set of realistic queue items for development."""
    return [
        ReviewQueueItem(
            protocol_id=_STUB_PROTOCOL_ID,
            version=2,
            condition_name="Major Depressive Disorder",
            modality="tDCS",
            submitted_by=_STUB_CREATOR,
            submitted_at=_NOW,
            evidence_level="Level I",
            qa_issues_count=1,
            priority="high",
        ).model_dump(mode="json"),
        ReviewQueueItem(
            protocol_id=UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901"),
            version=1,
            condition_name="Generalized Anxiety Disorder",
            modality="TMS",
            submitted_by=_STUB_CREATOR,
            submitted_at=_NOW,
            evidence_level="Level II",
            qa_issues_count=0,
            priority="normal",
        ).model_dump(mode="json"),
        ReviewQueueItem(
            protocol_id=UUID("c3d4e5f6-a7b8-9012-cdef-123456789012"),
            version=3,
            condition_name="Chronic Pain Syndrome",
            modality="tDCS",
            submitted_by=_STUB_CREATOR,
            submitted_at=_NOW,
            evidence_level="Level III",
            qa_issues_count=4,
            priority="high",
        ).model_dump(mode="json"),
    ]


def _stub_review_response(
    protocol_id: UUID,
    decision: str,
    comments: list[ReviewComment],
    overall_notes: Optional[str],
) -> ReviewResponse:
    """Build a ReviewResponse with deterministic stub values."""
    return ReviewResponse(
        review_id=uuid4(),
        protocol_id=protocol_id,
        protocol_version=2,
        reviewer=_STUB_REVIEWER,
        status=decision,
        comments=comments,
        overall_notes=overall_notes,
        reviewed_at=datetime.now(timezone.utc),
        signature_hash=None,
    )


def _stub_review_view(protocol_id: UUID, version: int) -> dict:
    """Build a full review-view payload with representative stub data."""
    return ProtocolReviewView(
        protocol_id=protocol_id,
        version=version,
        condition={
            "slug": "major-depressive-disorder",
            "display_name": "Major Depressive Disorder",
            "icd10": "F32",
            "category": "mood_disorders",
        },
        modality={
            "slug": "tdcs",
            "display_name": "Transcranial Direct Current Stimulation",
            "class": "non_invasive_brain_stimulation",
        },
        sections=[
            {
                "slug": "patient_selection",
                "title": "Patient Selection Criteria",
                "content": "Adults aged 18-65 with confirmed MDD diagnosis (DSM-5)...",
                "evidence_citations": [
                    {"pmid": "31234567", "title": "tDCS for MDD: a meta-analysis", "level": "I"},
                ],
                "qa_status": "pass",
            },
            {
                "slug": "stimulation_parameters",
                "title": "Stimulation Parameters",
                "content": "Anode over left DLPFC (F3), cathode over right supraorbital...",
                "evidence_citations": [
                    {"pmid": "30987654", "title": "Optimal tDCS montage for depression", "level": "II"},
                ],
                "qa_status": "warning",
                "qa_issues": [
                    {
                        "id": "qa-001",
                        "severity": "WARNING",
                        "message": "Current density exceeds 0.06 mA/cm² — verify electrode size.",
                    },
                ],
            },
            {
                "slug": "safety_monitoring",
                "title": "Safety & Monitoring",
                "content": "Monitor for skin irritation, phosphenes, headache...",
                "evidence_citations": [],
                "qa_status": "flag",
                "qa_issues": [
                    {
                        "id": "qa-002",
                        "severity": "WARNING",
                        "message": "No evidence citation for seizure risk threshold claim.",
                    },
                ],
            },
        ],
        safety={
            "contraindications": ["metallic cranial implants", "history of seizures"],
            "warnings": ["monitor for skin irritation under electrodes"],
            "emergency_protocol": "Discontinue stimulation immediately if seizure occurs.",
        },
        evidence_summary={
            "total_citations": 12,
            "level_I": 3,
            "level_II": 5,
            "level_III": 4,
            "coverage_pct": 85.0,
            "weakest_section": "safety_monitoring",
        },
        qa_report={
            "total_issues": 2,
            "by_severity": {"BLOCK": 0, "WARNING": 2, "INFO": 0},
            "issues": [
                {
                    "id": "qa-001",
                    "section": "stimulation_parameters",
                    "severity": "WARNING",
                    "message": "Current density exceeds 0.06 mA/cm².",
                    "overridden": False,
                },
                {
                    "id": "qa-002",
                    "section": "safety_monitoring",
                    "severity": "WARNING",
                    "message": "No evidence citation for seizure risk threshold claim.",
                    "overridden": False,
                },
            ],
        },
        previous_reviews=[],
        generation_metadata={
            "generator_version": "1.0.0",
            "blueprint": "evidence_based_protocol",
            "generated_at": _NOW.isoformat(),
            "knowledge_snapshot": "2026-03-15",
        },
    ).model_dump(mode="json")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/queue",
    response_model=dict,
    summary="List protocols pending review",
)
async def get_review_queue(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    condition: Optional[str] = Query(None, description="Filter by condition slug"),
    priority: Optional[str] = Query(None, description="Filter by priority: normal | high"),
):
    """Return the queue of protocols awaiting clinician review.

    Results are sorted by submission time with **high-priority** items
    (those carrying safety or QA flags) listed first.

    Pagination is 1-indexed; the response includes ``total`` for the client
    to compute page count.
    """
    items = _stub_queue_items()

    # Apply filters on stub data
    if condition:
        items = [
            i for i in items
            if condition.lower() in i["condition_name"].lower()
        ]
    if priority:
        items = [i for i in items if i["priority"] == priority]

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/queue/count",
    response_model=dict,
    summary="Pending review count",
)
async def get_review_queue_count():
    """Return the count of protocols pending review.

    Intended for badge / notification display on the frontend.
    """
    items = _stub_queue_items()
    return {
        "pending": len(items),
        "high_priority": sum(1 for i in items if i["priority"] == "high"),
    }


@router.get(
    "/{protocol_id}/review-view",
    response_model=dict,
    summary="Full protocol review view",
)
async def get_review_view(
    protocol_id: UUID,
    version: Optional[int] = Query(None, description="Specific version; latest if omitted"),
):
    """Return the complete protocol data formatted for the review screen.

    Includes:
    - Full protocol content organised by section
    - Per-section evidence citations with levels
    - QA issues grouped by severity
    - Safety warnings and contraindications
    - Previous review history for this protocol
    - Generation metadata (blueprint, version, timestamp)
    """
    effective_version = version if version is not None else 2
    return _stub_review_view(protocol_id, effective_version)


@router.get(
    "/{protocol_id}/diff",
    response_model=dict,
    summary="Version diff",
)
async def get_version_diff(
    protocol_id: UUID,
    from_version: int = Query(..., ge=1, description="Baseline version"),
    to_version: int = Query(..., ge=1, description="Target version"),
):
    """Return a section-level diff between two protocol versions.

    Useful for reviewing what changed after a revision request.
    Each entry in ``changes`` identifies the section, the type of change,
    and a textual summary of the delta.
    """
    if from_version >= to_version:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_version must be less than to_version.",
        )

    diff = ReviewDiffView(
        protocol_id=protocol_id,
        from_version=from_version,
        to_version=to_version,
        changes=[
            {
                "section_slug": "stimulation_parameters",
                "change_type": "modified",
                "summary": "Electrode size updated from 25 cm² to 35 cm² to reduce current density.",
                "old_snippet": "...electrode size: 25 cm²...",
                "new_snippet": "...electrode size: 35 cm²...",
            },
            {
                "section_slug": "safety_monitoring",
                "change_type": "modified",
                "summary": "Added evidence citation for seizure risk threshold (PMID 31345678).",
                "old_snippet": "...seizure risk is low...",
                "new_snippet": "...seizure risk is low (Bikson et al., 2016; PMID 31345678)...",
            },
        ],
    )
    return diff.model_dump(mode="json")


@router.post(
    "/{protocol_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit review decision",
)
async def submit_review(protocol_id: UUID, request: SubmitReviewRequest):
    """Submit a review decision for a protocol.

    **Decision types:**

    - ``approve`` -- Protocol transitions to APPROVED status.
      Enforces the **four-eyes principle**: the approving clinician must
      differ from the protocol creator.
    - ``reject`` -- Protocol transitions to REJECTED status.
      At least one comment is required explaining the rejection reason.
    - ``request_revision`` -- Protocol returns to DRAFT status.
      At least one comment with severity ``required_change`` must be
      included so the author knows what to fix.

    An audit event is created for every decision regardless of outcome.

    Raises:
        400: Invalid decision value.
        409: Protocol is not in PENDING_REVIEW status.
        403: Reviewer is the same as the protocol creator (four-eyes violation).
        422: Missing required comments for reject / request_revision.
    """
    valid_decisions = {"approve", "reject", "request_revision"}
    if request.decision not in valid_decisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid decision '{request.decision}'. "
                f"Must be one of: {', '.join(sorted(valid_decisions))}."
            ),
        )

    # Stub: simulate four-eyes check (would compare against real creator)
    # In production, fetch protocol.created_by and compare to current user.

    if request.decision == "reject" and not request.comments:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Rejection requires at least one comment explaining the reason.",
        )

    if request.decision == "request_revision":
        has_required_change = any(
            c.severity == "required_change" for c in request.comments
        )
        if not has_required_change:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Revision requests must include at least one comment "
                    "with severity 'required_change'."
                ),
            )

    logger.info(
        "Review submitted for protocol %s: decision=%s, comments=%d",
        protocol_id,
        request.decision,
        len(request.comments),
    )

    review = _stub_review_response(
        protocol_id=protocol_id,
        decision=request.decision,
        comments=request.comments,
        overall_notes=request.overall_notes,
    )
    return review


@router.get(
    "/{protocol_id}/reviews",
    response_model=dict,
    summary="List all reviews for a protocol",
)
async def list_reviews(protocol_id: UUID):
    """Return the full review history for a protocol across all versions.

    Results are ordered chronologically (oldest first).
    """
    # Stub: return one historical review plus indication of structure
    past_review = ReviewResponse(
        review_id=UUID("d4e5f6a7-b8c9-0123-def0-123456789abc"),
        protocol_id=protocol_id,
        protocol_version=1,
        reviewer=_STUB_REVIEWER,
        status="request_revision",
        comments=[
            ReviewComment(
                section_slug="stimulation_parameters",
                text="Current density too high for the stated electrode size. Please recalculate.",
                severity="required_change",
            ),
        ],
        overall_notes="Promising protocol but safety parameters need adjustment.",
        reviewed_at=_NOW,
        signature_hash=None,
    )
    return {
        "protocol_id": str(protocol_id),
        "reviews": [past_review.model_dump(mode="json")],
    }


@router.post(
    "/{protocol_id}/sign",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Digitally sign an approved protocol",
)
async def sign_protocol(protocol_id: UUID):
    """Generate a lightweight digital signature for an approved protocol.

    Computes a SHA-256 hash over the protocol content, reviewer identity,
    and current timestamp.  This hash is stored alongside the protocol for
    audit trail purposes.

    Raises:
        409: Protocol is not in APPROVED status (stub always succeeds).
    """
    # In production: verify protocol.status == APPROVED, load full content
    timestamp = datetime.now(timezone.utc)
    payload = f"{protocol_id}|{_STUB_REVIEWER}|{timestamp.isoformat()}"
    signature_hash = hashlib.sha256(payload.encode()).hexdigest()

    logger.info(
        "Protocol %s signed by %s — hash=%s",
        protocol_id,
        _STUB_REVIEWER,
        signature_hash[:16],
    )

    return {
        "protocol_id": str(protocol_id),
        "reviewer": _STUB_REVIEWER,
        "signed_at": timestamp.isoformat(),
        "signature_hash": signature_hash,
    }


@router.get(
    "/{protocol_id}/evidence-check",
    response_model=dict,
    summary="Detailed evidence verification",
)
async def get_evidence_check(protocol_id: UUID):
    """Return a detailed evidence verification report for review.

    Covers:
    - Per-section evidence coverage percentage
    - Claims with low or missing evidence support
    - Contradicting evidence pairs (if any)
    - Review flags raised by the QA engine
    """
    return {
        "protocol_id": str(protocol_id),
        "sections": [
            {
                "slug": "patient_selection",
                "coverage_pct": 95.0,
                "citations_count": 4,
                "low_evidence_claims": [],
            },
            {
                "slug": "stimulation_parameters",
                "coverage_pct": 80.0,
                "citations_count": 5,
                "low_evidence_claims": [
                    {
                        "claim": "2 mA is optimal for DLPFC stimulation in MDD",
                        "current_level": "III",
                        "note": "Based on single RCT; awaiting replication.",
                    },
                ],
            },
            {
                "slug": "safety_monitoring",
                "coverage_pct": 60.0,
                "citations_count": 3,
                "low_evidence_claims": [
                    {
                        "claim": "Seizure risk below 0.01% at stated parameters",
                        "current_level": "missing",
                        "note": "No direct citation found; inferred from general tDCS safety literature.",
                    },
                ],
            },
        ],
        "contradictions": [
            {
                "claim_a": "2 mA provides superior antidepressant effect (PMID 30987654)",
                "claim_b": "No dose-response relationship found above 1 mA (PMID 31111111)",
                "resolution_status": "unresolved",
            },
        ],
        "qa_flags": [
            {
                "id": "qa-002",
                "section": "safety_monitoring",
                "severity": "WARNING",
                "message": "No evidence citation for seizure risk threshold claim.",
            },
        ],
    }


@router.post(
    "/{protocol_id}/override-qa",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Override a QA issue",
)
async def override_qa_issue(
    protocol_id: UUID,
    issue_id: str = Query(..., description="QA issue identifier to override"),
    justification: str = Query(
        ...,
        min_length=10,
        description="Clinician justification for the override (min 10 chars)",
    ),
):
    """Override a WARNING-level QA issue with a clinician justification.

    Only ``WARNING``-severity issues may be overridden. ``BLOCK``-level
    issues cannot be bypassed and must be resolved in the protocol content.

    An audit event is created recording the override, the justification,
    and the clinician identity.

    Raises:
        400: Issue is BLOCK-level and cannot be overridden.
        404: Issue ID not found on this protocol.
    """
    # Stub: simulate a BLOCK-level check
    if issue_id.startswith("block-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Issue '{issue_id}' is BLOCK-level and cannot be overridden. "
                "Resolve the underlying problem in the protocol content."
            ),
        )

    logger.info(
        "QA issue %s overridden on protocol %s — justification: %s",
        issue_id,
        protocol_id,
        justification[:80],
    )

    return {
        "protocol_id": str(protocol_id),
        "issue_id": issue_id,
        "overridden": True,
        "overridden_by": _STUB_REVIEWER,
        "overridden_at": datetime.now(timezone.utc).isoformat(),
        "justification": justification,
    }
