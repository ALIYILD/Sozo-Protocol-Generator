"""Citation completeness — major claims vs reference coverage (heuristic)."""
from __future__ import annotations

import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

_CLAIM_VERBS = (
    "reduces bradykinesia",
    "improves gait",
    "restores function",
    "significantly decreases",
    "clinically proven",
)


def run_citation_completeness_check(
    text: str,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    low = text.lower()
    ref_section = "\n## references" in low or low.startswith("## references")

    for phrase in _CLAIM_VERBS:
        if phrase in low:
            idx = low.index(phrase)
            prev_nl = text.rfind("\n", 0, idx)
            next_nl = text.find("\n", idx)
            line = text[(prev_nl + 1) if prev_nl >= 0 else 0 : next_nl if next_nl >= 0 else len(text)]
            if not re.search(r"PMID|(?<!\bno )\bdoi\b|10\.\d{4,}/", line, re.IGNORECASE):
                findings.append(
                    ValidationFinding(
                        code=FailureTaxonomy.CITATION_WEAK_OR_MISMATCHED.value,
                        severity=Severity.MEDIUM,
                        message=f"Strong outcome claim may lack adjacent citation: {phrase!r}",
                        reasons=[
                            "Link efficacy or comparative claims to PMID-backed sources "
                            "or soften language for internal drafting."
                        ],
                    )
                )

    if case_inputs.get("require_references_section") and not ref_section:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MISSING_CITATION.value,
                severity=Severity.MEDIUM,
                message="Expected a references section for evidence mapping tasks.",
                reasons=["Add a references block or explicit evidence appendix."],
            )
        )

    return ValidatorReport(
        validator_id="citation_completeness_checker",
        findings=findings,
    )
