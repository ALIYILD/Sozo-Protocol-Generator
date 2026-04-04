"""Protocol Structure Validator — headings, optional SozoProtocol JSON."""
from __future__ import annotations

import json
import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

_HEADING_RE = re.compile(r"^#+\s*(.+)$", re.MULTILINE)


def _headings(text: str) -> list[str]:
    return [m.groups()[0].strip().lower() for m in _HEADING_RE.finditer(text)]


def run_protocol_structure_validation(
    text: str,
    *,
    case_inputs: dict[str, Any],
    structured_protocol: dict[str, Any] | None = None,
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    required = case_inputs.get("required_headings") or case_inputs.get(
        "required_sections",
    )
    if isinstance(required, list) and required:
        have = set(_headings(text))
        for h in required:
            key = str(h).strip().lower()
            if key not in have and not any(key in x for x in have):
                findings.append(
                    ValidationFinding(
                        code=FailureTaxonomy.STRUCTURE_VIOLATION.value,
                        severity=Severity.MEDIUM,
                        message=f"Missing expected heading/section: {h!r}",
                        reasons=[
                            "Structured protocol drafts should include required sections "
                            "for internal QA comparability."
                        ],
                    )
                )

    proto = structured_protocol or case_inputs.get("protocol_json")
    if proto:
        try:
            from sozo_generator.schemas.protocol import SozoProtocol

            SozoProtocol.model_validate(proto)
        except Exception as exc:  # noqa: BLE001 — surface validation errors as findings
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.STRUCTURE_VIOLATION.value,
                    severity=Severity.HIGH,
                    message="structured protocol JSON does not conform to SozoProtocol.",
                    reasons=[str(exc)],
                )
            )

    fenced = re.findall(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    for block in fenced[:1]:
        try:
            obj = json.loads(block)
            from sozo_generator.schemas.protocol import SozoProtocol

            SozoProtocol.model_validate(obj)
        except Exception as exc:  # noqa: BLE001
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.STRUCTURE_VIOLATION.value,
                    severity=Severity.MEDIUM,
                    message="Fenced JSON block is not valid SozoProtocol.",
                    reasons=[str(exc)],
                )
            )

    monitoring = case_inputs.get("require_monitoring_section", False)
    if monitoring:
        blob = text.lower()
        if "monitoring" not in blob and "impedance" not in blob:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.STRUCTURE_VIOLATION.value,
                    severity=Severity.MEDIUM,
                    message="Monitoring / impedance content not detected.",
                    reasons=[
                        "tDCS-style internal drafts typically document monitoring "
                        "expectations for clinician review."
                    ],
                )
            )

    return ValidatorReport(
        validator_id="protocol_structure_validator",
        findings=findings,
    )
