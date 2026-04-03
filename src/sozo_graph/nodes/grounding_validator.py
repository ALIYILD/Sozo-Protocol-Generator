"""
grounding_validator — validates all composed sections against evidence.

Type: Deterministic
Wraps: sozo_generator.grounding.validator.GroundingValidator
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("grounding_validator")
def grounding_validator(state: SozoGraphState) -> dict:
    """Validate composed sections against the evidence pool."""
    decisions = []
    protocol = state.get("protocol", {})
    evidence = state.get("evidence", {})
    condition = state.get("condition", {})

    composed = protocol.get("composed_sections", [])
    articles = evidence.get("articles", [])

    if not composed:
        decisions.append("No composed sections to validate")
        return {
            "protocol": {
                **protocol,
                "grounding_score": 0.0,
                "grounding_issues": [{"severity": "block", "message": "No sections composed"}],
            },
            "_decisions": decisions,
        }

    # Build set of valid evidence IDs
    valid_ids = set()
    for a in articles:
        if a.get("pmid"):
            valid_ids.add(a["pmid"])
        if a.get("doi"):
            valid_ids.add(a["doi"])

    # Validate each section
    all_issues = []
    total_citations = 0
    verified_citations = 0

    for section in composed:
        section_id = section.get("section_id", "unknown")
        cited = section.get("cited_evidence_ids", [])
        total_citations += len(cited)

        for eid in cited:
            if eid in valid_ids:
                verified_citations += 1
            else:
                all_issues.append({
                    "severity": "warning",
                    "section_id": section_id,
                    "message": f"Citation '{eid}' not found in evidence pool",
                })

        # Check claims have evidence
        for claim in section.get("claims", []):
            claim_eids = claim.get("evidence_ids", [])
            if not claim_eids:
                all_issues.append({
                    "severity": "block",
                    "section_id": section_id,
                    "message": f"Claim '{claim.get('claim_text', '')[:60]}' has no evidence IDs",
                })

        # Check for prohibited language
        content = section.get("content", "").lower()
        prohibited = [
            "proven to cure", "guaranteed", "100% effective",
            "fda-approved for neuromodulation",
        ]
        for phrase in prohibited:
            if phrase in content:
                all_issues.append({
                    "severity": "block",
                    "section_id": section_id,
                    "message": f"Prohibited language: '{phrase}'",
                })

    # Compute grounding score
    if total_citations > 0:
        grounding_score = verified_citations / total_citations
    else:
        grounding_score = 0.0

    blocking_issues = [i for i in all_issues if i["severity"] == "block"]

    decisions.append(
        f"Grounding: {verified_citations}/{total_citations} citations verified "
        f"(score: {grounding_score:.2f}), "
        f"{len(blocking_issues)} blocking issues, "
        f"{len(all_issues) - len(blocking_issues)} warnings"
    )

    return {
        "protocol": {
            **protocol,
            "grounding_score": round(grounding_score, 3),
            "grounding_issues": all_issues,
        },
        "_decisions": decisions,
    }
