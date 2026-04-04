"""Evidence Validator — PMIDs, overclaims, unsupported clinical statements."""
from __future__ import annotations

import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

_PMID_RE = re.compile(r"(?:PMID[:\s#]*|pubmed\.gov/)(\d{1,9})\b", re.IGNORECASE)
_DOI_RE = re.compile(r"\b10\.\d{4,}/[^\s\]]+", re.IGNORECASE)

_OVERCLAIM_PHRASES = (
    "fda approved for",
    "guaranteed improvement",
    "cures parkinson",
    "cures motor symptoms",
    "proven to reverse",
    "completely safe",
    "no risk of",
    "definitely effective",
    "will eliminate dyskinesia",
)

_CERTAINTY_MECH = (
    "the mechanism is definitively",
    "we know with certainty that",
    "proven beyond doubt",
)


def _supports_sentence(sentence: str) -> bool:
    s = sentence.lower()
    if any(p in s for p in _OVERCLAIM_PHRASES):
        return False
    if any(p in s for p in _CERTAINTY_MECH):
        return False
    return True


def _actionable_sentence(sentence: str) -> bool:
    s = sentence.strip()
    low = s.lower()
    if len(s) < 40:
        return False
    cues = (
        " ma ",
        " ma.",
        "minute session",
        "sessions per week",
        "apply",
        "stimulate",
        "montage",
        "anode",
        "cathode",
        "recommended dose",
        "titration",
    )
    return any(c in low for c in cues)


def run_evidence_validation(
    text: str,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    pmids = set(_PMID_RE.findall(text))
    dois = _DOI_RE.findall(text)

    if case_inputs.get("require_pmids") and not pmids and not dois:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MISSING_CITATION.value,
                severity=Severity.HIGH,
                message="No PMID or DOI-like citation markers detected in draft.",
                reasons=["Task requires traceable literature identifiers; none found."],
            )
        )

    lowered = text.lower()
    for phrase in _OVERCLAIM_PHRASES:
        if phrase in lowered:
            idx = lowered.index(phrase)
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.REGULATORY_OVERCLAIM.value,
                    severity=Severity.HIGH,
                    message=f"Possible regulatory or efficacy overstatement: {phrase!r}",
                    reasons=[
                        "Clinical drafts should avoid guaranteed efficacy or "
                        "unsupported regulatory claims."
                    ],
                    locator=f"offset~{idx}",
                )
            )

    for phrase in _CERTAINTY_MECH:
        if phrase in lowered:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.UNSUPPORTED_CLAIM.value,
                    severity=Severity.MEDIUM,
                    message=f"High-certainty mechanism language: {phrase!r}",
                    reasons=[
                        "Prefer qualified mechanistic language unless tied to citations."
                    ],
                )
            )

    relaxed = case_inputs.get("relaxed_citation_check", False)
    if relaxed and (pmids or dois):
        pass
    else:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sent in sentences:
            if not _actionable_sentence(sent):
                continue
            if not _supports_sentence(sent):
                continue
            window = sent
            if not _PMID_RE.search(window) and "pmid" not in sent.lower():
                chunk_has_ref = bool(case_inputs.get("citation_optional_for_fixture"))
                if not chunk_has_ref and pmids and "reference" in lowered:
                    chunk_has_ref = True
                if not chunk_has_ref:
                    findings.append(
                        ValidationFinding(
                            code=FailureTaxonomy.EVIDENCE_GAP.value,
                            severity=Severity.MEDIUM,
                            message="Actionable protocol sentence lacks adjacent PMID/DOI marker.",
                            reasons=[
                                "Prefer linking stimulation parameters and montage instructions "
                                "to traceable references or flag as descriptive-only."
                            ],
                            locator=sent[:120],
                        )
                    )

    return ValidatorReport(validator_id="evidence_validator", findings=findings)
