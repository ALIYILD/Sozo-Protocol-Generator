"""
evidence_sufficiency_gate — checks if there is enough evidence to proceed.

Type: Deterministic
Safety gate: soft block — interrupts to clinician if insufficient.
"""
from __future__ import annotations

from ..audit.logger import audited_node
from ..state import SozoGraphState


@audited_node("evidence_sufficiency_gate")
def evidence_sufficiency_gate(state: SozoGraphState) -> dict:
    """Check evidence sufficiency before proceeding to composition."""
    decisions = []
    evidence = state.get("evidence", {})

    sufficient = evidence.get("evidence_sufficient", False)
    summary = evidence.get("evidence_summary", {})
    grade_dist = summary.get("grade_distribution", {})
    gaps = evidence.get("evidence_gaps", [])

    if sufficient:
        decisions.append(
            f"Evidence sufficient: {grade_dist.get('A', 0)} Grade A, "
            f"{grade_dist.get('B', 0)} Grade B articles available"
        )
        return {
            "evidence": {**evidence, "evidence_sufficient": True},
            "_decisions": decisions,
        }

    # Insufficient — build gap report for clinician
    gap_report = list(gaps)
    if grade_dist.get("A", 0) == 0 and grade_dist.get("B", 0) == 0:
        gap_report.append("No Grade A or B evidence found for primary protocol parameters")
    if summary.get("total_articles", 0) < 5:
        gap_report.append(f"Only {summary.get('total_articles', 0)} articles after screening")

    decisions.append(
        f"Evidence INSUFFICIENT: {gap_report}. Flagging for clinician review."
    )

    return {
        "evidence": {
            **evidence,
            "evidence_sufficient": False,
            "evidence_gaps": gap_report,
        },
        "_decisions": decisions,
    }
