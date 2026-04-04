"""Validate benchmark-attached DocumentSpec structure (schema + sanity checks)."""
from __future__ import annotations

from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport


def run_structured_spec_validation(
    document_spec: dict[str, Any] | None,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    if document_spec is None:
        return ValidatorReport(validator_id="structured_spec_validator", findings=[])

    require_sections = case_inputs.get("require_document_spec_sections", 1)
    min_sections = int(require_sections) if isinstance(require_sections, int) else 1

    try:
        from sozo_generator.schemas.documents import DocumentSpec

        spec = DocumentSpec.model_validate(document_spec)
    except Exception as exc:  # noqa: BLE001
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MALFORMED_STRUCTURED_OUTPUT.value,
                severity=Severity.HIGH,
                message="document_spec is not valid DocumentSpec JSON.",
                reasons=[str(exc)],
            )
        )
        return ValidatorReport(
            validator_id="structured_spec_validator",
            findings=findings,
        )

    if len(spec.sections) < min_sections:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MALFORMED_STRUCTURED_OUTPUT.value,
                severity=Severity.MEDIUM,
                message=f"DocumentSpec has too few sections ({len(spec.sections)} < {min_sections}).",
                reasons=["Canonical assembly should produce a non-trivial section tree."],
            )
        )

    empty_titles = sum(1 for s in spec.sections if not (s.title or "").strip())
    if empty_titles:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MALFORMED_STRUCTURED_OUTPUT.value,
                severity=Severity.MEDIUM,
                message=f"{empty_titles} top-level section(s) lack titles.",
                reasons=["Section titles support reviewer navigation and benchmark headings."],
            )
        )

    if not (spec.condition_slug or "").strip():
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MALFORMED_STRUCTURED_OUTPUT.value,
                severity=Severity.LOW,
                message="DocumentSpec.condition_slug is empty.",
                reasons=[],
            )
        )

    return ValidatorReport(validator_id="structured_spec_validator", findings=findings)
