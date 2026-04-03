"""
review_processor — applies clinician edits and stamps approval/rejection.

Type: Deterministic
Runs after the clinician review interrupt resumes.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..audit.logger import audited_node
from ..state import SozoGraphState


@audited_node("review_processor")
def review_processor(state: SozoGraphState) -> dict:
    """Process clinician review decision: approve, reject, or apply edits."""
    decisions = []
    review = state.get("review", {})
    protocol = state.get("protocol", {})

    status = review.get("status", "pending")
    reviewer_id = review.get("reviewer_id", "unknown")
    revision = review.get("revision_number", 0)

    if status == "approved":
        decisions.append(f"Protocol APPROVED by {reviewer_id} (revision {revision})")
        return {
            "review": {
                **review,
                "approval_stamp": {
                    "reviewer_id": reviewer_id,
                    "reviewer_credentials": review.get("reviewer_credentials", ""),
                    "approved_at": datetime.now(timezone.utc).isoformat(),
                    "revision_number": revision,
                    "protocol_version": f"1.0.{revision}",
                },
            },
            "status": "approved",
            "_decisions": decisions,
        }

    elif status == "rejected":
        decisions.append(
            f"Protocol REJECTED by {reviewer_id}: {review.get('review_notes', 'No reason given')}"
        )
        return {
            "status": "rejected",
            "_decisions": decisions,
        }

    elif status == "edited":
        # Apply section edits
        edits = review.get("edits_applied", [])
        sections = list(protocol.get("composed_sections", []))

        for edit in edits:
            section_id = edit.get("section_id")
            field = edit.get("field", "content")
            new_value = edit.get("new_value")

            for section in sections:
                if section.get("section_id") == section_id:
                    section[field] = new_value
                    section["generation_method"] = "clinician_edited"
                    decisions.append(f"Applied edit to {section_id}.{field}")
                    break

        # Apply parameter overrides
        overrides = review.get("parameter_overrides", [])
        base_seq = dict(protocol.get("base_sequence", {}))

        for override in overrides:
            decisions.append(
                f"Parameter override: {override.get('parameter')} "
                f"{override.get('old_value')} → {override.get('new_value')} "
                f"(reason: {override.get('override_reason', 'none')})"
            )

        new_revision = revision + 1
        decisions.append(f"Edits applied — revision {revision} → {new_revision}")

        return {
            "protocol": {
                **protocol,
                "composed_sections": sections,
                "base_sequence": base_seq,
            },
            "review": {
                **review,
                "revision_number": new_revision,
                "status": "pending",  # needs re-review after edits
            },
            "_decisions": decisions,
        }

    decisions.append(f"Review status '{status}' — no action taken")
    return {"_decisions": decisions}
